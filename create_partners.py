import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("DATABASE_URL")

try:
    print(f"Connecting to: {db_url.replace('Johnorbes2026%2A', '***')}")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT,
            logo_base64 TEXT NOT NULL,
            inst_id INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    print('Tabla partners creada correctamente.')
    conn.close()
except Exception as e:
    print(f'Error: {e}')
