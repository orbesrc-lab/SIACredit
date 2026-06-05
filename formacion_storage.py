import os
import json
import uuid
import sqlite3
from datetime import datetime

IS_VERCEL = os.environ.get("VERCEL") == "1"

# ---- Supabase (si disponible) ----
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
_supabase_client = None

def _get_supabase():
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    if not url or not key:
        return None
    try:
        from supabase import create_client
        _supabase_client = create_client(url, key)
        return _supabase_client
    except Exception:
        return None

# ---- SQLite local como fallback ----
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'lms_local.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def _get_local_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _init_local_db():
    conn = _get_local_conn()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS lms_courses (
            id TEXT PRIMARY KEY,
            inst_id INTEGER,
            program_id INTEGER,
            data TEXT
        );
        CREATE TABLE IF NOT EXISTS lms_teachers (
            id TEXT PRIMARY KEY,
            inst_id INTEGER,
            data TEXT
        );
        CREATE TABLE IF NOT EXISTS lms_students (
            id TEXT PRIMARY KEY,
            inst_id INTEGER,
            program_id INTEGER,
            student_email TEXT,
            data TEXT
        );
        CREATE TABLE IF NOT EXISTS lms_submissions (
            id TEXT PRIMARY KEY,
            inst_id INTEGER,
            program_id INTEGER,
            course_id TEXT,
            activity_id TEXT,
            student_email TEXT,
            data TEXT
        );
        CREATE TABLE IF NOT EXISTS lms_forums (
            id TEXT PRIMARY KEY,
            inst_id INTEGER,
            course_id TEXT,
            timestamp TEXT,
            data TEXT
        );
    """)
    conn.commit()
    conn.close()

_init_local_db()

def _supabase_available():
    """Check quickly if Supabase is reachable (only on Vercel or if explicitly configured)."""
    if IS_VERCEL:
        return _get_supabase() is not None
    # Locally default to SQLite unless Supabase explicitly works
    supabase = _get_supabase()
    return supabase is not None

def generate_id():
    return uuid.uuid4().hex[:9]

def get_default_program_id(inst_id):
    if inst_id == 1: return 47
    elif inst_id == 2: return 48
    elif inst_id == 3: return 50
    return 47

# ==================== TEACHERS ====================

def load_teachers(inst_id):
    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                res = supabase.table('lms_teachers').select('data').eq('inst_id', inst_id).execute()
                return [row['data'] for row in res.data] if res.data else []
            except Exception as e:
                print(f"Supabase error load_teachers: {e}")
    # Local SQLite
    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute("SELECT data FROM lms_teachers WHERE inst_id=?", (inst_id,))
    rows = cur.fetchall()
    conn.close()
    return [json.loads(r['data']) for r in rows]

def save_teacher(inst_id, teacher_data):
    teacher_id = teacher_data.get('id')
    if not teacher_id:
        teacher_id = "t_" + generate_id()
        teacher_data['id'] = teacher_id
    teacher_data['inst_id'] = inst_id

    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                supabase.table('lms_teachers').upsert({
                    "id": teacher_id, "inst_id": inst_id, "data": teacher_data
                }).execute()
                return teacher_data
            except Exception as e:
                print(f"Supabase error save_teacher: {e}")

    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO lms_teachers (id, inst_id, data) VALUES (?, ?, ?)",
        (teacher_id, inst_id, json.dumps(teacher_data))
    )
    conn.commit()
    conn.close()
    return teacher_data

def delete_teacher(inst_id, teacher_id):
    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                supabase.table('lms_teachers').delete().eq('id', teacher_id).eq('inst_id', inst_id).execute()
                return True
            except Exception as e:
                print(f"Supabase error delete_teacher: {e}")

    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM lms_teachers WHERE id=? AND inst_id=?", (teacher_id, inst_id))
    conn.commit()
    conn.close()
    return True

# ==================== STUDENTS ====================

def load_students(inst_id):
    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                res = supabase.table('lms_students').select('data').eq('inst_id', inst_id).execute()
                return [row['data'] for row in res.data] if res.data else []
            except Exception as e:
                print(f"Supabase error load_students: {e}")

    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute("SELECT data FROM lms_students WHERE inst_id=?", (inst_id,))
    rows = cur.fetchall()
    conn.close()
    return [json.loads(r['data']) for r in rows]

def save_student(inst_id, student_data):
    student_id = student_data.get('id')
    if not student_id:
        student_id = "s_" + generate_id()
        student_data['id'] = student_id
    student_data['inst_id'] = inst_id
    if 'enrolled_courses' not in student_data:
        student_data['enrolled_courses'] = []
    program_id = student_data.get('program_id', get_default_program_id(inst_id))

    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                supabase.table('lms_students').upsert({
                    "id": student_id, "inst_id": inst_id, "program_id": program_id,
                    "student_email": student_data.get('email', ''), "data": student_data
                }).execute()
                return student_data
            except Exception as e:
                print(f"Supabase error save_student: {e}")

    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO lms_students (id, inst_id, program_id, student_email, data) VALUES (?, ?, ?, ?, ?)",
        (student_id, inst_id, program_id, student_data.get('email', ''), json.dumps(student_data))
    )
    conn.commit()
    conn.close()
    return student_data

def delete_student(inst_id, student_id):
    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                supabase.table('lms_students').delete().eq('id', student_id).eq('inst_id', inst_id).execute()
                return True
            except Exception as e:
                print(f"Supabase error delete_student: {e}")

    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM lms_students WHERE id=? AND inst_id=?", (student_id, inst_id))
    conn.commit()
    conn.close()
    return True

def enroll_student_in_course(inst_id, student_id, course_id):
    students = load_students(inst_id)
    student = next((s for s in students if s['id'] == student_id), None)
    if student:
        if 'enrolled_courses' not in student: student['enrolled_courses'] = []
        if course_id not in student['enrolled_courses']:
            student['enrolled_courses'].append(course_id)
            save_student(inst_id, student)
        return True
    return False

def unenroll_student_from_course(inst_id, student_id, course_id):
    students = load_students(inst_id)
    student = next((s for s in students if s['id'] == student_id), None)
    if student:
        if 'enrolled_courses' in student and course_id in student['enrolled_courses']:
            student['enrolled_courses'].remove(course_id)
            save_student(inst_id, student)
        return True
    return False

# ==================== COURSES ====================

def load_courses(inst_id, program_id):
    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                res = supabase.table('lms_courses').select('data').eq('inst_id', inst_id).execute()
                courses = []
                if res.data:
                    for row in res.data:
                        c = row['data']
                        if not program_id or program_id == 0 or c.get('program_id') == program_id:
                            courses.append(c)
                return courses
            except Exception as e:
                print(f"Supabase error load_courses: {e}")

    if not program_id or program_id == 0:
        program_id = get_default_program_id(inst_id)
    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute("SELECT data FROM lms_courses WHERE inst_id=?", (inst_id,))
    rows = cur.fetchall()
    conn.close()
    courses = [json.loads(r['data']) for r in rows]
    return [c for c in courses if not program_id or c.get('program_id') == program_id]

def load_course(course_id):
    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                res = supabase.table('lms_courses').select('data').eq('id', course_id).execute()
                if res.data:
                    return res.data[0]['data']
            except Exception as e:
                print(f"Supabase error load_course: {e}")

    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute("SELECT data FROM lms_courses WHERE id=?", (course_id,))
    row = cur.fetchone()
    conn.close()
    return json.loads(row['data']) if row else None

def save_course(inst_id, program_id, course_data):
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

    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                supabase.table('lms_courses').upsert({
                    "id": course_id, "inst_id": inst_id,
                    "program_id": program_id, "data": course_data
                }).execute()
                return course_data
            except Exception as e:
                print(f"Supabase error save_course: {e}")

    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO lms_courses (id, inst_id, program_id, data) VALUES (?, ?, ?, ?)",
        (course_id, inst_id, program_id, json.dumps(course_data))
    )
    conn.commit()
    conn.close()
    return course_data

def delete_course(inst_id, program_id, course_id):
    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                supabase.table('lms_courses').delete().eq('id', course_id).eq('inst_id', inst_id).execute()
            except Exception as e:
                print(f"Supabase error delete_course: {e}")
    else:
        conn = _get_local_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM lms_courses WHERE id=? AND inst_id=?", (course_id, inst_id))
        conn.commit()
        conn.close()

    # Clean enrollments
    students = load_students(inst_id)
    for s in students:
        if 'enrolled_courses' in s and course_id in s['enrolled_courses']:
            s['enrolled_courses'].remove(course_id)
            save_student(inst_id, s)
    return True

def load_public_courses():
    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                res = supabase.table('lms_courses').select('data').execute()
                return [row['data'] for row in res.data] if res.data else []
            except Exception as e:
                print(f"Supabase error load_public_courses: {e}")

    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute("SELECT data FROM lms_courses")
    rows = cur.fetchall()
    conn.close()
    return [json.loads(r['data']) for r in rows]

# ==================== SUBMISSIONS ====================

def load_submissions(inst_id, program_id):
    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                res = supabase.table('lms_submissions').select('data').eq('inst_id', inst_id).execute()
                subs = []
                if res.data:
                    for row in res.data:
                        s = row['data']
                        if not program_id or program_id == 0 or s.get('program_id') == program_id:
                            subs.append(s)
                return subs
            except Exception as e:
                print(f"Supabase error load_submissions: {e}")

    if not program_id or program_id == 0:
        program_id = get_default_program_id(inst_id)
    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute("SELECT data FROM lms_submissions WHERE inst_id=?", (inst_id,))
    rows = cur.fetchall()
    conn.close()
    subs = [json.loads(r['data']) for r in rows]
    return [s for s in subs if not program_id or s.get('program_id') == program_id]

def save_submission(inst_id, program_id, submission_data):
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

    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                supabase.table('lms_submissions').upsert({
                    "id": sub_id, "inst_id": inst_id, "program_id": program_id,
                    "course_id": submission_data.get('course_id', ''),
                    "activity_id": submission_data.get('activity_id', ''),
                    "student_email": submission_data.get('student_email', ''),
                    "data": submission_data
                }).execute()
                return submission_data
            except Exception as e:
                print(f"Supabase error save_submission: {e}")

    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO lms_submissions (id, inst_id, program_id, course_id, activity_id, student_email, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (sub_id, inst_id, program_id,
         submission_data.get('course_id', ''),
         submission_data.get('activity_id', ''),
         submission_data.get('student_email', ''),
         json.dumps(submission_data))
    )
    conn.commit()
    conn.close()
    return submission_data

def grade_submission(inst_id, program_id, submission_id, grade_data):
    # Find submission
    subs = load_submissions(inst_id, program_id)
    s = next((x for x in subs if x['id'] == submission_id), None)
    if s:
        s['grade'] = grade_data.get('grade')
        s['feedback'] = grade_data.get('feedback')
        s['status'] = 'graded'
        return save_submission(inst_id, program_id, s)
    return None

# ==================== FORUMS ====================

def load_forum_messages(inst_id, course_id):
    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                res = supabase.table('lms_forums').select('data').eq('inst_id', inst_id).eq('course_id', course_id).order('timestamp', desc=False).execute()
                return [row['data'] for row in res.data] if res.data else []
            except Exception as e:
                print(f"Supabase error load_forum: {e}")

    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute("SELECT data FROM lms_forums WHERE inst_id=? AND course_id=? ORDER BY timestamp ASC",
                (inst_id, course_id))
    rows = cur.fetchall()
    conn.close()
    return [json.loads(r['data']) for r in rows]

def save_forum_message(inst_id, course_id, msg_data):
    msg_id = msg_data.get('id', 'msg_' + generate_id())
    msg_data['id'] = msg_id
    ts = msg_data.get('timestamp', datetime.now().isoformat())

    if IS_VERCEL:
        supabase = _get_supabase()
        if supabase:
            try:
                supabase.table('lms_forums').upsert({
                    "id": msg_id, "inst_id": inst_id, "course_id": course_id,
                    "timestamp": ts, "data": msg_data
                }).execute()
                return msg_data
            except Exception as e:
                print(f"Supabase error save_forum_message: {e}")

    conn = _get_local_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO lms_forums (id, inst_id, course_id, timestamp, data) VALUES (?, ?, ?, ?, ?)",
        (msg_id, inst_id, course_id, ts, json.dumps(msg_data))
    )
    conn.commit()
    conn.close()
    return msg_data

# ==================== Stubs (para compatibilidad) ====================
def sync_courses_only(inst_id=None, program_id=None, supabase=None):
    pass

def pull_from_supabase(inst_id=None, program_id=None, supabase=None):
    pass
