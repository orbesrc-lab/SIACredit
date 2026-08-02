import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('SUPABASE_DB_URL') or os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url)
cur = conn.cursor()
tables = ['skel_tokens_acceso', 'skel_evaluaciones']
for t in tables:
    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{t}';")
    cols = [r[0] for r in cur.fetchall()]
    print(f'{t}: {cols}')
