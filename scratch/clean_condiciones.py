import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)

# Delete all factors for condiciones institucionales (program_id=56)
res = supabase.table('factors').delete().eq('inst_id', 1).eq('program_id', 56).execute()
print(f'Deleted {len(res.data)} factors from condiciones institucionales')
