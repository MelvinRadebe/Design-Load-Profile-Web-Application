# database_manager.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
import sys
from typing import List, Optional
from default_data_provider import DefaultDataProvider


class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self):
        self.db_file = self._get_db_path()
        self.time_periods = self._make_time_periods()
        
    def _get_db_path(self) -> str:
        """Determine database file path"""
        if getattr(sys, 'frozen', False):
            return os.path.join(os.path.dirname(sys.executable), "load_profile.db")
        else:
            return os.path.join(os.path.expanduser("~"), "load_profile.db")
    
    def _make_time_periods(self) -> List[str]:
        """Build 12×2h intervals with wrap to midnight (last ends 00:00)"""
        periods = []
        for i in range(0, 24, 2):
            start = f"{i:02d}:00"
            end = f"{(i + 2) % 24:02d}:00"  # 22:00–00:00
            periods.append(f"{start}–{end}")
        return periods
    
    def init_db(self) -> None:
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        # Create appliances table with Use Time % column
        c.execute('''
            CREATE TABLE IF NOT EXISTS appliances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Appliance TEXT,
                Quantity INTEGER,
                "Power (W)" REAL,
                "Duty Cycle (%)" REAL,
                "Power Factor" REAL,
                "Use Time (%)" REAL,
                "00:00–02:00" INTEGER,
                "02:00–04:00" INTEGER,
                "04:00–06:00" INTEGER,
                "06:00–08:00" INTEGER,
                "08:00–10:00" INTEGER,
                "10:00–12:00" INTEGER,
                "12:00–14:00" INTEGER,
                "14:00–16:00" INTEGER,
                "16:00–18:00" INTEGER,
                "18:00–20:00" INTEGER,
                "20:00–22:00" INTEGER,
                "22:00–00:00" INTEGER,
                Priority TEXT,
                Room TEXT,
                "Apparent Power (VA)" REAL,
                "Total Daily Energy (Wh)" REAL
            )
        ''')

        # Create change log table
        c.execute('''
            CREATE TABLE IF NOT EXISTS change_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_type TEXT,
                appliance_id INTEGER,
                appliance_name TEXT,
                change_details TEXT,
                timestamp TEXT
            )
        ''')

        conn.commit()
        conn.close()
    
    def migrate_time_columns(self) -> None:
        """Migrate old time column format if needed"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("PRAGMA table_info(appliances)")
            cols = [row[1] for row in c.fetchall()]

            if "22:00–24:00" in cols and "22:00–00:00" not in cols:
                c.execute('ALTER TABLE appliances ADD COLUMN "22:00–00:00" INTEGER DEFAULT 0')
                c.execute('UPDATE appliances SET "22:00–00:00" = "22:00–24:00"')
                conn.commit()
                try:
                    c.execute('ALTER TABLE appliances DROP COLUMN "22:00–24:00"')
                    conn.commit()
                except Exception:
                    pass  # Older SQLite versions don't support DROP COLUMN
            conn.close()
        except Exception as e:
            st.warning(f"Time-column migration warning: {e}")
    
    def update_schema(self) -> None:
        """Update database schema if needed"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("PRAGMA table_info(appliances)")
            columns = [row[1] for row in c.fetchall()]
            if "Use Time (%)" not in columns:
                c.execute('ALTER TABLE appliances ADD COLUMN "Use Time (%)" REAL DEFAULT 50')
                conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"Error updating database: {e}")
    
    def load_data(self) -> pd.DataFrame:
        """Load data from database"""
        try:
            conn = sqlite3.connect(self.db_file)
            df = pd.read_sql_query("SELECT * FROM appliances", conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def save_data(self, new_df: pd.DataFrame, old_df: Optional[pd.DataFrame] = None) -> bool:
        """Save data to database with change logging"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            if old_df is not None:
                old_df = old_df.set_index('id')
                new_df_indexed = new_df.set_index('id')

                deleted_ids = set(old_df.index) - set(new_df_indexed.index)
                for id_ in deleted_ids:
                    appliance_name = old_df.loc[id_, 'Appliance']
                    c.execute(
                        "INSERT INTO change_log (change_type, appliance_id, appliance_name, change_details, timestamp) VALUES (?, ?, ?, ?, ?)",
                        ('DELETE', id_, appliance_name, f"Deleted appliance: {appliance_name}", datetime.now().isoformat())
                    )
                    c.execute("DELETE FROM appliances WHERE id = ?", (id_,))

                for id_ in new_df_indexed.index:
                    if id_ in old_df.index:
                        if not new_df_indexed.loc[id_].equals(old_df.loc[id_]):
                            changes = {col: new_df_indexed.loc[id_, col] for col in new_df_indexed.columns if new_df_indexed.loc[id_, col] != old_df.loc[id_, col]}
                            c.execute(
                                "INSERT INTO change_log (change_type, appliance_id, appliance_name, change_details, timestamp) VALUES (?, ?, ?, ?, ?)",
                                ('UPDATE', id_, new_df_indexed.loc[id_, 'Appliance'], f"Updated: {changes}", datetime.now().isoformat())
                            )
                    else:
                        c.execute(
                            "INSERT INTO change_log (change_type, appliance_id, appliance_name, change_details, timestamp) VALUES (?, ?, ?, ?, ?)",
                            ('INSERT', id_, new_df_indexed.loc[id_, 'Appliance'], f"Added new appliance: {new_df_indexed.loc[id_, 'Appliance']}", datetime.now().isoformat())
                        )

            new_df.to_sql('appliances', conn, if_exists='replace', index=True)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error saving data: {e}")
            return False
    
    def initialize_with_default_data(self) -> None:
        """Initialize database with default data if empty"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM appliances")
            if c.fetchone()[0] == 0:
                default_data = DefaultDataProvider().get_default_data()
                df = pd.DataFrame(default_data, columns=[
                    "Appliance", "Quantity", "Power (W)", "Duty Cycle (%)", "Power Factor", "Use Time (%)"
                ] + self.time_periods + ["Priority", "Room"])
                df["Apparent Power (VA)"] = (df["Power (W)"] / df["Power Factor"]).round(1)
                df["Total Daily Energy (Wh)"] = 0
                df.to_sql('appliances', conn, if_exists='replace', index=True, index_label='id')
            conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"Error initializing database: {e}")