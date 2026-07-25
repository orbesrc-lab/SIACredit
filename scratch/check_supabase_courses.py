import sys
sys.path.append('c:\\SIAC')
from dotenv import load_dotenv
load_dotenv('c:\\SIAC\\.env')
import os
print('SUPABASE_URL:', os.environ.get('SUPABASE_URL'))

# Need to reload formacion_storage to pick up the env vars
import importlib
import formacion_storage
importlib.reload(formacion_storage)

print('Supabase client:', formacion_storage._get_supabase())
courses = formacion_storage._sb_load('lms_courses', {'inst_id': 1})
if courses:
    print('Found', len(courses), 'courses in Supabase')
    import json
    for c in courses:
        data = c.get('data')
        if isinstance(data, str): data = json.loads(data)
        print('Title:', data.get('title'), 'Name:', data.get('name'))
else:
    print('Supabase returned None or empty')
