import pandas as pd
import streamlit as st
import os
from sqlalchemy import create_engine, text

def get_db_connection():
    """Establishes a connection to the Database (MySQL/MariaDB)."""
    try:
        # Try getting secrets from Streamlit secrets first
        try:
            if "mysql" in st.secrets:
                secrets = st.secrets["mysql"]
                host = secrets['host']
                port = secrets['port']
                dbname = secrets['dbname']
                user = secrets['user']
                password = secrets['password']
                # Construct the connection string for MySQL
                db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
                
                engine = create_engine(db_url)
                return engine
                
            elif "postgres" in st.secrets:
                 # Keep legacy support or fallback if needed (though we migrated)
                secrets = st.secrets["postgres"]
                host = secrets['host']
                port = secrets['port']
                dbname = secrets['dbname']
                user = secrets['user']
                password = secrets['password']
                sslmode = secrets['sslmode']
                db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode={sslmode}"
                engine = create_engine(db_url)
                return engine

        except (FileNotFoundError, KeyError):
            # Fallback to environment variables (for GitHub Actions)
            pass
            
        print("DEBUG: Missing database credentials in secrets.toml")
        return None

    except Exception as e:
        print(f"DEBUG: Database connection error: {e}")
        return None

def init_db():
    """Initializes the database table if it doesn't exist."""
    engine = get_db_connection()
    if engine:
        try:
            with engine.connect() as conn:
                # Create energy_readings table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS energy_readings (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP,
                        device_id TEXT,
                        device_name TEXT,
                        power_w FLOAT,
                        energy_kwh FLOAT
                    );
                """))
                conn.commit()
        except Exception as e:
            print(f"DEBUG: Database init error: {e}")
            st.error(f"Database init error: {e}")

def save_energy_readings(readings):
    """Saves a list of energy readings to the database."""
    engine = get_db_connection()
    if engine:
        try:
            with engine.connect() as conn:
                for r in readings:
                    conn.execute(text("""
                        INSERT INTO energy_readings (timestamp, device_id, device_name, power_w, energy_kwh)
                        VALUES (:timestamp, :device_id, :device_name, :power_w, :energy_kwh)
                    """), {
                        "timestamp": r['timestamp'],
                        "device_id": r['id'],
                        "device_name": r['name'],
                        "power_w": r['power_w'],
                        "energy_kwh": r['energy_kwh']
                    })
                conn.commit()
            return True
        except Exception as e:
            print(f"DEBUG Error saving: {e}")
            st.error(f"Error saving energy readings: {e}")
            return False
    return False

def get_energy_readings():
    """Retrieves all energy readings."""
    engine = get_db_connection()
    if engine:
        try:
            with engine.connect() as conn:
                df = pd.read_sql("SELECT * FROM energy_readings ORDER BY timestamp DESC", conn)
                return df
        except Exception as e:
            st.error(f"Error fetching energy readings: {e}")
            return pd.DataFrame()
    return pd.DataFrame()
