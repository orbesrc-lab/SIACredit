import os
import json
import uuid
from datetime import datetime
from supabase import create_client, Client

IS_VERCEL = os.environ.get("VERCEL") == "1"

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key) if url and key else None

def generate_id():
    return uuid.uuid4().hex[:9]

def get_default_program_id(inst_id):
    if inst_id == 1: return 47
    elif inst_id == 2: return 48
    elif inst_id == 3: return 50
    return 47

# === DOCENTES / TEACHERS ===

def load_teachers(inst_id):
    if not supabase: return []
    res = supabase.table('lms_teachers').select('data').eq('inst_id', inst_id).execute()
    return [row['data'] for row in res.data] if res.data else []

def save_teacher(inst_id, teacher_data):
    if not supabase: return None
    teacher_id = teacher_data.get('id')
    if not teacher_id:
        teacher_id = "t_" + generate_id()
        teacher_data['id'] = teacher_id
    teacher_data['inst_id'] = inst_id
    
    supabase.table('lms_teachers').upsert({
        "id": teacher_id,
        "inst_id": inst_id,
        "data": teacher_data
    }).execute()
    return teacher_data

def delete_teacher(inst_id, teacher_id):
    if not supabase: return False
    supabase.table('lms_teachers').delete().eq('id', teacher_id).eq('inst_id', inst_id).execute()
    return True

# === ESTUDIANTES / STUDENTS ===

def load_students(inst_id):
    if not supabase: return []
    res = supabase.table('lms_students').select('data').eq('inst_id', inst_id).execute()
    return [row['data'] for row in res.data] if res.data else []

def save_student(inst_id, student_data):
    if not supabase: return None
    student_id = student_data.get('id')
    if not student_id:
        student_id = "s_" + generate_id()
        student_data['id'] = student_id
    student_data['inst_id'] = inst_id
    if 'enrolled_courses' not in student_data:
        student_data['enrolled_courses'] = []
    
    program_id = student_data.get('program_id', get_default_program_id(inst_id))
    
    supabase.table('lms_students').upsert({
        "id": student_id,
        "inst_id": inst_id,
        "program_id": program_id,
        "student_email": student_data.get('email', ''),
        "data": student_data
    }).execute()
    return student_data

def delete_student(inst_id, student_id):
    if not supabase: return False
    supabase.table('lms_students').delete().eq('id', student_id).eq('inst_id', inst_id).execute()
    return True

def enroll_student_in_course(inst_id, student_id, course_id):
    if not supabase: return False
    res = supabase.table('lms_students').select('data').eq('id', student_id).eq('inst_id', inst_id).execute()
    if res.data:
        s = res.data[0]['data']
        if 'enrolled_courses' not in s: s['enrolled_courses'] = []
        if course_id not in s['enrolled_courses']:
            s['enrolled_courses'].append(course_id)
            save_student(inst_id, s)
        return True
    return False

def unenroll_student_from_course(inst_id, student_id, course_id):
    if not supabase: return False
    res = supabase.table('lms_students').select('data').eq('id', student_id).eq('inst_id', inst_id).execute()
    if res.data:
        s = res.data[0]['data']
        if 'enrolled_courses' in s and course_id in s['enrolled_courses']:
            s['enrolled_courses'].remove(course_id)
            save_student(inst_id, s)
        return True
    return False

# === CURSOS / COURSES ===

def load_courses(inst_id, program_id):
    if not supabase: return []
    if not program_id or program_id == 0:
        program_id = get_default_program_id(inst_id)
    res = supabase.table('lms_courses').select('data').eq('inst_id', inst_id).execute()
    courses = []
    if res.data:
        for row in res.data:
            c = row['data']
            if program_id == 0 or c.get('program_id') == program_id:
                courses.append(c)
    return courses

def load_course(course_id):
    if not supabase: return None
    res = supabase.table('lms_courses').select('data').eq('id', course_id).execute()
    if res.data:
        return res.data[0]['data']
    return None

def save_course(inst_id, program_id, course_data):
    if not supabase: return None
    if not program_id or program_id == 0:
        program_id = get_default_program_id(inst_id)
    course_id = course_data.get('id')
    if not course_id:
        course_id = "c_" + generate_id()
        course_data['id'] = course_id
        
    course_data['inst_id'] = inst_id
    course_data['program_id'] = program_id
    
    for key in ['outcomes', 'competencies', 'units', 'meetings', 'resources']:
        if key not in course_data: course_data[key] = []
        
    if 'units' in course_data:
        for u in course_data['units']:
            if 'topics' not in u: u['topics'] = []
            if 'resources' not in u: u['resources'] = []
            if 'activities' not in u: u['activities'] = []
            if 'evaluations' not in u: u['evaluations'] = []

    supabase.table('lms_courses').upsert({
        "id": course_id,
        "inst_id": inst_id,
        "program_id": program_id,
        "data": course_data
    }).execute()
    return course_data

def delete_course(inst_id, program_id, course_id):
    if not supabase: return False
    supabase.table('lms_courses').delete().eq('id', course_id).eq('inst_id', inst_id).execute()
    
    # Clean student enrollments
    students = load_students(inst_id)
    for s in students:
        if 'enrolled_courses' in s and course_id in s['enrolled_courses']:
            s['enrolled_courses'].remove(course_id)
            save_student(inst_id, s)
    return True

def load_public_courses():
    if not supabase: return []
    res = supabase.table('lms_courses').select('data').execute()
    return [row['data'] for row in res.data] if res.data else []

# === ENTREGAS / SUBMISSIONS ===

def load_submissions(inst_id, program_id):
    if not supabase: return []
    if not program_id or program_id == 0:
        program_id = get_default_program_id(inst_id)
    res = supabase.table('lms_submissions').select('data').eq('inst_id', inst_id).execute()
    subs = []
    if res.data:
        for row in res.data:
            s = row['data']
            if program_id == 0 or s.get('program_id') == program_id:
                subs.append(s)
    return subs

def save_submission(inst_id, program_id, submission_data):
    if not supabase: return None
    if not program_id or program_id == 0:
        program_id = get_default_program_id(inst_id)
    sub_id = submission_data.get('id')
    if not sub_id:
        sub_id = "sub_" + generate_id()
        submission_data['id'] = sub_id
    
    submission_data['inst_id'] = inst_id
    submission_data['program_id'] = program_id
    submission_data['status'] = submission_data.get('status', 'pending')
    submission_data['grade'] = submission_data.get('grade', None)
    submission_data['feedback'] = submission_data.get('feedback', None)
    
    supabase.table('lms_submissions').upsert({
        "id": sub_id,
        "inst_id": inst_id,
        "program_id": program_id,
        "course_id": submission_data.get('course_id', ''),
        "activity_id": submission_data.get('activity_id', ''),
        "student_email": submission_data.get('student_email', ''),
        "data": submission_data
    }).execute()
    return submission_data

def grade_submission(inst_id, program_id, submission_id, grade_data):
    if not supabase: return None
    res = supabase.table('lms_submissions').select('data').eq('id', submission_id).execute()
    if res.data:
        s = res.data[0]['data']
        s['grade'] = grade_data.get('grade')
        s['feedback'] = grade_data.get('feedback')
        s['status'] = 'graded'
        return save_submission(inst_id, program_id, s)
    return None

# === Funciones de Sync Eliminadas ===
def sync_courses_only(inst_id, program_id):
    pass

def pull_from_supabase(inst_id, program_id):
    pass
