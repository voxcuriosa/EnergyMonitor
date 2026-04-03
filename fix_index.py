import ftplib
import re

FTP_HOST = "voxcuriosa.no"
FTP_USER = "cpjvfkip"
FTP_PASS = "F2gw2FSXJcJLtk!"

def fix_index():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd("/public_html")

        # Download index.html
        with open("index_temp.html", "wb") as f:
            ftp.retrbinary("RETR index.html", f.write)

        with open("index_temp.html", "r", encoding="utf-8") as f:
            content = f.read()

        # Replace link to Streamlit with new link
        # It's probably https://energymonitor-*.streamlit.app or similar
        # Since we don't know the exact string, we use Regex or just replace 'https://.*streamlit.app.*' inside href?
        # Let's search for the actual streaming link.
        stream_matches = re.findall(r'href="(https://[^"]*streamlit[^"]*)"', content)
        if stream_matches:
            for m in stream_matches:
                print("Replacing:", m)
                content = content.replace(m, "https://voxcuriosa.no/energymonitor/")
        else:
            # Maybe it just opens energy port in some other way? Let's check portal links.
            print("No streamlit links found. Looking for energy/energi links...")
            out = re.findall(r'href="(.*?)"', content)
            print("Links found:", [o for o in out if 'energy' in o.lower() or 'strøm' in o.lower()])
            
            # Just do a blanket replace if we find an energy link
            content = re.sub(r'href="https://energymonitor-[^"]+"', 'href="https://voxcuriosa.no/energymonitor/"', content)

        with open("index_temp.html", "w", encoding="utf-8") as f:
            f.write(content)

        with open("index_temp.html", "rb") as f:
            ftp.storbinary("STOR index.html", f)
            
        print("Done replacing link in index.html!")
        ftp.quit()
    except Exception as e:
        print("FTP Error:", e)

if __name__ == "__main__":
    fix_index()
