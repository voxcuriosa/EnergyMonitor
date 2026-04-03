import ftplib
import os

FTP_HOST = "voxcuriosa.no"
FTP_USER = "cpjvfkip"
FTP_PASS = "F2gw2FSXJcJLtk!"

def list_ftp():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd("/public_html")
        dirs = []
        ftp.dir(dirs.append)
        for d in dirs:
            print(d)
        ftp.quit()
    except Exception as e:
        print("FTP Error:", e)

if __name__ == "__main__":
    list_ftp()
