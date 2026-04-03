import ftplib

FTP_HOST = "voxcuriosa.no"
FTP_USER = "cpjvfkip"
FTP_PASS = "F2gw2FSXJcJLtk!"

def upload():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd("/public_html")
    
    with open(r"c:\Users\chr1203\OneDrive - Telemark fylkeskommune\Jobb\Diverse\Antigravity\vox_portal\index.html", "rb") as f:
        ftp.storbinary("STOR index.html", f)
        
    print("Uploaded fresh index.html with flervalgsgenerator preserved and energy monitor updated!")
    ftp.quit()

if __name__ == "__main__":
    upload()
