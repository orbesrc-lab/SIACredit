import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(dotenv_path="c:/SIAC/.env")
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

try:
    print("Testing insert into security_backup_logs...")
    # Find a user to get a valid user_id
    res = supabase.table('users').select('*').limit(1).execute()
    if not res.data:
        print("No users found.")
        exit(1)
        
    user = res.data[0]
    user_id = user['id']
    email = user['email']
    
    # Try insert
    response = supabase.table('security_backup_logs').insert({
        'user_id': user_id,
        'user_email': email,
        'inst_id': 1,
        'action_type': 'DEBUG_TEST',
        'status': 'SUCCESS'
    }).execute()
    
    print("Insert response:", response)
    
except Exception as e:
    print(f"Exception during insert: {type(e).__name__}: {e}")
