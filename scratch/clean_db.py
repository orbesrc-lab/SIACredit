import os
import json
from dotenv import load_dotenv

load_dotenv('c:\\SIAC\\.env')

from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
sb = create_client(url, key)

print("Cleaning up lms_teachers...")
res = sb.table('statistics').select('id, data_json').eq('table_id', 'LMS_TEACHERS_1').execute()
if res.data:
    row_id = res.data[0]['id']
    all_records = json.loads(res.data[0]['data_json'])
    new_records = [r for r in all_records if r] # filter out empty dicts
    sb.table('statistics').update({"data_json": json.dumps(new_records)}).eq("id", row_id).execute()
    print("Cleaned up teachers.")

print("Cleaning up lms_students...")
res = sb.table('statistics').select('id, data_json').eq('table_id', 'LMS_STUDENTS_1').execute()
if res.data:
    row_id = res.data[0]['id']
    all_records = json.loads(res.data[0]['data_json'])
    new_records = [r for r in all_records if r]
    sb.table('statistics').update({"data_json": json.dumps(new_records)}).eq("id", row_id).execute()
    print("Cleaned up students.")
