import json
import sqlite3
import os
import sys

sys.path.append('.')
import formacion_storage

# Cargar todos los cursos disponibles en el proyecto
courses_to_restore = []

# 1. De local_courses.json
if os.path.exists('instance/local_courses.json'):
    try:
        with open('instance/local_courses.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                courses_to_restore.extend(data)
            elif isinstance(data, dict):
                courses_to_restore.append(data)
    except Exception as e:
        print("Error reading local_courses.json:", e)

# 2. De scratch/course_data.json
if os.path.exists('scratch/course_data.json'):
    try:
        with open('scratch/course_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and data.get('title'):
                # Evitar duplicados por id o title
                if not any(c.get('id') == data.get('id') or c.get('title') == data.get('title') for c in courses_to_restore):
                    courses_to_restore.append(data)
    except Exception as e:
        print("Error reading course_data.json:", e)

# 3. De instance/lms_local.db
if os.path.exists('instance/lms_local.db'):
    try:
        conn = sqlite3.connect('instance/lms_local.db')
        c = conn.cursor()
        c.execute("SELECT data FROM lms_courses")
        for row in c.fetchall():
            if row[0]:
                try:
                    cdata = json.loads(row[0])
                    if isinstance(cdata, dict) and cdata.get('title'):
                        if not any(c.get('id') == cdata.get('id') or c.get('title') == cdata.get('title') for c in courses_to_restore):
                            courses_to_restore.append(cdata)
                except Exception:
                    pass
        conn.close()
    except Exception as e:
        print("Error reading lms_local.db:", e)

print(f"Total cursos recolectados para restaurar: {len(courses_to_restore)}")
for c in courses_to_restore:
    print(f" -> {c.get('id')}: {c.get('title')}")

# Guardar en local_courses.json
with open('instance/local_courses.json', 'w', encoding='utf-8') as f:
    json.dump(courses_to_restore, f, ensure_ascii=False, indent=2)
print("Guardado en instance/local_courses.json!")

# Guardar en lms_local.db para inst_id 1 y 2
conn = sqlite3.connect('instance/lms_local.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS lms_courses (id TEXT PRIMARY KEY, inst_id INTEGER, program_id INTEGER, data TEXT)")

for inst_id in [1, 2, 3]:
    for crs in courses_to_restore:
        cid = crs.get('id') or 'c_' + crs.get('title', '')[:8]
        crs_copy = dict(crs)
        crs_copy['inst_id'] = inst_id
        crs_copy['program_id'] = 0
        c.execute("INSERT OR REPLACE INTO lms_courses (id, inst_id, program_id, data) VALUES (?,?,?,?)",
                  (f"{cid}_{inst_id}", inst_id, 0, json.dumps(crs_copy, ensure_ascii=False)))
        # Y con el id original
        c.execute("INSERT OR REPLACE INTO lms_courses (id, inst_id, program_id, data) VALUES (?,?,?,?)",
                  (cid, inst_id, 0, json.dumps(crs_copy, ensure_ascii=False)))

conn.commit()
conn.close()
print("Guardado en instance/lms_local.db para instituciones 1, 2, 3!")
