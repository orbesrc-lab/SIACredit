import os, json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('c:/SIAC/.env')
sb = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

res = sb.table('statistics').select('id, table_id, inst_id').eq('table_id', 'INST_AI_CONFIG').execute()
for r in res.data:
    new_id = f"INST_AI_CONFIG_{r['inst_id']}"
    print(f"Migrating {r['id']} to {new_id}")
    sb.table('statistics').update({'table_id': new_id}).eq('id', r['id']).execute()
print("Done")
