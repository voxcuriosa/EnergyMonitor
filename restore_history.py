import sqlite3
import os
import shutil
import datetime

db_path = r'C:\Users\chr1203\AppData\Roaming\Antigravity\User\globalStorage\state.vscdb'
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = f"{db_path}.pre_restore_{timestamp}"

try:
    # 1. Backup the current DB
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)
        print(f"Backed up current database to {backup_path}")

    # 2. Connect and delete the key
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    key = 'antigravityUnifiedStateSync.trajectorySummaries'
    cursor.execute("DELETE FROM ItemTable WHERE key = ?", (key,))
    affected_rows = cursor.rowcount
    
    if affected_rows > 0:
        conn.commit()
        print(f"Successfully deleted key '{key}' from DB. Extension should rebuild history on next reload.")
    else:
        print(f"Key '{key}' was not found or already empty.")
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
