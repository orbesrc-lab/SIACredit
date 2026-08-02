import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
sb = create_client(url, key)

# Get all cargos
cargos = sb.table('skel_cargos').select('*').execute().data

# Group by (empresa_id, nombre)
grouped = {}
for c in cargos:
    key = (c['empresa_id'], c['nombre'].strip().lower())
    if key not in grouped:
        grouped[key] = []
    grouped[key].append(c)

for key, copies in grouped.items():
    if len(copies) > 1:
        print(f"Found {len(copies)} copies of cargo '{key[1]}' for empresa {key[0]}")
        survivor = copies[0]['id']
        duplicates = [c['id'] for c in copies[1:]]
        
        # Update colaboradores to point to the survivor
        for dup in duplicates:
            # Update colaboradores
            sb.table('skel_colaboradores').update({"cargo_id": survivor}).eq('cargo_id', dup).execute()
            # Update skel_cargos_diccionario
            sb.table('skel_cargos_diccionario').update({"cargo_id": survivor}).eq('cargo_id', dup).execute()
            
            # Finally delete the duplicate cargo
            sb.table('skel_cargos').delete().eq('id', dup).execute()
        
        print(f"-> Kept {survivor}, deleted {duplicates}")

print("Deduplication complete.")
