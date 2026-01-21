import streamlit as st
from database import get_db_connection
from datetime import datetime
import psycopg2

def insert_baseline():
    st.title("💾 Manuell Data Insetting")
    
    # Value from user
    value = 179220
    name = "Totalt"
    timestamp = datetime(2025, 1, 1, 0, 0, 0)
    
    st.write(f"Forsøker å sette inn: **{name}** = {value} kWh @ {timestamp}")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insert query
        query = """
            INSERT INTO energy_readings (timestamp, device_name, energy_kwh, power_w)
            VALUES (%s, %s, %s, %s)
        """
        
        cur.execute(query, (timestamp, name, value, 0))
        conn.commit()
        
        st.success("✅ Data satt inn i databasen!")
        st.balloons()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        st.error(f"❌ Feil ved insetting: {e}")

if __name__ == "__main__":
    insert_baseline()
