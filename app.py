from flask import Flask, render_template, request, jsonify, session, Response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import urllib.request
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "siacredit_secret_key")
CORS(app)

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
    return response



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
        return jsonify({"status": "error", "message": str(e)}), 500

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

@app.route('/estadisticas.html')
def estadisticas():
    return render_template('estadisticas.html')

@app.route('/configuracion.html')
def configuracion():
    return render_template('configuracion.html')

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
        return jsonify({"status": "error", "message": str(e)}), 500

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
            return jsonify({"status": "error", "message": "Debes seleccionar un Programa Académico activo antes de guardar el Modelo de Evaluación."}), 400
        
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
            return jsonify({"status": "error", "message": str(e)}), 500

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
            return jsonify({"status": "error", "message": str(e)}), 500

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
        return jsonify({"status": "error", "message": str(e)}), 500

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
                return jsonify({"status": "error", "message": str(e)}), 500
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
                return jsonify({"status": "error", "message": "Supabase no retornó datos del programa."}), 500
        except Exception as e:
            print(f"Error creating program: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

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
            return jsonify({"status": "error", "message": str(e)}), 500
    elif request.method == 'PUT':
        data = request.json
        try:
            supabase.table('programs').update({
                "name": data.get('name'),
                "period": data.get('period')
            }).eq("id", prog_id).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

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
            return jsonify({"status": "error", "message": str(e)}), 500

    try:
        res = supabase.table('institution').select("*").execute()
        return jsonify(res.data)
    except:
        return jsonify([])

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
        return jsonify({"status": "error", "message": str(e)}), 500

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
        return jsonify({"status": "error", "message": str(e)}), 500

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
            return jsonify({"status": "error", "message": str(e)}), 500

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
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
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
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/change-password', methods=['POST'])
def change_password():
    data = request.json
    email = data.get('email')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    try:
        res = supabase.table('users').select("*").eq("email", email).execute()
        if not res.data:
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
        user = res.data[0]
        if check_password_hash(user['password_hash'], old_password):
            new_hash = generate_password_hash(new_password)
            supabase.table('users').update({"password_hash": new_hash}).eq("email", email).execute()
            return jsonify({"status": "success", "message": "Contraseña actualizada"})
        return jsonify({"status": "error", "message": "Contraseña actual incorrecta"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
        return jsonify({"status": "error", "message": str(e)}), 500

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
            return jsonify({"status": "error", "message": "Email requerido"}), 400
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
            return jsonify({"status": "success", "data": res.data[0], "temp_password": temp_password})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    try:
        if inst_id == 0:
            res = supabase.table('users').select("*").execute()
        else:
            # Usuarios de la institución (filtramos por inst_id)
            res = supabase.table('users').select("*").eq("inst_id", inst_id).execute()
        
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
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/users/<user_id>/activate', methods=['POST'])
def activate_user(user_id):
    data = request.json
    new_role = data.get('role', 'lider')
    try:
        # Get current user to remove [PENDING] prefix
        user_res = supabase.table('users').select("name, role").eq("id", user_id).execute()
        if user_res.data:
            current_name = user_res.data[0].get('name', '')
            clean_name = current_name.replace('[PENDING] ', '').replace('[PENDING]', '')
            supabase.table('users').update({"role": new_role, "name": clean_name}).eq("id", user_id).execute()
        else:
            supabase.table('users').update({"role": new_role}).eq("id", user_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/users/<user_id>/role', methods=['POST'])
def change_user_role(user_id):
    """Endpoint dedicado para cambiar el rol de un usuario activo.
    Permite al superadmin (admin) delegar el rol inst_admin a un usuario
    y opcionalmente reasignarlo a una institución."""
    data = request.json
    new_role = data.get('role')
    new_inst_id = data.get('inst_id')  # Opcional: reasignar institución

    if not new_role:
        return jsonify({"status": "error", "message": "El campo 'role' es requerido."}), 400

    # Roles válidos que se pueden asignar (no se puede asignar 'admin' desde aquí)
    allowed_roles = {'lider', 'operativo', 'inst_admin'}
    if new_role not in allowed_roles:
        return jsonify({"status": "error", "message": f"Rol inválido. Roles permitidos: {', '.join(allowed_roles)}"}), 400

    try:
        # Verificar que el usuario target no sea el superadmin
        target_res = supabase.table('users').select("role, name").eq("id", user_id).execute()
        if not target_res.data:
            return jsonify({"status": "error", "message": "Usuario no encontrado."}), 404

        target_role = target_res.data[0].get('role')
        if target_role == 'admin':
            return jsonify({"status": "error", "message": "No se puede modificar el rol del Superadministrador."}), 403

        update_payload = {"role": new_role}
        # Limpiar prefijo [PENDING] si lo tiene
        current_name = target_res.data[0].get('name', '') or ''
        if '[PENDING]' in current_name:
            update_payload["name"] = current_name.replace('[PENDING] ', '').replace('[PENDING]', '').strip()

        # Si se proporciona un inst_id y el rol es inst_admin, actualizar institución
        if new_inst_id is not None and new_role == 'inst_admin':
            update_payload["inst_id"] = new_inst_id

        supabase.table('users').update(update_payload).eq("id", user_id).execute()
        return jsonify({"status": "success", "message": f"Rol actualizado a '{new_role}' correctamente."})
    except Exception as e:
        print(f"Error al cambiar rol del usuario {user_id}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

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
        return jsonify({"status": "error", "message": str(e)}), 500


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
                
                char_info = {
                    "id": c_id,
                    "number": c.get('number', ''),
                    "name": c.get('name', ''),
                    "aspectos": [],
                    "nota_promedio": score
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
                        "evidencias": [{"name": ev['name'], "file_path": ev.get('file_url', ev.get('file_path'))} for ev in evidencias]
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
        return jsonify({"error": str(e)}), 500


def call_ai(messages, max_tokens=1500, temperature=0.7):
    # Forzamos Google Gemini ignorando la DB para evitar problemas de persistencia
    provider = "gemini"
    api_key = "AIzaSyCUzl0g6_n35SGaBoMH8cf7mvSP8TkszUg"
    model = "gemini-2.5-flash"
    
    try:
        # We can still read DB for other things in the future, but AI is fixed
        check = supabase.table('statistics').select("data_json").eq("table_id", "GLOBAL_CONFIG").order("id", desc=True).limit(1).execute()
        if check.data:
            data = json.loads(check.data[0]['data_json'])
            # No overriden AI settings from DB anymore


    except Exception as e:
        print(f"Error fetching AI config: {e}")

    if not api_key:
        raise Exception("La API Key de Inteligencia Artificial no está configurada.")


    if provider == 'anthropic':
        import urllib.request
        import json
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
            raise Exception(f"{str(e)} [DEBUG: provider={provider}, base_url={base_url}, rows={len(check.data) if 'check' in locals() else 'unknown'}]")



@app.route('/api/analyze', methods=['POST'])
def analyze_stats():
    req_data = request.json
    table_id = req_data.get('table_id')
    all_data = req_data.get('all_data', {})
    
    try:
        if table_id:
            data_context = json.dumps(all_data.get(table_id, []), ensure_ascii=False)
            prompt = f"Actúa como par académico del CNA. Analiza los siguientes datos estadísticos del cuadro '{table_id}' e identifica tendencias, fortalezas o aspectos críticos. Responde directamente con el análisis en formato Markdown. Datos: {data_context}"
        else:
            data_context = json.dumps(all_data, ensure_ascii=False)
            if len(data_context) > 30000:
                data_context = data_context[:30000] + "... [truncado]"
            prompt = f"Actúa como par académico del CNA. Analiza de manera integral los siguientes cuadros de datos estadísticos institucionales. Resalta los aspectos más importantes, tendencias globales y posibles oportunidades de mejora. Responde directamente con el análisis en formato Markdown. Datos: {data_context}"

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
        return jsonify({"error": str(e)}), 500

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
        return jsonify({"error": str(e)}), 500

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

        check = supabase.table('evidences').select("id").eq("aspect_id", aspect_id).execute()
        
        if check.data and not is_annex:
            # Update existing main evidence
            supabase.table('evidences').update({
                "name": filename,
                "file_url": file_url,
                "period": period,
                "dependency": dependency,
                "user_email": email,
                "inst_id": inst_id,
                "program_id": program_id
            }).eq("id", check.data[0]['id']).execute()
        else:
            # Insert new evidence (main or annex)
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
        return jsonify({"error": str(e)}), 500
    
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
        return jsonify({"error": "No file part"}), 400
    
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
        return jsonify({"error": "No selected file"}), 400

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
        return jsonify({"error": str(e)}), 500

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
        return jsonify({"status": "error", "message": "No encontrado"}), 404
    except Exception as e:
        print(f"Error deleting library doc: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

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
            # Remove api_key for security when sending to frontend, unless it's just to check if it exists
            # We can send it back but masked, or just send a flag that it's set
            resp_data = dict(current_data)
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
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/evidences/<int:evidence_id>', methods=['DELETE'])
def delete_evidence(evidence_id):
    try:
        supabase.table('evidences').delete().eq("id", evidence_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error deleting evidence: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

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
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/download')
def proxy_download():
    """Proxy file download from Supabase Storage with correct filename and Content-Disposition."""
    file_url = request.args.get('url', '')
    file_name = request.args.get('name', 'archivo')
    if not file_url:
        return jsonify({'error': 'URL requerida'}), 400
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
        return jsonify({'error': str(e)}), 500

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

        system_prompt = "Eres un asistente experto en acreditación de alta calidad para instituciones de educación superior en Colombia (CNA). Responde de manera concisa, profesional y analítica basándote en estándares de calidad académica."
        
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
        return jsonify({"error": str(e)}), 500

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
        Actúa como un Par Académico experto del Consejo Nacional de Acreditación (CNA) de Colombia.
        A continuación se te provee un JSON con la información de la autoevaluación de un programa académico.
        Incluye calificaciones, justificaciones y referencias a cuadros estadísticos.
        
        JSON de Autoevaluación:
        {data_str}

        Por favor, redacta un informe ejecutivo y analítico exhaustivo en formato Markdown estructurado.
        Estructura obligatoria del informe:
        # Informe de Autoevaluación con fines de Acreditación
        ## 1. Introducción y Apreciación General
        ## 2. Análisis por Factores
        (Para cada factor con datos relevantes, menciona sus fortalezas, oportunidades de mejora y su calificación promedio)
        ## 3. Conclusiones
        ## 4. Recomendaciones y Plan de Mejoramiento
        
        Escribe de forma formal, propositiva y basada estrictamente en los datos provistos.
        """
        
        report_text = call_ai(
            messages=[
                {"role": "system", "content": "Eres el redactor experto de informes de acreditación institucional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        return jsonify({"status": "success", "report": report_text})
    except Exception as e:
        print(f"Error AI Generate Report: {e}")
        return jsonify({"error": str(e)}), 500


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

    try:
        # Serializar datos de condiciones, limitando el tamaño
        data_str = json.dumps(condiciones_data, ensure_ascii=False)
        if len(data_str) > 28000:
            data_str = data_str[:28000] + "... [datos truncados]"

        system_prompt = (
            "Eres un experto en evaluación de condiciones de calidad para el Ministerio de Educación "
            "Nacional de Colombia (MEN). Dominas a profundidad el Decreto 1330 de 2019, la Resolución "
            "0529 del MEN y los lineamientos para la Renovación de Registro Calificado (RRC) de programas "
            "de educación superior. Tu rol es redactar texto de soporte académico-normativo riguroso, "
            "propositivo y basado estrictamente en los datos del programa."
        )

        prompt = f"""
Se te entrega la información de autoevaluación del programa académico **{program_name}** 
de la institución **{inst_name}**, mapeada a las 9 condiciones de calidad del Decreto 1330 de 2019 
y la Resolución 0529 del MEN.

Datos por condición:
{data_str}

Redacta el SOPORTE DOCUMENTAL para el proceso de Renovación de Registro Calificado.
Para CADA UNA de las 9 condiciones debes generar:

1. **Análisis de cumplimiento**: descripción de cómo el programa evidencia el cumplimiento 
   de la condición, apoyándote en los datos e indicadores provistos.
2. **Indicadores normativos cubiertos**: lista los aspectos de la Resolución 0529 que tienen soporte.
3. **Aspectos por fortalecer**: señala brevemente los indicadores que requieren mayor documentación 
   o que están en proceso de consolidación.
4. **Calificación estimada**: Cumple plenamente / Cumple en alto grado / Cumple aceptablemente / 
   En proceso de cumplimiento, según los datos.

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
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)


