# energy_calculator.py
import pandas as pd
from typing import List, Tuple


class EnergyCalculator:
    """Handles energy and power calculations"""
    
    def __init__(self, time_periods: List[str]):
        self.time_periods = time_periods
    
    def compute_energy(self, row: pd.Series) -> pd.Series:
        """Calculate energy (Wh) per 2-hour interval using Use Time %"""
        duty = row["Duty Cycle (%)"] / 100
        use_time = row["Use Time (%)"] / 100
        power = row["Power (W)"]
        qty = row["Quantity"]
        result = []
        for t in self.time_periods:
            is_on = row[t]
            interval_energy = 2 * qty * power * duty * use_time * int(is_on)
            result.append(interval_energy)
        return pd.Series(result, index=self.time_periods)
    
    def compute_average_power(self, row: pd.Series) -> pd.Series:
        """Calculate average power per interval"""
        qty = row["Quantity"]
        power = row["Power (W)"]
        result = []
        for t in self.time_periods:
            is_on = row[t]
            interval_power = qty * power * int(is_on)
            result.append(interval_power)
        return pd.Series(result, index=self.time_periods)
    
    def compute_instantaneous_power(self, row: pd.Series) -> pd.Series:
        """Calculate instantaneous power per interval"""
        return self.compute_average_power(row)  # Same as average for now
    
    def calculate_peak_loads(self, df: pd.DataFrame) -> Tuple[float, float]:
        """Calculate peak real and apparent power loads"""
        peak_load_real = (df[self.time_periods].astype(int).values *
                         (df["Quantity"] * df["Power (W)"]).values.reshape(-1, 1)).sum(axis=0).max()

        peak_load_apparent = (df[self.time_periods].astype(int).values *
                             (df["Quantity"] * df["Apparent Power (VA)"]).values.reshape(-1, 1)).sum(axis=0).max()
        
        return peak_load_real, peak_load_apparent