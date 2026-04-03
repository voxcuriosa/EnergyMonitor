import sys
import tomli
from unittest.mock import MagicMock
from sqlalchemy import text

# 1. Setup Environment (Mocking Streamlit for database.py)
try:
    with open(".streamlit/secrets.toml", "rb") as f:
        secrets = tomli.load(f)
    mock_st = MagicMock()
    mock_st.secrets = secrets
    sys.modules["streamlit"] = mock_st
except Exception as e:
    print(f"Failed to load secrets: {e}")
    sys.exit(1)

from database import get_db_connection

def delete_records():
    print("Connecting to database...")
    engine = get_db_connection()
    if not engine:
        print("Failed to connect.")
        return

    # Records identified as bad:
    # 1356: 30.97 kWh on Jan 1st (incorrectly low reading)
    # 1370: 5.98 kWh on Feb 1st (incorrectly low reading)
    bad_ids = (1356, 1370)
    
    try:
        with engine.connect() as conn:
            print(f"Deleting IDs: {bad_ids}")
            result = conn.execute(text("DELETE FROM energy_readings WHERE id IN :ids"), {"ids": bad_ids})
            conn.commit()
            print(f"Successfully deleted {result.rowcount} records.")
    except Exception as e:
        print(f"Error during deletion: {e}")

if __name__ == "__main__":
    delete_records()
