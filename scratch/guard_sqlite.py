"""
Guard all SQLite local DB calls so they check _LOCAL_DB_OK first.
This prevents any crashes on Vercel where the filesystem is read-only.
"""
with open('c:/SIAC/formacion_storage.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Patch functions that LOAD data - they return empty list if DB not available
load_pattern = '    conn = _get_local_conn()\n    cur = conn.cursor()\n    cur.execute("SELECT data FROM'
load_new = '    if not _LOCAL_DB_OK:\n        return []\n    conn = _get_local_conn()\n    cur = conn.cursor()\n    cur.execute("SELECT data FROM'
content = content.replace(load_pattern, load_new)

# Patch load_course which returns None
load_one_pattern = '    conn = _get_local_conn()\n    cur = conn.cursor()\n    cur.execute("SELECT data FROM lms_courses WHERE id=?"'
load_one_new = '    if not _LOCAL_DB_OK:\n        return None\n    conn = _get_local_conn()\n    cur = conn.cursor()\n    cur.execute("SELECT data FROM lms_courses WHERE id=?"'
content = content.replace(load_one_pattern, load_one_new)

# Patch INSERT OR REPLACE calls - they save data, skip silently if no DB
save_pattern = '    conn = _get_local_conn()\n    cur = conn.cursor()\n    cur.execute(\n        "INSERT OR REPLACE INTO'
save_new = '    if not _LOCAL_DB_OK:\n        return teacher_data if \'teacher_data\' in dir() else None\n    conn = _get_local_conn()\n    cur = conn.cursor()\n    cur.execute(\n        "INSERT OR REPLACE INTO'
# Better: just wrap with check at function level in each save

# Actually, let's do a targeted replacement per function
# For save functions: if not _LOCAL_DB_OK: return <data>  before conn = ...
import re

# Replace all patterns: "    conn = _get_local_conn()\n    cur = conn.cursor()\n    cur.execute(\n        \"INSERT"
def fix_save_block(content, table_hint, return_val):
    old = f'    conn = _get_local_conn()\n    cur = conn.cursor()\n    cur.execute(\n        "INSERT OR REPLACE INTO {table_hint}'
    new = f'    if not _LOCAL_DB_OK:\n        return {return_val}\n    conn = _get_local_conn()\n    cur = conn.cursor()\n    cur.execute(\n        "INSERT OR REPLACE INTO {table_hint}'
    return content.replace(old, new)

content = fix_save_block(content, 'lms_teachers', 'teacher_data')
content = fix_save_block(content, 'lms_students', 'student_data')
content = fix_save_block(content, 'lms_courses', 'course_data')
content = fix_save_block(content, 'lms_submissions', 'submission_data')
content = fix_save_block(content, 'lms_forums', 'msg_data')

# Fix DELETE calls
old_del = '    conn = _get_local_conn()\n    cur = conn.cursor()\n    cur.execute("DELETE FROM'
new_del = '    if not _LOCAL_DB_OK:\n        return True\n    conn = _get_local_conn()\n    cur = conn.cursor()\n    cur.execute("DELETE FROM'
content = content.replace(old_del, new_del)

with open('c:/SIAC/formacion_storage.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify no unguarded _get_local_conn left (other than the definition)
remaining = [(i+1, l.strip()) for i, l in enumerate(content.splitlines()) 
             if '_get_local_conn()' in l and 'def _get_local_conn' not in l and 'if not _LOCAL_DB_OK' not in l]
print(f"Remaining unguarded _get_local_conn calls: {remaining}")
print("Done!")
