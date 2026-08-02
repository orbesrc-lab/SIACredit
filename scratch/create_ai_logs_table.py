import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print('DATABASE_URL not found')
    exit(1)

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS ai_chat_logs (
            id SERIAL PRIMARY KEY,
            inst_id INTEGER,
            user_uid VARCHAR(255),
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            provider VARCHAR(50),
            model VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    print('Success')
except Exception as e:
    print(e)
finally:
    if 'conn' in locals() and conn: conn.close()

