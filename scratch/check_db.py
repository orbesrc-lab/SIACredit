import os
import re

url = None
key = None
with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    for line in f:
        m1 = re.search(r'os\.getenv\("SUPABASE_URL",\s*"([^"]+)"\)', line)
        if m1: url = m1.group(1)
        m2 = re.search(r'os\.getenv\("SUPABASE_KEY",\s*"([^"]+)"\)', line)
        if m2: key = m2.group(1)

print("URL:", url)
print("KEY:", key[:5] + "..." if key else None)

if url and key:
    from supabase import create_client
    sb = create_client(url, key)
    res = sb.table('statistics').select('data_json').eq('table_id', 'GLOBAL_CONFIG').execute()
    print("DB DATA:", res.data)
