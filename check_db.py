import sqlite3
import os
import json

roaming = os.path.expandvars(r"%APPDATA%\Antigravity\User\globalStorage")
vscdb_path = os.path.join(roaming, "state.vscdb")

try:
    conn = sqlite3.connect(vscdb_path)
    cursor = conn.cursor()
    cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%antigravity%' OR key LIKE '%gemini%'")
    keys = cursor.fetchall()
    print("Found keys related to antigravity/gemini:")
    for k in keys:
        print(f" - {k[0]}")
        
    # Check if there is a history index or similar
    cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%history%' OR key LIKE '%workspace%' OR key LIKE '%trajectory%'")
    data = cursor.fetchall()
    print("\nInteresting values:")
    for row in data:
        key, val = row
        if key == 'antigravityUnifiedStateSync.trajectorySummaries':
             print(f"Key: {key}\nVal: {val}\n")
        else:
             print(f"Key: {key}\nVal: {val[:200]}...\n")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
