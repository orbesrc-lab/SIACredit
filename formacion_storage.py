import os
import json
import uuid

IS_VERCEL = os.environ.get("VERCEL") == "1"

if IS_VERCEL:
    COURSES_FILE = "/tmp/local_courses.json"
    TEACHERS_FILE = "/tmp/local_teachers.json"
    STUDENTS_FILE = "/tmp/local_students.json"
else:
    COURSES_FILE = os.path.join("instance", "local_courses.json")
    TEACHERS_FILE = os.path.join("instance", "local_teachers.json")
    STUDENTS_FILE = os.path.join("instance", "local_students.json")

def generate_id():
    return uuid.uuid4().hex[:9]

def ensure_files_exist():
    if IS_VERCEL:
        if not os.path.exists(COURSES_FILE):
            try:
                with open(COURSES_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            except Exception as e:
                print(f"Error creating COURSES_FILE in /tmp: {e}")
        if not os.path.exists(TEACHERS_FILE):
            try:
                with open(TEACHERS_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            except Exception as e:
                print(f"Error creating TEACHERS_FILE in /tmp: {e}")
        if not os.path.exists(STUDENTS_FILE):
            try:
                with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            except Exception as e:
                print(f"Error creating STUDENTS_FILE in /tmp: {e}")
    else:
        os.makedirs("instance", exist_ok=True)
        if not os.path.exists(COURSES_FILE):
            with open(COURSES_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        if not os.path.exists(TEACHERS_FILE):
            with open(TEACHERS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        if not os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)

# === DOCENTES / TEACHERS ===

def load_teachers(inst_id):
    ensure_files_exist()
    try:
        with open(TEACHERS_FILE, 'r', encoding='utf-8') as f:
            all_teachers = json.load(f)
        return [t for t in all_teachers if t.get('inst_id') == inst_id]
    except Exception as e:
        print(f"Error loading teachers: {e}")
        return []

def save_teacher(inst_id, teacher_data):
    ensure_files_exist()
    try:
        with open(TEACHERS_FILE, 'r', encoding='utf-8') as f:
            all_teachers = json.load(f)
        
        teacher_id = teacher_data.get('id')
        if not teacher_id:
            teacher_id = "t_" + generate_id()
            teacher_data['id'] = teacher_id
            teacher_data['inst_id'] = inst_id
            all_teachers.append(teacher_data)
        else:
            for idx, t in enumerate(all_teachers):
                if t.get('id') == teacher_id:
                    teacher_data['inst_id'] = inst_id
                    all_teachers[idx] = teacher_data
                    break
        
        with open(TEACHERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_teachers, f, indent=2, ensure_ascii=False)
        return teacher_data
    except Exception as e:
        print(f"Error saving teacher: {e}")
        return None

def delete_teacher(inst_id, teacher_id):
    ensure_files_exist()
    try:
        with open(TEACHERS_FILE, 'r', encoding='utf-8') as f:
            all_teachers = json.load(f)
        all_teachers = [t for t in all_teachers if not (t.get('id') == teacher_id and t.get('inst_id') == inst_id)]
        with open(TEACHERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_teachers, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error deleting teacher: {e}")
        return False


# === ESTUDIANTES / STUDENTS ===

def load_students(inst_id):
    ensure_files_exist()
    try:
        with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
            all_students = json.load(f)
        return [s for s in all_students if s.get('inst_id') == inst_id]
    except Exception as e:
        print(f"Error loading students: {e}")
        return []

def save_student(inst_id, student_data):
    ensure_files_exist()
    try:
        with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
            all_students = json.load(f)
        
        student_id = student_data.get('id')
        if not student_id:
            student_id = "s_" + generate_id()
            student_data['id'] = student_id
            student_data['inst_id'] = inst_id
            if 'enrolled_courses' not in student_data:
                student_data['enrolled_courses'] = []
            all_students.append(student_data)
        else:
            for idx, s in enumerate(all_students):
                if s.get('id') == student_id:
                    student_data['inst_id'] = inst_id
                    if 'enrolled_courses' not in student_data:
                        student_data['enrolled_courses'] = s.get('enrolled_courses', [])
                    all_students[idx] = student_data
                    break
        
        with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_students, f, indent=2, ensure_ascii=False)
        return student_data
    except Exception as e:
        print(f"Error saving student: {e}")
        return None

def delete_student(inst_id, student_id):
    ensure_files_exist()
    try:
        with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
            all_students = json.load(f)
        all_students = [s for s in all_students if not (s.get('id') == student_id and s.get('inst_id') == inst_id)]
        with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_students, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error deleting student: {e}")
        return False

def enroll_student_in_course(inst_id, student_id, course_id):
    ensure_files_exist()
    try:
        with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
            all_students = json.load(f)
        
        for s in all_students:
            if s.get('id') == student_id and s.get('inst_id') == inst_id:
                if 'enrolled_courses' not in s:
                    s['enrolled_courses'] = []
                if course_id not in s['enrolled_courses']:
                    s['enrolled_courses'].append(course_id)
                break
                
        with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_students, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error enrolling student: {e}")
        return False

def unenroll_student_from_course(inst_id, student_id, course_id):
    ensure_files_exist()
    try:
        with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
            all_students = json.load(f)
        
        for s in all_students:
            if s.get('id') == student_id and s.get('inst_id') == inst_id:
                if 'enrolled_courses' in s and course_id in s['enrolled_courses']:
                    s['enrolled_courses'].remove(course_id)
                break
                
        with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_students, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error unenrolling student: {e}")
        return False


# === CURSOS / COURSES ===

def load_courses(inst_id, program_id):
    ensure_files_exist()
    try:
        with open(COURSES_FILE, 'r', encoding='utf-8') as f:
            all_courses = json.load(f)
        return [c for c in all_courses if c.get('inst_id') == inst_id and c.get('program_id') == program_id]
    except Exception as e:
        print(f"Error loading courses: {e}")
        return []

def load_course(course_id):
    ensure_files_exist()
    try:
        with open(COURSES_FILE, 'r', encoding='utf-8') as f:
            all_courses = json.load(f)
        for c in all_courses:
            if c.get('id') == course_id:
                return c
    except Exception as e:
        print(f"Error loading single course: {e}")
    return None

def save_course(inst_id, program_id, course_data):
    ensure_files_exist()
    try:
        with open(COURSES_FILE, 'r', encoding='utf-8') as f:
            all_courses = json.load(f)
        
        course_id = course_data.get('id')
        
        # Ensure units structures are initialized
        if 'units' in course_data:
            for u in course_data['units']:
                if 'topics' not in u: u['topics'] = []
                if 'resources' not in u: u['resources'] = []
                if 'activities' not in u: u['activities'] = []
                if 'evaluations' not in u: u['evaluations'] = []
        
        if not course_id:
            # New course
            course_id = "c_" + generate_id()
            course_data['id'] = course_id
            course_data['inst_id'] = inst_id
            course_data['program_id'] = program_id
            
            if 'outcomes' not in course_data: course_data['outcomes'] = []
            if 'competencies' not in course_data: course_data['competencies'] = []
            if 'units' not in course_data: course_data['units'] = []
            if 'meetings' not in course_data: course_data['meetings'] = []
            if 'resources' not in course_data: course_data['resources'] = [] # Deprecated but kept for safety
            
            all_courses.append(course_data)
        else:
            # Update existing
            for idx, c in enumerate(all_courses):
                if c.get('id') == course_id:
                    course_data['inst_id'] = inst_id
                    course_data['program_id'] = program_id
                    
                    for key in ['outcomes', 'competencies', 'units', 'meetings', 'resources']:
                        if key not in course_data:
                            course_data[key] = c.get(key, [])
                            
                    all_courses[idx] = course_data
                    break
        
        with open(COURSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_courses, f, indent=2, ensure_ascii=False)
        return course_data
    except Exception as e:
        print(f"Error saving course: {e}")
        return None

def delete_course(inst_id, program_id, course_id):
    ensure_files_exist()
    try:
        with open(COURSES_FILE, 'r', encoding='utf-8') as f:
            all_courses = json.load(f)
        
        all_courses = [c for c in all_courses if not (c.get('id') == course_id and c.get('inst_id') == inst_id and c.get('program_id') == program_id)]
        
        with open(COURSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_courses, f, indent=2, ensure_ascii=False)
        
        # Clean up student enrollments for this course
        try:
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                all_students = json.load(f)
            for s in all_students:
                if 'enrolled_courses' in s and course_id in s['enrolled_courses']:
                    s['enrolled_courses'].remove(course_id)
            with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_students, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error cleaning up student enrollments: {e}")
            
        return True
    except Exception as e:
        print(f"Error deleting course: {e}")
        return False

def load_public_courses():
    ensure_files_exist()
    try:
        with open(COURSES_FILE, 'r', encoding='utf-8') as f:
            all_courses = json.load(f)
        return all_courses
    except Exception as e:
        print(f"Error loading public courses: {e}")
        return []

# === SINCRONIZACION CON SUPABASE ===

def sync_courses_only(inst_id, program_id, supabase_client):
    try:
        courses = load_courses(inst_id, program_id)
        table_key = f"LMS_COURSES_{inst_id}_{program_id}"
        check = supabase_client.table('statistics').select("id").eq("table_id", table_key).eq("inst_id", inst_id).eq("program_id", program_id).execute()
        if check.data:
            supabase_client.table('statistics').update({"data_json": json.dumps(courses, ensure_ascii=False)}).eq("id", check.data[0]['id']).execute()
        else:
            supabase_client.table('statistics').insert({
                "table_id": table_key,
                "data_json": json.dumps(courses, ensure_ascii=False),
                "inst_id": inst_id,
                "program_id": program_id
            }).execute()
        return True
    except Exception as e:
        print(f"Error syncing courses: {e}")
        return False

def sync_teachers_only(inst_id, supabase_client):
    try:
        teachers = load_teachers(inst_id)
        table_key = f"LMS_TEACHERS_{inst_id}"
        check = supabase_client.table('statistics').select("id").eq("table_id", table_key).eq("inst_id", inst_id).execute()
        if check.data:
            supabase_client.table('statistics').update({"data_json": json.dumps(teachers, ensure_ascii=False)}).eq("id", check.data[0]['id']).execute()
        else:
            supabase_client.table('statistics').insert({
                "table_id": table_key,
                "data_json": json.dumps(teachers, ensure_ascii=False),
                "inst_id": inst_id,
                "program_id": 0
            }).execute()
        return True
    except Exception as e:
        print(f"Error syncing teachers: {e}")
        return False

def sync_students_only(inst_id, supabase_client):
    try:
        students = load_students(inst_id)
        table_key = f"LMS_STUDENTS_{inst_id}"
        check = supabase_client.table('statistics').select("id").eq("table_id", table_key).eq("inst_id", inst_id).execute()
        if check.data:
            supabase_client.table('statistics').update({"data_json": json.dumps(students, ensure_ascii=False)}).eq("id", check.data[0]['id']).execute()
        else:
            supabase_client.table('statistics').insert({
                "table_id": table_key,
                "data_json": json.dumps(students, ensure_ascii=False),
                "inst_id": inst_id,
                "program_id": 0
            }).execute()
        return True
    except Exception as e:
        print(f"Error syncing students: {e}")
        return False

def pull_from_supabase(inst_id, program_id, supabase_client):
    ensure_files_exist()
    try:
        # Pull Courses
        table_key_c = f"LMS_COURSES_{inst_id}_{program_id}"
        res_c = supabase_client.table('statistics').select("data_json").eq("table_id", table_key_c).eq("inst_id", inst_id).eq("program_id", program_id).execute()
        if res_c.data:
            courses = json.loads(res_c.data[0]['data_json'])
            with open(COURSES_FILE, 'r', encoding='utf-8') as f:
                all_courses = json.load(f)
            all_courses = [c for c in all_courses if not (c.get('inst_id') == inst_id and c.get('program_id') == program_id)]
            all_courses.extend(courses)
            with open(COURSES_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_courses, f, indent=2, ensure_ascii=False)

        # Pull Teachers
        table_key_t = f"LMS_TEACHERS_{inst_id}"
        res_t = supabase_client.table('statistics').select("data_json").eq("table_id", table_key_t).eq("inst_id", inst_id).execute()
        if res_t.data:
            teachers = json.loads(res_t.data[0]['data_json'])
            with open(TEACHERS_FILE, 'r', encoding='utf-8') as f:
                all_teachers = json.load(f)
            all_teachers = [t for t in all_teachers if t.get('inst_id') != inst_id]
            all_teachers.extend(teachers)
            with open(TEACHERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_teachers, f, indent=2, ensure_ascii=False)

        # Pull Students
        table_key_s = f"LMS_STUDENTS_{inst_id}"
        res_s = supabase_client.table('statistics').select("data_json").eq("table_id", table_key_s).eq("inst_id", inst_id).execute()
        if res_s.data:
            students = json.loads(res_s.data[0]['data_json'])
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                all_students = json.load(f)
            all_students = [s for s in all_students if s.get('inst_id') != inst_id]
            all_students.extend(students)
            with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_students, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error pulling LMS data: {e}")
        return False
