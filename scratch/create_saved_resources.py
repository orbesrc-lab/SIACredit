import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("ERROR: DATABASE_URL no encontrado en .env")
    exit(1)

try:
    print('Conectando a base de datos...')
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS saved_resources (
        id SERIAL PRIMARY KEY,
        user_email TEXT NOT NULL,
        resource_id TEXT NOT NULL,
        title TEXT NOT NULL,
        authors TEXT,
        year INTEGER,
        url TEXT,
        apa_citation TEXT,
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    print('OK: Tabla saved_resources creada')
    
    conn.commit()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
