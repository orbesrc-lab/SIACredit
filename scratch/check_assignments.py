import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
sb = create_client(url, key)

print("Cargos Diccionario:", sb.table('skel_cargos_diccionario').select('cargo_id', count='exact').execute().count)
cargos = sb.table('skel_cargos').select('id, nombre').execute().data
print("Cargos:", cargos[:5])
