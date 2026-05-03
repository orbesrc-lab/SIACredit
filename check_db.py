import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

# Try to add name column via a special approach
# Since we can't run DDL via the REST API directly with anon/publishable key,
# we'll use the supabase-py client to do data-level operations
# The ALTER TABLE must be done from Supabase dashboard SQL Editor

# Check if name column exists by attempting to select it
print("Verificando si la columna 'name' existe...")
resp = requests.get(
    f'{url}/rest/v1/users?select=id,email,role,inst_id&limit=5',
    headers={
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
)
print(f"Status: {resp.status_code}")
print(f"Data: {resp.json()}")

# Try with name column
resp2 = requests.get(
    f'{url}/rest/v1/users?select=id,email,role,name,inst_id&limit=5',
    headers={
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
)
print(f"\nWith 'name' column - Status: {resp2.status_code}")
if resp2.status_code == 200:
    print("OK - columna 'name' existe!")
    print(resp2.json())
else:
    print("La columna 'name' NO existe aun.")
    print("Necesitas ejecutar este SQL en el SQL Editor de Supabase:")
    print("  ALTER TABLE users ADD COLUMN IF NOT EXISTS name TEXT;")
    print("  UPDATE users SET name = split_part(email, '@', 1) WHERE name IS NULL OR name = '';")
