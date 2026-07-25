import os, psycopg2
from dotenv import load_dotenv

load_dotenv('c:\\SIAC\\.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
conn.autocommit = True
cur = conn.cursor()

try:
    cur.execute("SELECT id FROM storage.buckets WHERE id = 'lms_files';")
    if not cur.fetchone():
        cur.execute("INSERT INTO storage.buckets (id, name, public) VALUES ('lms_files', 'lms_files', true);")
        print("Bucket 'lms_files' created.")
    
    cur.execute("""
        DROP POLICY IF EXISTS "Public Access lms_files" ON storage.objects;
        CREATE POLICY "Public Access lms_files" ON storage.objects FOR ALL USING (bucket_id = 'lms_files');
    """)
    print("Storage policy for 'lms_files' updated.")
except Exception as e:
    print("Error:", e)
finally:
    conn.close()
