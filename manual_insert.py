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
    
    if len(sys.argv) > 3:
        date_str = sys.argv[3]
        timestamp = datetime.fromisoformat(date_str)
    else:
        timestamp = datetime.now()

    print(f"🛠️ Inserting: {device_name} = {energy_val} kWh @ {timestamp}")
    
    # Check for dry run (safety)
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    
    data = [{
        "timestamp": timestamp,
        "device_name": device_name,
        "energy_kwh": energy_val,
        "power_w": 0,
        "id": "manual_insert"
    }]
    
    if dry_run:
        print("🐫 DRY RUN: Not saving.")
        return

    if save_energy_readings(data):
        print("✅ Successfully inserted.")
    else:
        print("❌ Failed to insert.")
        sys.exit(1)

if __name__ == "__main__":
    main()
