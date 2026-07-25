import os, json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('c:/SIAC/.env')
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
supabase = create_client(url, key)

res = supabase.table('statistics').select('id, data_json').eq('table_id', 'GLOBAL_CONFIG').order('id', desc=True).limit(50).execute()
for r in res.data:
    try:
        data = json.loads(r['data_json'])
        if 'ai_api_key' in data:
            print(f"Row {r['id']} ({data.get('ai_provider')}): {data['ai_api_key']}")
    except:
        pass
