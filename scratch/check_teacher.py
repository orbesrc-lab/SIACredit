import os, psycopg2
from dotenv import load_dotenv
load_dotenv('c:\\SIAC\\.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute("SELECT * FROM users WHERE email = 'jvorbesg@gmail.com';")
print('User:', cur.fetchone())
