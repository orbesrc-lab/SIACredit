import json, os, psycopg2
from dotenv import load_dotenv

load_dotenv('c:\\SIAC\\.env')
conn=psycopg2.connect(os.getenv('DATABASE_URL'))
cur=conn.cursor()
cur.execute("SELECT data_json FROM statistics WHERE table_id = 'LMS_COURSES_1_0'")
row = cur.fetchone()
if row:
    courses = json.loads(row[0])
    for c in courses:
        print(f"Course: {c.get('title')}")
        units = c.get('units', {})
        if isinstance(units, dict):
            units = list(units.values())
        print(f"  Units: {len(units)}")
        for u in units:
            acts = u.get('activities', {})
            evs = u.get('evaluations', {})
            if isinstance(acts, dict): acts = list(acts.values())
            if isinstance(evs, dict): evs = list(evs.values())
            print(f"    - {u.get('name')}: {len(acts)} acts, {len(evs)} evals")
