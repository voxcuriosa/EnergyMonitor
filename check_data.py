import streamlit as st
import os
from database import get_energy_readings

# This script verifies data is readable using the app's own logic
# It assumes secrets.toml is configured correctly for MySQL

def check_db():
    print("🚀 Verifying Data Access via App Logic (MySQL)...")
    try:
        df = get_energy_readings()
        
        if not df.empty:
            print(f"✅ FOUND DATA! Found {len(df)} entries.")
            print("First 5 rows:")
            print(df.head())
            
            # Additional check for 'Totalt' device
            totalt_df = df[df['device_name'] == 'Totalt']
            if not totalt_df.empty:
                 print(f"✅ Found 'Totalt' entries: {len(totalt_df)}")
            else:
                 print("⚠️ No 'Totalt' device found (might be normal if not in data yet).")
                 
        else:
            print("❌ NO DATA FOUND in database via get_energy_readings().")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_db()
