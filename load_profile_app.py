# load_profile_app.py - Main Application File
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Tuple

from database_manager import DatabaseManager
from data_validator import DataValidator
from energy_calculator import EnergyCalculator
from chart_generator import ChartGenerator


class LoadProfileApp:
    """Main application class that coordinates all components"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.data_validator = DataValidator()
        self.energy_calculator = EnergyCalculator(self.db_manager.time_periods)
        self.chart_generator = ChartGenerator(self.db_manager.time_periods)
        self._initialize_app()
    
    def _initialize_app(self) -> None:
        """Initialize the application"""
        # Initialize database
        self.db_manager.init_db()
        self.db_manager.migrate_time_columns()
        self.db_manager.update_schema()
        self.db_manager.initialize_with_default_data()
        
        # Configure Streamlit
        st.set_page_config(
            page_title="Load Profile for a Grid-Tied PV System: (Catalogue Method)", 
            layout="wide"
        )
    
    def run(self) -> None:
        """Run the main application"""
        st.title("🔆 Load Profile for a Grid-Tied PV System: (Catalogue Method)🔆")
        
        # Display explanatory note
        st.info("""
        **Note on "Use Time (%)" Column**: This column represents the percentage of time an appliance is ON during each 2-hour period when selected. For example, if an appliance is typically used for 1 hour in a 2-hour period, set this to 50%. This helps in accurately estimating energy consumption based on actual usage patterns.
        """)
        
        # Load and process data
        df = self.db_manager.load_data()
        if df.empty:
            st.error("No data available. Please check database connection.")
            st.stop()
        
        # Store original data for change detection
        if 'original_df' not in st.session_state:
            st.session_state.original_df = df.copy()
        
        # Data editing interface
        edited_df = self._create_data_editor(df)
        
        # Validate and process edited data
        edited_df = self.data_validator.validate_df(edited_df)
        edited_df["Apparent Power (VA)"] = (edited_df["Power (W)"] / edited_df["Power Factor"]).round(1)
        
        # Calculate energy and power data
        energy_df, average_power_df, instantaneous_power_df = self._calculate_energy_and_power(edited_df)
        
        # Calculate total daily energy
        edited_df["Total Daily Energy (Wh)"] = energy_df[self.db_manager.time_periods].sum(axis=1)
        total_energy = edited_df["Total Daily Energy (Wh)"].sum()
        
        # Save changes button
        if st.button("Save Changes"):
            if self.db_manager.save_data(edited_df, st.session_state.original_df):
                st.session_state.original_df = edited_df.copy()
                st.success("Changes saved to database!")
            else:
                st.error("Failed to save changes!")
        
        # Display results
        self._display_appliance_table(edited_df)
        self._display_charts(edited_df, energy_df, average_power_df, total_energy)
        self._display_summaries(edited_df, energy_df, total_energy)
        self._display_comparison_charts(edited_df)
    
    def _create_data_editor(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create the data editor interface with time columns grouped together"""
        column_config = {
            "Power (W)": st.column_config.NumberColumn(min_value=0),
            "Quantity": st.column_config.NumberColumn(min_value=0),
            "Power Factor": st.column_config.NumberColumn(min_value=0.01, max_value=1.0),
            "Duty Cycle (%)": st.column_config.NumberColumn(min_value=0, max_value=100),
            "Use Time (%)": st.column_config.NumberColumn(
                min_value=0, max_value=100,
                help="Percentage of time appliance is ON during each 2-hour period when selected"
            ),
        }
        for t in self.db_manager.time_periods:
            column_config[t] = st.column_config.CheckboxColumn()

    # --- Force the editor to keep all 2h time slots together ---
        desired_order = (
            ["Appliance", "Quantity", "Power (W)", "Duty Cycle (%)", "Power Factor", "Use Time (%)"]
            + self.db_manager.time_periods
            + ["Priority", "Room", "Apparent Power (VA)", "Total Daily Energy (Wh)"]
     )
    # Keep any unexpected/existing columns safely at the end
        ordered = [c for c in desired_order if c in df.columns] + [c for c in df.columns if c not in desired_order]
        df = df.reindex(columns=ordered)
    # -----------------------------------------------------------

        return st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            key="editor",
            column_config=column_config
    )
    def _calculate_energy_and_power(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Calculate energy and power dataframes"""
        energy_df = df.apply(self.energy_calculator.compute_energy, axis=1)
        energy_df["Appliance"] = df["Appliance"]

        average_power_df = df.apply(self.energy_calculator.compute_average_power, axis=1)
        average_power_df["Appliance"] = df["Appliance"]

        instantaneous_power_df = df.apply(self.energy_calculator.compute_instantaneous_power, axis=1)
        instantaneous_power_df["Appliance"] = df["Appliance"]

        return energy_df, average_power_df, instantaneous_power_df
    
    def _display_appliance_table(self, df: pd.DataFrame) -> None:
        """Display the appliance table"""
        st.markdown("### 📋 Appliance Table with Energy Calculations")
        display_columns = [
            "Appliance", "Quantity", "Power (W)", "Use Time (%)", 
            "Power Factor", "Apparent Power (VA)", "Total Daily Energy (Wh)", 
            "Priority", "Room"
        ]
        st.dataframe(df[display_columns], use_container_width=True)
    
    def _display_charts(self, df: pd.DataFrame, energy_df: pd.DataFrame, 
                       average_power_df: pd.DataFrame, total_energy: float) -> None:
        """Display main charts"""
        # Power consumption over time
        st.markdown("### 🔌 Power Consumption Over Time")
        plot_df = average_power_df.set_index("Appliance")[self.db_manager.time_periods].T
        plot_df["Total Load (W)"] = plot_df.sum(axis=1)
        
        power_chart = self.chart_generator.create_power_consumption_chart(plot_df)
        st.plotly_chart(power_chart, use_container_width=True)
        
        # Optional stacked bar chart for energy
        if st.checkbox("Show stacked bar by appliance (Energy)"):
            stacked_chart = self.chart_generator.create_stacked_energy_chart(energy_df)
            st.plotly_chart(stacked_chart, use_container_width=True)
        
        # Individual appliance bar chart
        st.markdown("### 📊 Individual Appliance Daily Energy Consumption (Bar Chart)")
        
        # Check for zero-energy appliances
        zero_energy_appliances = df.loc[df["Total Daily Energy (Wh)"] == 0, "Appliance"].tolist()
        if zero_energy_appliances:
            st.warning(f"Appliances with zero energy consumption: {', '.join(zero_energy_appliances)}")
        
        daily_energy_chart = self.chart_generator.create_daily_energy_bar_chart(df)
        if daily_energy_chart:
            st.plotly_chart(daily_energy_chart, use_container_width=True)
        
        # Time series charts
        self._display_time_series_charts(df, average_power_df)
    
    def _display_time_series_charts(self, df: pd.DataFrame, average_power_df: pd.DataFrame) -> None:
        """Display time series charts with filtering options"""
        # Main time series chart
        st.markdown("### 📈 Individual Appliance Power Consumption Time Series")
        
        timeseries_chart = self.chart_generator.create_time_series_chart(
            average_power_df, 
            "Power Consumption Time Series - All Appliances (Including Use Time %)"
        )
        st.plotly_chart(timeseries_chart, use_container_width=True)
        
        # Filter options
        st.markdown("#### 🔍 Filter Appliances by Category")
        col1, col2, col3 = st.columns(3)
        with col1:
            show_essential = st.checkbox("Show Essential Only", value=False)
        with col2:
            show_medium = st.checkbox("Show Medium Priority", value=True)
        with col3:
            show_non_essential = st.checkbox("Show Non-Essential", value=True)
        
        if show_essential or show_medium or show_non_essential:
            priorities_to_show = []
            if show_essential:
                priorities_to_show.append("essential")
            if show_medium:
                priorities_to_show.append("medium")
            if show_non_essential:
                priorities_to_show.append("non-essential")
            
            filtered_df = df[df["Priority"].isin(priorities_to_show)]
            filtered_power_df = filtered_df.apply(self.energy_calculator.compute_average_power, axis=1)
            filtered_power_df["Appliance"] = filtered_df["Appliance"]
            
            # Create filtered chart with priority-based coloring
            fig_filtered = self._create_filtered_time_series_chart(filtered_df, filtered_power_df)
            st.plotly_chart(fig_filtered, use_container_width=True)
    
    def _create_filtered_time_series_chart(self, filtered_df: pd.DataFrame, 
                                          filtered_power_df: pd.DataFrame) -> go.Figure:
        """Create filtered time series chart with priority-based colors"""
        fig_filtered = go.Figure()

        for i, appliance in enumerate(filtered_power_df["Appliance"]):
            appliance_data = filtered_power_df[filtered_power_df["Appliance"] == appliance][self.db_manager.time_periods].values[0]
            priority = filtered_df[filtered_df["Appliance"] == appliance]["Priority"].values[0]
            if max(appliance_data) > 0:
                color = '#FF6B6B' if priority == 'essential' else '#FFD93D' if priority == 'medium' else '#45B7D1'
                fig_filtered.add_trace(go.Scatter(
                    x=self.db_manager.time_periods,
                    y=appliance_data,
                    mode='lines+markers',
                    name=f'{appliance} ({priority})',
                    line=dict(color=color, width=2),
                    marker=dict(size=6),
                    hovertemplate=f'<b>{appliance}</b><br>' +
                                 f'Priority: {priority}<br>' +
                                 'Time: %{x}<br>' +
                                 'Avg Power: %{y:.1f} W<br>' +
                                 '<extra></extra>'
                ))

        fig_filtered.update_layout(
            title="Filtered Power Consumption Time Series (Including Use Time %)",
            xaxis_title="Time Period",
            yaxis_title="Power Consumption (W)",
            height=600,
            hovermode='x unified',
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
            margin=dict(r=250)
        )
        fig_filtered.update_xaxes(showgrid=False)
        fig_filtered.update_yaxes(showgrid=False)
        return fig_filtered
    
    def _display_summaries(self, df: pd.DataFrame, energy_df: pd.DataFrame, total_energy: float) -> None:
        """Display load summaries by category"""
        peak_load_real, peak_load_apparent = self.energy_calculator.calculate_peak_loads(df)
        
        # 1. All Appliances Summary (OFF-GRID)
        st.markdown("### 1. 🟢 All Appliances (OFF-GRID)")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Daily Energy", f"{total_energy:.0f} Wh", f"{total_energy/1000:.2f} kWh")
        col2.metric("Peak Real Power", f"{peak_load_real:.0f} W", f"{peak_load_real/1000:.2f} kW")
        col3.metric("Peak Apparent Power", f"{peak_load_apparent:.0f} VA", f"{peak_load_apparent/1000:.2f} kVA")
        col4.metric("Load Percentage", "100.0%", "All Appliances")
        col5.metric("Number of Appliances", len(df), "")

        # 2. Essential + Medium Priority Appliances Summary
        self._display_essential_medium_summary(df, energy_df, peak_load_apparent)
        
        # 3. Essential Only Appliances Summary
        self._display_essential_only_summary(df, energy_df, peak_load_apparent)
    
    def _display_essential_medium_summary(self, df: pd.DataFrame, energy_df: pd.DataFrame, 
                                        peak_load_apparent: float) -> None:
        """Display Essential + Medium priority summary"""
        essential_medium_df = df[df["Priority"].str.lower().isin(["essential", "medium"])].copy()
        if not essential_medium_df.empty:
            essential_medium_energy_df = energy_df[energy_df["Appliance"].isin(essential_medium_df["Appliance"])]
            essential_medium_total_energy = essential_medium_energy_df[self.db_manager.time_periods].sum().sum()

            essential_medium_peak_load_real = (essential_medium_df[self.db_manager.time_periods].astype(int).values *
                                              (essential_medium_df["Quantity"] * essential_medium_df["Power (W)"] * essential_medium_df["Use Time (%)"] / 100).values.reshape(-1, 1)).sum(axis=0).max()

            essential_medium_peak_load_apparent = (essential_medium_df[self.db_manager.time_periods].astype(int).values *
                                                  (essential_medium_df["Quantity"] * essential_medium_df["Apparent Power (VA)"] * essential_medium_df["Use Time (%)"] / 100).values.reshape(-1, 1)).sum(axis=0).max()

            essential_medium_load_allocation = (essential_medium_peak_load_apparent / peak_load_apparent * 100) if peak_load_apparent > 0 else 0

            st.markdown("### 2. 🟠 Essential + Medium Priority (No Geyser & Stove)")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Essential+Medium Daily Energy", f"{essential_medium_total_energy:.0f} Wh", f"{essential_medium_total_energy/1000:.2f} kWh")
            col2.metric("Essential+Medium Peak Real Power", f"{essential_medium_peak_load_real:.0f} W", f"{essential_medium_peak_load_real/1000:.2f} kW")
            col3.metric("Essential+Medium Peak Apparent Power", f"{essential_medium_peak_load_apparent:.0f} VA", f"{essential_medium_peak_load_apparent/1000:.2f} kVA")
            col4.metric("Load Percentage", f"{essential_medium_load_allocation:.1f}%", "of Total System")
            col5.metric("Essential+Medium Count", len(essential_medium_df), "")
    
    def _display_essential_only_summary(self, df: pd.DataFrame, energy_df: pd.DataFrame, 
                                      peak_load_apparent: float) -> None:
        """Display Essential only summary"""
        essential_df = df[df["Priority"].str.lower() == "essential"].copy()
        if not essential_df.empty:
            essential_energy_df = energy_df[energy_df["Appliance"].isin(essential_df["Appliance"])]
            essential_total_energy = essential_energy_df[self.db_manager.time_periods].sum().sum()

            essential_peak_load_real = (essential_df[self.db_manager.time_periods].astype(int).values *
                                       (essential_df["Quantity"] * essential_df["Power (W)"] * essential_df["Use Time (%)"] / 100).values.reshape(-1, 1)).sum(axis=0).max()

            essential_peak_load_apparent = (essential_df[self.db_manager.time_periods].astype(int).values *
                                           (essential_df["Quantity"] * essential_df["Apparent Power (VA)"] * essential_df["Use Time (%)"] / 100).values.reshape(-1, 1)).sum(axis=0).max()

            essential_load_allocation = (essential_peak_load_apparent / peak_load_apparent * 100) if peak_load_apparent > 0 else 0

            st.markdown("### 3. 🔴 Essential Only")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Essential Daily Energy", f"{essential_total_energy:.0f} Wh", f"{essential_total_energy/1000:.2f} kWh")
            col2.metric("Essential Peak Real Power", f"{essential_peak_load_real:.0f} W", f"{essential_peak_load_real/1000:.2f} kW")
            col3.metric("Essential Peak Apparent Power", f"{essential_peak_load_apparent:.0f} VA", f"{essential_peak_load_apparent/1000:.2f} kVA")
            col4.metric("Load Percentage", f"{essential_load_allocation:.1f}%", "of Total System")
            col5.metric("Essential Count", len(essential_df), "")
    
    def _display_comparison_charts(self, df: pd.DataFrame) -> None:
        """Display aggregated load profiles comparison"""
        st.markdown("### 🔄 Aggregated Load Profiles (Comparison)")

        # 1. All appliances (off-grid)
        average_power_df = df.apply(self.energy_calculator.compute_average_power, axis=1)
        average_power_df["Appliance"] = df["Appliance"]
        all_profile = average_power_df.set_index("Appliance")[self.db_manager.time_periods].sum()

        # 2. Essential + Medium (excluding heating appliances)
        ess_med_df = df[df["Priority"].str.lower().isin(["essential", "medium"])].copy()
        ess_med_df = ess_med_df[~ess_med_df["Appliance"].str.contains("Geyser|Stove", case=False)]
        ess_med_profile = (ess_med_df[self.db_manager.time_periods].astype(int).values *
                          (ess_med_df["Quantity"] * ess_med_df["Power (W)"]).values.reshape(-1, 1)).sum(axis=0)

        # 3. Essentials only
        ess_df = df[df["Priority"].str.lower() == "essential"].copy()
        ess_profile = (ess_df[self.db_manager.time_periods].astype(int).values *
                      (ess_df["Quantity"] * ess_df["Power (W)"]).values.reshape(-1, 1)).sum(axis=0)

        # Build comparison dataframe
        comparison_df = pd.DataFrame({
            "Time Period": self.db_manager.time_periods,
            "All Appliances (Off-Grid)": all_profile.values,
            "Essential + Medium (No Heating)": ess_med_profile,
            "Essentials Only": ess_profile
        })

        # Create and display comparison chart
        comparison_chart = self.chart_generator.create_comparison_chart(comparison_df)
        st.plotly_chart(comparison_chart, use_container_width=True)


# Main execution
if __name__ == "__main__":
    app = LoadProfileApp()
    app.run()