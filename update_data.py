import time
import os
from homey_client import HomeyClient
from database import save_energy_readings, init_db

def main():
    print("Starting Energy Data Update...")
    
    # Check for Dry Run
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    if dry_run:
        print("DRY RUN ENABLED: Data will be fetched but NOT saved to database.")

    # 1. Initialize Database (Ensure table exists)
    print("Checking database table...")
    init_db()
    
    # 2. Fetch Data from Homey
    print("Connecting to Homey API...")
    try:
        client = HomeyClient()
        
        # DEBUG: Print lengths of ID and Key (safe way to check secrets exist)
        h_id_len = len(client.homey_id) if client.homey_id else 0
        h_key_len = len(client.api_key) if client.api_key else 0
        print(f"DEBUG: Homey ID length: {h_id_len}, API Key length: {h_key_len}")
        
        data = client.get_energy_data()
        
        if not data:
            print("Warning: No data received from Homey (or error occurred).")
            return

        print(f"Success: Received {len(data)} readings from Homey.")
        
        # 3. Save to Database
        if dry_run:
            print(f"Success: [DRY RUN] Would have saved {len(data)} readings to database.")
            print("Success! Connection test passed.")
            return

        print("Saving to database...")
        success = save_energy_readings(data)
        
        if success:
            print("Success! Data updated.")
        else:
            print("Error: Failed to save data to database.")
            exit(1) # Fail the action
            
    except Exception as e:
        print(f"Error: Critical Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
