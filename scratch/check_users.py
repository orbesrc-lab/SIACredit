import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

try:
    res = supabase.table("users").select("*").execute()
    print("USERS IN DATABASE:")
    for u in res.data:
        print(f"ID: {u.get('id')} | Email: {u.get('email')} | Name: {u.get('name')} | Role: {u.get('role')} | Inst: {u.get('inst_id')}")
except Exception as e:
    print(f"Error: {e}")
