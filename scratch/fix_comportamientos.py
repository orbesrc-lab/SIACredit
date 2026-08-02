import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
sb = create_client(url, key)

# 1. Obtener todas las competencias
comps = sb.table('skel_diccionario_competencias').select('id, nombre').execute().data

# 2. Obtener todos los comportamientos
comports = sb.table('skel_diccionario_comportamientos').select('competencia_id').execute().data
comps_with_comports = set(c['competencia_id'] for c in comports)

inserts = []
for comp in comps:
    if comp['id'] not in comps_with_comports:
        # Create a default question for this competency
        inserts.append({
            "competencia_id": comp['id'],
            "descripcion": f"¿Cómo evalúas el nivel de desempeño o dominio en: {comp['nombre']}?",
            "nivel_esperado": 5
        })

if inserts:
    print(f"Insertando {len(inserts)} comportamientos por defecto...")
    sb.table('skel_diccionario_comportamientos').insert(inserts).execute()
    print("¡Listo!")
else:
    print("Todas las competencias ya tienen comportamientos.")
