import os, json
from dotenv import load_dotenv
load_dotenv('c:\\SIAC\\.env')
from supabase import create_client

sb = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))
res = sb.table('statistics').select('data_json').like('table_id', 'LMS_COURSES_%').execute()

for row in res.data:
    courses = json.loads(row['data_json'])
    for c in courses:
        data = c.get('data', c)
        print(f"ID: {data.get('id')}, Title: {data.get('title')}")
