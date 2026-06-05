import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print("--- Querying all rows in 'statistics' table ---")
res = supabase.table('statistics').select("id, table_id, inst_id, program_id").execute()
for row in res.data:
    print(row)
