import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

load_dotenv("c:/SIAC/.env")
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

inst_id = 3
program_id = 3

try:
    model_res = supabase.table('factors').select("*, characteristics(*, aspects(*))").eq("inst_id", inst_id).eq("program_id", program_id).execute()
    factors = model_res.data
    factors.sort(key=lambda x: int(x.get('number', 999)))
    
    evals_res = supabase.table('evaluations').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
    evals_map = {e['aspect_id']: e for e in evals_res.data}
    
    evid_res = supabase.table('evidences').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
    evid_map = {}
    for ev in evid_res.data:
        aspect_id = ev['aspect_id']
        if aspect_id not in evid_map:
            evid_map[aspect_id] = []
        evid_map[aspect_id].append(ev)
        
    stats_res = supabase.table('statistics').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
    stats_map = {s['table_id']: json.loads(s['data_json']) for s in stats_res.data}
    
    report_data = {
        "institucion_id": inst_id,
        "programa_id": program_id,
        "factores": [],
        "cuadros": stats_map
    }
    
    for f in factors:
        factor_info = {
            "id": f['id'],
            "number": f['number'],
            "name": f['name']
        }
        
        chars = f.get('characteristics', [])
        chars.sort(key=lambda x: float(x.get('number', 999)))
        
        for c in chars:
            aspects = c.get('aspects', [])
            aspects.sort(key=lambda x: float(x.get('number', 999)))
            
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
