import os
import requests
import json
from homey_client import HomeyClient

def inspect_devices():
    print("🔍 Inspecting Homey Devices...")
    try:
        # Re-use HomeyClient logic for auth, but we need full access, not just energy func
        # We'll just instantiate it to get base_url and headers
        client = HomeyClient()
        
        # Override headers to be sure (HomeyClient does this but explicit is good)
        headers = client.headers
        url = client.base_url # This is .../api/manager/devices/device
        
        print(f"🌐 Fetching from: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        devices = response.json()
        print(f"✅ Found {len(devices)} devices. Filtering for relevant ones...\n")
        
        relevant_devices = []
        
        for dev_id, dev in devices.items():
            name = dev.get('name', 'Unknown')
            # Check if it matches what we are looking for loosely
            if "vib" in name.lower() or "vvb" in name.lower() or "tibber" in name.lower() or "easee" in name.lower() or "puls" in name.lower():
                print(f"🎯 MATCH FOUND: {name}")
                print(f"   ID: {dev_id}")
                print(f"   Class: {dev.get('class')}")
                print(f"   Driver: {dev.get('driverUri')}")
                print(f"   Capabilities: {list(dev.get('capabilities', []))}")
                print("-" * 40)
                relevant_devices.append(dev)
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_devices()
