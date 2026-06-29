import os, psycopg2, uuid
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv('c:\\SIAC\\.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
conn.autocommit = True
cur = conn.cursor()

try:
    user_id = str(uuid.uuid4())
    pass_hash = generate_password_hash('Profesor2025!')
    
    cur.execute("""
        INSERT INTO users (id, email, password_hash, role, name, inst_id, program_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (email) DO UPDATE SET password_hash = EXCLUDED.password_hash, role = EXCLUDED.role;
    """, (user_id, 'jvorbesg@gmail.com', pass_hash, 'profesor', 'John Vicente Orbes Gómez', 1, 0))
    print("Teacher user successfully created/updated.")
except Exception as e:
    print("Error:", e)
finally:
    conn.close()
