import ftplib
import os
import io

FTP_HOST = "voxcuriosa.no"
FTP_USER = "cpjvfkip"
FTP_PASS = "F2gw2FSXJcJLtk!"
REMOTE_DIR = "public_html/energymonitor"

def deploy():
    print(f"Deploying to {FTP_HOST}/{REMOTE_DIR}...")
    
    # Extract secrets
    db_host, db_user, db_pass, db_name = "", "", "", ""
    try:
        with open(".streamlit/secrets.toml", "r") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("["):
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key == "host": db_host = val
                    if key == "user": db_user = val
                    if key == "password": db_pass = val
                    if key == "dbname": db_name = val
    except Exception as e:
        print("Could not read secrets:", e)
        return

    # Prepare api.php
    api_content = ""
    with open("api.php", "r", encoding="utf-8") as f:
        api_content = f.read()
    
    api_content = api_content.replace("{{DB_HOST}}", db_host)
    api_content = api_content.replace("{{DB_USER}}", db_user)
    api_content = api_content.replace("{{DB_PASS}}", db_pass)
    api_content = api_content.replace("{{DB_NAME}}", db_name)
    
    # FTP Login
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print("Logged in!")
        
        # Navigate / Create dir
        try:
            ftp.cwd("/" + REMOTE_DIR)
        except:
            print(f"Creating directory {REMOTE_DIR}...")
            dirs = REMOTE_DIR.split("/")
            ftp.cwd("/")
            for d in dirs:
                if d:
                    try:
                        ftp.cwd(d)
                    except:
                        ftp.mkd(d)
                        ftp.cwd(d)

        # Delete old index.html if exists
        try:
            ftp.delete("index.html")
        except:
            pass

        # Upload index.php
        print("Uploading index.php...")
        with open("index.php", "rb") as f:
            ftp.storbinary("STOR index.php", f)
            
        # Upload auth.php
        print("Uploading auth.php...")
        with open("auth.php", "rb") as f:
            ftp.storbinary("STOR auth.php", f)
            
        # Upload JS
        print("Uploading app.js...")
        with open("app.js", "rb") as f:
            ftp.storbinary("STOR app.js", f)
            
        # Upload PHP
        print("Uploading api.php...")
        bio = io.BytesIO(api_content.encode('utf-8'))
        ftp.storbinary("STOR api.php", bio)

        ftp.quit()
        print("Deploy complete! Visit https://voxcuriosa.no/energymonitor/")
    except Exception as e:
        print("FTP Error:", e)

if __name__ == "__main__":
    deploy()
