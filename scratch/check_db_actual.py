import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("URL:", url)
print("KEY length:", len(key) if key else 0)

try:
    sb = create_client(url, key)
    res = sb.table('statistics').select('*').eq('table_id', 'GLOBAL_CONFIG').execute()
    print("GLOBAL_CONFIG rows:")
    for row in res.data:
        print(f"ID: {row['id']}, inst_id: {row['inst_id']}, program_id: {row['program_id']}, data_json: {row['data_json']}")
except Exception as e:
    print("Error:", e)
