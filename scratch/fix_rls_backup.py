import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get('DATABASE_URL')

if not db_url:
    print("No DATABASE_URL found.")
    exit(1)

# PostgreSQL policy to allow insert from anyone, including anon and service_role
sql = """
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'security_backup_logs' 
        AND policyname = 'Permitir insercion de logs'
    ) THEN
        CREATE POLICY "Permitir insercion de logs" 
        ON public.security_backup_logs 
        FOR INSERT 
        WITH CHECK (true);
    END IF;
END $$;
"""

try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(sql)
    print("Policy successfully created.")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error executing policy: {e}")
