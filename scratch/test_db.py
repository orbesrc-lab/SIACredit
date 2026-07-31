import os
import psycopg2

db_url = "postgresql://postgres.ftpkhueqooyqvwliifzb:Johnorbes2026%2A@aws-1-us-west-2.pooler.supabase.com:6543/postgres"

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'security_backup_logs';")
    rows = cur.fetchall()
    if rows:
        print("Columns in security_backup_logs:")
        for r in rows:
            print(r)
        
        cur.execute("SELECT * FROM security_backup_logs LIMIT 5;")
        logs = cur.fetchall()
        print("Logs:", logs)
    else:
        print("Table security_backup_logs does NOT exist!")
    
    cur.close()
    conn.close()
except Exception as e:
    print("Database error:", e)
