# 🔆 Load Profile App — Catalogue Method

A **Streamlit** application for building residential load profiles using the **Catalogue Method**.  
The app allows you to catalogue appliances, adjust their duty cycles and usage patterns, and visualize how power and energy consumption evolve throughout the day.

---

## 📌 Features

- 🗂 **Database-backed catalogue** with default South African household appliances  
- ✏️ **Editable table** with:
  - Appliance, quantity, power (W), duty cycle (%), power factor
  - **Use Time %** per 2-hour interval
  - 12 × 2-hour slots (`00:00–02:00` … `22:00–00:00`)
- ⚡ **Energy calculations**:
  - Interval energy (Wh)
  - Apparent power (VA)
  - Total daily energy per appliance
  - Peak real and apparent load
- 📊 **Interactive charts** with Plotly:
  - Power consumption over time
  - Stacked bar chart by appliance
  - Daily energy per appliance grouped by **priority** (essential / medium / non-essential)
  - Appliance-level time series
  - Aggregated scenario comparison (all, essential+medium, essentials only)
- 📝 **Change logging** (insert, update, delete) tracked in the database

---

---

## 📝 Instructions

1. **Launch the app**
   - Run:
     ```bash
     streamlit run app.py
     ```
   - Your browser will open at [http://localhost:8501](http://localhost:8501).

2. **Explore the default dataset**
   - The app loads a pre-configured set of common household appliances (lights, fridge, TV, kettle, etc.).
   - Each appliance has:
     - **Quantity**
     - **Rated Power (W)**
     - **Duty Cycle (%)**
     - **Power Factor**
     - **Use Time (%)**
     - **2-hour usage slots (checkboxes)**

3. **Edit or add appliances**
   - Use the interactive table to:
     - Change values (e.g., wattage, duty cycle, use time %).
     - Tick the **time slots** when the appliance is active.
   - Add new rows for extra appliances or delete those not needed.

4. **Understand the “Use Time (%)” column**
   - This sets the fraction of the 2-hour slot when the appliance is ON.
   - Example:
     - A kettle that runs for ~10 min in a 2-hour slot → set **Use Time (%) = 8**.
     - A fridge compressor that cycles for ~30 min/hour → **Use Time (%) = 50**.

5. **Save your changes**
   - Click **Save Changes**.
   - The app will:
     - Update the database (`load_profile.db`).
     - Log any insert, update, or delete in the `change_log` table.

6. **View results**
   - 📊 **Power Consumption Over Time** → see the household’s total load profile.
   - 🟦 **Stacked Energy Chart** (optional checkbox) → breakdown of energy use by appliance.
   - 🔴 **Daily Energy Bar Chart** → compare total daily Wh by appliance and priority.
   - 📈 **Time Series** → appliance-level power usage across the day.
   - 🔄 **Comparison Profiles**:
     - **All appliances (off-grid)**
     - **Essential + Medium priority (no heating appliances)**
     - **Essentials only**

7. **Interpret summaries**
   - Each scenario shows:
     - Total daily energy (Wh/kWh).
     - Peak real power (W).
     - Peak apparent power (VA).
     - Appliance count and load allocation.

---



## 📂 Project Structure

```text
load_profile_app/
│
├── app.py                  # Main Streamlit entry point
├── database_manager.py     # Handles SQLite operations
├── default_data_provider.py# Default appliance dataset
├── data_validator.py       # Cleans and validates appliance data
├── energy_calculator.py    # Energy & power calculation logic
├── chart_generator.py      # Plotly-based visualizations
├── load_profile.db         # SQLite database (auto-created)
└── README.md               # Project documentation
