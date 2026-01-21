import psycopg2
import streamlit as st
from datetime import datetime
import os

def check_db():
    try:
        # Load secrets manually since we might not run via streamlit run
        secrets = st.secrets["postgres"]
        
        print(f"📂 Current Directory: {os.getcwd()}")
        ca_path = os.path.abspath("ca.pem")
        print(f"🔒 Cert Path: {ca_path}")
        print(f"👀 Does cert exist? {os.path.exists(ca_path)}")

        print("🚀 Attempting to connect to DB...")
        conn = psycopg2.connect(
            host=secrets["host"],
            port=secrets["port"],
            dbname=secrets["dbname"],
            user=secrets["user"],
            password=secrets["password"],
            sslmode=secrets["sslmode"],
            connect_timeout=5
        )
        print("✅ Connected!")
        
        cur = conn.cursor()
        
        # Check specifically for Totalt on 2025-01-01
        query = """
            SELECT * FROM energy_readings 
            WHERE device_name = 'Totalt' 
            AND timestamp >= '2025-01-01 00:00:00'
            AND timestamp < '2025-01-02 00:00:00';
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        
        if rows:
            print(f"✅ FOUND DATA! Found {len(rows)} entries.")
            for row in rows:
                print(f"   - {row}")
        else:
            print("❌ NO DATA FOUND for 'Totalt' on 2025-01-01.")
            
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_db()
