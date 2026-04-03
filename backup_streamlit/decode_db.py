import sqlite3
import os
import base64

db_path = r'C:\Users\chr1203\AppData\Roaming\Antigravity\User\globalStorage\state.vscdb'

def decode_summaries(blob_b64):
    try:
        data = base64.b64decode(blob_b64)
        # This is likely protobuf, let's just look for UUID-like strings
        import re
        uuids = re.findall(b'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', data)
        return [u.decode() for u in uuids]
    except:
        return []

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM ItemTable WHERE key = 'antigravityUnifiedStateSync.trajectorySummaries'")
    row = cursor.fetchone()
    if row:
        val = row[0]
        ids = decode_summaries(val)
        print(f"Total conversation IDs found in DB: {len(ids)}")
        for i, cid in enumerate(ids):
            print(f"{i+1}: {cid}")
    else:
        print("Key 'antigravityUnifiedStateSync.trajectorySummaries' not found in DB.")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
