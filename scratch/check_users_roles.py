
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("--- Usuarios ---")
users = supabase.table('users').select("*").execute()
for u in users.data:
    print(f"ID: {u['id']}, Email: {u['email']}, Role: {u['role']}, Name: {u.get('name')}, Inst: {u.get('inst_id')}")

print("\n--- Factores y Líderes ---")
factors = supabase.table('factors').select("id, number, name, leader_id").execute()
for f in factors.data:
    if f.get('leader_id'):
        print(f"Factor {f['number']}: {f['name']} - Leader ID: {f['leader_id']}")
