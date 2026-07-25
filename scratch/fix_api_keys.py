import sys
import json
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db import supabase

def fix_db():
    try:
        # Fix GLOBAL_CONFIG
        check = supabase.table('statistics').select("id, data_json").eq("table_id", "GLOBAL_CONFIG").execute()
        if check.data:
            row = check.data[0]
            data = json.loads(row['data_json'])
            if data.get('ai_api_key') and '••••' in data.get('ai_api_key'):
                print(f"Found corrupted global key. Removing it.")
                del data['ai_api_key']
                supabase.table('statistics').update({"data_json": json.dumps(data)}).eq("id", row["id"]).execute()
                print("Global config fixed.")
        
        # Fix all INST_AI_CONFIG_
        check2 = supabase.table('statistics').select("id, data_json").like("table_id", "INST_AI_CONFIG_%").execute()
        if check2.data:
            for row in check2.data:
                data = json.loads(row['data_json'])
                if data.get('ai_api_key') and '••••' in data.get('ai_api_key'):
                    print(f"Found corrupted inst key in {row['id']}. Removing it.")
                    del data['ai_api_key']
                    supabase.table('statistics').update({"data_json": json.dumps(data)}).eq("id", row["id"]).execute()
        
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_db()
