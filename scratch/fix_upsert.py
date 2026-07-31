import os
import re

file_path = r'c:\SIAC\routes\business.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        # Insert into statistics directly
        insert_res = supabase.table('statistics').insert({
            'inst_id': inst_id,
            'table_id': matrix_type.upper(),
            'program_id': None,
            'data_json': data
        }).execute()'''

replacement = '''        # Upsert logic to avoid unique constraint errors
        res = supabase.table('statistics').select("id").eq("table_id", matrix_type.upper()).eq("inst_id", inst_id).order("id", desc=True).limit(1).execute()
        
        if res.data:
            db_id = res.data[0]['id']
            supabase.table('statistics').update({
                'data_json': data
            }).eq("id", db_id).execute()
        else:
            supabase.table('statistics').insert({
                'inst_id': inst_id,
                'table_id': matrix_type.upper(),
                'program_id': None,
                'data_json': data
            }).execute()'''

content = content.replace(target, replacement)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Upsert logic implemented in business.py")
