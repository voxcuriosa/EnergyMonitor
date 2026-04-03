import ftplib

FTP_HOST = "voxcuriosa.no"
FTP_USER = "cpjvfkip"
FTP_PASS = "F2gw2FSXJcJLtk!"

def read_file(path):
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    try:
        def callback(line): print(line)
        ftp.retrlines(f'RETR {path}', callback)
    except:
        print(f"Could not read {path}")
    ftp.quit()

if __name__ == "__main__":
    read_file("/public_html/index.php")
    print("--- index_wrapper.php ---")
    read_file("/public_html/index_wrapper.php")
