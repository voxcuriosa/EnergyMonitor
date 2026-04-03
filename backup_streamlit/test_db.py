import os
import pymysql
import time

def test_db():
    print("Testing DB connection...")
    try:
        # Load secrets
        with open(".streamlit/secrets.toml", "r") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("["):
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val

        start = time.time()
        conn = pymysql.connect(
            host=os.environ['host'],
            user=os.environ['user'],
            password=os.environ['password'],
            database=os.environ['dbname'],
            port=int(os.environ['port']),
            connect_timeout=5
        )
        latency = time.time() - start
        print(f"SUCCESS! Connected in {latency:.2f}s")
        conn.close()
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    test_db()
