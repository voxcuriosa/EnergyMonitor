import os
import tomli
import sys
import pandas as pd
from unittest.mock import MagicMock

# 1. Setup Environment from Secrets
try:
    with open(".streamlit/secrets.toml", "rb") as f:
        secrets = tomli.load(f)
    mock_st = MagicMock()
    mock_st.secrets = secrets
    sys.modules["streamlit"] = mock_st
except Exception as e:
    print(f"Failed to load secrets: {e}")
    sys.exit(1)

from database import get_energy_readings

def check_2026():
    df = get_energy_readings()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    totalt = df[df['device_name'] == 'Totalt'].sort_values('timestamp')
    
    print("--- Totalt Readings for 2026 ---")
    mask_2026 = (totalt['timestamp'] >= '2026-01-01') & (totalt['timestamp'] < '2026-02-02')
    print(totalt[mask_2026])
    
    print("\n--- Totalt Readings near 2025/2026 transition ---")
    mask_transition = (totalt['timestamp'] >= '2025-12-30') & (totalt['timestamp'] < '2026-01-05')
    print(totalt[mask_transition])

if __name__ == "__main__":
    check_2026()
