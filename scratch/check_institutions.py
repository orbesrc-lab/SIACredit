import os
from supabase import create_client

url = None
key = None
if os.path.exists(r'c:\SIAC\.env'):
    with open(r'c:\SIAC\.env', 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                if k.strip() == 'SUPABASE_URL':
                    url = v.strip().strip('"').strip("'")
                elif k.strip() == 'SUPABASE_KEY':
                    key = v.strip().strip('"').strip("'")

print("URL:", url)
print("KEY:", key[:10] + "..." if key else None)

if url and key:
    sb = create_client(url, key)
    res = sb.table('institution').select('*').execute()
    print("Institutions:", res.data)
    res_users = sb.table('users').select('*').execute()
    print("Users:", res_users.data)
