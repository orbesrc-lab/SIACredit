from flask import Blueprint, jsonify, request, session, render_template
from utils.db import supabase, get_active_inst_id
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import json
import traceback

core_bp = Blueprint('core', __name__)

# --- API Endpoints con Supabase (Multi-tenant) ---

@core_bp.route('/api/model', methods=['GET', 'POST'])
def handle_model():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    if request.method == 'POST':
        data = request.json # Lista de factores
        inst_id = request.args.get('inst_id', 1, type=int) # Re-get for safety
        program_id = request.args.get('program_id', 0, type=int)

        # --- TRAZABILIDAD: No se puede guardar el modelo sin un programa activo ---
        if not program_id or program_id == 0:
            return jsonify({"status": "error", "message": "Debes seleccionar un Programa Académico activo antes de guardar el Modelo de Evaluación."})
        
        try:
            curr_factors = supabase.table('factors').select("id").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
            curr_f_ids = {f['id'] for f in curr_factors}
            
            curr_chars = supabase.table('characteristics').select("id").in_("factor_id", list(curr_f_ids)).execute().data if curr_f_ids else []
            curr_c_ids = {c['id'] for c in curr_chars}
            
            curr_aspects = supabase.table('aspects').select("id").in_("char_id", list(curr_c_ids)).execute().data if curr_c_ids else []
            curr_a_ids = {a['id'] for a in curr_aspects}
            
            incoming_f_ids = set()
            incoming_c_ids = set()
            incoming_a_ids = set()
            
            for f in data:
                incoming_f_ids.add(f['id'])
                # Upsert Factor
                try:
                    supabase.table('factors').upsert({
                        "id": f['id'], "number": f['number'], "name": f['name'], 
                        "weight": f.get('weight', 0), "inst_id": inst_id, "program_id": program_id,
                        "leader_id": f.get('leader_id') or None
                    }).execute()
                except Exception:
                    supabase.table('factors').upsert({
                        "id": f['id'], "number": f['number'], "name": f['name'], 
                        "weight": f.get('weight', 0), "inst_id": inst_id, "program_id": program_id
                    }).execute()
                
                for c in f.get('characteristics', []):
                    incoming_c_ids.add(c['id'])
                    supabase.table('characteristics').upsert({
                        "id": c['id'], "factor_id": f['id'], "number": c['number'], 
                        "name": c['name'], "weight": c.get('weight', 0)
                    }).execute()
                    
                    for a in c.get('aspects', []):
                        incoming_a_ids.add(a['id'])
                        supabase.table('aspects').upsert({
                            "id": a['id'], "char_id": c['id'], "text": a['text']
                        }).execute()
            
            # Delete aspects not in incoming (and their evidences)
            diff_a = curr_a_ids - incoming_a_ids
            if diff_a:
                for chunk in [list(diff_a)[i:i+100] for i in range(0, len(diff_a), 100)]:
                    try: supabase.table('evidences').delete().in_("aspect_id", chunk).execute()
                    except Exception: pass
                    supabase.table('aspects').delete().in_("id", chunk).execute()

            # Delete characteristics not in incoming (and their evaluations)
            diff_c = curr_c_ids - incoming_c_ids
            if diff_c:
                for chunk in [list(diff_c)[i:i+100] for i in range(0, len(diff_c), 100)]:
                    try: supabase.table('evaluations').delete().in_("char_id", chunk).execute()
                    except Exception: pass
                    supabase.table('characteristics').delete().in_("id", chunk).execute()

            # Delete factors (cascades) not in incoming
            diff_f = curr_f_ids - incoming_f_ids
            if diff_f:
                for chunk in [list(diff_f)[i:i+100] for i in range(0, len(diff_f), 100)]:
                    supabase.table('factors').delete().in_("id", chunk).eq("inst_id", inst_id).eq("program_id", program_id).execute()

            return jsonify({"status": "success", "message": "Modelo sincronizado para programa " + str(program_id)})
        except Exception as e:
            print(f"Error during sync: {e}")
            return jsonify({"status": "error", "message": str(e)})

    try:
        try:
            res = supabase.table('factors').select("*, characteristics(*, aspects(*)), leader_id").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        except Exception:
            res = supabase.table('factors').select("*, characteristics(*, aspects(*))").eq("inst_id", inst_id).eq("program_id", program_id).execute()
            
        sorted_data = sorted(res.data, key=lambda x: float(x['number']))
        return jsonify(sorted_data)
    except Exception as e:
        print(f"Error fetching model: {e}")
        return jsonify([])

@core_bp.route('/api/evaluations', methods=['GET', 'POST'])
def handle_evaluations():
    raw_inst_id = request.args.get('inst_id', 1, type=int)
    inst_id = get_active_inst_id(raw_inst_id)
    program_id = request.args.get('program_id', 0, type=int)
    if request.method == 'POST':
        data = request.json
        try:
            for char_id, eval_data in data.items():
                try:
                    existing = supabase.table('evaluations').select('id').eq('char_id', char_id).execute()
                    if existing.data:
                        supabase.table('evaluations').update({
                            "rating": eval_data.get('rating', 0), 
                            "just": eval_data.get('just', ''),
                            "inst_id": inst_id,
                            "program_id": program_id
                        }).eq('char_id', char_id).execute()
                    else:
                        supabase.table('evaluations').insert({
                            "char_id": char_id, 
                            "rating": eval_data.get('rating', 0), 
                            "just": eval_data.get('just', ''),
                            "inst_id": inst_id,
                            "program_id": program_id
                        }).execute()
                except Exception:
                    # Fallback si no existen las columnas inst_id/program_id
                    existing_fb = supabase.table('evaluations').select('id').eq('char_id', char_id).execute()
                    if existing_fb.data:
                        supabase.table('evaluations').update({
                            "rating": eval_data.get('rating', 0), 
                            "just": eval_data.get('just', '')
                        }).eq('char_id', char_id).execute()
                    else:
                        supabase.table('evaluations').insert({
                            "char_id": char_id, 
                            "rating": eval_data.get('rating', 0), 
                            "just": eval_data.get('just', '')
                        }).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            print(f"Error saving eval: {e}")
            return jsonify({"status": "error", "message": str(e)})

    try:
        # Intentar carga con filtros
        try:
            evals = supabase.table('evaluations').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
            if not evals.data: # Si no hay nada con filtros, probar carga global
                evals = supabase.table('evaluations').select("*").execute()
        except Exception:
            evals = supabase.table('evaluations').select("*").execute()
            
        eval_dict = {e['char_id']: {"rating": e['rating'], "just": e['just']} for e in evals.data}
        return jsonify(eval_dict)
    except Exception as e:
        print(f"Error loading evals: {e}")
        return jsonify({})

@core_bp.route('/api/evaluations/<char_id>', methods=['DELETE'])
def delete_evaluation(char_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    try:
        supabase.table('evaluations').delete().eq("char_id", char_id).eq("inst_id", inst_id).eq("program_id", program_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error deleting eval: {e}")
        return jsonify({"status": "error", "message": str(e)})

# Helper to create notification and log email simulation
def create_notification(inst_id, program_id, email, tipo, titulo, mensaje):
    try:
        # In-app notification
        supabase.table('notificaciones').insert({
            "inst_id": inst_id,
            "program_id": program_id,
            "usuario_email": email,
            "tipo": tipo,
            "titulo": titulo,
            "mensaje": mensaje,
            "leido": False
        }).execute()
        
        # Email simulator log
        print(f"\n[EMAIL SIMULATOR] Sending email to {email}")
        print(f"Subject: {titulo}")
        print(f"Body: {mensaje}\n")
    except Exception as e:
        print(f"Error creating notification: {e}")

def calculate_plan_avance(plan, inst_id, program_id):
    tipo = plan.get('indicador_tipo', 'porcentaje')
    if tipo == 'porcentaje':
        num = plan.get('indicador_meta_num')
        den = plan.get('indicador_meta_den')
        try:
            num = int(num) if num is not None else 0
            den = int(den) if den is not None else 1
        except (ValueError, TypeError):
            num, den = 0, 1
        if den <= 0:
            return 0
        return int((num / den) * 100)
    elif tipo == 'documento':
        url = plan.get('indicador_documento_url')
        return 100 if url else 0
    elif tipo == 'opinion':
        survey_id = plan.get('indicador_survey_id')
        question_id = plan.get('indicador_question_id')
        if not survey_id or not question_id:
            return 0
        try:
            responses = survey_storage.load_local_responses_for_survey(str(survey_id))
            if not responses:
                responses = survey_storage.load_local_responses_for_survey(survey_id)
            
            vals = []
            for r in responses:
                ans = r.get('answers') or {}
                val = ans.get(str(question_id))
                if val is not None:
                    try:
                        vals.append(float(val))
                    except ValueError:
                        pass
            if not vals:
                return 0
            avg = sum(vals) / len(vals)
            return min(100, int((avg / 5.0) * 100))
        except Exception as e:
            print(f"Error calculating opinion progress: {e}")
            return 0
    try:
        return int(plan.get('avance', 0))
    except (ValueError, TypeError):
        return 0

@core_bp.route('/api/planes_mejora', methods=['GET', 'POST'])
def handle_planes_mejora():
    raw_inst_id = request.args.get('inst_id', 1, type=int)
    inst_id = get_active_inst_id(raw_inst_id)
    program_id = request.args.get('program_id', 0, type=int)
    
    if request.method == 'POST':
        data = request.json
        try:
            if data and 'avance' in data and data.get('indicador_meta_num') is None:
                data = data.copy()
                data['indicador_meta_num'] = data.get('avance')
                data['indicador_meta_den'] = 100
            char_id = data.get('char_id')
            accion = data.get('accion')
            responsable = data.get('responsable')
            fecha_limite = data.get('fecha_limite')
            fecha_inicio = data.get('fecha_inicio')
            meta = data.get('meta')
            indicador_tipo = data.get('indicador_tipo', 'porcentaje')
            indicador_meta_num = data.get('indicador_meta_num', 0)
            indicador_meta_den = data.get('indicador_meta_den', 1)
            indicador_documento_url = data.get('indicador_documento_url')
            indicador_survey_id = data.get('indicador_survey_id')
            indicador_question_id = data.get('indicador_question_id')
            presupuesto_tiempo = data.get('presupuesto_tiempo')
            presupuesto_dinero = data.get('presupuesto_dinero', 0)
            responsable_rol = data.get('responsable_rol', 'lider')
            
            if not char_id or not accion or not responsable or not fecha_limite:
                return jsonify({"status": "error", "message": "Datos incompletos"})
            
            avance = calculate_plan_avance({
                "indicador_tipo": indicador_tipo,
                "indicador_meta_num": indicador_meta_num,
                "indicador_meta_den": indicador_meta_den,
                "indicador_documento_url": indicador_documento_url,
                "indicador_survey_id": indicador_survey_id,
                "indicador_question_id": indicador_question_id,
                "avance": data.get('avance', 0)
            }, inst_id, program_id)
            
            estado = data.get('estado', 'Pendiente')
            if avance >= 100:
                estado = 'Completado'
            elif avance > 0 and estado == 'Pendiente':
                estado = 'En proceso'
                
            res = supabase.table('planes_mejora').insert({
                "inst_id": inst_id,
                "program_id": program_id,
                "char_id": char_id,
                "accion": accion,
                "responsable": responsable,
                "fecha_limite": fecha_limite,
                "fecha_inicio": fecha_inicio,
                "meta": meta,
                "indicador_tipo": indicador_tipo,
                "indicador_meta_num": int(indicador_meta_num) if indicador_meta_num is not None else 0,
                "indicador_meta_den": int(indicador_meta_den) if indicador_meta_den is not None else 1,
                "indicador_documento_url": indicador_documento_url,
                "indicador_survey_id": str(indicador_survey_id) if indicador_survey_id else None,
                "indicador_question_id": indicador_question_id,
                "presupuesto_tiempo": presupuesto_tiempo,
                "presupuesto_dinero": float(presupuesto_dinero) if presupuesto_dinero is not None else 0.0,
                "responsable_rol": responsable_rol,
                "estado": estado,
                "avance": avance
            }).execute()
            
            titulo_notif = "Nueva accion de mejora asignada"
            msg_notif = f"Se te ha asignado la accion de mejora: '{accion}' con fecha limite {fecha_limite}."
            create_notification(inst_id, program_id, responsable, 'nueva_asignacion', titulo_notif, msg_notif)
            
            return jsonify({"status": "success", "data": res.data})
        except Exception as e:
            print(f"Error creating plan de mejora: {e}")
            return jsonify({"status": "error", "message": str(e)})
            
    char_id = request.args.get('char_id')
    try:
        query = supabase.table('planes_mejora').select("*").eq("inst_id", inst_id).eq("program_id", program_id)
        if char_id:
            query = query.eq("char_id", char_id)
        res = query.execute()
        planes_list = res.data or []
        
        if any(p.get('indicador_tipo') == 'opinion' for p in planes_list):
            try:
                survey_storage.pull_from_supabase(inst_id, program_id, supabase)
            except Exception as e:
                print(f"Error pulling surveys: {e}")
                
        updated_planes = []
        for p in planes_list:
            old_avance = p.get('avance', 0)
            new_avance = calculate_plan_avance(p, inst_id, program_id)
            
            old_estado = p.get('estado')
            new_estado = old_estado
            if new_avance >= 100:
                new_estado = 'Completado'
            elif new_avance > 0 and old_estado == 'Pendiente':
                new_estado = 'En proceso'
            elif new_avance == 0 and old_estado == 'Completado':
                new_estado = 'Pendiente'
                
            if new_avance != old_avance or new_estado != old_estado:
                p['avance'] = new_avance
                p['estado'] = new_estado
                try:
                    supabase.table('planes_mejora').update({
                        "avance": new_avance,
                        "estado": new_estado
                    }).eq("id", p['id']).execute()
                except Exception as db_err:
                    print(f"Error auto-persisting avance/estado: {db_err}")
                    
            updated_planes.append(p)
            
        return jsonify(updated_planes)
    except Exception as e:
        print(f"Error loading planes de mejora: {e}")
        return jsonify([])

@core_bp.route('/api/planes_mejora/<int:plan_id>', methods=['PUT', 'DELETE'])
def update_delete_plan_mejora(plan_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    
    if request.method == 'DELETE':
        try:
            supabase.table('planes_mejora').delete().eq("id", plan_id).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            print(f"Error deleting plan de mejora: {e}")
            return jsonify({"status": "error", "message": str(e)})
            
    data = request.json
    try:
        if data and 'avance' in data and data.get('indicador_meta_num') is None:
            data = data.copy()
            data['indicador_meta_num'] = data.get('avance')
            data['indicador_meta_den'] = 100
        existing = supabase.table('planes_mejora').select("*").eq("id", plan_id).execute()
        if not existing.data:
            return jsonify({"status": "error", "message": "Plan no encontrado"})
        plan_data = existing.data[0]
        
        merged_data = {}
        for k, v in plan_data.items():
            merged_data[k] = v
        for k, v in data.items():
            if v is not None:
                merged_data[k] = v
                
        avance = calculate_plan_avance(merged_data, inst_id, program_id)
        estado = merged_data.get('estado')
        if avance >= 100:
            estado = 'Completado'
        elif avance > 0 and (estado == 'Pendiente' or not estado):
            estado = 'En proceso'
        elif avance == 0 and estado == 'Completado':
            estado = 'Pendiente'
            
        update_data = {
            "accion": data.get('accion'),
            "responsable": data.get('responsable'),
            "fecha_limite": data.get('fecha_limite'),
            "fecha_inicio": data.get('fecha_inicio'),
            "meta": data.get('meta'),
            "indicador_tipo": data.get('indicador_tipo'),
            "indicador_meta_num": int(data.get('indicador_meta_num')) if data.get('indicador_meta_num') is not None else None,
            "indicador_meta_den": int(data.get('indicador_meta_den')) if data.get('indicador_meta_den') is not None else None,
            "indicador_documento_url": data.get('indicador_documento_url'),
            "indicador_survey_id": str(data.get('indicador_survey_id')) if data.get('indicador_survey_id') is not None else None,
            "indicador_question_id": data.get('indicador_question_id'),
            "presupuesto_tiempo": data.get('presupuesto_tiempo'),
            "presupuesto_dinero": float(data.get('presupuesto_dinero')) if data.get('presupuesto_dinero') is not None else None,
            "responsable_rol": data.get('responsable_rol'),
            "estado": estado,
            "avance": avance
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        res = supabase.table('planes_mejora').update(update_data).eq("id", plan_id).execute()
        
        if data.get('fecha_limite'):
            msg_notif = f"Se ha actualizado la fecha limite de la accion '{data.get('accion', 'asignada')}' al {data.get('fecha_limite')}."
            create_notification(inst_id, program_id, data.get('responsable') or plan_data.get('responsable'), 'nueva_asignacion', "Actualizacion de fecha de accion", msg_notif)
            
        return jsonify({"status": "success", "data": res.data})
    except Exception as e:
        print(f"Error updating plan de mejora: {e}")
        return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/planes_mejora/upload_soporte', methods=['POST'])
def upload_soporte_plan():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    plan_id = request.form.get('plan_id', 'unknown')
    
    import re
    import time
    clean_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
    timestamp = int(time.time())
    parts = clean_filename.rsplit('.', 1)
    if len(parts) == 2:
        clean_filename = f"{parts[0]}_{timestamp}.{parts[1]}"
    else:
        clean_filename = f"{clean_filename}_{timestamp}"
        
    file_path = f"planes_soporte/{plan_id}/{clean_filename}"
    try:
        file_content = file.read()
        supabase.storage.from_('evidencias').upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": file.content_type, "upsert": "true"}
        )
        file_url = supabase.storage.from_('evidencias').get_public_url(file_path)
        return jsonify({"status": "success", "url": file_url, "name": file.filename})
    except Exception as e:
        print(f"Error uploading soporte plan: {e}")
        return jsonify({"error": str(e)})

@core_bp.route('/api/notificaciones', methods=['GET'])
def get_notificaciones():
    raw_inst_id = request.args.get('inst_id', 1, type=int)
    inst_id = get_active_inst_id(raw_inst_id)
    program_id = request.args.get('program_id', 0, type=int)
    email = request.args.get('email')
    
    if not email:
        return jsonify([])
        
    try:
        res = supabase.table('notificaciones').select("*").eq("inst_id", inst_id).eq("program_id", program_id).eq("usuario_email", email).order("created_at", desc=True).execute()
        return jsonify(res.data or [])
    except Exception as e:
        print(f"Error getting notifications: {e}")
        return jsonify([])

@core_bp.route('/api/notificaciones/<int:notif_id>/read', methods=['POST'])
def read_notificacion(notif_id):
    try:
        res = supabase.table('notificaciones').update({"leido": True}).eq("id", notif_id).execute()
        return jsonify({"status": "success", "data": res.data})
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/notificaciones/read-all', methods=['POST'])
def read_all_notificaciones():
    email = request.json.get('email')
    raw_inst_id = request.args.get('inst_id', 1, type=int)
    inst_id = get_active_inst_id(raw_inst_id)
    program_id = request.args.get('program_id', 0, type=int)
    
    if not email:
        return jsonify({"status": "error", "message": "Email es requerido"})
        
    try:
        res = supabase.table('notificaciones').update({"leido": True}).eq("inst_id", inst_id).eq("program_id", program_id).eq("usuario_email", email).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error marking all notifications as read: {e}")
        return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/estadisticas', methods=['GET', 'POST'])
def handle_stats():
    if request.method == 'POST':
        data = request.json
        if "table_id" in data and "data" in data:
            # Formato nuevo usado por evidencias.html
            table_id = data["table_id"]
            rows = data["data"]
            inst_id = data.get("inst_id", 1)
            program_id = data.get("program_id", 0)
            
            try:
                # Upsert requiere que la tabla statistics tenga primary key o unique constraint en (table_id, inst_id, program_id)
                # Si falla, intentamos hacer update/insert manual
                check = supabase.table('statistics').select("id").eq("table_id", table_id).eq("inst_id", inst_id).eq("program_id", program_id).execute()
                if check.data:
                    supabase.table('statistics').update({"data_json": json.dumps(rows)}).eq("id", check.data[0]["id"]).execute()
                else:
                    supabase.table('statistics').insert({
                        "table_id": table_id, "data_json": json.dumps(rows), "inst_id": inst_id, "program_id": program_id
                    }).execute()
                return jsonify({"status": "success"})
            except Exception as e:
                print(f"Error saving stats: {e}")
                return jsonify({"status": "error", "message": str(e)})
        else:
            # Formato viejo
            inst_id = request.args.get('inst_id', 1, type=int)
            program_id = request.args.get('program_id', 0, type=int)
            for table_id, rows in data.items():
                check = supabase.table('statistics').select("id").eq("table_id", table_id).eq("inst_id", inst_id).eq("program_id", program_id).execute()
                if check.data:
                    supabase.table('statistics').update({"data_json": json.dumps(rows)}).eq("id", check.data[0]["id"]).execute()
                else:
                    supabase.table('statistics').insert({
                        "table_id": table_id, "data_json": json.dumps(rows), "inst_id": inst_id, "program_id": program_id
                    }).execute()
            return jsonify({"status": "success"})

    try:
        inst_id = request.args.get('inst_id', 1, type=int)
        program_id = request.args.get('program_id', 0, type=int)
        table_id = request.args.get('table_id')
        
        query = supabase.table('statistics').select("*").eq("inst_id", inst_id).eq("program_id", program_id)
        if table_id:
            query = query.eq("table_id", table_id)
        stats = query.execute()

        if table_id:
            if stats.data:
                # El frontend espera que el resultado venga envuelto en {"data": ...}
                return jsonify({"data": json.loads(stats.data[0]['data_json'])})
            return jsonify({})

        result = {s['table_id']: json.loads(s['data_json']) for s in stats.data}
        return jsonify(result)
    except Exception as e:
        print(f"Error loading stats: {e}")
        return jsonify({})

@core_bp.route('/api/programs', methods=['GET', 'POST'])
def handle_programs():
    inst_id = request.args.get('inst_id', 1, type=int)
    if request.method == 'POST':
        data = request.json
        try:
            insert_data = {
                "name": data.get('name'),
                "period": data.get('period', ''),
                "inst_id": inst_id
            }
            res = supabase.table('programs').insert(insert_data).execute()
            
            if res.data and len(res.data) > 0:
                return jsonify({"status": "success", "data": res.data[0]})
            else:
                # Intento de recuperación si RLS oculta el retorno
                fallback = supabase.table('programs').select("*")\
                    .eq("name", insert_data['name'])\
                    .eq("inst_id", inst_id)\
                    .order("id", desc=True).limit(1).execute()
                if fallback.data:
                    return jsonify({"status": "success", "data": fallback.data[0]})
                return jsonify({"status": "error", "message": "Supabase no retornó datos del programa."})
        except Exception as e:
            print(f"Error creating program: {e}")
            return jsonify({"status": "error", "message": str(e)})

    try:
        res = supabase.table('programs').select("*").eq("inst_id", inst_id).execute()
        return jsonify(res.data)
    except:
        return jsonify([])

@core_bp.route('/api/programs/<int:prog_id>', methods=['DELETE', 'PUT'])
def handle_program_specific(prog_id):
    if request.method == 'DELETE':
        try:
            # Deep cascade delete manually to prevent FK constraint errors
            try: supabase.table('users').delete().eq("program_id", prog_id).execute()
            except Exception: pass
            try: supabase.table('evaluations').delete().eq("program_id", prog_id).execute()
            except Exception: pass
            try: supabase.table('evidences').delete().eq("program_id", prog_id).execute()
            except Exception: pass
            try: supabase.table('statistics').delete().eq("program_id", prog_id).execute()
            except Exception: pass
            
            # Deep cascade for factors -> characteristics -> aspects
            try:
                factors = supabase.table('factors').select("id").eq("program_id", prog_id).execute().data
                if factors:
                    factor_ids = [f['id'] for f in factors]
                    chars = supabase.table('characteristics').select("id").in_("factor_id", factor_ids).execute().data
                    if chars:
                        char_ids = [c['id'] for c in chars]
                        supabase.table('aspects').delete().in_("char_id", char_ids).execute()
                        supabase.table('characteristics').delete().in_("factor_id", factor_ids).execute()
                    supabase.table('factors').delete().eq("program_id", prog_id).execute()
            except Exception as e: 
                print("Error deep cascading factors for program:", e)

            supabase.table('programs').delete().eq("id", prog_id).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    elif request.method == 'PUT':
        data = request.json
        try:
            supabase.table('programs').update({
                "name": data.get('name'),
                "period": data.get('period')
            }).eq("id", prog_id).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/programs/metadata', methods=['GET', 'POST'])
def handle_program_metadata():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    table_id = f"PROGRAM_METADATA_{program_id}"
    
    if request.method == 'POST':
        data = request.json
        try:
            existing = supabase.table('statistics').select("id").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", table_id).execute()
            if existing.data:
                supabase.table('statistics').update({
                    "data_json": json.dumps(data)
                }).eq("id", existing.data[0]['id']).execute()
            else:
                supabase.table('statistics').insert({
                    "inst_id": inst_id,
                    "program_id": program_id,
                    "table_id": table_id,
                    "data_json": json.dumps(data)
                }).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            print("Error saving program metadata:", e)
            return jsonify({"status": "error", "message": str(e)})
    
    try:
        res = supabase.table('statistics').select("data_json").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", table_id).execute()
        if res.data:
            return jsonify(json.loads(res.data[0]['data_json']))
        return jsonify({})
    except Exception as e:
        return jsonify({})

@core_bp.route('/api/institutions', methods=['GET', 'POST'])
def handle_all_institutions():
    if request.method == 'POST':
        data = request.json
        try:
            # Fallback for tables without auto-increment identity
            max_id_res = supabase.table('institution').select("id").order("id", desc=True).limit(1).execute()
            next_id = 1
            if max_id_res.data:
                next_id = int(max_id_res.data[0]['id']) + 1

            res = supabase.table('institution').insert({
                "id": next_id,
                "name": data.get('name'),
                "logo_url": data.get('logo_url', ''),
                "description": data.get('program', ''),
                "code": data.get('period', '')
            }).execute()
            return jsonify({"status": "success", "data": res.data[0]})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    try:
        res = supabase.table('institution').select("*").execute()
        return jsonify(res.data)
    except Exception as e:
        print(f"Error en GET /api/institutions: {e}")
        return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/institutions/<int:inst_id>', methods=['DELETE'])
def delete_institution(inst_id):
    try:
        # PROTECCIÓN: No permitir borrar la institución principal (ID 1)
        if inst_id == 1:
            return jsonify({"status": "error", "message": "No se puede eliminar la institución principal del sistema."}), 403
            
        # ON DELETE CASCADE en Supabase se encarga de borrar hijos automáticamente
        supabase.table('institution').delete().eq("id", inst_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/institutions/<int:inst_id>/suspend', methods=['POST'])
def suspend_institution(inst_id):
    try:
        inst = supabase.table('institution').select("code").eq("id", inst_id).execute()
        if inst.data:
            code = inst.data[0].get('code', '')
            if '[SUSPENDIDO]' not in code:
                new_code = f"[SUSPENDIDO] {code}"
                supabase.table('institution').update({"code": new_code}).eq("id", inst_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/institution', methods=['GET', 'POST'])
def handle_institution():
    inst_id = request.args.get('inst_id', 1, type=int)
    if request.method == 'POST':
        data = request.json
        try:
            update_data = {
                "name": data.get('name'),
                "logo_url": data.get('logo_url')
            }
            # Only update description/code if they are provided, otherwise leave them alone
            if 'program' in data:
                update_data["description"] = data['program']
            if 'period' in data:
                update_data["code"] = data['period']
                
            supabase.table('institution').update(update_data).eq("id", inst_id).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    try:
        inst = supabase.table('institution').select("*").eq("id", inst_id).execute()
        if inst.data:
            data = inst.data[0]
            data['program'] = data.get('description', '')
            data['period'] = data.get('code', '')
            return jsonify(data)
    except:
        pass
    return jsonify({"name": "Nueva Institución", "logo_url": "", "program": "Programa Académico", "period": "2026-1"})

@core_bp.route('/api/login', methods=['POST'])
def handle_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    try:
        res = supabase.table('users').select("*").eq("email", email).execute()
        if not res.data:
            # Buscar si el correo pertenece a un estudiante matriculado localmente
            try:
                import formacion_storage
                students = formacion_storage.load_students(1)
                student = next((s for s in students if s.get('email') == email), None)
                if student:
                    # Permitir ingresar con contraseña temporal estándar o el prefijo de su correo
                    if password in ['123456', 'SIACTemp2025!', email.split('@')[0]]:
                        return jsonify({
                            "status": "success",
                            "user": { 
                                "id": student['id'],
                                "email": student['email'], 
                                "role": "estudiante",
                                "inst_id": 1,
                                "program_id": 0
                            }
                        })
            except Exception as e:
                print(f"Error buscando estudiante para login: {e}")
                
            return jsonify({"status": "error", "message": "Usuario no encontrado"})
        user = res.data[0]
        
        # Bloquear usuarios pendientes verificando el prefijo en su nombre
        if user.get('name') and str(user.get('name')).startswith('[PENDING]'):
            return jsonify({"status": "error", "message": "Tu cuenta está pendiente de activación por un Administrador."}), 403
            
        if check_password_hash(user['password_hash'], password):
            # Check if institution is suspended
            if user.get('inst_id') and user['inst_id'] != 1:
                inst_res = supabase.table('institution').select("code").eq("id", user['inst_id']).execute()
                if inst_res.data:
                    code = inst_res.data[0].get('code', '')
                    if code and '[SUSPENDIDO]' in code:
                        return jsonify({"status": "error", "message": "Tu institución se encuentra suspendida temporalmente."}), 403
                        
            return jsonify({
                "status": "success",
                "user": { 
                    "id": user['id'],
                    "email": user['email'], 
                    "role": user['role'],
                    "inst_id": user['inst_id'],
                    "program_id": user.get('program_id', 0)
                }
            })
        return jsonify({"status": "error", "message": "Contraseña incorrecta"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/change-password', methods=['POST'])
def change_password():
    data = request.json
    email = data.get('email')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    try:
        res = supabase.table('users').select("*").eq("email", email).execute()
        if not res.data:
            return jsonify({"status": "error", "message": "Usuario no encontrado"})
        user = res.data[0]
        if check_password_hash(user['password_hash'], old_password):
            new_hash = generate_password_hash(new_password)
            supabase.table('users').update({"password_hash": new_hash}).eq("email", email).execute()
            return jsonify({"status": "success", "message": "Contraseña actualizada"})
        return jsonify({"status": "error", "message": "Contraseña actual incorrecta"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({"status": "error", "message": "Email requerido"})
    try:
        res = supabase.table('users').select("*").eq("email", email).execute()
        if not res.data:
            # Por seguridad, retornamos éxito aunque no exista para no revelar usuarios
            return jsonify({"status": "success", "message": "Si el correo existe, recibirás las instrucciones."})
            
        import string
        import random
        # Generar contraseña temporal segura
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        temp_password = ''.join(random.choice(alphabet) for i in range(10))
        
        # Actualizar en BD
        new_hash = generate_password_hash(temp_password)
        supabase.table('users').update({"password_hash": new_hash}).eq("email", email).execute()
        
        # Enviar correo
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
            <h2 style="color: #2563eb;">Recuperación de Contraseña</h2>
            <p>Hola,</p>
            <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en SKEL 360.</p>
            <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Tu nueva contraseña temporal es:</strong> <span style="font-family: monospace; font-size: 1.1em; font-weight: bold; color: #b91c1c;">{temp_password}</span></p>
            </div>
            <p><strong>URL de acceso:</strong> <a href="https://skel360.online/login.html">https://skel360.online/login.html</a></p>
            <p>Te recomendamos encarecidamente que cambies esta contraseña por una propia tan pronto ingreses al sistema, en la sección de Configuración.</p>
            <p style="color: #64748b; font-size: 0.9em; margin-top: 30px;">Si no solicitaste este cambio, por favor contacta al administrador.</p>
        </div>
        """
        success = send_email(email, "Recuperación de Contraseña - SKEL 360", html_content)
        
        if success:
            return jsonify({"status": "success", "message": "Si el correo existe, recibirás las instrucciones."})
        else:
            return jsonify({"status": "error", "message": "Error al enviar el correo. Por favor contacta al administrador."})
            
    except Exception as e:
        print(f"Error in forgot-password: {e}")
        return jsonify({"status": "error", "message": "Error interno del servidor"})

@core_bp.route('/api/init-admin', methods=['GET'])
def init_admin():
    try:
        res = supabase.table('users').select("*").eq("email", "orbesrc@gmail.com").execute()
        if not res.data:
            admin_hash = generate_password_hash("admin123")
            supabase.table('users').insert({
                "email": "orbesrc@gmail.com",
                "password_hash": admin_hash,
                "role": "admin",
                "inst_id": None
            }).execute()
            return jsonify({"status": "success", "message": "Admin inicializado"})
        return jsonify({"status": "info", "message": "Admin ya existe"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# --- Gestión de Usuarios por Institución ---

@core_bp.route('/api/users', methods=['GET', 'POST'])
def handle_users():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    print(f"DEBUG: Fetching users for inst_id={inst_id}, program_id={program_id}")
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        if not email:
            return jsonify({"status": "error", "message": "Email requerido"})
        # Check if user exists
        existing = supabase.table('users').select("id").eq("email", email).execute()
        if existing.data:
            return jsonify({"status": "error", "message": "El usuario ya existe"}), 409
        temp_password = data.get('password', 'SIACTemp2025!')
        password_hash = generate_password_hash(temp_password)
        try:
            try:
                # Intento con todos los campos (name y program_id)
                res = supabase.table('users').insert({
                    "email": email,
                    "password_hash": password_hash,
                    "role": data.get('role', 'lider'),
                    "inst_id": inst_id,
                    "program_id": program_id,
                    "name": data.get('name', email.split('@')[0])
                }).execute()
            except Exception:
                try:
                    # Fallback sin program_id pero con name
                    res = supabase.table('users').insert({
                        "email": email,
                        "password_hash": password_hash,
                        "role": data.get('role', 'lider'),
                        "inst_id": inst_id,
                        "name": data.get('name', email.split('@')[0])
                    }).execute()
                except Exception:
                    # Fallback extremo: sin program_id y sin name
                    res = supabase.table('users').insert({
                        "email": email,
                        "password_hash": password_hash,
                        "role": data.get('role', 'lider'),
                        "inst_id": inst_id
                    }).execute()
            
            # Enviar correo de bienvenida
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
                <h2 style="color: #2563eb;">¡Bienvenido a SKEL 360!</h2>
                <p>Hola,</p>
                <p>Se ha creado una cuenta para ti en nuestra plataforma.</p>
                <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>URL de acceso:</strong> <a href="https://skel360.online/login.html">https://skel360.online/login.html</a></p>
                    <p style="margin: 5px 0;"><strong>Usuario:</strong> {email}</p>
                    <p style="margin: 5px 0;"><strong>Contraseña temporal:</strong> {temp_password}</p>
                </div>
                <p>Te recomendamos cambiar tu contraseña una vez hayas ingresado, en la sección de Configuración.</p>
                <p style="color: #64748b; font-size: 0.9em;">Saludos,<br>El equipo de SKEL 360</p>
            </div>
            """
            send_email(email, "¡Bienvenido a SKEL 360! - Tus credenciales de acceso", html_content)
            
            return jsonify({"status": "success", "data": res.data[0], "temp_password": temp_password})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    try:
        print(f"DEBUG GET: inst_id={inst_id} (type={type(inst_id)})")
        if inst_id == 0:
            res = supabase.table('users').select("*").execute()
            print(f"DEBUG GET inst_id=0: returned {len(res.data)} users")
        else:
            # Usuarios de la institución (filtramos por inst_id)
            res = supabase.table('users').select("*").eq("inst_id", inst_id).execute()
            print(f"DEBUG GET inst_id={inst_id}: returned {len(res.data)} users")
            if not res.data:
                # Try string fallback
                res_str = supabase.table('users').select("*").eq("inst_id", str(inst_id)).execute()
                print(f"DEBUG GET string fallback for inst_id={inst_id}: returned {len(res_str.data)} users")
                if res_str.data:
                    res = res_str
        
        return jsonify(res.data)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify([])


@core_bp.route('/api/users/<user_id>/reset-password', methods=['POST'])
def reset_user_password(user_id):
    data = request.json
    new_password = data.get('new_password', 'SIACTemp2025!')
    try:
        new_hash = generate_password_hash(new_password)
        supabase.table('users').update({"password_hash": new_hash}).eq("id", user_id).execute()
        return jsonify({"status": "success", "temp_password": new_password})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/users/<user_id>/activate', methods=['POST'])
def activate_user(user_id):
    data = request.json
    new_role = data.get('role', 'lider')
    try:
        # Get current user to remove [PENDING] or [ASPIRANTE] prefix
        user_res = supabase.table('users').select("name, role, email").eq("id", user_id).execute()
        if user_res.data:
            import re
            current_name = user_res.data[0].get('name', '')
            user_email = user_res.data[0].get('email', '')
            clean_name = re.sub(r'\[(?:PENDING|ASPIRANTE)[^\]]*\]\s*', '', current_name).strip()

            supabase.table('users').update({"role": new_role, "name": clean_name}).eq("id", user_id).execute()
            
            # Always update the name in lms_students if they exist and still have the prefix
            inst_id = user_res.data[0].get('inst_id', 1)
            students = formacion_storage.load_students(inst_id)
            for s in students:
                if s.get('email') == user_email:
                    s_name = s.get('name', '')
                    if '[ASPIRANTE]' in s_name or '[PENDING' in s_name:
                        s['name'] = clean_name
                        formacion_storage.save_student(inst_id, s)
        else:
            supabase.table('users').update({"role": new_role}).eq("id", user_id).execute()
            
        # Send Activation Email if we have the user data
        if user_res.data and user_email:
            try:
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
                    <h2 style="color: #2563eb;">¡Cuenta Activada Exitosamente!</h2>
                    <p>Hola <strong>{clean_name}</strong>,</p>
                    <p>¡Tenemos excelentes noticias! Tu cuenta institucional en <strong>SKEL 360</strong> ha sido aprobada y activada por un administrador del sistema.</p>
                    <p>Ya puedes acceder a la plataforma y explorar los módulos asignados a tu perfil.</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://skel360.online/login.html" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Ingresar a SKEL 360</a>
                    </div>
                    <p style="color: #64748b; font-size: 0.9em; margin-top: 40px;">Saludos cordiales,<br>El equipo de SKEL 360</p>
                </div>
                """
                send_email(user_email, "¡Tu cuenta en SKEL 360 ha sido activada!", html_content)
            except Exception as e:
                print(f"DEBUG: Error enviando correo de activacion: {e}")
                
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/users/<user_id>/role', methods=['POST'])
def change_user_role(user_id):
    """Endpoint dedicado para cambiar el rol de un usuario activo.
    Permite al superadmin (admin) delegar el rol inst_admin a un usuario
    y opcionalmente reasignarlo a una institución."""
    data = request.json
    new_role = data.get('role')
    new_inst_id = data.get('inst_id')  # Opcional: reasignar institución

    if not new_role:
        return jsonify({"status": "error", "message": "El campo 'role' es requerido."})

    # Roles válidos que se pueden asignar (no se puede asignar 'admin' desde aquí)
    allowed_roles = {'lider', 'operativo', 'inst_admin', 'estudiante', 'profesor'}
    if new_role not in allowed_roles:
        return jsonify({"status": "error", "message": f"Rol inválido. Roles permitidos: {', '.join(allowed_roles)}"})

    try:
        # Verificar que el usuario target no sea el superadmin
        target_res = supabase.table('users').select("role, name").eq("id", user_id).execute()
        if not target_res.data:
            return jsonify({"status": "error", "message": "Usuario no encontrado."})

        target_role = target_res.data[0].get('role')
        if target_role == 'admin':
            return jsonify({"status": "error", "message": "No se puede modificar el rol del Superadministrador."}), 403

        update_payload = {"role": new_role}
        # Limpiar prefijo [PENDING] si lo tiene
        current_name = target_res.data[0].get('name', '') or ''
        import re
        update_payload["name"] = re.sub(r'\[(?:PENDING|ASPIRANTE)[^\]]*\]\s*', '', current_name).strip()

        # Si se proporciona un inst_id y el rol es inst_admin, actualizar institución
        if new_inst_id is not None and new_role == 'inst_admin':
            update_payload["inst_id"] = new_inst_id

        supabase.table('users').update(update_payload).eq("id", user_id).execute()
        
        # Integrar con el módulo de formación (LMS) si el rol es docente o estudiante
        try:
            user_res = supabase.table('users').select("email, inst_id").eq("id", user_id).execute()
            if user_res.data:
                user_email = user_res.data[0].get('email', '')
                inst_id = new_inst_id if new_inst_id else user_res.data[0].get('inst_id', 1)
                
                if new_role == 'profesor':
                    teachers = formacion_storage.load_teachers(inst_id)
                    if not any(t.get('email') == user_email for t in teachers):
                        import uuid
                        new_teacher = {
                            "id": str(uuid.uuid4())[:8],
                            "name": update_payload.get("name", current_name),
                            "email": user_email,
                            "specialty": "Docente General"
                        }
                        formacion_storage.save_teacher(inst_id, new_teacher)
                elif new_role == 'estudiante':
                    students = formacion_storage.load_students(inst_id)
                    if not any(s.get('email') == user_email for s in students):
                        import uuid
                        new_student = {
                            "id": str(uuid.uuid4())[:8],
                            "name": update_payload.get("name", current_name),
                            "email": user_email
                        }
                        formacion_storage.save_student(inst_id, new_student)
        except Exception as lms_err:
            print(f"Error al integrar con LMS: {lms_err}")

        return jsonify({"status": "success", "message": f"Rol actualizado a '{new_role}' correctamente."})
    except Exception as e:
        print(f"Error al cambiar rol del usuario {user_id}: {e}")
        return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        # 1. Liberar al usuario de cualquier factor donde sea líder para evitar errores de FK
        try:
            supabase.table('factors').update({"leader_id": None}).eq("leader_id", user_id).execute()
        except Exception as e:
            print(f"Aviso al liberar líder en factores: {e}")
            
        # 2. Proceder con la eliminación del usuario
        supabase.table('users').delete().eq("id", user_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error al eliminar usuario {user_id}: {e}")
        return jsonify({"status": "error", "message": str(e)})


