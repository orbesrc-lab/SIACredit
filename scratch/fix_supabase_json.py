import sys
sys.path.append('c:\\SIAC')
from dotenv import load_dotenv
load_dotenv('c:\\SIAC\\.env')
import json
import formacion_storage
client = formacion_storage._get_supabase()

resp = client.table('lms_courses').select('id, data').execute()

for row in resp.data:
    data_val = row['data']
    if isinstance(data_val, str):
        # Double-serialized. We need to parse it and update.
        try:
            parsed = json.loads(data_val)
            print(f"Updating {row['id']} to be a proper JSON object.")
            client.table('lms_courses').update({'data': parsed}).eq('id', row['id']).execute()
        except Exception as e:
            print(f"Error parsing {row['id']}: {e}")
    else:
        print(f"Course {row['id']} is already a dict.")
