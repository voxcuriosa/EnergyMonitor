import ftplib
import re

FTP_HOST = "voxcuriosa.no"
FTP_USER = "cpjvfkip"
FTP_PASS = "F2gw2FSXJcJLtk!"

def fix():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd("/public_html")

    with open("index_temp2.html", "wb") as f:
        ftp.retrbinary("RETR index.html", f.write)

    with open("index_temp2.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Revert Flervalgsgenerator!
    # I accidentally replaced flervalgsgenerator.streamlit.app. But wait! I replaced the ENTIRE URL!
    # In index_temp2, I will find two https://voxcuriosa.no/energymonitor/ links. 
    # One of them used to be flervalgsgenerator.
    # Where was it? Probably near the word "Flervalgsgenerator".
    # I can just do a regex sub or manual replace based on surrounding text.
    
    # Or even better, download index.html from github or local if we have it? The user's `Kunnskap` or `vox_portal` has the source!
    pass

if __name__ == "__main__":
    fix()
