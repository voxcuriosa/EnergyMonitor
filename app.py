import streamlit as st
import pandas as pd
from homey_client import HomeyClient
from database import save_energy_readings, get_energy_readings
import auth

st.set_page_config(page_title="Strømovervåking", page_icon="⚡", layout="wide")

# --- Version Logic ---
def get_version():
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "1.00"

current_version = get_version()
st.sidebar.markdown(f"**v{current_version}**")

# --- AUTHENTICATION ---
# Vi henter innlogging fra auth.py. Denne funksjonen stopper appen hvis man ikke er logget inn.
user_info = auth.authenticate_user()

# Sjekk om e-posten har tilgang
ALLOWED_USERS = ["borchgrevink@gmail.com"]

if user_info["email"] not in ALLOWED_USERS:
    st.error(f"Beklager, brukeren {user_info['email']} har ikke tilgang.")
    if st.button("Logg ut"):
        del st.session_state["user_info"]
        st.rerun()
    st.stop()

# Hvis vi kom hit, er brukeren godkjent!
st.sidebar.success(f"Logget inn som: {user_info['name']}")
if st.sidebar.button("Logg ut"):
    del st.session_state["user_info"]
    st.rerun()

st.title("⚡ Strømforbruk (Homey Pro)")

# --- Main App Logic ---

# Button to fetch new data
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Hent strømdata fra Homey nå"):
        with st.spinner("Kobler til Homey..."):
            client = HomeyClient()
            data = client.get_energy_data()
            if data:
                if save_energy_readings(data):
                    st.success(f"Hentet og lagret data for {len(data)} enheter.")
                    st.rerun()
                else:
                    st.error("Kunne ikke lagre data til databasen.")
            else:
                st.error("Fant ingen data eller kunne ikke koble til Homey.")
with col2:
    if st.button("Slett mellomlager og oppdater"):
        st.cache_data.clear()
        st.rerun()

# Display Data
readings_df = get_energy_readings()

if not readings_df.empty:
    # Ensure timestamp is datetime
    readings_df['timestamp'] = pd.to_datetime(readings_df['timestamp'])
    
    # Filter unwanted devices
    readings_df = readings_df[~readings_df['device_name'].isin(['Vann', 'Tibber puls'])]
    
    # Get unique devices sorted alphabetically
    devices = sorted(readings_df['device_name'].unique())
    
    # Prepare rows
    rows = []
    
    years = [2023, 2024, 2025]
    months = range(1, 13)
    
    # Helper to get reading at specific date
    def get_reading(date, device_name):
        dev_data = readings_df[readings_df['device_name'] == device_name]
        if dev_data.empty: return None
        
        match = dev_data[dev_data['timestamp'] == date]
        if not match.empty:
            return match.iloc[0]['energy_kwh']
        return None

    month_names = ["Januar", "Februar", "Mars", "April", "Mai", "Juni", 
                   "Juli", "August", "September", "Oktober", "November", "Desember"]

    yearly_sums = {}
    
    # Estimates for Bad kjeller 2025
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

    for year in years:
        year_total = {dev: 0.0 for dev in devices}
        has_data_for_year = False
        
        for month in months:
            start_date = pd.Timestamp(year=year, month=month, day=1)
            
            if month == 12:
                end_date = pd.Timestamp(year=year+1, month=1, day=1)
            else:
                end_date = pd.Timestamp(year=year, month=month+1, day=1)
                
            row_data = {"Periode": f"{month_names[month-1]} {year}"}
            
            has_month_data = False
            for dev in devices:
                # Check for estimate first (Bad kjeller 2025)
                if year == 2025 and month in estimates_2025 and dev == "Bad kjeller - Varmekabler":
                    consumption = estimates_2025[month]
                    row_data[dev] = f"{consumption} (Estimert)"
                    year_total[dev] += consumption
                    has_month_data = True
                    continue

                val_start = get_reading(start_date, dev)
                val_end = get_reading(end_date, dev)
                
                if val_start is not None and val_end is not None:
                    consumption = val_end - val_start
                    if consumption < 0:
                        consumption = val_end
                    
                    row_data[dev] = f"{consumption:.0f}"
                    year_total[dev] += consumption
                    has_month_data = True
                else:
                    row_data[dev] = ""
            
            if has_month_data:
                rows.append(row_data)
                has_data_for_year = True
        
        # Add Summary Row for Year
        if has_data_for_year:
            sum_row = {"Periode": f"**Sum {year}**"}
            for dev in devices:
                start_date = pd.Timestamp(year, 1, 1)
                end_date = pd.Timestamp(year + 1, 1, 1)
                
                dev_readings = readings_df[
                    (readings_df['device_name'] == dev) & 
                    (readings_df['timestamp'] >= start_date) &
                    (readings_df['timestamp'] <= end_date)
                ].sort_values('timestamp')
                
                total_acc = 0
                if not dev_readings.empty:
                    prev_val = dev_readings.iloc[0]['energy_kwh']
                    for _, r in dev_readings.iloc[1:].iterrows():
                        curr_val = r['energy_kwh']
                        diff = curr_val - prev_val
                        if diff < 0:
                            if curr_val < (prev_val * 0.5):
                                total_acc += curr_val
                            else:
                                total_acc += diff
                        else:
                            total_acc += diff
                        prev_val = curr_val
                
                if year == 2025 and dev == "Bad kjeller - Varmekabler":
                    total_acc = year_total[dev]

                if total_acc > 0:
                    sum_row[dev] = f"**{total_acc:.0f}**"
                else:
                    sum_row[dev] = "0"
                
            rows.append(sum_row)
            yearly_sums[year] = sum_row.copy()
            
            for prev_year in range(year - 1, 2022, -1):
                if prev_year in yearly_sums:
                    comp_row = yearly_sums[prev_year].copy()
                    comp_row['Periode'] = f"**Sum {prev_year}**"
                    rows.append(comp_row)
    
    # Create DataFrame
    if rows:
        display_df = pd.DataFrame(rows)
        
        # --- Inject Manual Data for Totalt ---
        husholdning_col = "Totalt"
        manual_data = {
            2024: {
                1: 3386, 2: 2466, 3: 1826, 4: 2036, 5: 1405, 6: 1495,
                7: 1313, 8: 1456, 9: 1511, 10: 1802, 11: 2273, 12: 2833
            },
            2025: {
                1: 3148, 2: 2654, 3: 2362, 4: 1679, 5: 1549, 6: 1099,
                7: 1199, 8: 1224, 9: 1382, 10: 1921, 11: 2172
            }
        }
        
        if husholdning_col not in display_df.columns:
            display_df[husholdning_col] = ""

        for idx, row in display_df.iterrows():
            periode = row['Periode']
            if "**Sum" in periode:
                try:
                    year = int(periode.replace("**Sum ", "").replace("**", ""))
                    if year in manual_data:
                        total = sum(manual_data[year].values())
                        display_df.at[idx, husholdning_col] = f"**{total}**"
                except ValueError:
                    pass
            else:
                try:
                    parts = periode.split(" ")
                    if len(parts) == 2:
                        month_name = parts[0]
                        year = int(parts[1])
                        month_idx = month_names.index(month_name) + 1
                        if year in manual_data and month_idx in manual_data[year]:
                            display_df.at[idx, husholdning_col] = str(manual_data[year][month_idx])
                except (ValueError, IndexError):
                    pass

        other_cols = [c for c in devices if c != husholdning_col]
        cols = ["Periode", husholdning_col] + other_cols
        final_cols_ordered = [c for c in cols if c in display_df.columns]
        display_df = display_df[final_cols_ordered]
        
        devices = [husholdning_col] + other_cols
        
        default_hidden = ["Kjellerstue - Varmeovn", "Kjellerstue - Varmekabler ", "Vaskerom - varme"]
        default_selection = [d for d in devices if d not in default_hidden]
        
        selected_devices = st.multiselect(
            "Velg enheter som skal vises:",
            options=devices,
            default=default_selection
        )
        
        final_cols = ["Periode"] + selected_devices
        display_df_filtered = display_df[final_cols]
        
        st.markdown("### Forbruksoversikt")
        st.dataframe(display_df_filtered, hide_index=True, use_container_width=True)
        
        with st.expander("Feilsøking (Debug)"):
            st.write(f"Antall målinger totalt: {len(readings_df)}")
            st.write(f"Unike enheter: {devices}")
            st.write("Siste 5 målinger (Raw):")
            st.dataframe(readings_df.sort_values('timestamp').tail(5))
    else:
        st.info("Ingen data å vise for perioden.")
        
    with st.expander("Se rådata (Historikk)"):
        st.dataframe(readings_df)
        
else:
    st.info("Ingen strømdata registrert ennå. Trykk på knappen over for å hente første måling.")
