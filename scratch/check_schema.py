import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('c:\\SIAC\\.env')
db_url = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    # List tables
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tables = cur.fetchall()
    print("Tables:", [t[0] for t in tables])
    
    # List columns in users
    if ('users',) in tables:
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users';")
        cols = cur.fetchall()
        print("Users table columns:", cols)
    
    conn.close()
except Exception as e:
    print("Error:", e)
