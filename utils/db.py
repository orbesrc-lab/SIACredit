import os
from dotenv import load_dotenv
from supabase import create_client, Client, ClientOptions

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
options = ClientOptions(postgrest_client_timeout=8)
supabase: Client = create_client(url, key, options=options)

def get_active_inst_id(requested_id=None):
    try:
        if requested_id and int(requested_id) > 1:
            check = supabase.table('institution').select("id").eq("id", int(requested_id)).execute()
            if check.data:
                return int(requested_id)
        
        res = supabase.table('factors').select("inst_id").limit(1).execute()
        if res.data:
            return res.data[0]['inst_id']

        res_inst = supabase.table('institution').select("id").order("id", desc=True).limit(1).execute()
        if res_inst.data:
            return res_inst.data[0]['id']
    except Exception as e:
        print(f"Error resolving inst_id: {e}")
    return 7
