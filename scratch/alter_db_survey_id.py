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
    
    print("Alterando tipo de columna 'indicador_survey_id' a VARCHAR(50)...")
    cur.execute("""
        ALTER TABLE planes_mejora 
        ALTER COLUMN indicador_survey_id TYPE VARCHAR(50);
    """)
    conn.commit()
    conn.close()
    print("SUCCESS - Columna alterada con exito.")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
