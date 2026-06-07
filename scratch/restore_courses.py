import json
import os
import sys
from dotenv import load_dotenv

load_dotenv('c:/SIAC/.env')

# Append root directory to sys.path
sys.path.append(os.path.abspath('c:/SIAC'))

import formacion_storage

try:
    with open('c:/SIAC/instance/local_courses.json', 'r', encoding='utf-8') as f:
        courses = json.load(f)
except FileNotFoundError:
    print("No local_courses.json found.")
    courses = []

count = 0
for course in courses:
    inst_id = course.get('inst_id', 1)
    program_id = course.get('program_id', 47)
    saved = formacion_storage.save_course(inst_id, program_id, course)
    if saved:
        count += 1
        print(f"Restored course: {course.get('title', 'Unknown')}")

print(f"Total courses restored: {count}")
