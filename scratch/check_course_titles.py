import sys
sys.path.append('c:\\SIAC')
import formacion_storage
import json

courses = formacion_storage.load_courses(1, 0)
for c in courses:
    data = c.get('data')
    if isinstance(data, str):
        try:
            d = json.loads(data)
            print(f"ID: {c.get('id')} Keys: {list(d.keys())}")
            print(f"Name: {d.get('name')} | Title: {d.get('title')}")
        except:
            pass
