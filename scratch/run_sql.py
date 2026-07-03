import os
import psycopg2
from dotenv import load_dotenv

def execute_sql():
    load_dotenv('c:\\SIAC\\.env')
    db_url = os.getenv('DATABASE_URL')
    
    with open('c:\\SIAC\\schema_security_logs.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
        
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        print("SQL executed successfully.")
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    execute_sql()
