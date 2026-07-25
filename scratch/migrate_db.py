import psycopg2
import os

DATABASE_URL = "postgresql://postgres.ftpkhueqooyqvwliifzb:Johnorbes2026%2A@aws-1-us-west-2.pooler.supabase.com:6543/postgres"

DDL = """
CREATE TABLE IF NOT EXISTS lms_courses (
    id TEXT PRIMARY KEY,
    inst_id INT,
    program_id INT,
    data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lms_teachers (
    id TEXT PRIMARY KEY,
    inst_id INT,
    data JSONB
);

CREATE TABLE IF NOT EXISTS lms_students (
    id TEXT PRIMARY KEY,
    inst_id INT,
    program_id INT,
    course_id TEXT,
    student_email TEXT,
    data JSONB
);

CREATE TABLE IF NOT EXISTS lms_submissions (
    id TEXT PRIMARY KEY,
    inst_id INT,
    program_id INT,
    course_id TEXT,
    activity_id TEXT,
    student_email TEXT,
    data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lms_forums (
    id TEXT PRIMARY KEY,
    inst_id INT,
    program_id INT,
    course_id TEXT,
    user_email TEXT,
    data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

def migrate():
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        print("Executing DDL...")
        cur.execute(DDL)
        print("Tables created successfully!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
