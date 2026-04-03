import ftplib

FTP_HOST = "voxcuriosa.no"
FTP_USER = "cpjvfkip"
FTP_PASS = "F2gw2FSXJcJLtk!"

def cleanup():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd("/public_html")
    
    # 1. Create backup folder if not exists
    try:
        ftp.mkd("backup_streamlit")
        print("Created backup_streamlit folder on FTP.")
    except:
        pass

    # 2. List of things to move to backup (if they exist)
    # Streamlit related or old test versions
    to_move = ["energy_test", ".github", "app.py", "requirements.txt", ".streamlit"]
    
    for item in to_move:
        try:
            ftp.rename(item, f"backup_streamlit/{item}")
            print(f"Moved {item} to backup_streamlit on FTP.")
        except:
            print(f"Skipping {item} (not found or error).")

    ftp.quit()

if __name__ == "__main__":
    cleanup()
