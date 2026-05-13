import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("c:/SIAC/.env")

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

res = supabase.table('factors').select("id, number, name").execute()
print("All Factors in DB:", res.data)
