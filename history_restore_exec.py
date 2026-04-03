import os
import shutil
import datetime

# Paths
ROAMING = r"C:\Users\chr1203\AppData\Roaming\Antigravity\User"
GEMINI = r"C:\Users\chr1203\.gemini\antigravity"
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def backup_storage():
    print(f"Backing up storage to safe_backup_{TIMESTAMP}...")
    gs_path = os.path.join(ROAMING, "globalStorage")
    ws_path = os.path.join(ROAMING, "workspaceStorage")
    
    gs_backup = os.path.join(ROAMING, f"globalStorage.safe_backup_{TIMESTAMP}")
    ws_backup = os.path.join(ROAMING, f"workspaceStorage.safe_backup_{TIMESTAMP}")
    
    if os.path.exists(gs_path):
        shutil.copytree(gs_path, gs_backup)
        print(f"Backed up globalStorage to {gs_backup}")
    
    if os.path.exists(ws_path):
        shutil.copytree(ws_path, ws_backup)
        print(f"Backed up workspaceStorage to {ws_backup}")

def toggle_files(folder_name):
    print(f"Toggling files in {folder_name}...")
    path = os.path.join(GEMINI, folder_name)
    temp_path = os.path.join(GEMINI, f"{folder_name}_temp_{TIMESTAMP}")
    
    if os.path.exists(path):
        os.rename(path, temp_path)
        print(f"Moved {folder_name} to {temp_path}")
        os.makedirs(path, exist_ok=True)
        
        # Move files back
        for item in os.listdir(temp_path):
            s = os.path.join(temp_path, item)
            d = os.path.join(path, item)
            shutil.move(s, d)
        
        print(f"Moved files back to {path}")
        os.rmdir(temp_path)

def refresh_db():
    print("Refreshing internal database index...")
    db_path = os.path.join(ROAMING, "globalStorage", "state.vscdb")
    db_bak = os.path.join(ROAMING, "globalStorage", f"state.vscdb.pre_restore_{TIMESTAMP}")
    
    # Check if we should use the smaller backup
    backup_db = os.path.join(ROAMING, "globalStorage.bak", "state.vscdb")
    
    if os.path.exists(db_path):
        shutil.copy2(db_path, db_bak)
        print(f"Backed up current database to {db_bak}")
    
    # We won't swap the DB yet, let's try the toggle first as it's less intrusive.
    # But we will touch the DB to ensure VS Code detects a change.
    with open(db_path, "ab") as f:
        os.fsync(f.fileno())
    print("Touched database to trigger reload.")

if __name__ == "__main__":
    backup_storage()
    toggle_files("conversations")
    toggle_files("implicit")
    refresh_db()
    print("Restoration process completed successfully.")
