from flask import Flask, render_template, request, jsonify, session, Response, send_from_directory, redirect
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import urllib.request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI
import survey_storage
import formacion_storage
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "siacredit_secret_key")
CORS(app)

from routes.crm import crm_bp
app.register_blueprint(crm_bp)


@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' data: https://fonts.gstatic.com; "
        "connect-src 'self' https://*.supabase.co https://ftpkhueqooyqvwliifzb.supabase.co wss://*.supabase.co; "
        "img-src 'self' data: https: blob:; "
        "frame-src 'self' https:; "
        "object-src 'none';"
    )
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # Prevenir cacheo del navegador para forzar actualizaciones (soluciona problemas de Vercel sirviendo versión antigua)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    
    return response

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, html_content):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_EMAIL", "orbesrc@gmail.com")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")
    
    if not smtp_pass:
        print("Advertencia: SMTP_PASSWORD no configurado. Correo no enviado.")
        return False
        
    msg = MIMEMultipart()
    msg['From'] = f"SKEL 360 <{smtp_user}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        # Usamos SMTP_SSL para el puerto 465 que es el estándar de Hostinger
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error enviando correo a {to_email}: {e}")
        return False

def get_active_inst_id(requested_id):
    try:
        # Primero intentamos ver si el ID pedido existe
        check = supabase.table('institution').select("id").eq("id", requested_id).execute()
        if check.data:
            return requested_id
        
        # Si no existe, buscamos la primera institución real disponible
        res = supabase.table('institution').select("id").limit(1).execute()
        if res.data:
            return res.data[0]['id']
    except Exception as e:
        print(f"Error resolving inst_id: {e}")
    return requested_id or 1

# Inicializar Cliente Supabase
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def force_update_gemini_config():
    try:
        config_data = json.dumps({
            "theme": "dark",
            "ai_provider": "gemini",
            "ai_model": "gemini-2.5-flash",
            "ai_api_key": ""
        })
        check = supabase.table('statistics').select("id").eq("table_id", "GLOBAL_CONFIG").order("id", desc=True).limit(1).execute()
        if check.data:
            row_id = check.data[0]['id']
            supabase.table('statistics').update({"data_json": config_data}).eq("id", row_id).execute()
        else:
            supabase.table('statistics').insert({
                "table_id": "GLOBAL_CONFIG",
                "data_json": config_data,
                "inst_id": 1,
                "program_id": 1
            }).execute()
    except Exception as e:
        print(f"Error in force_update_gemini_config: {e}")

try:
    force_update_gemini_config()
except Exception:
    pass

# Ruta de depuración para arreglar la base de datos
@app.route('/api/debug/fix-db')
def fix_db():
    try:
        # 1. Ver qué hay realmente en la base de datos
        insts = supabase.table('institution').select("*").execute().data
        
        # 2. Intentar asegurar que exista la 1 si no hay nada
        if not insts:
            supabase.table('institution').insert({
                "id": 1, "name": "CORPORACIÓN UNIVERSITARIA CENTRO SUPERIOR", "code": "UNICUCES"
            }).execute()
            insts = supabase.table('institution').select("*").execute().data
        
        return jsonify({
            "status": "success", 
            "total_instituciones": len(insts),
            "datos_reales_db": insts,
            "inst_id_que_estamos_usando": insts[0]['id'] if insts else "Ninguna"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/debug/force-update-gemini')
def route_force_update_gemini():
    try:
        config_data = json.dumps({
            "theme": "dark",
            "ai_provider": "gemini",
            "ai_model": "gemini-2.5-flash",
            "ai_api_key": ""
        })
        check = supabase.table('statistics').select("id").eq("table_id", "GLOBAL_CONFIG").order("id", desc=True).limit(1).execute()
        if check.data:
            row_id = check.data[0]['id']
            res = supabase.table('statistics').update({"data_json": config_data}).eq("id", row_id).execute()
            return jsonify({"status": "success", "action": "update", "row_id": row_id, "data": res.data})
        else:
            first_inst = supabase.table('institution').select("id").limit(1).execute()
            inst_id = first_inst.data[0]['id'] if first_inst.data else 1
            first_prog = supabase.table('programs').select("id").limit(1).execute()
            prog_id = first_prog.data[0]['id'] if first_prog.data else 1
            
            res = supabase.table('statistics').insert({
                "table_id": "GLOBAL_CONFIG",
                "data_json": config_data,
                "inst_id": inst_id,
                "program_id": prog_id
            }).execute()
            return jsonify({"status": "success", "action": "insert", "data": res.data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# --- Rutas para SEO (Indexación) ---
@app.route('/robots.txt')
def static_from_root_robots():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/sitemap.xml')
def static_from_root_sitemap():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/google3bc9f2eb5c06c742.html')
def static_from_root_google_verification():
    return send_from_directory(app.static_folder, request.path[1:])

# --- Rutas para servir las páginas HTML ---
@app.route('/')
@app.route('/index.html')
def index():
    try:
        # Fetch sin eq("inst_id", 0) porque ya no usamos 0
        res = supabase.table('statistics').select("data_json").eq("table_id", "GLOBAL_CONFIG").execute()
        config = json.loads(res.data[0]['data_json']) if res.data else {"theme": "dark"}
    except Exception:
        config = {"theme": "dark"}
    return render_template('index.html', theme=config.get('theme', 'dark'))

@app.route('/login.html')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registro.html')
@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/evidencias.html')
def evidencias():
    return render_template('evidencias.html')

@app.route('/autoevaluacion.html')
def autoevaluacion():
    return render_template('autoevaluacion.html')

@app.route('/informes.html')
def informes():
    return render_template('informes.html')

@app.route('/dofa.html')
def dofa():
    return render_template('dofa.html')

@app.route('/estadisticas.html')
def estadisticas():
    return render_template('estadisticas.html')

@app.route('/configuracion.html')
def configuracion():
    return render_template('configuracion.html')

@app.route('/formacion.html')
def formacion():
    return render_template('formacion.html')

@app.route('/biblioteca.html')
def biblioteca():
    return render_template('biblioteca.html')

# Endpoint de emergencia para recrear admin
@app.route('/api/setup-admin', methods=['GET'])
def setup_admin():
    try:
        # Crear institución si no existe
        existing = supabase.table('institution').select("id").execute().data
        if not existing:
            supabase.table('institution').insert({
                "name": "SKEL Administración", "code": "2025", "description": "Institución principal"
            }).execute()
        
        inst = supabase.table('institution').select("id").execute().data
        inst_id = inst[0]['id'] if inst else 1
        
        # Verificar si ya existe el admin
        admin_check = supabase.table('users').select("id").eq("email", "orbesrc@gmail.com").execute().data
        if admin_check:
            return jsonify({"status": "exists", "message": "El admin ya existe. Usa email: orbesrc@gmail.com"})
        
        # Crear admin con contraseña hasheada (Global Admin: inst_id = None)
        hashed = generate_password_hash("Admin2025!")
        supabase.table('users').insert({
            "email": "orbesrc@gmail.com",
            "password_hash": hashed,
            "role": "admin",
            "inst_id": None
        }).execute()
        
        return jsonify({"status": "success", "message": "Admin creado. Email: orbesrc@gmail.com / Password: Admin2025!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# --- API Endpoints con Supabase (Multi-tenant) ---

@app.route('/api/model', methods=['GET', 'POST'])
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

@app.route('/api/evaluations', methods=['GET', 'POST'])
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

@app.route('/api/evaluations/<char_id>', methods=['DELETE'])
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

@app.route('/api/planes_mejora', methods=['GET', 'POST'])
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

@app.route('/api/planes_mejora/<int:plan_id>', methods=['PUT', 'DELETE'])
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

@app.route('/api/planes_mejora/upload_soporte', methods=['POST'])
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

@app.route('/api/notificaciones', methods=['GET'])
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

@app.route('/api/notificaciones/<int:notif_id>/read', methods=['POST'])
def read_notificacion(notif_id):
    try:
        res = supabase.table('notificaciones').update({"leido": True}).eq("id", notif_id).execute()
        return jsonify({"status": "success", "data": res.data})
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/notificaciones/read-all', methods=['POST'])
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

@app.route('/api/estadisticas', methods=['GET', 'POST'])
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

@app.route('/api/programs', methods=['GET', 'POST'])
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

@app.route('/api/programs/<int:prog_id>', methods=['DELETE', 'PUT'])
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

@app.route('/api/programs/metadata', methods=['GET', 'POST'])
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

@app.route('/api/institutions', methods=['GET', 'POST'])
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

@app.route('/api/institutions/<int:inst_id>', methods=['DELETE'])
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

@app.route('/api/institutions/<int:inst_id>/suspend', methods=['POST'])
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

@app.route('/api/institution', methods=['GET', 'POST'])
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

@app.route('/api/login', methods=['POST'])
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

@app.route('/api/change-password', methods=['POST'])
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

@app.route('/api/forgot-password', methods=['POST'])
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

@app.route('/api/init-admin', methods=['GET'])
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

@app.route('/api/users', methods=['GET', 'POST'])
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


@app.route('/api/users/<user_id>/reset-password', methods=['POST'])
def reset_user_password(user_id):
    data = request.json
    new_password = data.get('new_password', 'SIACTemp2025!')
    try:
        new_hash = generate_password_hash(new_password)
        supabase.table('users').update({"password_hash": new_hash}).eq("id", user_id).execute()
        return jsonify({"status": "success", "temp_password": new_password})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/users/<user_id>/activate', methods=['POST'])
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

@app.route('/api/users/<user_id>/role', methods=['POST'])
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

@app.route('/api/users/<user_id>', methods=['DELETE'])
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


# --- Dashboard Stats ---

@app.route('/api/dashboard/stats')
def dashboard_stats():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    try:
        evidences = supabase.table('evidences').select("id, status").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        factors = supabase.table('factors').select("id").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        evals = supabase.table('evaluations').select("char_id, rating").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        
        users_query = supabase.table('users').select("id").eq("inst_id", inst_id)
        if program_id != 0:
            users_query = users_query.eq("program_id", program_id)
        users_count = users_query.execute().data

        total_ev = len(evidences)
        pending_ev = len([e for e in evidences if e['status'] == 'pendiente'])
        approved_ev = len([e for e in evidences if e['status'] == 'aprobado'])
        total_factors = len(factors)
        evaluated_factors = len(set(e['char_id'] for e in evals))
        avg_rating = round(sum(e['rating'] for e in evals) / len(evals), 2) if evals else 0
        global_progress = round((avg_rating / 5) * 100, 1) if avg_rating > 0 else 0

        return jsonify({
            "total_evidences": total_ev,
            "pending_evidences": pending_ev,
            "approved_evidences": approved_ev,
            "total_factors": total_factors,
            "evaluated_chars": evaluated_factors,
            "global_progress": global_progress,
            "total_users": len(users_count)
        })
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({"global_progress": 0, "total_evidences": 0, "pending_evidences": 0, "approved_evidences": 0, "total_factors": 0, "evaluated_chars": 0, "total_users": 0})


@app.route('/api/reports/summary')
def report_summary():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    try:
        # Traer factores con sus pesos y características
        factors = supabase.table('factors').select("*, characteristics(id, weight)").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        evals = supabase.table('evaluations').select("char_id, rating").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        eval_map = {e['char_id']: e['rating'] for e in evals}
        
        summary = []
        global_weighted_score = 0
        total_factor_weight = 0

        for f in factors:
            factor_score = 0
            # Sumar ponderación de características
            for c in f.get('characteristics', []):
                rating = eval_map.get(c['id'], 0)
                weight = c.get('weight', 0)
                factor_score += rating * (weight / 100)
            
            f_weight = f.get('weight', 0)
            global_weighted_score += factor_score * (f_weight / 100)
            total_factor_weight += f_weight

            summary.append({
                "name": f"Factor {f['number']}: {f['name']}",
                "avg": round(factor_score, 2),
                "cumplimiento": round((factor_score / 5) * 100, 1) if factor_score > 0 else 0,
                "weight": f_weight
            })
            
        return jsonify({
            "factors": summary,
            "global_avg": round(global_weighted_score, 2),
            "global_progress": round((global_weighted_score / 5) * 100, 1) if global_weighted_score > 0 else 0
        })
    except Exception as e:
        print(f"Error in summary: {e}")
        return jsonify({"factors": [], "global_avg": 0})

@app.route('/api/informe_dinamico', methods=['GET'])
def get_informe_dinamico():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    
    try:
        def safe_float(val):
            try:
                if val is None or str(val).strip() == '': return 999.0
                return float(val)
            except (ValueError, TypeError):
                return 999.0

        # 1. Traer modelo
        try:
            model_res = supabase.table('factors').select("*, characteristics(*, aspects(*))").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        except Exception:
            model_res = supabase.table('factors').select("*, characteristics(*, aspects(*))").eq("inst_id", inst_id).eq("program_id", program_id).execute()
            
        factors = model_res.data
        factors.sort(key=lambda x: safe_float(x.get('number')))
        
        # 2. Traer evaluaciones
        evals_res = supabase.table('evaluations').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        evals_map = {e['char_id']: e for e in evals_res.data}
        
        # 3. Traer evidencias
        evid_res = supabase.table('evidences').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        evid_map = {}
        for ev in evid_res.data:
            aspect_id = ev['aspect_id']
            if aspect_id not in evid_map:
                evid_map[aspect_id] = []
            evid_map[aspect_id].append(ev)
            
        # 4. Traer cuadros estadísticos (statistics)
        stats_res = supabase.table('statistics').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        stats_map = {s['table_id']: json.loads(s['data_json']) for s in stats_res.data}
        
        # 5. Traer encuestas y respuestas (para cruzar con autoevaluación)
        try:
            survey_storage.pull_from_supabase(inst_id, program_id, supabase)
        except Exception as e:
            print(f"Error pulling surveys for dynamic report: {e}")
            
        local_surveys = survey_storage.load_local_surveys(inst_id, program_id)
        local_responses = survey_storage.load_local_responses(inst_id, program_id)
        
        q_map = {}
        for s in local_surveys:
            for q in s.get('questions', []):
                q_map[q['id']] = {
                    "char_id": q.get('char_id'),
                    "aspect_id": q.get('aspect_id'),
                    "type": q.get('type')
                }
                
        char_perceptions = {}
        for r in local_responses:
            answers = r.get('answers', {})
            target = r.get('target', 'Comunidad')
            submitted_at = r.get('submitted_at', '')
            for q_id, val in answers.items():
                if q_id in q_map:
                    q_info = q_map[q_id]
                    char_id = q_info['char_id']
                    if not char_id:
                        continue
                    if char_id not in char_perceptions:
                        char_perceptions[char_id] = {
                            "rating_sum": 0.0,
                            "rating_count": 0,
                            "comments": []
                        }
                    if q_info['type'] == 'rating':
                        try:
                            val_f = float(val)
                            if 1.0 <= val_f <= 5.0:
                                char_perceptions[char_id]['rating_sum'] += val_f
                                char_perceptions[char_id]['rating_count'] += 1
                        except (ValueError, TypeError):
                            pass
                    elif q_info['type'] == 'text' and val and str(val).strip():
                        char_perceptions[char_id]['comments'].append({
                            "text": str(val).strip(),
                            "target": target,
                            "date": submitted_at[:10] if submitted_at else ''
                        })
        
        # Ensamblar datos
        report_data = {
            "institucion_id": inst_id,
            "programa_id": program_id,
            "factores": [],
            "cuadros": stats_map
        }
        
        for f in factors:
            factor_info = {
                "id": f['id'],
                "number": f.get('number', ''),
                "name": f.get('name', ''),
                "description": f.get('description', ''),
                "caracteristicas": [],
                "nota_promedio": 0,
                "cualitativo": "",
                "justificacion_general": ""
            }
            
            f_score_sum = 0
            f_score_count = 0
            f_justifications = []
            
            chars = f.get('characteristics', [])
            chars.sort(key=lambda x: safe_float(x.get('number')))
            
            for c in chars:
                c_id = c['id']
                e_data = evals_map.get(c_id, {})
                score = e_data.get('rating', 0)
                justification = e_data.get('just', '')
                
                perc = char_perceptions.get(c_id, {"rating_sum": 0.0, "rating_count": 0, "comments": []})
                avg_perc = round(perc['rating_sum'] / perc['rating_count'], 2) if perc['rating_count'] > 0 else 0.0
                
                char_info = {
                    "id": c_id,
                    "number": c.get('number', ''),
                    "name": c.get('name', ''),
                    "aspectos": [],
                    "nota_promedio": score,
                    "percepcion_promedio": avg_perc,
                    "percepcion_cantidad": perc['rating_count'],
                    "percepcion_comentarios": perc['comments']
                }
                
                if score > 0:
                    f_score_sum += score
                    f_score_count += 1
                    
                if justification:
                    f_justifications.append(justification)
                
                aspects = c.get('aspects', [])
                aspects.sort(key=lambda x: safe_float(x.get('number')))
                
                for a in aspects:
                    a_id = a['id']
                    evidencias = evid_map.get(a_id, [])
                    
                    aspect_info = {
                        "id": a_id,
                        "number": a.get('number', ''),
                        "name": a.get('name', a.get('text', '')),
                        "evidencias": [{"name": ev['name'], "file_url": ev.get('file_url', ev.get('file_path')), "period": ev.get('period', '')} for ev in evidencias]
                    }
                    char_info['aspectos'].append(aspect_info)
                
                factor_info['caracteristicas'].append(char_info)
                
            if f_score_count > 0:
                avg = round(f_score_sum / f_score_count, 2)
                factor_info['nota_promedio'] = avg
                if avg >= 4.5:
                    factor_info['cualitativo'] = "Se cumple plenamente"
                elif avg >= 4.0:
                    factor_info['cualitativo'] = "Se cumple en alto grado"
                elif avg >= 3.0:
                    factor_info['cualitativo'] = "Se cumple aceptablemente"
                elif avg > 0:
                    factor_info['cualitativo'] = "No se cumple"
                else:
                    factor_info['cualitativo'] = "Sin evaluar"
            else:
                factor_info['cualitativo'] = "Sin evaluar"
                
            # Unir justificaciones de manera simple
            factor_info['justificacion_general'] = " ".join(f_justifications[:3]) + ("..." if len(f_justifications) > 3 else "")
            
            report_data['factores'].append(factor_info)
            
        return jsonify(report_data)
    except Exception as e:
        print(f"Error informe dinamico: {e}")
        return jsonify({"error": str(e)})


def call_ai(messages, max_tokens=1500, temperature=0.7):
    import json
    provider = "zhipu"
    api_key = os.getenv("OPENAI_API_KEY", "f199cc37c8734a51bb52d58269b8ba21.qBpBccpnRN3vBsjN")
    model = "glm-4"
    
    db_error = None
    try:
        check = supabase.table('statistics').select("data_json").eq("table_id", "GLOBAL_CONFIG").order("id", desc=True).limit(1).execute()
        if check.data:
            data = json.loads(check.data[0]['data_json'])
            if data.get('ai_provider'): provider = data.get('ai_provider')
            if data.get('ai_api_key'): api_key = data.get('ai_api_key')
            if data.get('ai_model'): model = data.get('ai_model')
    except Exception as e:
        db_error = str(e)
        print(f"Error fetching AI config: {e}")

    if not api_key:
        raise Exception("La API Key de Inteligencia Artificial no está configurada.")


    if provider == 'anthropic':
        import urllib.request
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        system_text = ""
        anthropic_messages = []
        for m in messages:
            if m["role"] == "system":
                system_text += m["content"] + "\n"
            else:
                anthropic_messages.append(m)

        data = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": anthropic_messages
        }
        if system_text:
            data["system"] = system_text

        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            res_body = json.loads(response.read().decode('utf-8'))
            return res_body['content'][0]['text']
    else:
        if provider == 'openai':
            base_url = "https://api.openai.com/v1/"
        elif provider == 'gemini':
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        else:
            base_url = "https://open.bigmodel.cn/api/paas/v4/"
        
        client = OpenAI(api_key=api_key, base_url=base_url)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"{str(e)} [DEBUG: provider={provider}, base_url={base_url}, rows={len(check.data) if 'check' in locals() else 'unknown'}, db_error={db_error}]")



@app.route('/api/analyze', methods=['POST'])
def analyze_stats():
    req_data = request.json
    table_id = req_data.get('table_id')
    all_data = req_data.get('all_data', {})
    
    try:
        if table_id:
            data_context = json.dumps(all_data.get(table_id, []), ensure_ascii=False)
            prompt = f"Actúa como un evaluador experto y consultor analítico de alto nivel. Analiza de manera formal y rigurosa los siguientes datos estadísticos del cuadro '{table_id}' e identifica tendencias, fortalezas o aspectos críticos. Emplea un lenguaje técnico y académico. Responde directamente con el análisis en formato Markdown. Datos: {data_context}"
        else:
            data_context = json.dumps(all_data, ensure_ascii=False)
            if len(data_context) > 30000:
                data_context = data_context[:30000] + "... [truncado]"
            prompt = f"Actúa como un evaluador experto y consultor analítico de alto nivel. Analiza de manera formal, integral y rigurosa los siguientes cuadros de datos estadísticos institucionales. Resalta los aspectos más importantes, tendencias globales y posibles oportunidades de mejora. Emplea un lenguaje técnico y académico. Responde directamente con el análisis en formato Markdown. Datos: {data_context}"

        answer = call_ai(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1500
        )
        
        safe_answer = answer.replace('<', '&lt;').replace('>', '&gt;')
        return jsonify({"analysis": safe_answer})
    except Exception as e:
        print(f"Error AI Analysis: {e}")
        return jsonify({"analysis": f"Error procesando análisis: {str(e)}"})

@app.route('/api/direct_upload/url', methods=['POST'])
def library_upload_url():
    try:
        data = request.json
        filename = data.get('filename')
        aspect_id = data.get('aspect_id')
        period = data.get('period', 'Biblioteca')
        
        inst_id = data.get('inst_id', 1)
        program_id = data.get('program_id', 0)
        
        if not inst_id or inst_id == 0:
            first_inst = supabase.table('institution').select("id").limit(1).execute()
            inst_id = first_inst.data[0]['id'] if first_inst.data else 1
            
        import re
        import time
        clean_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Append timestamp to avoid 'Duplicate resource' 400 error on PUT
        timestamp = int(time.time())
        parts = clean_filename.rsplit('.', 1)
        if len(parts) == 2:
            clean_filename = f"{parts[0]}_{timestamp}.{parts[1]}"
        else:
            clean_filename = f"{clean_filename}_{timestamp}"
        
        # Consistent path logic with original API
        file_path = f"inst_{inst_id}/prog_{program_id}/{aspect_id}/{period}/{clean_filename}"
        
        res = supabase.storage.from_('evidencias').create_signed_upload_url(file_path)
        signed_url = res.get('signedUrl')
        
        # Public URL to access the file later
        file_url = supabase.storage.from_('evidencias').get_public_url(file_path)
        
        return jsonify({
            "status": "success",
            "signed_url": signed_url,
            "file_url": file_url,
            "file_path": file_path
        })
    except Exception as e:
        print(f"Error generating upload url: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/library/confirm_upload', methods=['POST'])
def library_confirm_upload():
    try:
        data = request.json
        aspect_id = data.get('aspect_id')
        filename = data.get('filename')
        file_url = data.get('file_url')
        inst_id = data.get('inst_id', 1)
        program_id = data.get('program_id', 0)

        if not inst_id or inst_id == 0:
            first_inst = supabase.table('institution').select("id").limit(1).execute()
            inst_id = first_inst.data[0]['id'] if first_inst.data else 1
            
        if not program_id or program_id == 0:
            first_prog = supabase.table('programs').select("id").limit(1).execute()
            program_id = first_prog.data[0]['id'] if first_prog.data else 1

        import time
        doc_record = {
            "id": int(time.time() * 1000),
            "name": filename,
            "file_url": file_url,
            "aspect_id": aspect_id
        }
        
        query = supabase.table('statistics').select("id, data_json").eq("table_id", aspect_id)
        if aspect_id != 'BIBLIOTECA_GLOBAL':
            query = query.eq("inst_id", inst_id)
        
        check = query.execute()
        if check.data:
            current_data = json.loads(check.data[0]['data_json'])
            if not isinstance(current_data, list): current_data = []
            current_data.append(doc_record)
            supabase.table('statistics').update({"data_json": json.dumps(current_data)}).eq("id", check.data[0]["id"]).execute()
        else:
            supabase.table('statistics').insert({
                "table_id": aspect_id,
                "data_json": json.dumps([doc_record]),
                "inst_id": inst_id,
                "program_id": program_id
            }).execute()

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error confirm upload: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/evidences/confirm_upload', methods=['POST'])
def evidences_confirm_upload():
    try:
        data = request.json
        aspect_id = data.get('aspect_id')
        filename = data.get('filename')
        file_url = data.get('file_url')
        period = data.get('period', 'N/A')
        email = data.get('email', 'unknown')
        is_annex = data.get('is_annex', False)
        
        inst_id = data.get('inst_id', 1)
        program_id = data.get('program_id', 0)

        if not inst_id or inst_id == 0:
            first_inst = supabase.table('institution').select("id").limit(1).execute()
            inst_id = first_inst.data[0]['id'] if first_inst.data else 1

        # Generar "dependency" extraído del aspect_id (e.g. FACTOR_1 -> 1)
        import re
        match = re.search(r'\d+', str(aspect_id))
        dependency = match.group() if match else "1"

        # Siempre insertamos como una nueva evidencia para permitir múltiples adjuntos (y diferentes años)
        insert_data = {
            "name": filename,
            "file_url": file_url,
            "period": period,
            "dependency": dependency,
            "aspect_id": aspect_id,
            "user_email": email,
            "status": "pendiente",
            "inst_id": inst_id,
            "program_id": program_id
        }
        if is_annex:
            insert_data['is_annex'] = True
        supabase.table('evidences').insert(insert_data).execute()

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error confirm evidences upload: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/surveys/upload', methods=['POST'])
def survey_upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    survey_id = request.form.get('survey_id', 'unknown')
    
    import re
    import time
    clean_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
    timestamp = int(time.time())
    parts = clean_filename.rsplit('.', 1)
    if len(parts) == 2:
        clean_filename = f"{parts[0]}_{timestamp}.{parts[1]}"
    else:
        clean_filename = f"{clean_filename}_{timestamp}"
        
    file_path = f"surveys/{survey_id}/{clean_filename}"
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
        print(f"Error uploading survey file: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    inst_id = request.form.get('inst_id', 1, type=int)
    program_id = request.form.get('program_id', 0, type=int)
    
    # Validar y corregir inst_id si es 0 o None para evitar errores de llave foránea
    if not inst_id or inst_id == 0:
        try:
            first_inst = supabase.table('institution').select("id").limit(1).execute()
            inst_id = first_inst.data[0]['id'] if first_inst.data else 1
        except Exception as e:
            print(f"Error fetching fallback institution: {e}")
            inst_id = 1

    # Validar y corregir program_id si es 0 o None para evitar errores de llave foránea
    if not program_id or program_id == 0:
        try:
            first_prog = supabase.table('programs').select("id").limit(1).execute()
            program_id = first_prog.data[0]['id'] if first_prog.data else 1
        except Exception as e:
            print(f"Error fetching fallback program: {e}")
            program_id = 1

    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    aspect_id = request.form.get('aspect_id')
    period = request.form.get('period', 'General')
    email = request.form.get('email')
    dependency = request.form.get('dependency', 'General')

    def sanitize_filename(filename):
        import re
        name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        return name

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    clean_filename = sanitize_filename(file.filename)
    # Nueva ruta incluyendo el periodo para evitar colisiones
    file_path = f"inst_{inst_id}/prog_{program_id}/{aspect_id}/{period}/{clean_filename}"
    try:
        file_content = file.read()
        supabase.storage.from_('evidencias').upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": file.content_type, "upsert": "true"}
        )
        file_url = supabase.storage.from_('evidencias').get_public_url(file_path)
        
        # Solo guardar en la tabla evidences si es un aspecto real (no una estadística)
        if aspect_id:
            if str(aspect_id).startswith('STAT_'):
                pass
            elif str(aspect_id).startswith('BIBLIOTECA_'):
                import time
                doc_record = {
                    "id": int(time.time() * 1000),
                    "name": file.filename,
                    "file_url": file_url,
                    "aspect_id": aspect_id
                }
                query = supabase.table('statistics').select("id, data_json").eq("table_id", aspect_id)
                if aspect_id != 'BIBLIOTECA_GLOBAL':
                    query = query.eq("inst_id", inst_id)
                
                check = query.execute()
                if check.data:
                    current_data = json.loads(check.data[0]['data_json'])
                    if not isinstance(current_data, list): current_data = []
                    current_data.append(doc_record)
                    supabase.table('statistics').update({"data_json": json.dumps(current_data)}).eq("id", check.data[0]["id"]).execute()
                else:
                    # Usar inst_id válido actual para evitar errores de llave foránea (inst_id=0 no existe)
                    save_inst_id = inst_id
                    
                    # Obtener un program_id válido
                    first_prog = supabase.table('programs').select("id").limit(1).execute()
                    save_prog_id = first_prog.data[0]['id'] if first_prog.data else 1
                    
                    supabase.table('statistics').insert({
                        "table_id": aspect_id,
                        "data_json": json.dumps([doc_record]),
                        "inst_id": save_inst_id,
                        "program_id": save_prog_id
                    }).execute()
            else:
                supabase.table('evidences').insert({
                    "aspect_id": aspect_id,
                    "name": file.filename,
                    "file_url": file_url,
                    "user_email": email,
                    "dependency": dependency,
                    "status": "pendiente",
                    "period": period,
                    "inst_id": inst_id,
                    "program_id": program_id
                }).execute()
            
        return jsonify({"status": "success", "url": file_url})
    except Exception as e:
        print(f"Error uploading: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/evidences', methods=['GET'])
def get_evidences():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    aspect_id = request.args.get('aspect_id')
    query = supabase.table('evidences').select("*").eq("inst_id", inst_id).eq("program_id", program_id)
    if aspect_id:
        query = query.eq("aspect_id", aspect_id)
    res = query.execute()
    return jsonify(res.data)

@app.route('/api/library', methods=['GET'])
def get_library():
    inst_id = request.args.get('inst_id', 1, type=int)
    try:
        global_res = supabase.table('statistics').select("data_json").eq("table_id", "BIBLIOTECA_GLOBAL").execute()
        global_docs = json.loads(global_res.data[0]['data_json']) if global_res.data else []
        
        inst_res = supabase.table('statistics').select("data_json").eq("table_id", "BIBLIOTECA_INST").eq("inst_id", inst_id).execute()
        inst_docs = json.loads(inst_res.data[0]['data_json']) if inst_res.data else []
        
        return jsonify({
            "global": global_docs,
            "institucional": inst_docs
        })
    except Exception as e:
        print(f"Error loading library: {e}")
        return jsonify({"global": [], "institucional": []})

@app.route('/api/library/<aspect_id>/<int:doc_id>', methods=['DELETE'])
def delete_library_doc(aspect_id, doc_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    # Global puede no tener inst_id, pero para buscar en statistics usamos inst_id si no es global
    query = supabase.table('statistics').select("id, data_json").eq("table_id", aspect_id)
    if aspect_id != 'BIBLIOTECA_GLOBAL':
        query = query.eq("inst_id", inst_id)
    
    try:
        check = query.execute()
        if check.data:
            current_data = json.loads(check.data[0]['data_json'])
            # Filtrar el doc a borrar
            new_data = [d for d in current_data if d.get('id') != doc_id]
            supabase.table('statistics').update({"data_json": json.dumps(new_data)}).eq("id", check.data[0]["id"]).execute()
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "No encontrado"})
    except Exception as e:
        print(f"Error deleting library doc: {e}")
        return jsonify({"status": "error", "message": str(e)})


import urllib.request
import urllib.parse
import urllib.error
import json

@app.route('/api/library/search', methods=['GET'])
def library_search():
    q = request.args.get('q', '')
    limit = request.args.get('limit', 20)
    
    if 'filetype:pdf' in q.lower():
        try:
            print(f"Searching Europe PMC for: {q}")
            clean_q = q.lower().replace('filetype:pdf', '').strip()
            epmc_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={urllib.parse.quote(clean_q)}+HAS_PDF:y&format=json&resultType=core&pageSize={limit}"
            epmc_req = urllib.request.Request(epmc_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(epmc_req) as response:
                epmc_data = json.loads(response.read().decode('utf-8'))
                results = []
                for item in epmc_data.get('resultList', {}).get('result', []):
                    title = item.get('title', 'Sin título')
                    year = item.get('pubYear', 'S.F.')
                    
                    author_string = item.get('authorString', '')
                    authorships = [{'author': {'display_name': a.strip()}} for a in author_string.split(',')] if author_string else [{'author': {'display_name': 'Autor Desconocido'}}]
                    
                    pdf_url = ''
                    for u in item.get('fullTextUrlList', {}).get('fullTextUrl', []):
                        if u.get('documentStyle') == 'pdf':
                            pdf_url = u.get('url')
                            break
                            
                    doi = item.get('doi', '')
                    
                    results.append({
                        'id': item.get('id', f"epmc_{len(results)}"),
                        'title': title,
                        'publication_year': year,
                        'authorships': authorships,
                        'primary_location': {'source': {'display_name': item.get('journalTitle', 'Europe PMC')}},
                        'doi': f"https://doi.org/{doi}" if doi else '',
                        'open_access': {'oa_url': pdf_url},
                        'type': 'pdf'
                    })
                return jsonify({'results': results, 'meta': {'source': 'europepmc'}})
        except Exception as e:
            print(f"Europe PMC scrape error: {e}")
            return jsonify({'error': 'Error al buscar PDFs en Europe PMC.'})

    try:
        q = request.args.get('q', '')
        limit = request.args.get('limit', '20')
        if not limit.isdigit():
            limit = '20'
        if int(limit) > 100:
            limit = '100'
            
        if not q:
            return jsonify({'results': []})
        
        # Prepare the OpenAlex API URL with has_pdf_url:true and user limit
        url = f"https://api.openalex.org/works?search={urllib.parse.quote(q)}&filter=is_oa:true,has_pdf_url:true&per-page={limit}"
        
        mailto = os.environ.get('OPENALEX_MAILTO', 'orbesrc@gmail.com')
        api_key = os.environ.get('OPENALEX_API_KEY')
        url += f"&mailto={urllib.parse.quote(mailto)}"
        if api_key:
            url += f"&api_key={api_key}"
            
        req = urllib.request.Request(url, headers={'User-Agent': f'SIACredit/1.0 (mailto:{mailto})'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return jsonify(data)
    except urllib.error.HTTPError as e:
        print(f"OpenAlex HTTP Error: {e.code} - {e.reason}")
        if e.code in [429, 503]:
            try:
                print("Falling back to Crossref API...")
                cr_url = f"https://api.crossref.org/works?query={urllib.parse.quote(q)}&select=title,author,URL,published-print,published-online,DOI,container-title,type,link&rows={limit}"
                cr_req = urllib.request.Request(cr_url, headers={'User-Agent': f'SIACredit/1.0 (mailto:{mailto})'})
                with urllib.request.urlopen(cr_req) as cr_res:
                    cr_data = json.loads(cr_res.read().decode('utf-8'))
                    
                results = []
                for item in cr_data.get('message', {}).get('items', []):
                    title = item.get('title', ['Sin título'])[0]
                    year = None
                    for date_field in ['published-print', 'published-online']:
                        if date_field in item and 'date-parts' in item[date_field] and item[date_field]['date-parts']:
                            year = item[date_field]['date-parts'][0][0]
                            break
                    
                    authorships = []
                    for a in item.get('author', []):
                        display_name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                        if display_name:
                            authorships.append({'author': {'display_name': display_name}})
                            
                    source_name = item.get('container-title', [''])[0]
                    if not source_name:
                        source_name = item.get('publisher', 'Publicación Independiente')
                        
                    doi = item.get('URL', '')
                    pdf_url = ""
                    for link in item.get('link', []):
                        if link.get('content-type') == 'application/pdf':
                            pdf_url = link.get('URL')
                            break
                            
                    results.append({
                        'title': title,
                        'publication_year': year,
                        'authorships': authorships,
                        'primary_location': {'source': {'display_name': source_name}},
                        'doi': doi,
                        'open_access': {'oa_url': pdf_url} if pdf_url else {},
                        'type': item.get('type', 'article')
                    })
                return jsonify({'results': results, 'fallback': 'crossref'})
            except Exception as cr_err:
                print(f"Crossref fallback failed: {cr_err}")
                return jsonify({'error': 'La red académica global está experimentando alta demanda en este momento. Por favor, intenta de nuevo en unos minutos.'}), 503
        return jsonify({'error': str(e)}), e.code
    except Exception as e:
        print(f"Error fetching OpenAlex: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/library/translate', methods=['POST'])
def library_translate():
    try:
        data = request.json
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'es') # 'es' o 'en'
        
        if not text:
            return jsonify({"status": "error", "message": "Texto vacío"})
            
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            translated_text = ''.join([sentence[0] for sentence in data[0] if sentence[0]])
            
        return jsonify({"status": "success", "translated": translated_text.strip()})
    except Exception as e:
        print(f"Error Translate: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route('/api/library/ovas', methods=['GET'])
def get_ovas():
    try:
        url = "https://phet.colorado.edu/services/metadata/1.2/simulations?format=json&type=html&locale=es"
        req = urllib.request.Request(url, headers={'User-Agent': 'SIACredit/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            sims = []
            for proj in data.get('projects', []):
                for sim in proj.get('simulations', []):
                    title = sim.get('title', 'Sin título')
                    if 'es' in sim.get('localizedTitles', {}):
                        title = sim['localizedTitles']['es']
                    elif 'en' in sim.get('localizedTitles', {}):
                        title = sim['localizedTitles']['en']
                        
                    sims.append({
                        'id': sim.get('name', ''),
                        'title': title,
                        'description': sim.get('description', {}).get('es', sim.get('description', {}).get('en', 'Simulador interactivo PhET')),
                        'runUrl': f"https://phet.colorado.edu/sims/html/{sim.get('name')}/latest/{sim.get('name')}_es.html",
                        'thumbUrl': f"https://phet.colorado.edu/sims/html/{sim.get('name')}/latest/{sim.get('name')}-600.png"
                    })
            
            # Sort by title
            sims.sort(key=lambda x: x['title'])
            return jsonify({'status': 'success', 'ovas': sims})
    except Exception as e:
        print(f"Error fetching OVAs: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/library/saved', methods=['GET', 'POST'])


def handle_saved_resources():
    if request.method == 'POST':
        data = request.json
        user_email = data.get('email')
        if not user_email:
            return jsonify({"status": "error", "message": "Email requerido"})
            
        try:
            supabase.table('saved_resources').insert({
                "user_email": user_email,
                "resource_id": data.get('resource_id'),
                "title": data.get('title'),
                "authors": data.get('authors', ''),
                "year": data.get('year'),
                "url": data.get('url', ''),
                "apa_citation": data.get('apa_citation', '')
            }).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            print(f"Error saving resource: {e}")
            return jsonify({"status": "error", "message": str(e)})
            
    # GET
    user_email = request.args.get('email')
    if not user_email:
        return jsonify([])
    try:
        res = supabase.table('saved_resources').select('*').eq('user_email', user_email).order('saved_at', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        print(f"Error fetching saved resources: {e}")
        return jsonify([])

@app.route('/api/library/saved/<int:id>', methods=['DELETE'])
def delete_saved_resource(id):
    try:
        supabase.table('saved_resources').delete().eq('id', id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error deleting saved resource: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/global-settings', methods=['GET', 'POST'])
def global_settings():
    try:
        check = supabase.table('statistics').select("id, data_json").eq("table_id", "GLOBAL_CONFIG").order("id", desc=True).limit(1).execute()
        current_data = {}
        row_id = None
        if check.data:
            row_id = check.data[0]['id']
            try:
                current_data = json.loads(check.data[0]['data_json'])
            except:
                pass

        if request.method == 'GET':
            # Remove api_key for security when sending to frontend, but send a flag that it exists
            resp_data = dict(current_data)
            resp_data['has_api_key'] = 'ai_api_key' in resp_data and bool(resp_data['ai_api_key'].strip())
            if 'ai_api_key' in resp_data:
                del resp_data['ai_api_key'] # Hide actual key from frontend
            return jsonify(resp_data)

        # POST
        data = request.json
        if 'theme' in data: current_data['theme'] = data.get('theme')
        if 'ai_provider' in data: current_data['ai_provider'] = data.get('ai_provider')
        if 'ai_model' in data: current_data['ai_model'] = data.get('ai_model')
        if 'ai_api_key' in data: current_data['ai_api_key'] = data.get('ai_api_key')
        
        config_data = json.dumps(current_data)
        
        if row_id:
            supabase.table('statistics').update({"data_json": config_data}).eq("id", row_id).execute()
        else:
            first_inst = supabase.table('institution').select("id").limit(1).execute()
            valid_inst_id = first_inst.data[0]['id'] if first_inst.data else 1
            
            first_prog = supabase.table('programs').select("id").limit(1).execute()
            valid_prog_id = first_prog.data[0]['id'] if first_prog.data else 1
            
            supabase.table('statistics').insert({
                "table_id": "GLOBAL_CONFIG",
                "data_json": config_data,
                "inst_id": valid_inst_id,
                "program_id": valid_prog_id
            }).execute()
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/evidences/<int:evidence_id>', methods=['DELETE'])
def delete_evidence(evidence_id):
    try:
        supabase.table('evidences').delete().eq("id", evidence_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error deleting evidence: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/evidences/status', methods=['POST'])
def update_evidence_status():
    data = request.json
    try:
        supabase.table('evidences').update({
            "status": data['status']
        }).eq("id", data['id']).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error updating status: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/proxy/external_pdf', methods=['GET'])
def proxy_external_pdf():
    file_url = request.args.get('url', '')
    if not file_url:
        return jsonify({'error': 'URL requerida'})
    try:
        import urllib.request
        import urllib.parse
        
        # Ensure the URL is properly encoded if it contains spaces
        parsed = urllib.parse.urlparse(file_url)
        safe_path = urllib.parse.quote(parsed.path, safe='/:@%')
        safe_url = parsed._replace(path=safe_path).geturl()
        
        req = urllib.request.Request(safe_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            return Response(data, mimetype='application/pdf', headers={
                'Content-Disposition': 'inline; filename="documento.pdf"',
                'Access-Control-Allow-Origin': '*'
            })
    except Exception as e:
        print(f"Error proxying external PDF: {e}")
        # If it fails, fallback by redirecting to the URL so at least it opens
        return redirect(file_url)

@app.route('/api/download')
def proxy_download():
    """Proxy file download from Supabase Storage with correct filename and Content-Disposition."""
    file_url = request.args.get('url', '')
    file_name = request.args.get('name', 'archivo')
    if not file_url:
        return jsonify({'error': 'URL requerida'})
    try:
        import urllib.parse
        import mimetypes
        # Safe encoding for URL in case it has spaces or special characters
        parsed = urllib.parse.urlparse(file_url)
        # Use safe='/:@%' to avoid double-encoding already-encoded chars
        safe_path = urllib.parse.quote(parsed.path, safe='/:@%')
        safe_url = parsed._replace(path=safe_path).geturl()
        
        req = urllib.request.Request(safe_url, headers={'User-Agent': 'SIACredit/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            content_type = resp.headers.get('Content-Type', 'application/octet-stream')
            # Strip charset and params from content type for clean mimetype
            content_type_clean = content_type.split(';')[0].strip()
        import io
        from flask import send_file

        # Siempre extraer el nombre real del archivo desde la URL de Supabase
        # El path de la URL contiene el nombre original con extensión
        parsed_url = urllib.parse.urlparse(file_url)
        # Obtener solo la última parte del path (sin query string, usando path no query)
        url_path_basename = urllib.parse.unquote(parsed_url.path.split('/')[-1])
        
        # Si el nombre recibido no tiene extensión o es genérico, usar el de la URL
        if not file_name or '.' not in file_name or file_name in ('evidencia', 'archivo'):
            if url_path_basename and '.' in url_path_basename:
                file_name = url_path_basename
            else:
                # Como último recurso, derivar extensión del content-type
                ext = mimetypes.guess_extension(content_type_clean) or ''
                # mimetypes puede dar .jpe en vez de .jpg, normalizar
                ext_map = {'.jpe': '.jpg', '.jpeg': '.jpg', '.htm': '.html'}
                ext = ext_map.get(ext, ext)
                file_name = (file_name or 'archivo') + ext
        else:
            # El nombre tiene extensión; si el de la URL tiene extensión diferente, priorizar la URL
            if url_path_basename and '.' in url_path_basename:
                url_ext = url_path_basename.rsplit('.', 1)[-1].lower()
                name_ext = file_name.rsplit('.', 1)[-1].lower()
                if url_ext != name_ext and url_ext:
                    # Reemplazar la extensión con la correcta según la URL del storage
                    file_name = file_name.rsplit('.', 1)[0] + '.' + url_ext

        return send_file(
            io.BytesIO(data),
            mimetype=content_type_clean,
            as_attachment=True,
            download_name=file_name
        )
    except Exception as e:
        print(f'Error proxying download: {e}')
        return jsonify({'error': str(e)})

# --- Rutas de Inteligencia Artificial ---

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.json
    question = data.get('question', '')
    file_url = data.get('file_url', '')

    try:
        # Extraer texto del archivo si se proporciona
        file_context = ""
        if file_url:
            try:
                import urllib.request
                import tempfile
                import os
                
                req = urllib.request.Request(file_url, headers={'User-Agent': 'SIACredit/1.0'})
                with urllib.request.urlopen(req, timeout=30) as response:
                    file_bytes = response.read()
                    
                    if file_url.lower().split('?')[0].endswith('.pdf'):
                        import PyPDF2
                        import io
                        pdf = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                        text = ""
                        for page in pdf.pages:
                            text += page.extract_text() + "\n"
                        file_context = text
                    elif file_url.lower().split('?')[0].endswith('.docx'):
                        import docx2txt
                        import io
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                            tmp.write(file_bytes)
                            tmp_path = tmp.name
                        file_context = docx2txt.process(tmp_path)
                        os.unlink(tmp_path)
                    else:
                        file_context = file_bytes.decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"Error parsing attached file: {e}")
                file_context = f"[Error al leer el archivo adjunto: {e}]"

        system_prompt = (
            "Te llamas Margy. Eres una asistente experta en evaluación y aseguramiento de alta calidad "
            "para organizaciones, instituciones educativas y empresas, desarrollada por SKEL. "
            "Responde de manera formal, académica, profesional y analítica basándote en altos estándares "
            "de calidad. Si te preguntan cómo te llamas o quién eres, responde que te llamas "
            "Margy, la asistente de evaluación de SKEL."
        )
        
        final_prompt = question
        if file_context:
            if len(file_context) > 20000:
                file_context = file_context[:20000] + "... [texto truncado]"
            final_prompt = f"El usuario ha adjuntado un documento con el siguiente contenido:\n\n{file_context}\n\nPregunta del usuario: {question if question else 'Resume el documento o extrae los aspectos clave para la acreditación.'}"

        answer = call_ai(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return jsonify({"status": "success", "answer": answer})
    except Exception as e:
        print(f"Error AI Chat: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/ai/generate_report', methods=['POST'])
def ai_generate_report():
    data = request.json
    report_data = data.get('report_data', {})
    
    try:
        # Convert report_data to string but limit its size to avoid context length limits
        data_str = json.dumps(report_data, ensure_ascii=False)
        if len(data_str) > 30000:
            data_str = data_str[:30000] + "... [Datos truncados]"

        prompt = f"""
        Actúa como un evaluador experto y consultor analítico de alto nivel.
        A continuación se te provee un JSON con la información de la evaluación de una organización, institución o programa académico.
        Incluye calificaciones de autoevaluación, justificaciones, evidencias documentales adjuntas y referencias a cuadros estadísticos,
        así como resultados cualitativos y cuantitativos de encuestas aplicadas, en caso de existir.
        
        JSON de Evaluación:
        {data_str}

        Por favor, redacta un informe ejecutivo y analítico exhaustivo en formato Markdown estructurado.
        Estructura obligatoria del informe:
        # Informe de Evaluación Analítica Integral
        ## 1. Introducción y Apreciación General
        ## 2. Análisis Detallado por Factores
        (Para cada factor o dimensión, DEBES triangular y analizar conjuntamente los siguientes 4 elementos, si están disponibles:
        1. **Autoevaluación**: Resultados y justificaciones declaradas.
        2. **Evidencias**: Nivel de soporte documental referenciado.
        3. **Estadísticas**: Datos, cifras y cuadros estadísticos asociados.
        4. **Encuestas**: En caso de existir, contrasta la percepción (promedios y comentarios) con la autoevaluación.
        Identifica de manera rigurosa las fortalezas y oportunidades de mejora basándote en la articulación de estos 4 elementos).
        ## 3. Conclusiones
        ## 4. Recomendaciones Estratégicas y Plan de Mejoramiento
        
        Escribe de forma formal, propositiva, con un lenguaje técnico, académico u organizacional avanzado, basado estrictamente en los datos provistos.
        """
        
        report_text = call_ai(
            messages=[
                {"role": "system", "content": "Eres un redactor experto de informes analíticos institucionales y organizacionales de alto nivel."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        return jsonify({"status": "success", "report": report_text})
    except Exception as e:
        print(f"Error AI Generate Report: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/ai/generate_dofa', methods=['POST'])
def ai_generate_dofa():
    data = request.json
    report_text = data.get('report_text', '')
    
    try:
        # Limitar tamaño si es excesivamente largo
        if len(report_text) > 40000:
            report_text = report_text[:40000] + "... [Texto truncado]"

        prompt = f"""
        Actúa como un analista experto en planeación estratégica institucional.
        Se te proporciona el Informe Parcial/Total de Autoevaluación de un programa académico.
        Tu tarea es determinar cuáles son las Fortalezas y Debilidades (Factores Internos) del programa basándote EXCLUSIVAMENTE en el texto provisto.
        
        Debes clasificar y priorizar estos factores de mayor a menor nivel de importancia.
        Utiliza estrictamente el formato D1, D2, D3... para las Debilidades y F1, F2, F3... para las Fortalezas, donde el número 1 es el más importante y crítico.
        Pueden diferenciarse en cantidad (p.ej. 5 Fortalezas y 3 Debilidades, o viceversa, extrae las más relevantes).
        
        Texto del Informe:
        {report_text}
        
        Debes devolver tu respuesta ESTRICTAMENTE en formato JSON válido, con la siguiente estructura:
        {{
            "fortalezas": [
                {{"id": "F1", "descripcion": "Descripción concisa...", "importancia": 1}}
            ],
            "debilidades": [
                {{"id": "D1", "descripcion": "Descripción concisa...", "importancia": 1}}
            ]
        }}
        Devuelve únicamente el texto JSON y NADA MÁS.
        """
        
        dofa_res = call_ai(
            messages=[
                {"role": "system", "content": "Eres un asistente experto que solo devuelve estructuras JSON puras y válidas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2500
        )
        
        # Limpieza básica por si el LLM incluye formato de bloque de código
        dofa_res = dofa_res.replace('```json', '').replace('```', '').strip()
        
        try:
            dofa_json = json.loads(dofa_res)
        except:
            dofa_json = {"fortalezas": [], "debilidades": [], "error_parseo": "El formato generado no fue un JSON válido."}
            
        return jsonify({"status": "success", "dofa": dofa_json})
    except Exception as e:
        print(f"Error AI Generate DOFA: {e}")
        return jsonify({"error": str(e)})


@app.route('/api/ai/generate_pesta', methods=['POST'])
def ai_generate_pesta():
    data = request.json
    inst_id = data.get('inst_id')
    program_id = data.get('program_id')
    contexto_espacial = data.get('contexto', 'Colombia')
    
    try:
        # Cargar metadatos del programa para el contexto
        meta_table = f"PROGRAM_METADATA_{program_id}"
        meta_res = supabase.table('statistics').select("data_json").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", meta_table).execute()
        meta_str = ""
        if meta_res.data:
            meta_str = "Metadatos del programa/institución: " + str(meta_res.data[0]['data_json'])

        prompt = f'''
        Actúa como un experto en planeación estratégica institucional.
        Debes realizar un barrido referencial y análisis PESTA (Político, Económico, Social, Tecnológico, Ambiental) para la institución y su respectivo campo disciplinar.
        
        Contexto espacial de evaluación: {contexto_espacial} (si se pide regional o internacional, enfócate en ese alcance geográfico).
        Información y contexto disciplinar del programa:
        {meta_str}
        
        Tu tarea es generar un informe PESTA secuencial enfocado en las tendencias del sector educativo/organizacional y disciplinar.
        A partir de este análisis PESTA, debes extraer y listar claramente las Oportunidades (O) y Amenazas (A) que afectan directamente a la institución.
        
        Debes devolver tu respuesta ESTRICTAMENTE en formato JSON válido, con la siguiente estructura:
        {{
            "informe_pesta": "# Análisis PESTA y Barrido Referencial\\n\\n## Político\\n...\\n\\n## Económico\\n...",
            "oportunidades": [
                {{"id": "O1", "descripcion": "Descripción concisa...", "importancia": 1}}
            ],
            "amenazas": [
                {{"id": "A1", "descripcion": "Descripción concisa...", "importancia": 1}}
            ]
        }}
        Prioriza los factores en 'importancia' de 1 a N, siendo 1 el más crítico.
        Asegúrate de escapar correctamente los saltos de línea (\\\\n) dentro del campo string 'informe_pesta' para que el JSON sea válido.
        Devuelve únicamente el texto JSON y NADA MÁS.
        '''
        
        pesta_res = call_ai(
            messages=[
                {"role": "system", "content": "Eres un asistente experto que solo devuelve estructuras JSON puras y válidas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=4000
        )
        
        # Limpieza básica
        pesta_res = pesta_res.replace('```json', '').replace('```', '').strip()
        
        try:
            pesta_json = json.loads(pesta_res)
        except Exception as e_json:
            print("Error parsing PESTA JSON:", str(e_json), "Raw Output:", pesta_res[:200])
            pesta_json = {"informe_pesta": "# Error\\nNo se pudo generar el formato correcto.", "oportunidades": [], "amenazas": [], "error_parseo": "El formato generado no fue un JSON válido."}
            
        return jsonify({"status": "success", "pesta": pesta_json})
    except Exception as e:
        print(f"Error AI Generate PESTA: {e}")
        return jsonify({"error": str(e)})


@app.route('/api/ai/cruce_dofa', methods=['POST'])
def ai_cruce_dofa():
    data = request.json
    fortalezas = data.get('fortalezas', [])
    debilidades = data.get('debilidades', [])
    oportunidades = data.get('oportunidades', [])
    amenazas = data.get('amenazas', [])
    
    try:
        prompt = f"""
        Actúa como un Doctor en Planeación Estratégica Gerencial y Académica.
        Se te proporcionan los factores internos (F, D) y externos (O, A) de un proceso de diagnóstico de una institución o programa académico:
        
        FORTALEZAS: {json.dumps(fortalezas, ensure_ascii=False)}
        DEBILIDADES: {json.dumps(debilidades, ensure_ascii=False)}
        OPORTUNIDADES: {json.dumps(oportunidades, ensure_ascii=False)}
        AMENAZAS: {json.dumps(amenazas, ensure_ascii=False)}
        
        Realiza el Cruce Estratégico (Matriz TOWS / DOFA) para generar estrategias maestras de alto impacto.
        NO te limites a un número algorítmico o fijo de estrategias (como 2 por cada cuadrante). 
        Analiza profundamente la interacción real de los datos empíricos que recibes, y determina con un grado de importancia e inteligencia cuántas estrategias son verdaderamente necesarias, viables y críticas para cada dimensión. Un cuadrante puede tener múltiples estrategias maestras si los datos lo justifican, y otro cuadrante puede tener muy pocas.
        
        Tipos de estrategias esperadas:
        - Estrategias FO (Maxi-Maxi): Usar fortalezas para aprovechar oportunidades.
        - Estrategias DO (Mini-Maxi): Superar debilidades aprovechando oportunidades.
        - Estrategias FA (Maxi-Mini): Usar fortalezas para evitar o mitigar amenazas.
        - Estrategias DA (Mini-Mini): Tácticas defensivas para reducir debilidades y evitar amenazas.
        
        Cada estrategia DEBE iniciar indicando explícitamente qué variables cruza (ej. "(F1, F2, O2) Diseñar un sistema de...").
        
        Devuelve tu respuesta ESTRICTAMENTE en formato JSON válido, con la siguiente estructura (los arreglos pueden tener la cantidad de estrategias que consideres estratégicamente pertinentes):
        {{
            "FO": ["Estrategia 1...", "Estrategia 2...", "..."],
            "DO": ["Estrategia 1...", "..."],
            "FA": ["Estrategia 1...", "Estrategia 2...", "Estrategia 3...", "..."],
            "DA": ["Estrategia 1...", "..."]
        }}
        Devuelve ÚNICAMENTE el texto JSON puro sin etiquetas Markdown.
        """
        
        cruce_res = call_ai(
            messages=[
                {"role": "system", "content": "Eres un Doctor experto en Planeación Estratégica Gerencial. Responde solo con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=3000
        )
        
        cruce_res = cruce_res.replace('```json', '').replace('```', '').strip()
        
        try:
            cruce_json = json.loads(cruce_res)
        except:
            cruce_json = {"FO":[], "DO":[], "FA":[], "DA":[], "error_parseo": "JSON inválido devuelto por la IA."}
            
        return jsonify({"status": "success", "matriz": cruce_json})
    except Exception as e:
        print(f"Error AI Cruce DOFA: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/ai/generar_rrc', methods=['POST'])
def ai_generar_rrc():
    """
    Genera el soporte documental para la Renovación de Registro Calificado
    basado en el informe de autoevaluación del programa activo.
    Aplica el Decreto 1330 de 2019 y la Resolución 0529 del MEN.
    """
    data = request.json
    inst_id    = data.get('inst_id', 1)
    program_id = data.get('program_id', 0)
    condiciones_data = data.get('condiciones', {})   # Ya mapeadas desde el frontend
    program_name     = data.get('program_name', 'Programa Académico')
    inst_name        = data.get('inst_name', 'Institución de Educación Superior')
    justification_url = data.get('justification_url', '')

    try:
        # Cargar metadatos
        meta_table = f"PROGRAM_METADATA_{program_id}"
        meta_res = supabase.table('statistics').select("data_json").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", meta_table).execute()
        meta_str = ""
        if meta_res.data:
            meta_str = "\nMetadatos de Denominación: " + str(meta_res.data[0]['data_json'])

        justification_str = ""
        if justification_url:
            justification_str = f"\nEvidencia documental adjunta (Soporte global): {justification_url}. EXIGENCIA: Analizar y referenciar explícitamente esta evidencia donde aplique."

        # Serializar datos de condiciones, limitando el tamaño
        data_str = json.dumps(condiciones_data, ensure_ascii=False)
        if len(data_str) > 28000:
            data_str = data_str[:28000] + "... [datos truncados]"

        system_prompt = (
            "Eres un evaluador experto y consultor analítico de alto nivel en aseguramiento de la calidad. "
            "Dominas estándares normativos y de evaluación de alto rigor académico y organizacional. "
            "Tu función es generar un SOPORTE DOCUMENTAL formal, técnico y estrictamente analítico "
            "articulando de forma rigurosa los criterios de calidad con los indicadores evaluados."
        )

        prompt = f"""
Basado en el documento 'Indicadores Comunes del Modelo de Autoevaluación CESU (Decretos 1330/2019 y 529/2024)', 
analiza la información de autoevaluación del programa académico **{program_name}** de la institución **{inst_name}**.{meta_str}{justification_str}

Datos por condición:
{data_str}

INSTRUCCIÓN CRÍTICA: Debes obligatoriamente referenciar de forma explícita los nombres de las *evidencias documentales* que soporten la condición, y argumentar basándote en los *cuadros estadísticos* (tasas, promedios) descritos en la información entregada para demostrar una verdadera trayectoria de mejoramiento y autorregulación. NO produzcas un texto puramente descriptivo sin datos.

Redacta el SOPORTE DOCUMENTAL para el proceso de Renovación de Registro Calificado.
Para CADA UNA de las 9 condiciones debes generar:

1. **Análisis de cumplimiento**: descripción de cómo el programa evidencia el cumplimiento de la condición, apoyándote en los datos e indicadores provistos.
2. **Indicadores normativos cubiertos**: lista los aspectos de la Resolución 0529 que tienen soporte.
3. **Aspectos por fortalecer**: señala brevemente los indicadores que requieren mayor documentación o que están en proceso de consolidación.
4. **Calificación estimada**: Cumple plenamente / Cumple en alto grado / Cumple aceptablemente / En proceso de cumplimiento, según los datos.

Usa formato Markdown estricto:
## Condición [N]: [Nombre]
### Análisis de Cumplimiento
### Indicadores con Soporte
### Aspectos por Fortalecer  
### Estimación de Cumplimiento

Al final agrega:
## Resumen Ejecutivo RRC
Con tabla de las 9 condiciones y su estimación.

Sé riguroso, formal y propositivo. Cita las normas cuando sea pertinente.
"""

        rrc_text = call_ai(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.65,
            max_tokens=3500
        )

        return jsonify({"status": "success", "report": rrc_text})

    except Exception as e:
        print(f"Error AI Generar RRC: {e}")
        return jsonify({"error": str(e)})




@app.route('/api/ai/generar_rrc_condicion', methods=['POST'])
def ai_generar_rrc_condicion():
    """
    Genera el soporte documental para una sola condición de RRC.
    """
    data = request.json
    inst_id    = data.get('inst_id', 1)
    program_id = data.get('program_id', 0)
    condicion_num = data.get('condicion_num', '1')
    condicion_data = data.get('condicion_data', {})
    program_name   = data.get('program_name', 'Programa Académico')
    inst_name      = data.get('inst_name', 'Institución de Educación Superior')
    justification_url = data.get('justification_url', '')

    try:
        # Cargar metadatos
        meta_table = f"PROGRAM_METADATA_{program_id}"
        meta_res = supabase.table('statistics').select("data_json").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", meta_table).execute()
        meta_str = ""
        if meta_res.data:
            meta_str = "\nMetadatos de Denominación: " + str(meta_res.data[0]['data_json'])

        justification_str = ""
        if justification_url:
            justification_str = f"\n\nEVIDENCIA PRINCIPAL OBLIGATORIA ADJUNTA PARA LA CONDICIÓN {condicion_num}: {justification_url}\nEXIGENCIA CRÍTICA: Debes analizar exhaustivamente este documento y basar la argumentación de la Condición {condicion_num} en los hallazgos de este soporte documental."

        data_str = json.dumps(condicion_data, ensure_ascii=False)

        system_prompt = (
            "Eres un evaluador experto y consultor analítico de alto nivel en aseguramiento de la calidad. "
            "Tu función es generar un SOPORTE DOCUMENTAL formal, técnico y estrictamente analítico "
            f"articulando de forma rigurosa los criterios de calidad con los indicadores evaluados, exclusivamente para la Condición {condicion_num}."
        )

        prompt = f"""
Basado en el documento 'Indicadores Comunes del Modelo de Autoevaluación CESU', 
analiza la información de autoevaluación del programa académico **{program_name}** de la institución **{inst_name}**.{meta_str}{justification_str}

Datos específicos de la Condición {condicion_num}:
{data_str}

INSTRUCCIÓN CRÍTICA: Debes obligatoriamente referenciar de forma explícita los nombres de las *evidencias documentales* que soporten la condición, y argumentar basándote en los *cuadros estadísticos* (tasas, promedios). NO produzcas un texto puramente descriptivo sin datos.

Redacta el SOPORTE DOCUMENTAL exclusivamente para la Condición {condicion_num}.

Debes generar:
1. **Análisis de cumplimiento**: descripción de cómo el programa evidencia el cumplimiento de la condición.
2. **Indicadores normativos cubiertos**.
3. **Aspectos por fortalecer**.
4. **Estimación de Cumplimiento**: Cumple plenamente / Cumple en alto grado / Cumple aceptablemente / En proceso de cumplimiento.

IMPORTANTE: No uses el título principal `## Condición {condicion_num}: ...`, porque el contenedor visual ya lo tiene.
Simplemente devuelve el contenido interno con esta estructura de subtítulos en Markdown:
### Análisis de Cumplimiento
[texto]
### Indicadores con Soporte
[texto]
### Aspectos por Fortalecer  
[texto]
### Estimación de Cumplimiento
[texto]
"""

        rrc_text = call_ai(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return jsonify({'status': 'success', 'report': rrc_text})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/rrc/report', methods=['GET', 'POST'])

def handle_rrc_report():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    table_id = f"RRC_REPORT_PROGRAM_{program_id}"
    
    if request.method == 'POST':
        data = request.json
        try:
            existing = supabase.table('statistics').select("id").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", table_id).execute()
            if existing.data:
                supabase.table('statistics').update({
                    "data_json": json.dumps({"report": data.get('report')})
                }).eq("id", existing.data[0]['id']).execute()
            else:
                supabase.table('statistics').insert({
                    "inst_id": inst_id,
                    "program_id": program_id,
                    "table_id": table_id,
                    "data_json": json.dumps({"report": data.get('report')})
                }).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            print("Error saving RRC report:", e)
            return jsonify({"status": "error", "message": str(e)})
    
    try:
        res = supabase.table('statistics').select("data_json").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", table_id).execute()
        if res.data:
            return jsonify(json.loads(res.data[0]['data_json']))
        return jsonify({})
    except Exception as e:
        print("Error fetching RRC report:", e)
        return jsonify({})

# --- Rutas del Módulo de Encuestas de Autoevaluación ---

@app.route('/encuestas.html')
def encuestas_page():
    return render_template('encuestas.html')

@app.route('/encuesta_publica.html')
def encuesta_publica_page():
    return render_template('encuesta_publica.html')

@app.route('/api/surveys', methods=['GET', 'POST'])
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

@app.route('/api/surveys/<survey_id>', methods=['GET', 'DELETE'])
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

@app.route('/api/surveys/<survey_id>/respond', methods=['POST'])
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

@app.route('/api/surveys/<survey_id>/responses', methods=['GET'])
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

@app.route('/api/surveys/sync', methods=['POST'])
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

@app.route('/api/teachers', methods=['GET', 'POST'])
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

@app.route('/api/teachers/<teacher_id>', methods=['DELETE'])
def delete_api_teacher(teacher_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    success = formacion_storage.delete_teacher(inst_id, teacher_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No se pudo eliminar el docente."})

@app.route('/api/courses', methods=['GET', 'POST'])
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

@app.route('/api/public/courses', methods=['GET'])
def handle_api_public_courses():
    try:
        courses = formacion_storage.load_courses(1, 0)
        return jsonify(courses)
    except Exception as e:
        print(f"Error loading public courses: {e}")
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

@app.route('/api/courses/<course_id>', methods=['GET', 'PUT', 'DELETE'])
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

@app.route('/api/lms_upload', methods=['POST'])
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
        return jsonify({"status": "error", "message": "No se pudo guardar el estudiante."})
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

@app.route('/api/submissions/<submission_id>/grade', methods=['PUT'])
def handle_api_grade_submission(submission_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    data = request.json
    graded = formacion_storage.grade_submission(inst_id, program_id, submission_id, data)
    if graded:
        return jsonify({"status": "success", "data": graded})
    return jsonify({"status": "error", "message": "No se pudo registrar la calificación."})

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_api_student(student_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    success = formacion_storage.delete_student(inst_id, student_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No se pudo eliminar el estudiante."})

@app.route('/api/students/<student_id>/enroll', methods=['POST'])
def enroll_student_api(student_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    course_id = request.json.get('course_id')
    if not course_id:
        return jsonify({"status": "error", "message": "course_id es requerido."})
    success = formacion_storage.enroll_student_in_course(inst_id, student_id, course_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No se pudo matricular al estudiante."})

@app.route('/api/students/<student_id>/unenroll', methods=['POST'])
def unenroll_student_api(student_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    course_id = request.json.get('course_id')
    if not course_id:
        return jsonify({"status": "error", "message": "course_id es requerido."})
    success = formacion_storage.unenroll_student_from_course(inst_id, student_id, course_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No se pudo cancelar la matrícula."})

@app.route('/api/courses/<course_id>/students', methods=['GET'])
def get_course_enrolled_students(course_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    all_students = formacion_storage.load_students(inst_id)
    enrolled = [s for s in all_students if 'enrolled_courses' in s and course_id in s['enrolled_courses']]
    return jsonify(enrolled)

@app.route('/api/public/enroll_course', methods=['POST'])
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

# --- CRM / PROSPECTOS RUTAS ---

@app.route('/crm.html')
def crm_view():
    return render_template('crm.html')

@app.route('/api/crm/prospects', methods=['GET', 'POST'])
def handle_prospects():
    if request.method == 'GET':
        try:
            res = supabase.table('prospects').select('*').order('created_at', desc=True).execute()
            return jsonify({"status": "success", "data": res.data})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
            
    elif request.method == 'POST':
        try:
            data = request.json
            if not data or 'institution' not in data:
                return jsonify({"status": "error", "message": "Institution is required"})
                
            prospect_data = {
                "name": data.get('name', 'Por Definir'),
                "position": data.get('position', ''),
                "institution": data.get('institution', ''),
                "snies_code": data.get('snies_code', ''),
                "email": data.get('email', ''),
                "linkedin": data.get('linkedin', ''),
                "notes": data.get('notes', ''),
                "status": "Pendiente"
            }
            res = supabase.table('prospects').insert(prospect_data).execute()
            return jsonify({"status": "success", "data": res.data})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

@app.route('/api/crm/prospects/<int:pid>', methods=['PUT', 'DELETE'])
def update_delete_prospect(pid):
    if request.method == 'DELETE':
        try:
            supabase.table('prospects').delete().eq('id', pid).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    if request.method == 'PUT':
        data = request.json
        try:
            res = supabase.table('prospects').update(data).eq('id', pid).execute()
            return jsonify({"status": "success", "data": res.data})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

import csv
import io

@app.route('/api/crm/upload_prospects', methods=['POST'])
def upload_prospects():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})
    
    try:
        # Detect encoding safely
        content = file.stream.read()
        try:
            decoded_content = content.decode("utf-8")
        except:
            decoded_content = content.decode("latin-1")
            
        stream = io.StringIO(decoded_content, newline=None)
        # Try to detect delimiter
        first_line = decoded_content.split('\n')[0]
        delimiter = ';' if ';' in first_line else ','
        
        reader = csv.DictReader(stream, delimiter=delimiter)
        
        inserted_count = 0
        prospects_to_insert = []
        for row in reader:
            name = row.get('Nombre', row.get('name', '')).strip()
            if not name:
                name = "Por Definir"
                
            institution = row.get('Institucion', row.get('Institución', row.get('institution', ''))).strip()
            if not institution:
                continue
                
            prospect_data = {
                "name": name,
                "position": row.get('Cargo', row.get('position', '')),
                "institution": institution,
                "snies_code": row.get('SNIES', row.get('snies_code', '')),
                "email": row.get('Correo', row.get('email', '')),
                "linkedin": row.get('LinkedIn', row.get('linkedin', '')),
                "notes": row.get('Notas', row.get('notes', '')),
                "status": "Pendiente"
            }
            prospects_to_insert.append(prospect_data)
            
        if prospects_to_insert:
            supabase.table('prospects').insert(prospects_to_insert).execute()
            inserted_count = len(prospects_to_insert)
            
        return jsonify({"status": "success", "message": f"{inserted_count} prospectos subidos correctamente"})
    except Exception as e:
        print(f"Error uploading prospects: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route('/api/crm/prospects/bulk_delete', methods=['POST'])
def bulk_delete_prospects():
    data = request.json
    if not data or 'ids' not in data:
        return jsonify({'status': 'error', 'message': 'No ids provided'})
    
    ids = data['ids']
    if not isinstance(ids, list) or len(ids) == 0:
        return jsonify({'status': 'error', 'message': 'Invalid ids array'})
        
    try:
        deleted_count = 0
        for pid in ids:
            supabase.table('prospects').delete().eq('id', pid).execute()
            deleted_count += 1
        return jsonify({'status': 'success', 'deleted_count': deleted_count})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/crm/send_email', methods=['POST'])
def send_email_route():
    data = request.json
    if not data or 'email' not in data or 'subject' not in data or 'body' not in data:
        return jsonify({'status': 'error', 'message': 'Missing email, subject, or body'})
    
    to_email = data['email']
    subject = data['subject']
    body = data['body']
    
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = os.getenv('SMTP_PORT', '465')
    smtp_username = os.getenv('SMTP_EMAIL') or os.getenv('SMTP_USERNAME') or 'orbesrc@gmail.com'
    smtp_password = os.getenv('SMTP_PASSWORD', 'xplguaejibtfyqdn')
    
    if not smtp_server or not smtp_username or not smtp_password:
        return jsonify({'status': 'error', 'message': 'SMTP configuration is missing on the server. Please check your .env file.'})
        
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(smtp_server, int(smtp_port))
        else:
            server = smtplib.SMTP(smtp_server, int(smtp_port))
            server.starttls()
            
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return jsonify({'status': 'success', 'message': 'Email sent successfully'})
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'status': 'error', 'message': f"Failed to send email: {str(e)}"})

# --- MÓDULO PLANIFICACIÓN Y CONTROL ---

@app.route('/planificacion.html')
def planificacion_page():
    return render_template('planificacion.html')

@app.route('/api/dofa/suggest_axes', methods=['POST'])
def suggest_dofa_axes():
    try:
        data = request.json
        dofa_data = data.get('dofa_data')
        
        if not dofa_data:
            return jsonify({'status': 'error', 'message': 'No hay datos DOFA'})

        strategies = []
        for q in ['FO', 'DO', 'FA', 'DA']:
            if q in dofa_data:
                for s in dofa_data[q]:
                    if s.strip():
                        strategies.append(f"[{q}] {s.strip()}")

        if not strategies:
            return jsonify({'status': 'error', 'message': 'No hay estrategias para agrupar'})

        prompt = (
            "Eres un experto en planificación estratégica institucional. A continuación te presento una lista de "
            "estrategias resultantes de una matriz DOFA. Tu tarea es analizar estas estrategias y agruparlas en 3 a 5 "
            "'Ejes Estratégicos' coherentes.\n"
            "Responde ÚNICAMENTE con un JSON estrictamente válido que siga esta estructura exacta (sin markdown ni explicaciones adicionales):\n"
            "[\n"
            "  {\n"
            "    \"name\": \"Nombre del Eje (Ej: Calidad Académica)\",\n"
            "    \"description\": \"Descripción breve del eje\",\n"
            "    \"strategies\": [\"[FO] Estrategia exacta 1\", \"[DO] Estrategia exacta 2\"]\n"
            "  }\n"
            "]\n\n"
            "Lista de estrategias a agrupar:\n" + "\n".join(f"- {s}" for s in strategies)
        )

        response = call_ai(
            messages=[
                {"role": "system", "content": "Eres un sistema de procesamiento de datos en JSON puro. No uses formato markdown de bloque (```json). Devuelve el texto JSON directamente."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2500
        )
        
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
            
        import json
        axes_suggestion = json.loads(response.strip())
        
        return jsonify({'status': 'success', 'axes': axes_suggestion})
    except Exception as e:
        print(f"Error en suggest_dofa_axes: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/planning/migrate_dofa', methods=['POST'])
def migrate_dofa():
    import re
    try:
        data = request.json
        inst_id = data.get('inst_id')
        program_id = data.get('program_id', 0)
        structured_axes = data.get('structured_axes')
        dofa_data = data.get('dofa_data')
        
        if not inst_id:
            return jsonify({'status': 'error', 'message': 'Faltan datos requeridos'})

        migrated_count = 0
        if structured_axes:
            # Flujo Nuevo con Ejes Sugeridos por IA
            for axis in structured_axes:
                axis_name = axis.get('name', 'Nuevo Eje')
                axis_res = supabase.table('planning_axes').select('*').eq('inst_id', inst_id).eq('name', axis_name).execute()
                if not axis_res.data:
                    axis_insert = supabase.table('planning_axes').insert({
                        'inst_id': inst_id,
                        'name': axis_name,
                        'description': axis.get('description', '')
                    }).execute()
                    axis_id = axis_insert.data[0]['id']
                else:
                    axis_id = axis_res.data[0]['id']

                for strategy in axis.get('strategies', []):
                    quad_match = re.match(r'^\[(FO|DO|FA|DA)\]\s*(.*)', strategy)
                    if quad_match:
                        quadKey = quad_match.group(1)
                        desc = quad_match.group(2)
                    else:
                        quadKey = 'FO' # fallback
                        desc = strategy
                    
                    if desc.strip():
                        check_res = supabase.table('planning_strategies').select('id').eq('inst_id', inst_id).eq('quadrant', quadKey).eq('description', desc.strip()).execute()
                        if not check_res.data:
                            supabase.table('planning_strategies').insert({
                                'inst_id': inst_id,
                                'program_id': program_id,
                                'axis_id': axis_id,
                                'quadrant': quadKey,
                                'description': desc.strip()
                            }).execute()
                            migrated_count += 1
                        else:
                            strategy_id = check_res.data[0]['id']
                            supabase.table('planning_strategies').update({
                                'axis_id': axis_id
                            }).eq('id', strategy_id).execute()
                            migrated_count += 1
        elif dofa_data:
            # Flujo Antiguo/Fallback
            axis_res = supabase.table('planning_axes').select('*').eq('inst_id', inst_id).eq('name', 'General DOFA').execute()
            if not axis_res.data:
                axis_insert = supabase.table('planning_axes').insert({
                    'inst_id': inst_id,
                    'name': 'General DOFA',
                    'description': 'Eje creado automáticamente desde el Cruce DOFA'
                }).execute()
                axis_id = axis_insert.data[0]['id']
            else:
                axis_id = axis_res.data[0]['id']

            for quadKey in ['FO', 'DO', 'FA', 'DA']:
                if quadKey in dofa_data:
                    for strategy in dofa_data[quadKey]:
                        if strategy.strip():
                            check_res = supabase.table('planning_strategies').select('id').eq('inst_id', inst_id).eq('quadrant', quadKey).eq('description', strategy.strip()).execute()
                            if not check_res.data:
                                supabase.table('planning_strategies').insert({
                                    'inst_id': inst_id,
                                    'program_id': program_id,
                                    'axis_id': axis_id,
                                    'quadrant': quadKey,
                                    'description': strategy.strip()
                                }).execute()
                                migrated_count += 1
                            
        return jsonify({'status': 'success', 'migrated_count': migrated_count})
    except Exception as e:
        print(f"Error en migrate_dofa: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/planning/tree', methods=['GET'])
def get_planning_tree():
    try:
        inst_id = request.args.get('inst_id')
        try:
            inst_id = int(inst_id)
        except (ValueError, TypeError):
            inst_id = 1
        if not inst_id:
            return jsonify({'status': 'error', 'message': 'inst_id is required'})

        axes = supabase.table('planning_axes').select('*').eq('inst_id', inst_id).execute().data
        strategies = supabase.table('planning_strategies').select('*').eq('inst_id', inst_id).execute().data
        
        strat_ids = [s['id'] for s in strategies] if strategies else []
        gen_objs = []
        if strat_ids:
            gen_objs = supabase.table('planning_general_objectives').select('*').in_('strategy_id', strat_ids).execute().data
            
        gen_obj_ids = [g['id'] for g in gen_objs] if gen_objs else []
        spec_objs = []
        if gen_obj_ids:
            spec_objs = supabase.table('planning_specific_objectives').select('*').in_('general_objective_id', gen_obj_ids).execute().data
            
        spec_obj_ids = [s['id'] for s in spec_objs] if spec_objs else []
        activities = []
        if spec_obj_ids:
            activities = supabase.table('planning_activities').select('*').in_('specific_objective_id', spec_obj_ids).execute().data

        act_by_spec = {}
        for a in activities:
            act_by_spec.setdefault(a['specific_objective_id'], []).append(a)
            
        spec_by_gen = {}
        for s in spec_objs:
            s['activities'] = act_by_spec.get(s['id'], [])
            spec_by_gen.setdefault(s['general_objective_id'], []).append(s)
            
        gen_by_strat = {}
        for g in gen_objs:
            g['specific_objectives'] = spec_by_gen.get(g['id'], [])
            gen_by_strat.setdefault(g['strategy_id'], []).append(g)
            
        strat_by_axis = {}
        for s in strategies:
            s['general_objectives'] = gen_by_strat.get(s['id'], [])
            strat_by_axis.setdefault(s['axis_id'], []).append(s)
            
        tree = []
        for ax in axes:
            ax['strategies'] = strat_by_axis.get(ax['id'], [])
            tree.append(ax)

        return jsonify({'status': 'success', 'tree': tree})
    except Exception as e:
        print(f"Error in planning tree: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/planning/node', methods=['POST'])
def add_planning_node():
    try:
        data = request.json
        node_type = data.get('type')
        inst_id = data.get('inst_id')
        try:
            inst_id = int(inst_id)
        except (ValueError, TypeError):
            inst_id = 1
        parent_id = data.get('parent_id')
        
        if not node_type or not inst_id or not parent_id:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros'})

        if node_type == 'strategy':
            supabase.table('planning_strategies').insert({
                'inst_id': inst_id,
                'axis_id': parent_id,
                'description': data.get('description', ''),
                'weight_percentage': data.get('weight_percentage', 0),
                'quadrant': data.get('quadrant', 'MANUAL')
            }).execute()
        elif node_type == 'gen_obj':
            supabase.table('planning_general_objectives').insert({
                'strategy_id': parent_id,
                'description': data.get('description', ''),
                'alignment_pdi': data.get('alignment_pdi', '')
            }).execute()
        elif node_type == 'spec_obj':
            supabase.table('planning_specific_objectives').insert({
                'general_objective_id': parent_id,
                'description': data.get('description', ''),
                'weight_percentage': data.get('weight_percentage', 0),
                'indicator_type': data.get('indicator_type', ''),
                'indicator_description': data.get('indicator_description', '')
            }).execute()
        elif node_type == 'activity':
            supabase.table('planning_activities').insert({
                'specific_objective_id': parent_id,
                'description': data.get('description', ''),
                'start_date': data.get('start_date'),
                'end_date': data.get('end_date'),
                'goal': data.get('goal', ''),
                'responsible': data.get('responsible', ''),
                'financial_budget': data.get('financial_budget', 0),
                'status': 'Pendiente'
            }).execute()
        else:
            return jsonify({'status': 'error', 'message': 'Tipo inválido'})

        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error in add planning node: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/planning/node/edit', methods=['POST'])
def edit_planning_node():
    try:
        data = request.json
        node_type = data.get('type')
        node_id = data.get('id')
        
        if not node_type or not node_id:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros'})

        table_map = {
            'axis': 'planning_axes',
            'strategy': 'planning_strategies',
            'gen_obj': 'planning_general_objectives',
            'spec_obj': 'planning_specific_objectives',
            'activity': 'planning_activities'
        }
        
        table_name = table_map.get(node_type)
        if not table_name:
            return jsonify({'status': 'error', 'message': 'Tipo inválido'})
            
        update_data = {}
        if 'description' in data: update_data['description'] = data['description']
        if 'name' in data: update_data['name'] = data['name']
        if 'weight_percentage' in data: update_data['weight_percentage'] = data['weight_percentage']
        if 'alignment_pdi' in data: update_data['alignment_pdi'] = data['alignment_pdi']
        if 'indicator_type' in data: update_data['indicator_type'] = data['indicator_type']
        if 'indicator_description' in data: update_data['indicator_description'] = data['indicator_description']
        if 'start_date' in data: update_data['start_date'] = data['start_date']
        if 'end_date' in data: update_data['end_date'] = data['end_date']
        if 'goal' in data: update_data['goal'] = data['goal']
        if 'responsible' in data: update_data['responsible'] = data['responsible']
        if 'financial_budget' in data: update_data['financial_budget'] = data['financial_budget']

        if update_data:
            supabase.table(table_name).update(update_data).eq('id', node_id).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/planning/node/delete', methods=['POST'])
def delete_planning_node():
    try:
        data = request.json
        node_type = data.get('type')
        node_id = data.get('id')
        
        if not node_type or not node_id:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros'})

        table_map = {
            'strategy': 'planning_strategies',
            'gen_obj': 'planning_general_objectives',
            'spec_obj': 'planning_specific_objectives',
            'activity': 'planning_activities'
        }
        
        table_name = table_map.get(node_type)
        if not table_name:
            return jsonify({'status': 'error', 'message': 'Tipo inválido'})
            
        supabase.table(table_name).delete().eq('id', node_id).execute()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error deleting planning node: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/planning/suggest', methods=['POST'])
def suggest_planning_node():
    try:
        data = request.json
        req_type = data.get('type')
        target_id = data.get('target_id')
        inst_id = data.get('inst_id')
        try:
            inst_id = int(inst_id)
        except (ValueError, TypeError):
            inst_id = 1
        
        if not req_type or not target_id:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros'})

        prompt = ""
        
        if req_type == 'gen_obj':
            strat = supabase.table('planning_strategies').select('*').eq('id', target_id).execute().data
            if not strat:
                return jsonify({'status': 'error', 'message': 'Estrategia no encontrada'})
            context_text = strat[0]['description']
            prompt = f"Actúa como un experto en planificación estratégica institucional. Basado en la siguiente ESTRATEGIA: '{context_text}', redacta UN solo OBJETIVO GENERAL claro, medible y ambicioso que permita cumplir esta estrategia. No incluyas explicaciones, responde ÚNICAMENTE con el texto del objetivo."
            
        elif req_type == 'spec_obj':
            gen = supabase.table('planning_general_objectives').select('*').eq('id', target_id).execute().data
            if not gen:
                return jsonify({'status': 'error', 'message': 'Objetivo General no encontrado'})
            context_text = gen[0]['description']
            prompt = f"Actúa como un experto en planificación estratégica institucional. Basado en el siguiente OBJETIVO GENERAL: '{context_text}', redacta UN solo OBJETIVO ESPECÍFICO que divida o concrete el objetivo general. Debe ser preciso y orientarse a un resultado medible. No incluyas explicaciones, responde ÚNICAMENTE con el texto del objetivo."
            
        elif req_type == 'activity':
            spec = supabase.table('planning_specific_objectives').select('*').eq('id', target_id).execute().data
            if not spec:
                return jsonify({'status': 'error', 'message': 'Objetivo Específico no encontrado'})
            context_text = spec[0]['description']
            prompt = f"Actúa como un experto en planificación estratégica institucional. Basado en el siguiente OBJETIVO ESPECÍFICO: '{context_text}', redacta UNA ACTIVIDAD concreta, ejecutable y clara que contribuya a lograr ese objetivo. No incluyas explicaciones, responde ÚNICAMENTE con el texto de la actividad."
        
        if not prompt:
            return jsonify({'status': 'error', 'message': 'Tipo inválido'})

        suggestion = call_ai(
            messages=[
                {"role": "system", "content": "Eres un experto en Planeación Estratégica. Responde ÚNICAMENTE con el texto de la sugerencia, sin markdown ni explicaciones adicionales."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        suggestion = suggestion.strip()
        if suggestion.startswith('"') and suggestion.endswith('"'):
            suggestion = suggestion[1:-1]
        
        return jsonify({'status': 'success', 'suggestion': suggestion})
    except Exception as e:
        print(f"Error in suggest_planning_node: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/planning/users', methods=['GET'])
def get_planning_users():
    """Returns list of users in the institution for assignment dropdowns."""
    try:
        inst_id = request.args.get('inst_id')
        try:
            inst_id = int(inst_id)
        except (ValueError, TypeError):
            inst_id = 1
        if not inst_id:
            return jsonify({'status': 'error', 'message': 'inst_id required'})
        res = supabase.table('users').select('id, name, email, role').eq('inst_id', inst_id).execute()
        users = res.data or []
        # Sort by role priority
        role_order = {'admin': 0, 'lider': 1, 'operador': 2, 'docente': 3, 'estudiante': 4}
        users.sort(key=lambda u: role_order.get(u.get('role', 'estudiante'), 99))
        return jsonify({'status': 'success', 'users': users})
    except Exception as e:
        print(f"Error in get_planning_users: {e}")
        return jsonify({'status': 'error', 'message': str(e)})



# ══════════════════════════════════════════════════════════════════
# BACKUP MODULE

try:
    import pyzipper
except ImportError:
    pyzipper = None
import contextlib

@contextlib.contextmanager
def create_zip_context(buf, password=None):
    if pyzipper and password:
        zf = pyzipper.AESZipFile(buf, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES)
        zf.setpassword(password.encode('utf-8'))
    else:
        zf = create_zip_context(buf, password)
    try:
        yield zf
    finally:
        zf.close()

def verify_backup_security(user_id, password, inst_id, action_type):
    from werkzeug.security import check_password_hash
    if not user_id or not password:
        return False, "Se requiere contrasea de administrador."
        
    res = supabase.table('users').select('email, password_hash').eq('id', user_id).execute()
    if not res.data:
        return False, "Usuario no encontrado."
        
    user = res.data[0]
    email = user.get('email')
    phash = user.get('password_hash')
    
    is_valid = check_password_hash(phash, password) if phash else False
    status = 'SUCCESS' if is_valid else 'DENIED'
    
    try:
        supabase.table('security_backup_logs').insert({
            'user_id': user_id,
            'user_email': email,
            'inst_id': int(inst_id) if inst_id else None,
            'action_type': action_type,
            'status': status
        }).execute()
    except Exception as e:
        print("Error logging security:", e)
        
    return is_valid, ("Acceso denegado. Contrasea incorrecta." if not is_valid else "")

# ══════════════════════════════════════════════════════════════════
import zipfile, csv, io, urllib.request as _ureq, traceback

@app.route('/backup')
def backup_page():
    return render_template('backup.html')

@app.route('/api/backup/stats', methods=['GET'])
def backup_stats():
    try:
        inst_id = request.args.get('inst_id', 1, type=int)
        kwargs = {}
        if inst_id:
            kwargs['inst_id'] = inst_id

        def cnt(table, **kw):
            try:
                q = supabase.table(table).select('id', count='exact')
                for k, v in kw.items():
                    q = q.eq(k, v)
                return q.execute().count or 0
            except Exception:
                return 0

        if inst_id:
            ev = cnt('evidences', inst_id=inst_id)
            fa = cnt('factors', inst_id=inst_id)
            us = cnt('users', inst_id=inst_id)
            ac = cnt('planning_activities')   # no inst_id col - approximate
        else:
            ev = cnt('evidences')
            fa = cnt('factors')
            us = cnt('users')
            ac = cnt('planning_activities')

        # Informes are stored in statistics table
        try:
            inf_q = supabase.table('statistics').select('id', count='exact')
            if inst_id:
                inf_q = inf_q.eq('inst_id', inst_id)
            inf = inf_q.execute().count or 0
        except Exception:
            inf = 0

        return jsonify({"evidencias": ev, "factores": fa, "usuarios": us,
                        "informes": inf, "actividades": ac})
    except Exception as e:
        return jsonify({"evidencias": 0, "factores": 0, "usuarios": 0,
                        "informes": 0, "actividades": 0})


def _safe_filename(s):
    """Remove/replace chars not safe for filesystem paths."""
    import re
    s = str(s or 'sin_nombre')
    s = re.sub(r'[^\w\s\-\.]', '_', s, flags=re.UNICODE)
    return s[:80].strip()


def _fetch_file_bytes(url):
    """Download a file URL. Returns bytes or None."""
    try:
        req = _ureq.Request(url, headers={'User-Agent': 'SIACredit-Backup/1.0'})
        with _ureq.urlopen(req, timeout=20) as r:
            return r.read()
    except Exception:
        return None


def _build_full_zip(inst_id, scope, modules, year, program_id, password=None):
    """Build the complete backup ZIP in memory and return bytes."""
    buf = io.BytesIO()
    with create_zip_context(buf, password) as zf:
        year_label = str(year) if year else 'todos_los_anos'

        # ── README ───────────────────────────────────────────────
        readme = (
            "BACKUP SIAC\n"
            f"Institución ID: {inst_id}\n"
            f"Alcance: {scope}\n"
            f"Año filtrado: {year_label}\n"
            f"Módulos: {', '.join(modules)}\n"
            f"Fecha de generación: {__import__('datetime').datetime.now().isoformat()}\n\n"
            "Estructura del ZIP:\n"
            "  backup_SIAC/\n"
            "    README.txt\n"
            "    datos/  (CSV de cada módulo)\n"
            "    evidencias/  (año/factor/caracteristica/aspecto/)\n"
        )
        zf.writestr("backup_SIAC/README.txt", readme)

        # ── DATOS CSV ────────────────────────────────────────────
        module_map = {
            'evaluaciones': ('evaluations', ['id','inst_id','program_id','created_at','status','score','comments']),
            'usuarios': ('users', ['id','name','email','role','inst_id','program_id']),
            'planes_mejora': ('planes_mejora', ['id','inst_id','description','status','created_at']),
        }

        for mod in modules:
            if mod in module_map:
                table, cols = module_map[mod]
                try:
                    q = supabase.table(table).select(','.join(cols))
                    if inst_id:
                        q = q.eq('inst_id', inst_id)
                    rows = q.execute().data or []
                    csv_buf = io.StringIO()
                    writer = csv.DictWriter(csv_buf, fieldnames=cols, extrasaction='ignore')
                    writer.writeheader()
                    writer.writerows(rows)
                    zf.writestr(f"backup_SIAC/datos/{mod}.csv", csv_buf.getvalue())
                except Exception as ex:
                    zf.writestr(f"backup_SIAC/datos/{mod}_error.txt", str(ex))

        # ── EVIDENCIAS con archivos ──────────────────────────────
        if 'evidencias' in modules:
            try:
                # Load hierarchy: factors -> characteristics -> aspects -> evidences
                fq = supabase.table('factors').select('id,name,characteristics(id,name,aspects(id,text))')
                if inst_id:
                    fq = fq.eq('inst_id', inst_id)
                if program_id:
                    fq = fq.eq('program_id', int(program_id))
                factors = fq.execute().data or []

                # Build aspect_id -> path map
                aspect_path = {}
                for f in factors:
                    fn = _safe_filename(f.get('name') or f.get('id'))
                    for c in (f.get('characteristics') or []):
                        cn = _safe_filename(c.get('name') or c.get('id'))
                        for a in (c.get('aspects') or []):
                            an = _safe_filename((a.get('text') or str(a.get('id')))[:50])
                            aspect_path[str(a['id'])] = f"{year_label}/{fn}/{cn}/{an}"

                # Fetch evidences
                eq = supabase.table('evidences').select('*')
                if inst_id:
                    eq = eq.eq('inst_id', inst_id)
                if program_id:
                    eq = eq.eq('program_id', int(program_id))
                evs = eq.execute().data or []

                csv_rows = []
                for ev in evs:
                    asp_path = aspect_path.get(str(ev.get('aspect_id') or ''), year_label + '/sin_clasificar')
                    base = f"backup_SIAC/evidencias/{asp_path}/"
                    # metadata file
                    meta = "\n".join([f"{k}: {v}" for k, v in ev.items() if k != 'file_url'])
                    ev_name = _safe_filename(ev.get('title') or ev.get('id') or 'evidencia')
                    zf.writestr(base + ev_name + "_info.txt", meta)
                    # download actual file if URL present
                    url = ev.get('file_url') or ev.get('url') or ''
                    if url:
                        fbytes = _fetch_file_bytes(url)
                        if fbytes:
                            ext = url.split('?')[0].rsplit('.', 1)[-1] if '.' in url else 'bin'
                            zf.writestr(base + ev_name + '.' + ext, fbytes)
                    csv_rows.append(ev)

                # CSV de evidencias
                if csv_rows:
                    csv_buf = io.StringIO()
                    keys = list(csv_rows[0].keys())
                    writer = csv.DictWriter(csv_buf, fieldnames=keys, extrasaction='ignore')
                    writer.writeheader(); writer.writerows(csv_rows)
                    zf.writestr("backup_SIAC/datos/evidencias.csv", csv_buf.getvalue())
            except Exception as ex:
                zf.writestr("backup_SIAC/evidencias/error.txt", traceback.format_exc())

        # ── PLANIFICACION ────────────────────────────────────────
        if 'planificacion' in modules:
            try:
                plan_tables = {
                    'ejes': 'planning_axes',
                    'estrategias': 'planning_strategies',
                    'objetivos_generales': 'planning_general_objectives',
                    'objetivos_especificos': 'planning_specific_objectives',
                    'actividades': 'planning_activities',
                }
                for name, table in plan_tables.items():
                    rows = supabase.table(table).select('*').execute().data or []
                    if rows:
                        csv_buf = io.StringIO()
                        writer = csv.DictWriter(csv_buf, fieldnames=list(rows[0].keys()), extrasaction='ignore')
                        writer.writeheader(); writer.writerows(rows)
                        zf.writestr(f"backup_SIAC/datos/planificacion_{name}.csv", csv_buf.getvalue())
            except Exception as ex:
                zf.writestr("backup_SIAC/datos/planificacion_error.txt", str(ex))

        # ── DOFA ─────────────────────────────────────────────────
        if 'dofa' in modules:
            try:
                strats = supabase.table('planning_strategies').select('*').execute().data or []
                if strats:
                    csv_buf = io.StringIO()
                    writer = csv.DictWriter(csv_buf, fieldnames=list(strats[0].keys()), extrasaction='ignore')
                    writer.writeheader(); writer.writerows(strats)
                    zf.writestr("backup_SIAC/datos/dofa_estrategias.csv", csv_buf.getvalue())
            except Exception as ex:
                zf.writestr("backup_SIAC/datos/dofa_error.txt", str(ex))

    buf.seek(0)
    return buf.read()


@app.route('/api/backup/generate', methods=['POST'])
def backup_generate():
    """Generate the full ZIP backup and stream it."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        is_valid, msg = verify_backup_security(user_id, password, inst_id, 'FULL_BACKUP')
        if not is_valid:
            return jsonify({'status': 'error', 'message': msg}), 403
        scope = data.get('scope', 'inst')
        modules = data.get('modules', [])
        year = data.get('year')
        program_id = data.get('program_id')

        if scope == 'super':
            inst_id = None  # All institutions

        zip_bytes = _build_full_zip(inst_id, scope, modules, year, program_id, password)
        ts = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"backup_SIAC_{ts}.zip"
        return Response(
            zip_bytes,
            mimetype='application/zip',
            headers={'Content-Disposition': f'attachment; filename="{fname}"'}
        )
    except Exception as e:
        print(f"Backup error: {e}\n{traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/backup/factor', methods=['POST'])
def backup_factor():
    """ZIP backup of a single factor."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        is_valid, msg = verify_backup_security(user_id, password, inst_id, 'FACTOR_BACKUP')
        if not is_valid:
            return jsonify({'status': 'error', 'message': msg}), 403
        factor_id = data.get('factor_id')
        caracteristica_id = data.get('caracteristica_id')
        year = data.get('year')

        buf = io.BytesIO()
        with create_zip_context(buf, password) as zf:
            # Load factor details
            fq = supabase.table('factors').select('id,name,characteristics(id,name,aspects(id,text))').eq('id', factor_id)
            factors = fq.execute().data or []
            if not factors:
                return jsonify({'status': 'error', 'message': 'Factor no encontrado'}), 404

            factor = factors[0]
            fname = _safe_filename(factor.get('name') or factor_id)
            zf.writestr(f"{fname}/README.txt",
                f"Factor: {factor.get('name')}\nID: {factor_id}\nAño: {year or 'todos'}\n")

            # Build aspect tree
            for c in (factor.get('characteristics') or []):
                if caracteristica_id and str(c['id']) != str(caracteristica_id):
                    continue
                cname = _safe_filename(c.get('name') or c['id'])
                for a in (c.get('aspects') or []):
                    aname = _safe_filename(a.get('name') or a['id'])
                    folder = f"{fname}/{cname}/{aname}/"

                    # Evidences for this aspect
                    eq = supabase.table('evidences').select('*').eq('aspect_id', a['id'])
                    evs = eq.execute().data or []
                    csv_rows = []
                    for ev in evs:
                        ev_title = _safe_filename(ev.get('title') or ev.get('id') or 'ev')
                        meta = "\n".join([f"{k}: {v}" for k, v in ev.items() if k != 'file_url'])
                        zf.writestr(folder + ev_title + "_info.txt", meta)
                        url = ev.get('file_url') or ev.get('url') or ''
                        if url:
                            fbytes = _fetch_file_bytes(url)
                            if fbytes:
                                ext = url.split('?')[0].rsplit('.', 1)[-1] if '.' in url else 'bin'
                                zf.writestr(folder + ev_title + '.' + ext, fbytes)
                        csv_rows.append(ev)

                    if csv_rows:
                        csv_buf = io.StringIO()
                        writer = csv.DictWriter(csv_buf, fieldnames=list(csv_rows[0].keys()), extrasaction='ignore')
                        writer.writeheader(); writer.writerows(csv_rows)
                        zf.writestr(f"{fname}/{cname}/{aname}/evidencias.csv", csv_buf.getvalue())

        buf.seek(0)
        return Response(buf.read(), mimetype='application/zip',
            headers={'Content-Disposition': f'attachment; filename="factor_{factor_id}_backup.zip"'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/backup/evidencias', methods=['POST'])
def backup_evidencias():
    """ZIP of evidences organized in folders."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        is_valid, msg = verify_backup_security(user_id, password, inst_id, 'EVIDENCIAS_BACKUP')
        if not is_valid:
            return jsonify({'status': 'error', 'message': msg}), 403
        year = data.get('year')
        status_filter = data.get('status')
        factor_id = data.get('factor_id')

        # Load hierarchy
        fq = supabase.table('factors').select('id,name,characteristics(id,name,aspects(id,text))')
        if inst_id:
            fq = fq.eq('inst_id', inst_id)
        if factor_id:
            fq = fq.eq('id', int(factor_id))
        factors = fq.execute().data or []

        aspect_path = {}
        for f in factors:
            fn = _safe_filename(f.get('name') or f['id'])
            for c in (f.get('characteristics') or []):
                cn = _safe_filename(c.get('name') or c['id'])
                for a in (c.get('aspects') or []):
                    an = _safe_filename((a.get('text') or str(a['id']))[:50])
                    year_seg = str(year) if year else 'sin_año'
                    aspect_path[str(a['id'])] = f"{year_seg}/{fn}/{cn}/{an}"

        # Fetch evidences
        eq = supabase.table('evidences').select('*')
        if inst_id:
            eq = eq.eq('inst_id', inst_id)
        if status_filter:
            eq = eq.eq('status', status_filter)
        evs = eq.execute().data or []

        buf = io.BytesIO()
        with create_zip_context(buf, password) as zf:
            zf.writestr("evidencias/README.txt",
                f"Backup de Evidencias SIAC\nFiltros: año={year}, estado={status_filter}\n"
                f"Total: {len(evs)} evidencias\n")

            all_rows = []
            for ev in evs:
                path = aspect_path.get(str(ev.get('aspect_id') or ''), 'sin_clasificar')
                base = f"evidencias/{path}/"
                ev_name = _safe_filename(ev.get('title') or ev.get('id') or 'evidencia')
                meta = "\n".join([f"{k}: {v}" for k, v in ev.items()])
                zf.writestr(base + ev_name + "_info.txt", meta)
                url = ev.get('file_url') or ev.get('url') or ''
                if url:
                    fbytes = _fetch_file_bytes(url)
                    if fbytes:
                        ext = url.split('?')[0].rsplit('.', 1)[-1] if '.' in url else 'bin'
                        zf.writestr(base + ev_name + '.' + ext, fbytes)
                all_rows.append(ev)

            # Master CSV
            if all_rows:
                csv_buf = io.StringIO()
                writer = csv.DictWriter(csv_buf, fieldnames=list(all_rows[0].keys()), extrasaction='ignore')
                writer.writeheader(); writer.writerows(all_rows)
                zf.writestr("evidencias/indice_evidencias.csv", csv_buf.getvalue())

        buf.seek(0)
        return Response(buf.read(), mimetype='application/zip',
            headers={'Content-Disposition': 'attachment; filename="evidencias_backup.zip"'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/backup/csv/<tipo>', methods=['POST'])
def backup_csv_single(tipo):
    """Export a single module as CSV."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        is_valid, msg = verify_backup_security(user_id, password, inst_id, 'CSV_MODULE_BACKUP')
        if not is_valid:
            return jsonify({'status': 'error', 'message': msg}), 403
        csv_map = {
            'evaluaciones_csv': ('evaluations', None),
            'evidencias_csv': ('evidences', None),
            'planificacion_csv': ('planning_activities', None),
            'usuarios_csv': ('users', None),
            'planes_csv': ('planes_mejora', None),
            'estadisticas_csv': ('statistics', None),
        }
        if tipo not in csv_map:
            return jsonify({'status': 'error', 'message': 'Tipo no válido'}), 400

        table, _ = csv_map[tipo]
        q = supabase.table(table).select('*')
        if inst_id and table not in ('planning_activities', 'planning_axes', 'planning_strategies'):
            q = q.eq('inst_id', inst_id)
        rows = q.execute().data or []

        if not rows:
            return Response("sin_datos\n", mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename="{tipo}.csv"'})

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)
        return Response(buf.getvalue(), mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{tipo}.csv"'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/backup/csv/all', methods=['POST'])
def backup_csv_all():
    """ZIP of ALL tables as CSV files."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        is_valid, msg = verify_backup_security(user_id, password, inst_id, 'CSV_ALL_BACKUP')
        if not is_valid:
            return jsonify({'status': 'error', 'message': msg}), 403

        tables_inst = ['evaluations', 'evidences', 'factors', 'users', 'planes_mejora',
                       'statistics', 'notificaciones']
        tables_global = ['planning_axes', 'planning_strategies', 'planning_general_objectives',
                         'planning_specific_objectives', 'planning_activities']

        buf = io.BytesIO()
        with create_zip_context(buf, password) as zf:
            for table in tables_inst:
                try:
                    q = supabase.table(table).select('*')
                    if inst_id:
                        q = q.eq('inst_id', inst_id)
                    rows = q.execute().data or []
                    if rows:
                        csv_buf = io.StringIO()
                        writer = csv.DictWriter(csv_buf, fieldnames=list(rows[0].keys()), extrasaction='ignore')
                        writer.writeheader(); writer.writerows(rows)
                        zf.writestr(f"datos/{table}.csv", csv_buf.getvalue())
                except Exception as ex:
                    zf.writestr(f"datos/{table}_error.txt", str(ex))

            for table in tables_global:
                try:
                    rows = supabase.table(table).select('*').execute().data or []
                    if rows:
                        csv_buf = io.StringIO()
                        writer = csv.DictWriter(csv_buf, fieldnames=list(rows[0].keys()), extrasaction='ignore')
                        writer.writeheader(); writer.writerows(rows)
                        zf.writestr(f"datos/{table}.csv", csv_buf.getvalue())
                except Exception as ex:
                    zf.writestr(f"datos/{table}_error.txt", str(ex))

        buf.seek(0)
        ts = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        return Response(buf.read(), mimetype='application/zip',
            headers={'Content-Disposition': f'attachment; filename="SIAC_CSVs_{ts}.zip"'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

@app.route('/api/backup/logs', methods=['POST'])
def get_backup_logs():
    data = request.json or {}
    user_id = data.get('user_id')
    
    # Optional: Check if user is admin
    res_user = supabase.table('users').select('role').eq('id', user_id).execute()
    if not res_user.data or res_user.data[0].get('role') not in ('admin', 'inst_admin', 'super_admin'):
         return jsonify({'status': 'error', 'message': 'No autorizado'}), 403
         
    inst_id = data.get('inst_id')
    q = supabase.table('security_backup_logs').select('*').order('timestamp', desc=True).limit(50)
    if inst_id:
        q = q.eq('inst_id', inst_id)
    res = q.execute()
    return jsonify({'status': 'success', 'logs': res.data or []})
