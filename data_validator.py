# data_validator.py
import pandas as pd


class DataValidator:
    """Validates and cleans appliance data"""
    
    @staticmethod
    def validate_df(df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clip dataframe values to acceptable ranges"""
        df = df.copy()
        df["Use Time (%)"] = df["Use Time (%)"].clip(0, 100)
        df["Power (W)"] = df["Power (W)"].clip(0)
        df["Duty Cycle (%)"] = df["Duty Cycle (%)"].clip(0, 100)
        df["Power Factor"] = df["Power Factor"].clip(0.01, 1.0)
        df["Quantity"] = df["Quantity"].clip(0)
        return df