import os
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv('c:\\SIAC\\.env')
db_url = os.getenv('DATABASE_URL')
try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT email, password_hash, role FROM users WHERE email = 'orbesrc@gmail.com';")
    row = cur.fetchone()
    if row:
        print(f"User found: {row[0]} | Role: {row[2]}")
        new_pass = 'Admin2025!'
        new_hash = generate_password_hash(new_pass)
        cur.execute("UPDATE users SET password_hash = %s, role = 'admin' WHERE email = %s;", (new_hash, 'orbesrc@gmail.com'))
        conn.commit()
        print(f"Password successfully reset to: {new_pass}")
    else:
        print("User orbesrc@gmail.com not found in database.")
    conn.close()
except Exception as e:
    print("Error:", e)
