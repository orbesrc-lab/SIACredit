import sqlite3
conn = sqlite3.connect('siacredit.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

# Check if lms tables exist
for t in ['lms_courses', 'lms_students', 'lms_teachers', 'lms_submissions']:
    if t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"{t}: {cur.fetchone()[0]} rows")
conn.close()
