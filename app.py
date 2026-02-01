import streamlit as st
import pandas as pd
import altair as alt
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
        try:
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
                    st.error("Fant ingen data. Sjekk logger for detaljer.")
                
        except Exception as e:
            st.error(f"⚠️ Det oppstod en feil: {e}")

with col2:
    if st.button("Slett mellomlager og oppdater"):
        st.cache_data.clear()
        st.rerun()
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
    
    years = [2023, 2024, 2025, 2026]
    months = range(1, 13)
    
    # Helper to get reading at specific date (with fuzzy match)
    def get_reading(date, device_name):
        dev_data = readings_df[readings_df['device_name'] == device_name]
        if dev_data.empty: return None
        
        # 1. Try exact match
        match = dev_data[dev_data['timestamp'] == date]
        if not match.empty:
            return match.iloc[0]['energy_kwh']
            
        # 2. Try fuzzy match (within 3 days forward)
        # Useful for cases like Dec 2025 where reading is on Dec 2nd
        window_end = date + pd.Timedelta(days=3)
        mask = (dev_data['timestamp'] > date) & (dev_data['timestamp'] <= window_end)
        near_matches = dev_data[mask].sort_values('timestamp')
        
        if not near_matches.empty:
            # Return the first reading found in the window
            return near_matches.iloc[0]['energy_kwh']
            
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

    # Manual Data for devices (injected later)
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
            
            # Force row creation if we have manual data for this month
            if year in manual_data and month in manual_data[year]:
                has_month_data = True
            
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
                            # Sanity check: If jump is massive (e.g. > 10,000 kWh), 
                            # it is likely a scale switch (daily -> cumulative) rather than consumption.
                            if diff < 10000:
                                total_acc += diff
                            else:
                                # If it's a massive jump, we don't add diff, 
                                # we just update prev_val (done below) to the new scale.
                                pass 
                        prev_val = curr_val
                
                if year == 2025 and dev == "Bad kjeller - Varmekabler":
                    total_acc = year_total[dev]

                if total_acc > 0:
                    sum_row[dev] = f"**{total_acc:.0f}**"
                else:
                    sum_row[dev] = "0"
                
            rows.append(sum_row)
            yearly_sums[year] = sum_row.copy()
            

    
    # Create DataFrame
    if rows:
        display_df = pd.DataFrame(rows)
        
        # --- Inject Manual Data ---
        # manual_data is defined at top of file
        
        # Ensure columns exist
        for year_data in manual_data.values():
            for month_data in year_data.values():
                for dev in month_data.keys():
                    if dev not in display_df.columns:
                        display_df[dev] = ""

        husholdning_col = "Totalt" # Still needed for ordering?

        for idx, row in display_df.iterrows():
            periode = row['Periode']
            
            # Logic for "Sum YYYY" rows
            if "**Sum" in periode:
                try:
                    year = int(periode.replace("**Sum ", "").replace("**", ""))
                    if year in manual_data:
                        # Sum up for each device in manual_data
                        # We need to iterate all months in that year and sum per device
                        device_sums = {}
                        for m_data in manual_data[year].values():
                            for dev, val in m_data.items():
                                device_sums[dev] = device_sums.get(dev, 0) + val
                        
                        for dev, total in device_sums.items():
                             # Check if we should override (logic: existing valid Total might be partial or full?)
                             # Current logic: If DB has data, we trust DB. But for Totalt/Easee 2024/2025 DB is effectively empty/incomplete.
                             # Let's check strict "if existing is almost zero/empty".
                             existing_val = display_df.at[idx, dev] if dev in display_df.columns else ""
                             if not existing_val or existing_val == "" or existing_val == "0" or existing_val == 0 or existing_val == "0.0":
                                 display_df.at[idx, dev] = f"**{total}**"

                except ValueError:
                    pass
            
            # Logic for monthly rows "Month YYYY"
            else:
                try:
                    parts = periode.split(" ")
                    if len(parts) == 2:
                        month_name = parts[0]
                        year = int(parts[1])
                        month_idx = month_names.index(month_name) + 1
                        
                        if year in manual_data and month_idx in manual_data[year]:
                            for dev, val in manual_data[year][month_idx].items():
                                existing_val = display_df.at[idx, dev] if dev in display_df.columns else ""
                                if not existing_val or existing_val == "" or existing_val == "0" or existing_val == 0:
                                    display_df.at[idx, dev] = str(val)
                                    
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
        
        # Add Footer (Repeat Headers)
        # Create a dictionary where key=col_name and value=col_name (or bolded)
        footer_row = {col: f"{col}" for col in final_cols} # Text only, styling via Styler
        # Append using pd.concat
        footer_df = pd.DataFrame([footer_row])
        display_df_filtered = pd.concat([display_df_filtered, footer_df], ignore_index=True)
        
        st.markdown("### Forbruksoversikt")
        
        # Style the dataframe
        # Target the last row for header-like styling
        def style_footer(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            # Apply style to last row - using dark grey background and white text for better dark mode contrast
            styles.iloc[-1] = 'font-weight: bold; background-color: #262730; color: white; border-top: 2px solid #4e4e4e;'
            return styles

        st.dataframe(
            display_df_filtered.style.apply(style_footer, axis=None),
            hide_index=True, 
            use_container_width=True
        )
        
        # --- BAR CHART SECTION ---
        st.divider()
        st.subheader("📊 Sammenligning av år (Stolpediagram)")
        
        # 1. Selectors for Chart
        chart_col1, chart_col2, chart_col3 = st.columns(3)
        with chart_col1:
             chart_years = st.multiselect("Velg år:", options=years, default=years)
        with chart_col2:
             chart_months = st.multiselect("Velg måneder:", options=month_names, default=month_names)
        with chart_col3:
             chart_devices = st.multiselect("Velg enheter:", options=other_cols, default=other_cols[:5]) # Default first 5 to avoid clutter
             
        if chart_years and chart_devices and chart_months:
            # 2. Prepare Data
            chart_data = []
            
            # Map month names to 1-12 indices
            selected_month_indices = [month_names.index(m) + 1 for m in chart_months]
            
            for y in chart_years:
                 for d in chart_devices:
                     total_val = 0
                     
                     for m_idx in selected_month_indices:
                         val = 0
                         
                         # Check manual data first
                         if y in manual_data and m_idx in manual_data[y]:
                             val = manual_data[y][m_idx].get(d, 0)
                             
                         # If manual data is 0 or low, try DB utilizing the robust get_reading helper
                         if val == 0:
                             start_date = pd.Timestamp(y, m_idx, 1)
                             if m_idx == 12:
                                 end_date = pd.Timestamp(y+1, 1, 1)
                             else:
                                 end_date = pd.Timestamp(y, m_idx+1, 1)
                             
                             # Use get_reading to handle fuzzy matching same as table
                             val_start = get_reading(start_date, d)
                             val_end = get_reading(end_date, d)
                             
                             if val_start is not None and val_end is not None:
                                 diff = val_end - val_start
                                 if diff > 0:
                                     val = diff
                                 elif val_end > 0 and diff < 0: 
                                      # Fallback for some weird resets if any, though table logic 
                                      # uses: if consumption < 0: consumption = val_end
                                      val = val_end
                         
                         # Check estimates (Bad kjeller 2025)
                         if y == 2025 and d == "Bad kjeller - Varmekabler" and m_idx in estimates_2025:
                             val = estimates_2025[m_idx]
                             
                         total_val += val
                     
                     chart_data.append({"År": str(y), "Enhet": d, "kWh": total_val})
            
            if chart_data:
                chart_df = pd.DataFrame(chart_data)
                
                # 3. Render Chart
                # Alternative Grouped Bar (better for many items)
                c_grouped = alt.Chart(chart_df).mark_bar().encode(
                    x=alt.X('Enhet', axis=alt.Axis(title=None)),
                    y=alt.Y('kWh', title='kWh'),
                    color='År',
                    xOffset='År',
                    tooltip=['År', 'Enhet', 'kWh']
                )
                
                st.altair_chart(c_grouped, use_container_width=True)
            else:
                 st.info("Ingen data for valgte år/enheter.")

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
