import os
from dotenv import load_dotenv

load_dotenv('c:\\SIAC\\.env')

import sys
sys.path.append('c:\\SIAC')
from formacion_storage import load_courses, load_course, load_teachers

print("Loading courses:")
try:
    courses = load_courses(1)
    print(f"Total courses: {len(courses) if courses else 'None'}")
    if courses:
        cid = courses[0].get('id')
        print(f"Testing load_course for {cid}:")
        c = load_course(cid)
        print("Course loaded:", c)
except Exception as e:
    print("Error:", e)

print("Loading teachers:")
try:
    teachers = load_teachers(1)
    print(f"Total teachers: {len(teachers) if teachers else 'None'}")
    if teachers:
        for t in teachers:
            print(t)
except Exception as e:
    print("Error:", e)
