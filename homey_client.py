import requests
import pandas as pd
from datetime import datetime, timedelta
import os

class HomeyClient:
    def __init__(self):
        # Authenticate using Streamlit Secrets or Environment Variables
        try:
            # Check Streamlit secrets first
            import streamlit as st
            self.homey_id = st.secrets["HOMEY_ID"]
            self.api_key = st.secrets["HOMEY_API_KEY"]
        except (ImportError, FileNotFoundError, KeyError):
            # Fallback to Environment Variables
            self.homey_id = os.environ.get("HOMEY_ID")
            self.api_key = os.environ.get("HOMEY_API_KEY")
        
        if not self.homey_id or not self.api_key:
            raise ValueError("Mangler Homey ID eller API Key. Sjekk secrets.toml eller miljøvariabler.")
            
        self.base_url = f"https://{self.homey_id}.connect.athom.com/api/manager/devices/device"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_energy_data(self):
        """Fetches all devices and filters for energy usage."""
        response = requests.get(self.base_url, headers=self.headers, timeout=10)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        
        devices = response.json()
        energy_devices = []
        
        # Name Mapping (Canonical Name <- Homey Name)
        # Homey Name might have trailing spaces or be different
        NAME_MAPPING = {
            "Bad": "Bad - Varmekabler",
            "Bad - Varmekabler ": "Bad - Varmekabler",
            "Bad kjeller": "Bad kjeller - Varmekabler",
            "Bad kjeller - Varmekabler ": "Bad kjeller - Varmekabler",
            "Stue - Varmekabler ": "Stue",
            "Stue - Varmekabler": "Stue",
            "Kjellergang - Varme": "Kjellergang",
            "Casper - Varme": "Casper",
            "Cornelius - Varmekabler ": "Cornelius",
            "Cornelius - Varmekabler": "Cornelius",
            "Varmepumpe ": "Varmepumpe",
            "Vindfang - Varmekabler": "Vindfang", # Assumption
            "Vindfang - Varmekabler ": "Vindfang",
            "CBV  (EHVKFY9X)": "Easee",
            "Tibber puls": "Totalt",
            "Tibber puls ": "Totalt",
        }
        
        IGNORED_DEVICES = ["Vann", "Vann "]

        for dev_id, dev in devices.items():
            caps = dev.get('capabilities', [])
            if 'meter_power' in caps: # Only interested in devices that measure total energy
                name = dev.get('name', 'Unknown')
                
                if name in IGNORED_DEVICES:
                    continue
                    
                # Apply mapping
                if name in NAME_MAPPING:
                    name = NAME_MAPPING[name]
                    
                capabilitiesObj = dev.get('capabilitiesObj', {})
                
                # Current Power (W)
                power_w = 0
                if 'measure_power' in capabilitiesObj:
                    power_w = capabilitiesObj['measure_power'].get('value', 0)
                    
                # Total Energy (kWh)
                energy_kwh = 0
                if 'meter_power' in capabilitiesObj:
                    energy_kwh = capabilitiesObj['meter_power'].get('value', 0)
                    
                energy_devices.append({
                    "id": dev_id,
                    "name": name,
                    "power_w": power_w,
                    "energy_kwh": energy_kwh,
                    "timestamp": datetime.now()
                })
        
        return energy_devices

    def get_energy_dataframe(self):
        data = self.get_energy_data()
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
