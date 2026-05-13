import os, json, traceback
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('c:/SIAC/.env')
sup = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

try:
    res = sup.table('factors').select('inst_id, program_id').execute()
    combos = set((r['inst_id'], r['program_id']) for r in res.data)
    errors = []
    
    for i, p in combos:
        try:
            f_res = sup.table('factors').select('*, characteristics(*, aspects(*))').eq('inst_id', i).eq('program_id', p).execute()
            e_res = sup.table('evaluations').select('*').eq('inst_id', i).eq('program_id', p).execute()
            ev_res = sup.table('evidences').select('*').eq('inst_id', i).eq('program_id', p).execute()
            s_res = sup.table('statistics').select('*').eq('inst_id', i).eq('program_id', p).execute()
            
            evals_map = {e['char_id']: e for e in e_res.data}
            evid_map = {}
            for ev in ev_res.data:
                aspect_id = ev['aspect_id']
                if aspect_id not in evid_map:
                    evid_map[aspect_id] = []
                evid_map[aspect_id].append(ev)
            
            def safe_float(val):
                try:
                    if val is None or str(val).strip() == '': return 999.0
                    return float(val)
                except (ValueError, TypeError):
                    return 999.0

            stats_map = {s['table_id']: json.loads(s['data_json']) for s in s_res.data}
            
            f_res.data.sort(key=lambda x: safe_float(x.get('number')))
            for f in f_res.data:
                chars = f.get('characteristics', [])
                chars.sort(key=lambda x: safe_float(x.get('number')))
                for c in chars:
                    aspects = c.get('aspects', [])
                    aspects.sort(key=lambda x: safe_float(x.get('number')))
        except Exception as ex:
            errors.append(f"Error for {i},{p}: {ex}")
            
    if errors:
        print("ERRORS FOUND:")
        for err in errors:
            print(err)
    else:
        print("ALL TESTS PASSED SUCCESSFULLY.")
except Exception as e:
    print(f"Top level error: {e}")
