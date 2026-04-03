import ftplib

FTP_HOST = "voxcuriosa.no"
FTP_USER = "cpjvfkip"
FTP_PASS = "F2gw2FSXJcJLtk!"

def list_contents(path):
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd(path)
    print(f"Contents of {path}:")
    ftp.retrlines('LIST')
    ftp.quit()

if __name__ == "__main__":
    list_contents("/public_html/energymonitor")
