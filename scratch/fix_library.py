import re

with open(r'c:\SIAC\routes\ai.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """def get_library():
    inst_id = request.args.get('inst_id', 1, type=int)
    try:
        global_res = supabase.table('statistics').select("data_json").eq("table_id", "BIBLIOTECA_GLOBAL").execute()
        
        def parse_data(data_row):
            if not data_row: return []
            dj = data_row[0].get('data_json', [])
            if isinstance(dj, str):
                import json
                try: return json.loads(dj)
                except: return []
            return dj
            
        global_docs = parse_data(global_res.data)
        
        inst_res = supabase.table('statistics').select("data_json").eq("table_id", "BIBLIOTECA_INST").eq("inst_id", inst_id).execute()
        inst_docs = parse_data(inst_res.data)
        
        return jsonify({
            "global": global_docs,
            "institucional": inst_docs
        })
    except Exception as e:
        print(f"Error loading library: {e}")
        return jsonify({"global": [], "institucional": []})"""

content = re.sub(r"def get_library\(\):.*?return jsonify\(\{\"global\": \[\], \"institucional\": \[\]\}\)", replacement, content, flags=re.DOTALL)

with open(r'c:\SIAC\routes\ai.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed get_library in ai.py")
