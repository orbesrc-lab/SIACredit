import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

load_dotenv("c:/SIAC/.env")
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

res = supabase.table('statistics').select("*").execute()
for r in res.data:
    try:
        json.loads(r['data_json'])
    except Exception as e:
        print(f"Error parsing JSON for id {r.get('id')}, table_id {r.get('table_id')}: {e}")
        print(f"Content: {r['data_json'][:100]}")
