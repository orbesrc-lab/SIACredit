import os
from dotenv import load_dotenv
import psycopg2

load_dotenv(dotenv_path="c:/SIAC/.env")
db_url = os.environ.get("DATABASE_URL")

sql = """
ALTER TABLE public.security_backup_logs DISABLE ROW LEVEL SECURITY;
"""

try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(sql)
    print("RLS disabled on security_backup_logs.")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
