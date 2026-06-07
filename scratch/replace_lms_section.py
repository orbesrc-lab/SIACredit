"""
Remove all leftover use_cloud references from app.py LMS section.
Replace the entire LMS section (teachers, students, submissions) with clean version.
"""
with open('c:/SIAC/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the marker
marker_start = "# === API ENDPOINTS FOR LMS (FORMACION) ==="
marker_end = "\nif __name__ == '__main__':"

start_idx = content.find(marker_start)
end_idx = content.find(marker_end)

if start_idx == -1 or end_idx == -1:
    print(f"Markers not found! start={start_idx}, end={end_idx}")
    exit(1)

# The new clean LMS section
new_lms_section = '''# === API ENDPOINTS FOR LMS (FORMACION) ===

@app.route('/api/teachers', methods=['GET', 'POST'])
def handle_api_teachers():
    inst_id = request.args.get('inst_id', 1, type=int)
    if request.method == 'POST':
        data = request.json
        saved = formacion_storage.save_teacher(inst_id, data)
        if saved:
            return jsonify({"status": "success", "data": saved})
        return jsonify({"status": "error", "message": "No se pudo guardar el docente."}), 500
    try:
        teachers = formacion_storage.load_teachers(inst_id)
        return jsonify(teachers)
    except Exception as e:
        print(f"Error loading teachers: {e}")
        return jsonify([]), 200

@app.route('/api/teachers/<teacher_id>', methods=['DELETE'])
def delete_api_teacher(teacher_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    success = formacion_storage.delete_teacher(inst_id, teacher_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No se pudo eliminar el docente."}), 500

@app.route('/api/courses', methods=['GET', 'POST'])
def handle_api_courses():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    if request.method == 'POST':
        data = request.json
        saved = formacion_storage.save_course(inst_id, program_id, data)
        if saved:
            return jsonify({"status": "success", "data": saved})
        return jsonify({"status": "error", "message": "No se pudo guardar el curso."}), 500
    try:
        courses = formacion_storage.load_courses(inst_id, program_id)
        return jsonify(courses)
    except Exception as e:
        print(f"Error loading courses: {e}")
        return jsonify([]), 200

@app.route('/api/courses/<course_id>/forum', methods=['GET', 'POST'])
def handle_course_forum(course_id):
    inst_id = int(request.args.get('inst_id', 1))
    program_id = int(request.args.get('program_id', 0))
    if program_id == 0:
        program_id = formacion_storage.get_default_program_id(inst_id)
    if request.method == 'GET':
        try:
            messages = formacion_storage.load_forum_messages(inst_id, course_id)
            return jsonify(messages)
        except Exception as e:
            print(f"Error loading forum: {e}")
            return jsonify([])
    if request.method == 'POST':
        data = request.json
        if not data or not data.get('content'):
            return jsonify({"status": "error", "message": "Content required"}), 400
        import datetime
        msg_id = "msg_" + formacion_storage.generate_id()
        timestamp = datetime.datetime.now().isoformat()
        new_msg = {
            "id": msg_id,
            "user_email": data.get("user_email", "unknown"),
            "user_name": data.get("user_name", "Usuario"),
            "role": data.get("role", "estudiante"),
            "content": data.get("content"),
            "timestamp": timestamp
        }
        try:
            saved = formacion_storage.save_forum_message(inst_id, course_id, new_msg)
            return jsonify({"status": "success", "data": saved})
        except Exception as e:
            print(f"Error saving forum msg: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/courses/<course_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_api_course_specific(course_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    if request.method == 'GET':
        course = formacion_storage.load_course(course_id)
        if course:
            return jsonify(course)
        return jsonify({"status": "error", "message": "Curso no encontrado."}), 404
    elif request.method == 'PUT':
        data = request.json
        data['id'] = course_id
        saved = formacion_storage.save_course(inst_id, program_id, data)
        if saved:
            return jsonify({"status": "success", "data": saved})
        return jsonify({"status": "error", "message": "No se pudo actualizar el curso."}), 500
    elif request.method == 'DELETE':
        success = formacion_storage.delete_course(inst_id, program_id, course_id)
        if success:
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "No se pudo eliminar el curso."}), 500

@app.route('/api/public/courses', methods=['GET'])
def get_public_courses_catalog():
    courses = formacion_storage.load_public_courses()
    public_catalog = []
    for c in courses:
        public_catalog.append({
            "id": c.get("id"), "title": c.get("title"),
            "description": c.get("description"), "duration": c.get("duration"),
            "level": c.get("level"), "category": c.get("category"),
            "certifier": c.get("certifier")
        })
    return jsonify(public_catalog)

@app.route('/api/courses/<course_id>/analytics', methods=['GET'])
def get_course_analytics(course_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    course = formacion_storage.load_course(course_id)
    if not course:
        return jsonify({"status": "error", "message": "Course not found"}), 404
    total_activities = sum(len(unit.get('activities', [])) for unit in course.get('units', []))
    submissions = formacion_storage.load_submissions(inst_id, program_id)
    course_submissions = [s for s in submissions if s.get('course_id') == course_id]
    students = formacion_storage.load_students(inst_id)
    enrolled_students = [s for s in students if 'enrolled_courses' in s and course_id in s['enrolled_courses']]
    analytics_data = []
    for student in enrolled_students:
        email = student.get('email')
        name = student.get('name', 'Estudiante')
        student_subs = [s for s in course_submissions if s.get('student_email') == email]
        completed = len(student_subs)
        progress = int((completed / total_activities) * 100) if total_activities > 0 else 0
        badges = []
        if completed >= 1: badges.append("🥉 Primer Paso")
        if progress >= 50: badges.append("🥈 Acelerado")
        if progress >= 100: badges.append("🥇 Maestría")
        analytics_data.append({
            "email": email, "name": name, "completed": completed,
            "total_activities": total_activities, "progress": progress, "badges": badges
        })
    return jsonify({"course_id": course_id, "total_activities": total_activities, "students": analytics_data})

@app.route('/api/upload', methods=['POST'])
def api_upload_lms_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    try:
        import uuid as _uuid
        ext = ""
        if '.' in file.filename:
            ext = "." + file.filename.rsplit('.', 1)[1].lower()
        file_id = "f_" + str(_uuid.uuid4().hex[:12]) + ext
        file_bytes = file.read()
        mime_type = file.content_type or 'application/octet-stream'
        sb = formacion_storage._get_supabase()
        if sb:
            sb.storage.from_('lms_files').upload(file_id, file_bytes, {"content-type": mime_type})
            public_url = sb.storage.from_('lms_files').get_public_url(file_id)
        else:
            # Fallback: save locally
            import os
            upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            with open(os.path.join(upload_dir, file_id), 'wb') as f:
                f.write(file_bytes)
            public_url = f"/static/uploads/{file_id}"
        return jsonify({"status": "success", "url": public_url, "filename": file.filename})
    except Exception as e:
        print(f"Error uploading file: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/public/courses/<course_id>/report', methods=['GET'])
def get_course_report(course_id):
    course = formacion_storage.load_course(course_id)
    if not course:
        return "<h3>Curso no encontrado</h3>", 404
    return render_template('curso_reporte.html', course=course)

@app.route('/api/students', methods=['GET', 'POST'])
def handle_api_students():
    inst_id = request.args.get('inst_id', 1, type=int)
    if request.method == 'POST':
        data = request.json
        saved = formacion_storage.save_student(inst_id, data)
        if saved:
            return jsonify({"status": "success", "data": saved})
        return jsonify({"status": "error", "message": "No se pudo guardar el estudiante."}), 500
    try:
        students = formacion_storage.load_students(inst_id)
        return jsonify(students)
    except Exception as e:
        print(f"Error loading students: {e}")
        return jsonify([]), 200

@app.route('/api/submissions', methods=['GET', 'POST'])
def handle_api_submissions():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    if request.method == 'POST':
        data = request.json
        saved = formacion_storage.save_submission(inst_id, program_id, data)
        if saved:
            return jsonify({"status": "success", "data": saved})
        return jsonify({"status": "error", "message": "No se pudo guardar la entrega."}), 500
    subs = formacion_storage.load_submissions(inst_id, program_id)
    course_id = request.args.get('course_id')
    student_email = request.args.get('student_email')
    activity_id = request.args.get('activity_id')
    if course_id:
        subs = [s for s in subs if s.get('course_id') == course_id]
    if student_email:
        subs = [s for s in subs if s.get('student_email') == student_email]
    if activity_id:
        subs = [s for s in subs if s.get('activity_id') == activity_id]
    return jsonify(subs)

@app.route('/api/submissions/<submission_id>/grade', methods=['PUT'])
def handle_api_grade_submission(submission_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    data = request.json
    graded = formacion_storage.grade_submission(inst_id, program_id, submission_id, data)
    if graded:
        return jsonify({"status": "success", "data": graded})
    return jsonify({"status": "error", "message": "No se pudo registrar la calificación."}), 500

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_api_student(student_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    success = formacion_storage.delete_student(inst_id, student_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No se pudo eliminar el estudiante."}), 500

@app.route('/api/students/<student_id>/enroll', methods=['POST'])
def enroll_student_api(student_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    course_id = request.json.get('course_id')
    if not course_id:
        return jsonify({"status": "error", "message": "course_id es requerido."}), 400
    success = formacion_storage.enroll_student_in_course(inst_id, student_id, course_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No se pudo matricular al estudiante."}), 500

@app.route('/api/students/<student_id>/unenroll', methods=['POST'])
def unenroll_student_api(student_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    course_id = request.json.get('course_id')
    if not course_id:
        return jsonify({"status": "error", "message": "course_id es requerido."}), 400
    success = formacion_storage.unenroll_student_from_course(inst_id, student_id, course_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No se pudo cancelar la matrícula."}), 500

@app.route('/api/courses/<course_id>/students', methods=['GET'])
def get_course_enrolled_students(course_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    all_students = formacion_storage.load_students(inst_id)
    enrolled = [s for s in all_students if 'enrolled_courses' in s and course_id in s['enrolled_courses']]
    return jsonify(enrolled)

'''

new_content = content[:start_idx] + new_lms_section + marker_end

with open('c:/SIAC/app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

# Verify
remaining = [i+1 for i, l in enumerate(new_content.splitlines()) if 'use_cloud' in l]
print(f"Remaining 'use_cloud' lines: {remaining}")
print("Done!")
