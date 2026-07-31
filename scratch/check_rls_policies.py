import os
from dotenv import load_dotenv
import psycopg2

load_dotenv(dotenv_path="c:/SIAC/.env")
db_url = os.environ.get("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("""
        SELECT polname, polcmd, polroles, polqual, polwithcheck 
        FROM pg_policy 
        WHERE polrelid = 'public.security_backup_logs'::regclass;
    """)
    rows = cur.fetchall()
    print("Policies on security_backup_logs:")
    for r in rows:
        print(r)
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
