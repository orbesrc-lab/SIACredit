import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('SUPABASE_DB_URL') or os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name='skel_diccionario_comportamientos';")
print("comportamientos:", cur.fetchall())

cur.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name='skel_diccionario_competencias';")
print("competencias:", cur.fetchall())
