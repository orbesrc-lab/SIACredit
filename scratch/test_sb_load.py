import sys
import os
sys.path.append('c:\\SIAC')
from formacion_storage import _sb_load, _sb_upsert

print("Loading courses:")
courses = _sb_load('lms_courses')
print(f"Total courses: {len(courses) if courses else 'None'}")
for c in courses:
    print(c.get('id'), c.get('title'))

print("\nLoading specific course (replace with actual id later):")
if courses:
    cid = courses[0].get('id')
    print(f"Testing filter for {cid}:")
    c = _sb_load('lms_courses', {'id': cid})
    print(c)
