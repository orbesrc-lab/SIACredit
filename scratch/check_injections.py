import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if not url or not key:
    print("SUPABASE_URL o SUPABASE_KEY faltantes en el .env")
    exit(1)

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

def check_table(table, columns):
    print(f"\n--- Checking table '{table}' ---")
    resp = requests.get(f'{url}/rest/v1/{table}?select={columns}', headers=headers)
    if resp.status_code != 200:
        print(f"Error {resp.status_code}: {resp.text}")
        return
    
    rows = resp.json()
    for row in rows:
        for col, val in row.items():
            if val and isinstance(val, str):
                if "<script" in val.lower() or "javascript:" in val.lower() or "window.location" in val.lower() or "redirect" in val.lower():
                    print(f"[MALICIOUS INJECTION FOUND] Table: {table}, Row ID: {row.get('id')}, Col: {col}")
                    print(f"Value: {val}")
                elif "<" in val or ">" in val:
                    print(f"[HTML tag found] Table: {table}, Row ID: {row.get('id')}, Col: {col}, Value: {val}")

check_table("institution", "id,name,description,logo_url")
check_table("programs", "id,name,period,inst_id")
check_table("users", "id,email,name,role")
