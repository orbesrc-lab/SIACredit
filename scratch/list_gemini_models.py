import json
import urllib.request
import os

from supabase import create_client, Client
url = os.environ.get('SUPABASE_URL', 'https://ftpkhueqooyqvwliifzb.supabase.co')
key = os.environ.get('SUPABASE_KEY', '')

# Need to read the key from check_db_actual.py or just use the local env vars?
# Actually I can just import supabase from utils.db
import sys
sys.path.append('c:\\SIAC')
from utils.db import supabase

check = supabase.table('statistics').select('data_json').eq('table_id', 'GLOBAL_CONFIG').order('id', desc=True).limit(1).execute()
if check.data:
    data = json.loads(check.data[0]['data_json'])
    api_key = data.get('ai_api_key')
    print('Found API Key!')
    
    url = f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}'
    try:
        with urllib.request.urlopen(url) as response:
            res = json.loads(response.read().decode())
            for m in res.get('models', []):
                print(m['name'], '-', m.get('displayName', ''))
    except Exception as e:
        print('ERROR:', e.read().decode() if hasattr(e, 'read') else str(e))
