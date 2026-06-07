import os
from dotenv import load_dotenv

load_dotenv('c:\\SIAC\\.env')

from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
sb = create_client(url, key)

print("Testing like on statistics...")
try:
    res = sb.table('statistics').select('table_id').like('table_id', 'LMS_COURSES_%').execute()
    print("Success:", res.data)
except Exception as e:
    print("Error:", e)
