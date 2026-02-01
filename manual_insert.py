import sys
import os
from datetime import datetime
from database import save_energy_readings

# Usage: python manual_insert.py "Device Name" "1234.5" "2025-01-01"

def main():
    if len(sys.argv) < 3:
        print("Usage: python manual_insert.py <device_name> <energy_kwh> [date_iso]")
        sys.exit(1)

    device_name = sys.argv[1]
    energy_val = float(sys.argv[2])
    date_str = sys.argv[3] # Expecting YYYY-MM-DD

    # Check for dry run (safety)
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    
    if dry_run:
        print(f"🐫 DRY RUN: Would insert {device_name} = {energy_val} kWh @ {date_str}. Not saving.")
        return

    if insert_manual(device_name, energy_val, date_str):
        print("✅ Manual insert process completed.")
    else:
        print("❌ Manual insert process failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
