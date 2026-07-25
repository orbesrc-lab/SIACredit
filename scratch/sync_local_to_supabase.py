import os
import json
from dotenv import load_dotenv
from supabase import create_client
import formacion_storage

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment!")
    exit(1)

supabase = create_client(url, key)

print("Starting manual sync from local instance to Supabase...")

# 1. Sync Courses
courses_file = formacion_storage.COURSES_FILE
if os.path.exists(courses_file):
    try:
        with open(courses_file, 'r', encoding='utf-8') as f:
            courses = json.load(f)
        
        # Get all distinct (inst_id, program_id)
        pairs = set()
        for c in courses:
            inst_id = c.get('inst_id', 1)
            program_id = c.get('program_id', 0)
            pairs.add((inst_id, program_id))
            
        for inst_id, program_id in pairs:
            print(f"Syncing courses for inst_id={inst_id}, program_id={program_id}...")
            success = formacion_storage.sync_courses_only(inst_id, program_id, supabase)
            print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"Error reading local courses: {e}")
else:
    print("No local courses file found.")

# 2. Sync Teachers
teachers_file = formacion_storage.TEACHERS_FILE
if os.path.exists(teachers_file):
    try:
        with open(teachers_file, 'r', encoding='utf-8') as f:
            teachers = json.load(f)
            
        inst_ids = set(t.get('inst_id', 1) for t in teachers)
        for inst_id in inst_ids:
            print(f"Syncing teachers for inst_id={inst_id}...")
            success = formacion_storage.sync_teachers_only(inst_id, supabase)
            print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"Error reading local teachers: {e}")
else:
    print("No local teachers file found.")

# 3. Sync Students
students_file = formacion_storage.STUDENTS_FILE
if os.path.exists(students_file):
    try:
        with open(students_file, 'r', encoding='utf-8') as f:
            students = json.load(f)
            
        inst_ids = set(s.get('inst_id', 1) for s in students)
        for inst_id in inst_ids:
            print(f"Syncing students for inst_id={inst_id}...")
            success = formacion_storage.sync_students_only(inst_id, supabase)
            print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"Error reading local students: {e}")
else:
    print("No local students file found.")

print("Sync completed!")
