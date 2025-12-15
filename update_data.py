import time
from homey_client import HomeyClient
from database import save_energy_readings, init_db

def main():
    print("🚀 Starting Energy Data Update...")
    
    # 1. Initialize Database (Ensure table exists)
    print("Checking database table...")
    init_db()
    
    # 2. Fetch Data from Homey
    print("Connecting to Homey API...")
    try:
        client = HomeyClient()
        data = client.get_energy_data()
        
        if not data:
            print("⚠️ No data received from Homey (or error occurred).")
            return

        print(f"✅ Received {len(data)} readings from Homey.")
        
        # 3. Save to Database
        print("Saving to database...")
        success = save_energy_readings(data)
        
        if success:
            print("🎉 Success! Data updated.")
        else:
            print("❌ Failed to save data to database.")
            exit(1) # Fail the action
            
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
