import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
supabase = create_client(url, key)

res = supabase.table('statistics').select('*').eq('table_id', 'DOFA_INTERNAL').execute()
print(json.dumps(res.data, indent=2))
