import pandas as pd
from database import get_energy_readings
import os

# --- Configuration & Helpers (Replica of app.py logic) ---

# Manual Data for devices
# Structure: { Year: { Month: { "DeviceName": Value } } }
manual_data = {
    2024: {
        1: {"Totalt": 3386, "Easee": 544}, 
        2: {"Totalt": 2466, "Easee": 403}, 
        3: {"Totalt": 1826, "Easee": 236}, 
        4: {"Totalt": 2036, "Easee": 247}, 
        5: {"Totalt": 1405, "Easee": 343}, 
        6: {"Totalt": 1495, "Easee": 386},
        7: {"Totalt": 1313, "Easee": 287}, 
        8: {"Totalt": 1456, "Easee": 384}, 
        9: {"Totalt": 1511, "Easee": 394}, 
        10: {"Totalt": 1802, "Easee": 341}, 
        11: {"Totalt": 2273, "Easee": 396}, 
        12: {"Totalt": 2833, "Easee": 523}
    },
    2025: {
        1: {"Totalt": 3148, "Easee": 593}, 
        2: {"Totalt": 2654, "Easee": 445}, 
        3: {"Totalt": 2362, "Easee": 332}, 
        4: {"Totalt": 1679, "Easee": 190}, 
        5: {"Totalt": 1549, "Easee": 282}, 
        6: {"Totalt": 1099, "Easee": 225},
        7: {"Totalt": 1199, "Easee": 289}, 
        8: {"Totalt": 1224, "Easee": 265}, 
        9: {"Totalt": 1382, "Easee": 262}, 
        10: {"Totalt": 1921, "Easee": 454}, 
        11: {"Totalt": 2172, "Easee": 456}, 
        12: {"Totalt": 2561, "Easee": 514}
    }
}

estimates_2025 = {
    3: 62,   # Mars
    4: 243,  # April
    5: 97,   # Mai
    6: 180,  # Juni
    7: 146,  # Juli
    8: 142,  # August
    9: 165,  # September
    10: 310, # Oktober
    11: 392  # November
}

readings_df = get_energy_readings()

# Parse timestamps
if not readings_df.empty:
    readings_df['timestamp'] = pd.to_datetime(readings_df['timestamp'])
    # Filter unwanted
    readings_df = readings_df[~readings_df['device_name'].isin(['Vann', 'Tibber puls'])]

def get_reading(date, device_name):
    dev_data = readings_df[readings_df['device_name'] == device_name]
    if dev_data.empty: return None
    
    # 1. Exact match
    match = dev_data[dev_data['timestamp'] == date]
    if not match.empty:
        return match.iloc[0]['energy_kwh']
        
    # 2. Fuzzy match (3 days)
    window_end = date + pd.Timedelta(days=3)
    mask = (dev_data['timestamp'] > date) & (dev_data['timestamp'] <= window_end)
    near_matches = dev_data[mask].sort_values('timestamp')
    
    if not near_matches.empty:
        return near_matches.iloc[0]['energy_kwh']
        
    return None

def main():
    print("Generating backup...")
    
    devices = sorted(readings_df['device_name'].unique()) if not readings_df.empty else []
    years = [2024, 2025] # Export specific years
    months = range(1, 13)
    month_names = ["Januar", "Februar", "Mars", "April", "Mai", "Juni", 
                   "Juli", "August", "September", "Oktober", "November", "Desember"]
    
    rows = []

    for year in years:
        for month in months:
            start_date = pd.Timestamp(year=year, month=month, day=1)
            if month == 12:
                end_date = pd.Timestamp(year=year+1, month=1, day=1)
            else:
                end_date = pd.Timestamp(year=year, month=month+1, day=1)
            
            row_data = {"Year": year, "Month": month_names[month-1]}
            
            has_month_data = False
            
            # DB Calculation
            for dev in devices:
                if year == 2025 and month in estimates_2025 and dev == "Bad kjeller - Varmekabler":
                     row_data[dev] = estimates_2025[month]
                     has_month_data = True
                     continue
                
                val_start = get_reading(start_date, dev)
                val_end = get_reading(end_date, dev)
                
                if val_start is not None and val_end is not None:
                    cons = val_end - val_start
                    row_data[dev] = round(cons) if cons >= 0 else round(val_end)
                    has_month_data = True
                else:
                    row_data[dev] = 0

            # Manual Injection
            if year in manual_data and month in manual_data[year]:
                has_month_data = True
                for dev, val in manual_data[year][month].items():
                    # Prioritize manual data if DB is empty or zero
                    if dev not in row_data or row_data[dev] == 0:
                        row_data[dev] = val
            
            if has_month_data:
                rows.append(row_data)

    df = pd.DataFrame(rows)
    
    # Ensure all manual columns exist
    for year_d in manual_data.values():
        for month_d in year_d.values():
            for dev in month_d.keys():
                if dev not in df.columns:
                    df[dev] = 0

    # Reorder
    fixed_cols = ["Year", "Month"]
    dev_cols = [c for c in df.columns if c not in fixed_cols]
    # Move Totalt and Easee to front if present
    priority = ["Totalt", "Easee"]
    sorted_devs = [c for c in priority if c in dev_cols] + sorted([c for c in dev_cols if c not in priority])
    
    df = df[fixed_cols + sorted_devs]
    
    output_file = "backup_energy_data.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig') # utf-8-sig for Excel compatibility
    print(f"Backup saved to: {os.path.abspath(output_file)}")
    print(df.head())

if __name__ == "__main__":
    main()
