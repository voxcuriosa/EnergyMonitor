import os
import pymysql
import requests

def inspect():
    with open(".streamlit/secrets.toml", "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("["):
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

    print("--- DB Readings ---")
    try:
        conn = pymysql.connect(
            host=os.environ['host'],
            user=os.environ['user'],
            password=os.environ['password'],
            database=os.environ['dbname'],
            port=int(os.environ['port'])
        )
        with conn.cursor() as cursor:
            # Check latest Varmepumpe & Fryser readings
            cursor.execute("SELECT timestamp, energy_kwh, device_name FROM energy_readings WHERE device_name LIKE '%varmepumpe%' OR device_name LIKE '%frys%' ORDER BY timestamp DESC LIMIT 20")
            for row in cursor.fetchall():
                print(row)
            
            # Check February readings for Varmepumpe to see if we can calculate April start - March start
            cursor.execute("SELECT timestamp, energy_kwh, device_name FROM energy_readings WHERE device_name LIKE '%varmepumpe%' AND timestamp >= '2026-02-01' AND timestamp <= '2026-03-02' ORDER BY timestamp DESC LIMIT 5")
            print("February / early March Varmepumpe readings:")
            for row in cursor.fetchall():
                print(row)
                
    except Exception as e:
        print("DB ERROR:", e)

    print("\n--- Homey ---")
    try:
        homey_id = os.environ.get('HOMEY_ID')
        api_key = os.environ.get('HOMEY_API_KEY')
        url = f"https://{homey_id}.connect.athom.com/api/manager/devices/device"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        response = requests.get(url, headers=headers)
        devices = response.json()
        print("Search raw:")
        for dev_id, dev in devices.items():
            name = dev.get('name', '').lower()
            if 'varmepumpe' in name or 'frys' in name:
                print(f"Name: {dev.get('name')} (ID: {dev_id})")
                caps = dev.get('capabilities', [])
                print(f" Caps: {caps}")
                cap_obj = dev.get('capabilitiesObj', {})
                for c, v in cap_obj.items():
                    if 'meter' in c or 'measure' in c:
                        print(f"  {c}: {v.get('value')}")
    except Exception as e:
        print("Homey ERROR:", e)

if __name__ == "__main__":
    inspect()
