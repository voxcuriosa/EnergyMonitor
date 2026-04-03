import os, pymysql

def test():
    db_host = os.environ.get('host', 'voxcuriosa.no')
    with open('../.streamlit/secrets.toml') as f:
        for l in f:
            if '=' in l and not l.strip().startswith('['):
                k,v = l.split('=',1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")
                
    db = pymysql.connect(host=os.environ['host'], user=os.environ['user'], password=os.environ['password'], database=os.environ['dbname'])
    cur = db.cursor()
    cur.execute("SELECT DISTINCT device_name, device_id FROM energy_readings WHERE device_name IN ('Easee', 'Kjellergang')")
    print('Device IDs:', cur.fetchall())


if __name__ == "__main__":
    test()
