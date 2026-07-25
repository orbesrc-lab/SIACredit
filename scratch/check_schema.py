import os, json
from supabase import create_client

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

if not supabase_url:
    # Try reading from .env if available, or print error
    with open('c:\\SIAC\\.env', 'r') as f:
        for line in f:
            if line.startswith('SUPABASE_URL='):
                supabase_url = line.strip().split('=')[1]
            if line.startswith('SUPABASE_KEY='):
                supabase_key = line.strip().split('=')[1]

supabase = create_client(supabase_url, supabase_key)
res = supabase.table('planning_axes').select('*').limit(1).execute()
print(json.dumps(res.data, indent=2))
