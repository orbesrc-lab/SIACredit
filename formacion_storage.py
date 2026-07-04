import os
import json
import uuid
from datetime import datetime

IS_VERCEL = os.environ.get("VERCEL") == "1"

# ---- Supabase ----
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

# ---- SQLite local (SOLO cuando no es Vercel) ----
_LOCAL_DB_OK = False

if not IS_VERCEL:
    try:
        import sqlite3 as _sqlite3
        _DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'lms_local.db')
        os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)

        def _local_conn():
            c = _sqlite3.connect(_DB_PATH)
            c.row_factory = _sqlite3.Row
            return c

        _c = _local_conn()
        _c.executescript("""
            CREATE TABLE IF NOT EXISTS lms_courses (id TEXT PRIMARY KEY, inst_id INTEGER, program_id INTEGER, data TEXT);
            CREATE TABLE IF NOT EXISTS lms_teachers (id TEXT PRIMARY KEY, inst_id INTEGER, data TEXT);
            CREATE TABLE IF NOT EXISTS lms_students (id TEXT PRIMARY KEY, inst_id INTEGER, program_id INTEGER, student_email TEXT, data TEXT);
            CREATE TABLE IF NOT EXISTS lms_submissions (id TEXT PRIMARY KEY, inst_id INTEGER, program_id INTEGER, course_id TEXT, activity_id TEXT, student_email TEXT, data TEXT);
            CREATE TABLE IF NOT EXISTS lms_forums (id TEXT PRIMARY KEY, inst_id INTEGER, course_id TEXT, timestamp TEXT, data TEXT);
        """)
        _c.commit()
        _c.close()
        _LOCAL_DB_OK = True
    except Exception as _e:
        print(f"[formacion_storage] SQLite no disponible localmente: {_e}")

def generate_id():
    return uuid.uuid4().hex[:9]

def get_default_program_id(inst_id):
    if inst_id == 1: return 47
    elif inst_id == 2: return 48
    elif inst_id == 3: return 50
    return 47

# ==================== HELPERS ====================

def _sb_load(table, filters=None):
    """Load rows directly from real table. Returns list of data dicts."""
    sb = _get_supabase()
    if not sb: return None
    try:
        q = sb.table(table).select('data')
        if filters:
            for k, v in filters.items():
                if k in ['inst_id', 'program_id', 'course_id', 'id']:
                    q = q.eq(k, v)
        res = q.execute()
        if res.data:
            return [row['data'] for row in res.data]
        return []
    except Exception as e:
        print(f"[supabase] Error loading {table}: {e}")
        return None

def _sb_upsert(table, row):
    """Upsert a row directly to real table. Returns True on success."""
    sb = _get_supabase()
    if not sb: return False
    try:
        db_row = {"id": row.get('id'), "inst_id": row.get('inst_id', 1), "data": row.get('data', row)}
        if 'program_id' in row: db_row['program_id'] = row['program_id']
        if 'course_id' in row: db_row['course_id'] = row['course_id']
        if 'student_email' in row: db_row['student_email'] = row['student_email']
        if 'activity_id' in row: db_row['activity_id'] = row['activity_id']
        if table == 'lms_forums' and 'timestamp' in row: db_row['timestamp'] = row['timestamp']

        sb.table(table).upsert(db_row).execute()
        return True
    except Exception as e:
        print(f"[supabase] Error upserting {table}: {e}")
        return False

def _sb_delete(table, filters):
    """Delete directly from real table. Returns True on success."""
    sb = _get_supabase()
    if not sb: return False
    try:
        q = sb.table(table).delete()
        if filters:
            for k, v in filters.items():
                q = q.eq(k, v)
        q.execute()
        return True
    except Exception as e:
        print(f"[supabase] Error deleting {table}: {e}")
        return False
    try:
        inst_id = row.get('inst_id', 1)
        table_key = f"{table.upper()}_{inst_id}"
        
        res = sb.table('statistics').select('id, data_json').eq('table_id', table_key).execute()
        if res.data:
            row_id = res.data[0]['id']
            all_records = json.loads(res.data[0]['data_json'])
            
            found = False
            for i, r in enumerate(all_records):
                if r.get('id') == row.get('id'):
                    all_records[i] = row
                    found = True
                    break
            if not found:
                all_records.append(row)
                
            sb.table('statistics').update({"data_json": json.dumps(all_records)}).eq("id", row_id).execute()
        else:
            sb.table('statistics').insert({
                "table_id": table_key,
                "data_json": json.dumps([row])
            }).execute()
        return True
    except Exception as e:
        print(f"[supabase] Error upserting {table} via statistics: {e}")
        return False

def _sb_delete(table, filters):
    """Delete from Supabase mapping to 'statistics'. Returns True on success."""
    sb = _get_supabase()
    if not sb: return False
    try:
        if filters and 'inst_id' in filters:
            inst_id = filters.get('inst_id')
            table_key = f"{table.upper()}_{inst_id}"
            res = sb.table('statistics').select('id, data_json').eq('table_id', table_key).execute()
        else:
            res = sb.table('statistics').select('id, data_json').like('table_id', f"{table.upper()}_%").execute()
            
        if res.data:
            for row in res.data:
                row_id = row['id']
                all_records = json.loads(row['data_json'])
                
                new_records = []
                changed = False
                for rec in all_records:
                    match = True
                    for k, v in filters.items():
                        if k == 'inst_id' and ('inst_id' in filters): continue
                        if rec.get(k) != v:
                            match = False
                            break
                    if not match:
                        new_records.append(rec)
                    else:
                        changed = True
                        
                if changed:
                    sb.table('statistics').update({"data_json": json.dumps(new_records)}).eq("id", row_id).execute()
        return True
    except Exception as e:
        print(f"[supabase] Error deleting {table} via statistics: {e}")
        return False

def _local_query(sql, params=()):
    """Run a SELECT on local SQLite, returns list of dicts."""
    if not _LOCAL_DB_OK:
        return []
    try:
        conn = _local_conn()
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()
        return [json.loads(r['data']) for r in rows]
    except Exception as e:
        print(f"[sqlite] Query error: {e}")
        return []

def _local_query_one(sql, params=()):
    """Run a SELECT on local SQLite, returns single dict or None."""
    if not _LOCAL_DB_OK:
        return None
    try:
        conn = _local_conn()
        cur = conn.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        conn.close()
        return json.loads(row['data']) if row else None
    except Exception as e:
        print(f"[sqlite] Query one error: {e}")
        return None

def _local_exec(sql, params=()):
    """Run an INSERT/UPDATE/DELETE on local SQLite."""
    if not _LOCAL_DB_OK:
        return
    try:
        conn = _local_conn()
        conn.execute(sql, params)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[sqlite] Exec error: {e}")

# ==================== TEACHERS ====================

def load_teachers(inst_id):
    result = _sb_load('lms_teachers', {'inst_id': inst_id})
    if result is not None:
        return result
    return _local_query("SELECT data FROM lms_teachers WHERE inst_id=?", (inst_id,))

def save_teacher(inst_id, teacher_data):
    if not teacher_data.get('id'):
        teacher_data['id'] = "t_" + generate_id()
    teacher_data['inst_id'] = inst_id
    tid = teacher_data['id']

    if _sb_upsert('lms_teachers', {"id": tid, "inst_id": inst_id, "data": teacher_data}):
        return teacher_data

    _local_exec(
        "INSERT OR REPLACE INTO lms_teachers (id, inst_id, data) VALUES (?,?,?)",
        (tid, inst_id, json.dumps(teacher_data))
    )
    return teacher_data

def delete_teacher(inst_id, teacher_id):
    if _sb_delete('lms_teachers', {'id': teacher_id, 'inst_id': inst_id}):
        return True
    _local_exec("DELETE FROM lms_teachers WHERE id=? AND inst_id=?", (teacher_id, inst_id))
    return True

# ==================== STUDENTS ====================

def load_students(inst_id):
    result = _sb_load('lms_students', {'inst_id': inst_id})
    if result is not None:
        return result
    return _local_query("SELECT data FROM lms_students WHERE inst_id=?", (inst_id,))

def save_student(inst_id, student_data):
    if not student_data.get('id'):
        student_data['id'] = "s_" + generate_id()
    student_data['inst_id'] = inst_id
    if 'enrolled_courses' not in student_data:
        student_data['enrolled_courses'] = []
    sid = student_data['id']
    program_id = student_data.get('program_id', get_default_program_id(inst_id))

    if _sb_upsert('lms_students', {
        "id": sid, "inst_id": inst_id, "program_id": program_id,
        "student_email": student_data.get('email', ''), "data": student_data
    }):
        return student_data

    _local_exec(
        "INSERT OR REPLACE INTO lms_students (id, inst_id, program_id, student_email, data) VALUES (?,?,?,?,?)",
        (sid, inst_id, program_id, student_data.get('email', ''), json.dumps(student_data))
    )
    return student_data

def delete_student(inst_id, student_id):
    if _sb_delete('lms_students', {'id': student_id, 'inst_id': inst_id}):
        return True
    _local_exec("DELETE FROM lms_students WHERE id=? AND inst_id=?", (student_id, inst_id))
    return True

def enroll_student_in_course(inst_id, student_id, course_id):
    students = load_students(inst_id)
    student = next((s for s in students if s['id'] == student_id), None)
    if student:
        if 'enrolled_courses' not in student:
            student['enrolled_courses'] = []
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

def load_courses(inst_id, program_id=0):
    result = _sb_load('lms_courses', {'inst_id': inst_id})
    if result is not None:
        if program_id and program_id != 0:
            return [c for c in result if c.get('program_id') == program_id]
        return result

    if not program_id or program_id == 0:
        program_id = get_default_program_id(inst_id)
    all_c = _local_query("SELECT data FROM lms_courses WHERE inst_id=?", (inst_id,))
    return [c for c in all_c if c.get('program_id') == program_id]

def load_course(course_id):
    result = _sb_load('lms_courses', {'id': course_id})
    if result is not None:
        return result[0] if result else None
    return _local_query_one("SELECT data FROM lms_courses WHERE id=?", (course_id,))

def save_course(inst_id, program_id, course_data):
    if not program_id or program_id == 0:
        program_id = get_default_program_id(inst_id)
    if not course_data.get('id'):
        course_data['id'] = "c_" + generate_id()
    course_data['inst_id'] = inst_id
    course_data['program_id'] = program_id
    for key in ['outcomes', 'competencies', 'units', 'meetings', 'resources']:
        if key not in course_data:
            course_data[key] = []
    if 'units' in course_data:
        for u in course_data['units']:
            for k in ['topics', 'resources', 'activities', 'evaluations']:
                if k not in u:
                    u[k] = []
    cid = course_data['id']

    if _sb_upsert('lms_courses', {
        "id": cid, "inst_id": inst_id, "program_id": program_id, "data": course_data
    }):
        return course_data

    _local_exec(
        "INSERT OR REPLACE INTO lms_courses (id, inst_id, program_id, data) VALUES (?,?,?,?)",
        (cid, inst_id, program_id, json.dumps(course_data))
    )
    return course_data

def delete_course(inst_id, program_id, course_id):
    _sb_delete('lms_courses', {'id': course_id, 'inst_id': inst_id})
    _local_exec("DELETE FROM lms_courses WHERE id=? AND inst_id=?", (course_id, inst_id))
    # Clean enrollments
    students = load_students(inst_id)
    for s in students:
        if 'enrolled_courses' in s and course_id in s['enrolled_courses']:
            s['enrolled_courses'].remove(course_id)
            save_student(inst_id, s)
    return True

def load_public_courses():
    sb = _get_supabase()
    if sb:
        try:
            res = sb.table('lms_courses').select('data').execute()
            return [r['data'] for r in res.data] if res.data else []
        except Exception as e:
            print(f"[supabase] Error load_public_courses: {e}")
    return _local_query("SELECT data FROM lms_courses", ())

# ==================== SUBMISSIONS ====================

def load_submissions(inst_id, program_id=0):
    result = _sb_load('lms_submissions', {'inst_id': inst_id})
    if result is not None:
        if program_id and program_id != 0:
            return [s for s in result if s.get('program_id') == program_id]
        return result

    if not program_id or program_id == 0:
        program_id = get_default_program_id(inst_id)
    all_s = _local_query("SELECT data FROM lms_submissions WHERE inst_id=?", (inst_id,))
    return [s for s in all_s if s.get('program_id') == program_id]

def save_submission(inst_id, program_id, submission_data):
    if not program_id or program_id == 0:
        program_id = get_default_program_id(inst_id)
    if not submission_data.get('id'):
        submission_data['id'] = "sub_" + generate_id()
    submission_data['inst_id'] = inst_id
    submission_data['program_id'] = program_id
    submission_data.setdefault('status', 'pending')
    submission_data.setdefault('grade', None)
    submission_data.setdefault('feedback', None)
    sid = submission_data['id']

    if _sb_upsert('lms_submissions', {
        "id": sid, "inst_id": inst_id, "program_id": program_id,
        "course_id": submission_data.get('course_id', ''),
        "activity_id": submission_data.get('activity_id', ''),
        "student_email": submission_data.get('student_email', ''),
        "data": submission_data
    }):
        return submission_data

    _local_exec(
        "INSERT OR REPLACE INTO lms_submissions (id, inst_id, program_id, course_id, activity_id, student_email, data) VALUES (?,?,?,?,?,?,?)",
        (sid, inst_id, program_id,
         submission_data.get('course_id', ''),
         submission_data.get('activity_id', ''),
         submission_data.get('student_email', ''),
         json.dumps(submission_data))
    )
    return submission_data

def grade_submission(inst_id, program_id, submission_id, grade_data):
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
    sb = _get_supabase()
    if sb:
        try:
            res = sb.table('lms_forums').select('data').eq('inst_id', inst_id).eq('course_id', course_id).order('timestamp', desc=False).execute()
            return [r['data'] for r in res.data] if res.data else []
        except Exception as e:
            print(f"[supabase] Error load_forum: {e}")

    if not _LOCAL_DB_OK:
        return []
    try:
        conn = _local_conn()
        cur = conn.cursor()
        cur.execute("SELECT data FROM lms_forums WHERE inst_id=? AND course_id=? ORDER BY timestamp ASC", (inst_id, course_id))
        rows = cur.fetchall()
        conn.close()
        return [json.loads(r['data']) for r in rows]
    except Exception as e:
        print(f"[sqlite] Error load_forum: {e}")
        return []

def save_forum_message(inst_id, course_id, msg_data):
    if not msg_data.get('id'):
        msg_data['id'] = 'msg_' + generate_id()
    ts = msg_data.get('timestamp', datetime.now().isoformat())

    if _sb_upsert('lms_forums', {
        "id": msg_data['id'], "inst_id": inst_id, "course_id": course_id,
        "timestamp": ts, "data": msg_data
    }):
        return msg_data

    _local_exec(
        "INSERT OR REPLACE INTO lms_forums (id, inst_id, course_id, timestamp, data) VALUES (?,?,?,?,?)",
        (msg_data['id'], inst_id, course_id, ts, json.dumps(msg_data))
    )
    return msg_data

# ==================== Stubs ====================
def sync_courses_only(*args, **kwargs): pass
def pull_from_supabase(*args, **kwargs): pass
