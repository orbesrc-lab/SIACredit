import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)

res = supabase.table('factors').select('id, number, name, leader_id, characteristics(id, number, name, aspects(id, text))').eq('inst_id', 1).eq('program_id', 56).execute()
print(f'Factors: {len(res.data)}')
for f in res.data:
    chars = f.get('characteristics', [])
    total_aspects = sum(len(c.get('aspects', [])) for c in chars)
    print(f"  Factor {f['number']}: {f['name'][:50]} | chars={len(chars)} | aspects={total_aspects} | leader={f.get('leader_id')}")
