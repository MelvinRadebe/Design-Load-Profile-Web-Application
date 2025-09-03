# default_data_provider.py
from typing import List


class DefaultDataProvider:
    """Provides default appliance data"""
    
    @staticmethod
    def get_default_data() -> List[List]:
        """Return default appliance data"""
        return [
            ["Ceiling Lights (Living)", 4, 9, 100, 0.95, 50, False, False, False, True, True, True, False, False, True, True, True, True, "essential", "Living Room"],
            ["Ceiling Lights (Bedrooms)", 3, 9, 100, 0.95, 30, False, False, False, True, True, False, False, False, True, True, True, True, "essential", "Bedroom"],
            ["Ceiling Lights (Kitchen)", 3, 9, 100, 0.95, 40, False, False, False, True, True, False, False, False, True, True, True, True, "essential", "Kitchen"],
            ["Ceiling Lights (Dining)", 3, 9, 100, 0.95, 30, False, False, False, True, True, False, False, False, True, True, True, True, "essential", "Dining Room"],
            ["Security Lights (Outside)", 3, 9, 100, 0.95, 90, False, False, False, True, True, False, False, False, True, True, True, True, "essential", "Outdoor"],
            ["Ceiling Lights (Garage)", 3, 9, 100, 0.95, 20, False, False, False, True, True, False, False, False, True, True, True, True, "essential", "Garage"],
            ["Ceiling LED Lights (Bathroom)", 3, 9, 100, 0.95, 25, False, False, False, True, True, False, False, False, True, True, True, True, "essential", "Bathroom"],
            ["Fridge", 1, 300, 40, 0.85, 100] + [True]*12 + ["essential", "Kitchen"],
            ["Phone Chargers", 2, 5, 80, 0.60, 60, False, False, False, False, True, True, True, True, True, True, True, True, "essential", "Living Room"],
            ["Laptop", 1, 65, 70, 0.65, 80, False, False, False, True, True, True, True, True, True, True, False, False, "essential", "Living Room"],
            ["TV", 1, 100, 90, 0.70, 70, False, False, False, False, False, True, True, True, True, True, True, False, "medium", "Living Room"],
            ["Washing Machine", 1, 500, 85, 0.80, 15, False, False, False, False, True, True, False, False, False, False, False, False, "medium", "Laundry"],
            ["Microwave", 1, 800, 95, 0.85, 5, True, True, True, False, False, False, False, False, True, True, True, True, "medium", "Kitchen"],
            ["Geyser", 1, 3000, 30, 1.00, 40, False, False, True, True, False, False, False, False, True, True, False, False, "non-essential", "Bathroom"],
            ["Stove", 1, 2000, 80, 1.00, 20, True, False, False, True, False, False, True, False, True, False, False, False, "non-essential", "Kitchen"],
            ["Hair Dryer", 1, 1200, 100, 0.98, 10, False, False, True, False, False, False, False, False, True, False, False, False, "non-essential", "Bathroom"],
            ["Kettle", 1, 2000, 100, 1.00, 5, True, False, False, True, False, False, True, False, True, False, False, False, "non-essential", "Kitchen"],
            ["Freezer", 1, 200, 40, 0.85, 100] + [True]*12 + ["essential", "Kitchen"],
            ["Dishwasher", 1, 1200, 90, 0.85, 25, False, False, False, False, True, True, True, False, False, False, False, False, "medium", "Kitchen"],
            ["Vacuum Cleaner", 1, 700, 50, 0.75, 15, False, False, False, False, False, False, False, True, False, False, False, False, "non-essential", "General"],
            ["Toaster", 1, 800, 60, 1.00, 5, False, False, False, True, False, False, False, False, False, False, False, False, "non-essential", "Kitchen"],
            ["Coffee Machine", 1, 900, 80, 0.95, 10, False, False, False, True, False, False, False, False, False, False, False, False, "non-essential", "Kitchen"],
            ["Iron", 1, 1000, 70, 1.00, 15, False, False, False, False, False, False, False, False, True, False, False, False, "non-essential", "Laundry"],
            ["Fan", 2, 50, 40, 0.65, 80, True, True, False, False, False, False, False, False, False, False, True, True, "essential", "Living Room"],
            ["Space Heater", 1, 1500, 50, 1.00, 30, False, False, False, False, False, False, False, False, True, True, False, False, "non-essential", "Living Room"],
            ["Game Console", 1, 120, 60, 0.70, 60, False, False, False, False, False, False, False, False, True, True, True, False, "medium", "Living Room"],
            ["Router", 1, 10, 100, 0.60, 100] + [True]*12 + ["essential", "Living Room"],
            ["Blender", 1, 400, 40, 0.75, 5, False, False, False, False, False, True, False, False, False, False, False, False, "non-essential", "Kitchen"],
            ["Rice Cooker", 1, 700, 50, 0.95, 15, False, False, False, True, False, False, False, False, False, False, False, False, "non-essential", "Kitchen"],
            ["Oven", 1, 2400, 80, 1.00, 20, False, False, False, False, False, False, True, True, False, False, False, False, "non-essential", "Kitchen"],
            ["Water Heater", 1, 3000, 30, 1.00, 20, False, False, False, True, False, False, False, False, False, False, False, False, "non-essential", "Bathroom"],
            ["Ceiling Fan", 1, 70, 50, 0.65, 70, True, True, False, False, False, False, False, False, False, False, True, True, "essential", "Bedroom"],
            ["Garage Door Opener", 1, 800, 20, 0.70, 2, False, False, False, False, False, False, False, False, True, False, False, False, "non-essential", "Garage"],
            ["Security System", 1, 50, 100, 0.60, 100] + [True]*12 + ["essential", "General"],
            ["Water Pump", 1, 1000, 30, 0.75, 10, False, False, False, True, False, False, False, False, False, False, False, False, "non-essential", "Outdoor"],
            ["Electric Stove", 1, 2500, 80, 1.00, 25, False, False, False, False, False, False, True, True, False, False, False, False, "non-essential", "Kitchen"],
            ["Ceiling Light (Bathroom)", 2, 15, 50, 0.95, 30, False, False, False, True, True, False, False, False, True, True, False, False, "essential", "Bathroom"],
            ["Outdoor Light", 4, 20, 70, 0.95, 85, True, True, False, False, False, False, False, False, True, True, True, True, "essential", "Outdoor"],
        ]