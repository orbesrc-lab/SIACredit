import sys
sys.path.append('c:\\SIAC')
from dotenv import load_dotenv
load_dotenv('c:\\SIAC\\.env')
import json

import formacion_storage
import importlib
importlib.reload(formacion_storage)

local_courses = formacion_storage._local_query('SELECT id, inst_id, program_id, data FROM lms_courses')
print(f"Found {len(local_courses)} courses in local DB")

client = formacion_storage._get_supabase()

for row in local_courses:
    # _local_query actually merged `data`! Wait, let's use sqlite3 directly to avoid the merge
    pass

import sqlite3
conn = sqlite3.connect(r'c:\SIAC\instance\lms_local.db')
c = conn.cursor()
c.execute('SELECT id, inst_id, program_id, data FROM lms_courses')
raw_rows = c.fetchall()

for id_, inst_id, program_id, data_str in raw_rows:
    cdata = {}
    if data_str:
        try:
            cdata = json.loads(data_str)
        except:
            pass
    
    # Ensure title is present
    if 'name' in cdata and not 'title' in cdata:
        cdata['title'] = cdata.pop('name')
    if not 'title' in cdata:
        cdata['title'] = 'Curso Sin Titulo'
        
    cdata['program_id'] = 0 # force global visibility
    cdata['inst_id'] = inst_id
        
    sb_row = {
        'id': id_,
        'inst_id': inst_id,
        'program_id': 0,
        'data': json.dumps(cdata)
    }
    
    # Check if exists in Supabase
    existing = client.table('lms_courses').select('id').eq('id', id_).execute()
    if existing.data:
        print(f"Updating course {cdata.get('title')} in Supabase")
        client.table('lms_courses').update(sb_row).eq('id', id_).execute()
    else:
        print(f"Inserting course {cdata.get('title')} into Supabase")
        client.table('lms_courses').insert(sb_row).execute()

print("Migration complete!")
