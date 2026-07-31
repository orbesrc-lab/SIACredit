import os
from dotenv import load_dotenv
import psycopg2

load_dotenv(dotenv_path="c:/SIAC/.env")
db_url = os.environ.get("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM security_backup_logs;")
    count = cur.fetchone()[0]
    print(f"Total logs in DB: {count}")
    
    cur.execute("SELECT id, user_id, user_email, inst_id, action_type, status, timestamp FROM security_backup_logs ORDER BY timestamp DESC LIMIT 5;")
    rows = cur.fetchall()
    print("Latest logs:")
    for r in rows:
        print(r)
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
