import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print("--- Row 25 (inst 1, prog 47) ---")
res25 = supabase.table('statistics').select("*").eq("id", 25).execute()
if res25.data:
    print("Table ID:", res25.data[0]['table_id'])
    print("Data:", res25.data[0]['data_json'])
else:
    print("Row 25 not found!")

print("--- Row 32 (inst 2, prog 48) ---")
res32 = supabase.table('statistics').select("*").eq("id", 32).execute()
if res32.data:
    print("Table ID:", res32.data[0]['table_id'])
    print("Data:", res32.data[0]['data_json'])
else:
    print("Row 32 not found!")
