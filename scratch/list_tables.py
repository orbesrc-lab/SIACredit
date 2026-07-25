import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("DATABASE_URL not found in .env")
    exit(1)

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Query to list tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    print("Tables in database:")
    for table in tables:
        t_name = table[0]
        # Query columns for this table
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (t_name,))
        columns = cur.fetchall()
        cols_str = ", ".join([f"{c[0]} ({c[1]}{' NULL' if c[2] == 'YES' else ' NOT NULL'})" for c in columns])
        print(f" - {t_name}: {cols_str}")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
