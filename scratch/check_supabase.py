import os
import json
from supabase import create_client
import re

url = ""
key = ""
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    url = re.search(r'SUPABASE_URL\s*=\s*os\.getenv\("SUPABASE_URL",\s*"([^"]+)"\)', content).group(1)
    key = re.search(r'SUPABASE_KEY\s*=\s*os\.getenv\("SUPABASE_KEY",\s*"([^"]+)"\)', content).group(1)

sb = create_client(url, key)
res = sb.table('statistics').select('data_json').eq('table_id', 'GLOBAL_CONFIG').execute()
print("DATABASE RESPONSE:", res.data)
