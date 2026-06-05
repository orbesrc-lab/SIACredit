import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

sb = create_client(url, key)
res = sb.table('statistics').select('*').like('table_id', '%LMS%').execute()
print(f"Found {len(res.data)} matching rows:")
for row in res.data:
    print(f"ID: {row.get('id')}, table_id: {row.get('table_id')}, inst_id: {row.get('inst_id')}, program_id: {row.get('program_id')}, data_len: {len(row.get('data_json', '')) if row.get('data_json') else 0}")
    try:
        data = json.loads(row.get('data_json', '{}'))
        print("Content sample:")
        print(json.dumps(data, indent=2)[:500])
    except Exception as e:
         print("Error parsing json:", e)
