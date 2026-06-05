import os
import re
from supabase import create_client

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    url = re.search(r'os\.getenv\("SUPABASE_URL",\s*"([^"]+)"\)', content).group(1)
    key = re.search(r'os\.getenv\("SUPABASE_KEY",\s*"([^"]+)"\)', content).group(1)

sb = create_client(url, key)
res = sb.table('statistics').select('*').limit(1).execute()
print(res.data)
