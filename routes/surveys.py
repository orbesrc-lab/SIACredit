from flask import Blueprint, jsonify, request, send_from_directory, render_template
from utils.db import supabase, get_active_inst_id
import json
import os
from survey_storage import survey_storage

surveys_bp = Blueprint('surveys', __name__)

# --- Rutas del Módulo de Encuestas de Autoevaluación ---

@surveys_bp.route('/encuestas.html')
def encuestas_page():
    return render_template('encuestas.html')

@surveys_bp.route('/encuesta_publica.html')
def encuesta_publica_page():
    return render_template('encuesta_publica.html')

@surveys_bp.route('/api/surveys', methods=['GET', 'POST'])
def handle_surveys():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    use_cloud = request.args.get('use_cloud', 'false').lower() == 'true' or survey_storage.IS_VERCEL

    if request.method == 'POST':
        data = request.json  # list of surveys
        if use_cloud:
            try:
                # Pull first to ensure we don't wipe out other responses stored in cloud when we save/sync
                survey_storage.pull_from_supabase(inst_id, program_id, supabase)
                # Save locally first, then sync
                survey_storage.save_local_surveys(inst_id, program_id, data)
                survey_storage.sync_surveys_only(inst_id, program_id, supabase)
                return jsonify({"status": "success", "message": "Encuestas guardadas localmente y sincronizadas en la nube"})
            except Exception as e:
                return jsonify({"status": "error", "message": f"Error al sincronizar en la nube: {str(e)}"})
        else:
            success = survey_storage.save_local_surveys(inst_id, program_id, data)
            if success:
                return jsonify({"status": "success", "message": "Encuestas guardadas localmente"})
            return jsonify({"status": "error", "message": "Error al guardar encuestas localmente"})

    # GET
    if use_cloud:
        try:
            # Pull from cloud first, then load local
            survey_storage.pull_from_supabase(inst_id, program_id, supabase)
        except Exception as e:
            print(f"Error pulling surveys from cloud, falling back to local: {e}")
            
    surveys = survey_storage.load_local_surveys(inst_id, program_id)
    return jsonify(surveys)

@surveys_bp.route('/api/surveys/<survey_id>', methods=['GET', 'DELETE'])
def handle_survey_specific(survey_id):
    if request.method == 'DELETE':
        inst_id = request.args.get('inst_id', 1, type=int)
        program_id = request.args.get('program_id', 0, type=int)
        use_cloud = request.args.get('use_cloud', 'false').lower() == 'true' or survey_storage.IS_VERCEL
        
        if use_cloud:
            try:
                survey_storage.pull_from_supabase(inst_id, program_id, supabase)
            except Exception as e:
                print(f"Error pulling surveys before delete: {e}")
                
        surveys = survey_storage.load_local_surveys(inst_id, program_id)
        surveys = [s for s in surveys if s.get('id') != survey_id]
        survey_storage.save_local_surveys(inst_id, program_id, surveys)
        
        if use_cloud:
            try:
                survey_storage.sync_surveys_only(inst_id, program_id, supabase)
            except Exception as e:
                return jsonify({"status": "error", "message": f"Error al sincronizar eliminación: {str(e)}"})
                
        return jsonify({"status": "success"})
        
    # GET (public, no auth)
    survey = survey_storage.get_survey_by_id_only(survey_id)
    if not survey:
        try:
            res = supabase.table('statistics').select("data_json, inst_id, program_id").like("table_id", "SURVEY_DEFINITIONS%").execute()
            for row in res.data:
                surveys = json.loads(row['data_json'])
                for s in surveys:
                    if s.get('id') == survey_id:
                        survey_storage.save_local_surveys(row['inst_id'], row['program_id'], surveys)
                        return jsonify(s)
        except Exception as e:
            print(f"Error searching survey in cloud: {e}")
        return jsonify({"error": "Encuesta no encontrada"})
        
    return jsonify(survey)

@surveys_bp.route('/api/surveys/<survey_id>/respond', methods=['POST'])
def respond_survey(survey_id):
    data = request.json  # answers dictionary
    survey = survey_storage.get_survey_by_id_only(survey_id)
    
    if not survey:
        try:
            res = supabase.table('statistics').select("data_json, inst_id, program_id").like("table_id", "SURVEY_DEFINITIONS%").execute()
            for row in res.data:
                surveys = json.loads(row['data_json'])
                for s in surveys:
                    if s.get('id') == survey_id:
                        survey_storage.save_local_surveys(row['inst_id'], row['program_id'], surveys)
                        survey = s
                        break
                if survey:
                    break
        except Exception as e:
            print(f"Error fetching survey on response: {e}")
            
    if not survey:
        return jsonify({"error": "Encuesta no encontrada"})
        
    inst_id = survey.get('inst_id', 1)
    program_id = survey.get('program_id', 0)
    use_cloud = request.args.get('use_cloud', 'false').lower() == 'true' or survey_storage.IS_VERCEL
    
    # CRITICAL: Pull from Supabase first if in cloud mode to avoid overwriting existing responses
    if use_cloud:
        try:
            survey_storage.pull_from_supabase(inst_id, program_id, supabase)
        except Exception as e:
            print(f"Error pulling from supabase before response: {e}")

    import datetime
    response_record = {
        "id": "resp_" + survey_storage.generate_id(),
        "survey_id": survey_id,
        "inst_id": inst_id,
        "program_id": program_id,
        "target": survey.get('target', 'general'),
        "submitted_at": datetime.datetime.now().isoformat(),
        "answers": data
    }
    
    if survey.get('status', 'activo') != 'activo':
        return jsonify({"error": "La encuesta ya no está activa o ha sido finalizada"})
        
    success = survey_storage.save_local_response(inst_id, program_id, response_record)
    
    if use_cloud:
        try:
            survey_storage.sync_responses_only(inst_id, program_id, supabase)
        except Exception as e:
            print(f"Error syncing response to cloud: {e}")
            
    if success:
        return jsonify({"status": "success", "message": "Respuesta guardada con éxito"})
    return jsonify({"status": "error", "message": "Error al registrar la respuesta"})

@surveys_bp.route('/api/surveys/<survey_id>/responses', methods=['GET'])
def get_survey_responses(survey_id):
    use_cloud = request.args.get('use_cloud', 'false').lower() == 'true' or survey_storage.IS_VERCEL
    
    inst_id = request.args.get('inst_id', type=int)
    program_id = request.args.get('program_id', type=int)
    
    if use_cloud and inst_id is not None and program_id is not None:
        try:
            survey_storage.pull_from_supabase(inst_id, program_id, supabase)
        except Exception as e:
            print(f"Error pulling responses: {e}")
            
    survey = survey_storage.get_survey_by_id_only(survey_id)
    if not survey and use_cloud:
        try:
            res = supabase.table('statistics').select("data_json, inst_id, program_id").like("table_id", "SURVEY_DEFINITIONS%").execute()
            for row in res.data:
                surveys = json.loads(row['data_json'])
                for s in surveys:
                    if s.get('id') == survey_id:
                        row_inst_id = row['inst_id']
                        row_program_id = row['program_id']
                        survey_storage.save_local_surveys(row_inst_id, row_program_id, surveys)
                        survey_storage.pull_from_supabase(row_inst_id, row_program_id, supabase)
                        survey = s
                        break
                if survey:
                    break
        except Exception as e:
            print(f"Error searching survey in cloud for responses: {e}")
            
    if not survey:
        return jsonify([])
        
    responses = survey_storage.load_local_responses_for_survey(survey_id)
    return jsonify(responses)

@surveys_bp.route('/api/surveys/sync', methods=['POST'])
def sync_surveys():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    action = request.json.get('action', 'push')
    
    try:
        if action == 'push':
            survey_storage.sync_to_supabase(inst_id, program_id, supabase)
            return jsonify({"status": "success", "message": "Datos sincronizados y subidos a la web (Supabase)"})
        else:
            survey_storage.pull_from_supabase(inst_id, program_id, supabase)
            return jsonify({"status": "success", "message": "Datos descargados desde la web (Supabase)"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# === API ENDPOINTS FOR LMS (FORMACION) ===

@surveys_bp.route('/api/teachers', methods=['GET', 'POST'])
def handle_api_teachers():
    inst_id = request.args.get('inst_id', 1, type=int)
    if request.method == 'POST':
        data = request.json
        saved = formacion_storage.save_teacher(inst_id, data)
        if saved:
            return jsonify({"status": "success", "data": saved})
        return jsonify({"status": "error", "message": "No se pudo guardar el docente."})
    try:
        teachers = formacion_storage.load_teachers(inst_id)
        return jsonify(teachers)
    except Exception as e:
        print(f"Error loading teachers: {e}")
        return jsonify([]), 200

@surveys_bp.route('/api/teachers/<teacher_id>', methods=['DELETE'])
def delete_api_teacher(teacher_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    success = formacion_storage.delete_teacher(inst_id, teacher_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No se pudo eliminar el docente."})

@surveys_bp.route('/api/courses', methods=['GET', 'POST'])
def handle_api_courses():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    if request.method == 'POST':
        data = request.json
        saved = formacion_storage.save_course(inst_id, program_id, data)
        if saved:
            return jsonify({"status": "success", "data": saved})
        return jsonify({"status": "error", "message": "No se pudo guardar el curso."})
    try:
        courses = formacion_storage.load_courses(inst_id, program_id)
        return jsonify(courses)
    except Exception as e:
        print(f"Error loading courses: {e}")
        return jsonify([]), 200

@surveys_bp.route('/api/public/courses', methods=['GET'])
def handle_api_public_courses():
    try:
        courses = formacion_storage.load_courses(1, 0)
        return jsonify(courses)
    except Exception as e:
        print(f"Error loading public courses: {e}")
        return jsonify([]), 200


@surveys_bp.route('/api/courses/<course_id>/forum', methods=['GET', 'POST'])
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
            return jsonify({"status": "error", "message": "Content required"})
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
            return jsonify({"status": "error", "message": str(e)})

@surveys_bp.route('/api/courses/<course_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_api_course_specific(course_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    if request.method == 'GET':
        course = formacion_storage.load_course(course_id)
        if course:
            for arr_field in ['outcomes', 'competencies', 'units', 'meetings', 'resources']:
                val = course.get(arr_field)
                if isinstance(val, dict):
                    course[arr_field] = list(val.values())
                elif not val:
                    course[arr_field] = []
            return jsonify(course)
        return jsonify({"status": "error", "message": "Curso no encontrado."})
    elif request.method == 'PUT':
        data = request.json
        data['id'] = course_id
        saved = formacion_storage.save_course(inst_id, program_id, data)
        if saved:
            return jsonify({"status": "success", "data": saved})
        return jsonify({"status": "error", "message": "No se pudo actualizar el curso."})
    elif request.method == 'DELETE':
        success = formacion_storage.delete_course(inst_id, program_id, course_id)
        if success:
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "No se pudo eliminar el curso."})

@surveys_bp.route('/api/public/courses', methods=['GET'])
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

@surveys_bp.route('/api/courses/<course_id>/analytics', methods=['GET'])
def get_course_analytics(course_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    course = formacion_storage.load_course(course_id)
    if not course:
        return jsonify({"status": "error", "message": "Course not found"})
    total_activities = sum(len(unit.get('activities', [])) + len(unit.get('evaluations', [])) for unit in course.get('units', []))
    submissions = formacion_storage.load_submissions(inst_id, program_id)
    course_submissions = [s for s in submissions if s.get('course_id') == course_id]
    students = formacion_storage.load_students(inst_id)
    enrolled_students = [s for s in students if 'enrolled_courses' in s and course_id in s['enrolled_courses']]
    analytics_data = []
    for student in enrolled_students:
        email = student.get('email')
        name = student.get('name', 'Estudiante')
        student_subs = [s for s in course_submissions if s.get('student_email') == email]
        total_units = len(course.get('units', []))
        completed_units = 0
        for unit in course.get('units', []):
            acts = list(unit.get('activities', {}).values()) if isinstance(unit.get('activities'), dict) else unit.get('activities', [])
            evals = list(unit.get('evaluations', {}).values()) if isinstance(unit.get('evaluations'), dict) else unit.get('evaluations', [])
            unit_acts = acts + evals
            if not unit_acts:
                continue
            unit_passed = True
            for act in unit_acts:
                sub = next((s for s in student_subs if s.get('activity_id') == act.get('id')), None)
                if not sub or sub.get('status') != 'graded':
                    unit_passed = False
                    break
                min_grade = float(act.get('min_grade') or 3.0)
                try:
                    grade = float(sub.get('grade') or 0)
                except ValueError:
                    grade = 0
                if grade < min_grade:
                    unit_passed = False
                    break
            if unit_passed:
                completed_units += 1

        completed = completed_units
        progress = int((completed_units / total_units) * 100) if total_units > 0 else 0
        progress = min(100, progress)
        
        badges = []
        if completed_units >= 1: badges.append("🥉 Unidad 1 Superada")
        if completed_units >= 2: badges.append("🥈 Unidad 2 Superada")
        if progress == 100 and total_units > 0: badges.append("🥇 Graduado con Honores")
        analytics_data.append({
            "email": email, "name": name, "completed": completed,
            "total_activities": total_activities, "progress": progress, "badges": badges
        })
    return jsonify({"course_id": course_id, "total_activities": total_activities, "students": analytics_data})

@surveys_bp.route('/api/lms_upload', methods=['POST'])
def api_upload_lms_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})
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
        return jsonify({"status": "error", "message": str(e)})

@surveys_bp.route('/api/public/courses/<course_id>/report', methods=['GET'])
def get_course_report(course_id):
    course = formacion_storage.load_course(course_id)
    if not course:
        return "<h3>Curso no encontrado</h3>", 404
    return render_template('curso_reporte.html', course=course)

@surveys_bp.route('/api/students', methods=['GET', 'POST'])
def handle_api_students():
    inst_id = request.args.get('inst_id', 1, type=int)
    if request.method == 'POST':
        data = request.json
        saved = formacion_storage.save_student(inst_id, data)
        if saved:
            return jsonify({"status": "success", "data": saved})
        return jsonify({"status": "error", "message": "No se pudo guardar el estudiante."})
    try:
        students = formacion_storage.load_students(inst_id)
        return jsonify(students)
    except Exception as e:
        print(f"Error loading students: {e}")
        return jsonify([]), 200

@surveys_bp.route('/api/submissions', methods=['GET', 'POST'])
def handle_api_submissions():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    if request.method == 'POST':
        data = request.json
        saved = formacion_storage.save_submission(inst_id, program_id, data)
        if saved:
            return jsonify({"status": "success", "data": saved})
        return jsonify({"status": "error", "message": "No se pudo guardar la entrega."})
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

@surveys_bp.route('/api/submissions/<submission_id>/grade', methods=['PUT'])
def handle_api_grade_submission(submission_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    data = request.json
    graded = formacion_storage.grade_submission(inst_id, program_id, submission_id, data)
    if graded:
        return jsonify({"status": "success", "data": graded})
    return jsonify({"status": "error", "message": "No se pudo registrar la calificación."})

@surveys_bp.route('/api/students/<student_id>', methods=['DELETE'])
def delete_api_student(student_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    success = formacion_storage.delete_student(inst_id, student_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No se pudo eliminar el estudiante."})

@surveys_bp.route('/api/students/<student_id>/enroll', methods=['POST'])
def enroll_student_api(student_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    course_id = request.json.get('course_id')
    if not course_id:
        return jsonify({"status": "error", "message": "course_id es requerido."})
    success = formacion_storage.enroll_student_in_course(inst_id, student_id, course_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No se pudo matricular al estudiante."})

@surveys_bp.route('/api/students/<student_id>/unenroll', methods=['POST'])
def unenroll_student_api(student_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    course_id = request.json.get('course_id')
    if not course_id:
        return jsonify({"status": "error", "message": "course_id es requerido."})
    success = formacion_storage.unenroll_student_from_course(inst_id, student_id, course_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No se pudo cancelar la matrícula."})

@surveys_bp.route('/api/courses/<course_id>/students', methods=['GET'])
def get_course_enrolled_students(course_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    all_students = formacion_storage.load_students(inst_id)
    enrolled = [s for s in all_students if 'enrolled_courses' in s and course_id in s['enrolled_courses']]
    return jsonify(enrolled)

@surveys_bp.route('/api/public/enroll_course', methods=['POST'])
def public_enroll_course():
    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    course_id = data.get('course_id')
    inst_id = data.get('inst_id', 1)
    
    if not name or not email or not password or not course_id:
        return jsonify({"status": "error", "message": "Datos incompletos"})

    try:
        sb = formacion_storage._get_supabase()
        if not sb:
            return jsonify({"status": "error", "message": "No database connection"})

        # 1. Check if user already exists
        user_res = sb.table('users').select("*").eq('email', email).execute()
        pending_name = f"[ASPIRANTE] {name}"
        
        if len(user_res.data) == 0:
            new_user = {
                "id": str(uuid.uuid4()),
                "name": pending_name,
                "email": email,
                "password_hash": generate_password_hash(password),
                "role": "estudiante",
                "inst_id": inst_id,
                "program_id": 0
            }
            sb.table('users').insert(new_user).execute()

        # 2. Check or create in lms_students
        students = formacion_storage.load_students(inst_id)
        student = next((s for s in students if s.get('email') == email), None)
        
        if not student:
            # Create student record
            student_data = {
                "name": pending_name,
                "email": email,
                "enrolled_courses": [course_id]
            }
            formacion_storage.save_student(inst_id, student_data)
        else:
            # Add to enrolled_courses if not there
            if course_id not in student.get('enrolled_courses', []):
                formacion_storage.enroll_student_in_course(inst_id, student['id'], course_id)
            
            if '[ASPIRANTE]' not in student.get('name', ''):
                student['name'] = f"[ASPIRANTE] {student.get('name', name).replace('[PENDING] ', '')}"
                formacion_storage.save_student(inst_id, student)
                
        return jsonify({"status": "success", "message": "Inscripción registrada correctamente"})

    except Exception as e:
        print(f"Error en enroll_course: {e}")
        return jsonify({"status": "error", "message": "Error interno"})

