import json
import os
import sys
sys.path.append('c:\\SIAC')
from utils.db import supabase

check = supabase.table('statistics').select('id, data_json').eq('table_id', 'GLOBAL_CONFIG').order('id', desc=True).limit(1).execute()
if check.data:
    row_id = check.data[0]['id']
    data = json.loads(check.data[0]['data_json'])
    if data.get('ai_model') in ['gemini-2.5-flash', 'gemini-1.5-flash']:
        data['ai_model'] = 'gemini-flash-latest'
        supabase.table('statistics').update({'data_json': json.dumps(data)}).eq('id', row_id).execute()
        print('Fixed in DB!')
    else:
        print('No fix needed in DB:', data.get('ai_model'))
