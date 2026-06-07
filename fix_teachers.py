import os
from supabase import create_client

url = "https://ftpkhueqooyqvwliifzb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ0cGtodWVxb295cXZ3bGlpZnpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzE2NTU4NiwiZXhwIjoyMDkyNzQxNTg2fQ.WKKO1YucBZ9ELihb3dUVGeGolboRZ0UEnnFydmZm594"
sb = create_client(url, key)

import json
res = sb.table('statistics').select('id, data_json').eq('table_id', 'LMS_TEACHERS_1').execute()
if res.data:
    row_id = res.data[0]['id']
    all_records = json.loads(res.data[0]['data_json'])
    print(f'Before: {all_records}')
    new_records = [r for r in all_records if r]
    print(f'After: {new_records}')
    sb.table('statistics').update({"data_json": json.dumps(new_records)}).eq("id", row_id).execute()
    print('Fixed!')
