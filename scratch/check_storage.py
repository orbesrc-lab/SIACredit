import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
if not url or not key:
    print("No Supabase credentials")
    exit(1)

supabase = create_client(url, key)

try:
    buckets = supabase.storage.list_buckets()
    print("Buckets:", [b.name for b in buckets])
    
    if 'lms_files' not in [b.name for b in buckets]:
        supabase.storage.create_bucket('lms_files', options={"public": True})
        print("Bucket 'lms_files' created.")
    else:
        print("Bucket 'lms_files' already exists.")
        
except Exception as e:
    print("Error with storage:", e)
