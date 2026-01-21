import os
import requests
from homey_client import HomeyClient

# Mock st.secrets using environment variables or a direct implementation for debugging
# We will subclass HomeyClient or just instance it if it supports env vars (which it does!)

def debug_homey():
    print("🔍 Starting Homey Debugger...")
    
    # Check if Env vars are set (User environment)
    # The user's metadata says they have secrets in `secrets.toml`, but `homey_client.py`
    # supports fallback to os.environ. 
    # Since I cannot read st.secrets in a plain python script easily without 'toml',
    # I will attempt to read secrets.toml manually if env vars are missing.
    
    try:
        if "HOMEY_ID" not in os.environ:
             # Try to read secrets.toml manually
             print("📂 Reading secrets.toml manualy...")
             with open(".streamlit/secrets.toml", "r") as f:
                 for line in f:
                     if "HOMEY_ID" in line:
                         os.environ["HOMEY_ID"] = line.split("=")[1].strip().strip('"')
                     if "HOMEY_API_KEY" in line:
                         os.environ["HOMEY_API_KEY"] = line.split("=")[1].strip().strip('"')
    except Exception as e:
        print(f"⚠️ Could not read secrets.toml: {e}")

    print(f"🆔 Homey ID Present: {'Yes' if os.environ.get('HOMEY_ID') else 'No'}")
    print(f"🔑 API Key Present: {'Yes' if os.environ.get('HOMEY_API_KEY') else 'No'}")

    try:
        client = HomeyClient()
        print(f"🌐 Connecting to: {client.base_url}")
        
        # Manually Request to see Status Code
        response = requests.get(client.base_url, headers=client.headers, timeout=10)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📜 Response Text (First 500 chars): {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} devices.")
        else:
            print("❌ Request Failed.")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    debug_homey()
