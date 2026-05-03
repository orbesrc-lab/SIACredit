from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "siacredit_secret_key")
CORS(app)


# Inicializar Cliente Supabase
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- Rutas para servir las páginas HTML ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login.html')
@app.route('/login')
def login():
    return render_template('login.html')

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

# --- API Endpoints con Supabase (Multi-tenant) ---

@app.route('/api/model', methods=['GET', 'POST'])
def handle_model():
    inst_id = request.args.get('inst_id', 1, type=int)
    if request.method == 'POST':
        data = request.json # Lista de factores
        inst_id = request.args.get('inst_id', 1, type=int) # Re-get for safety
        
        try:
            curr_factors = supabase.table('factors').select("id").eq("inst_id", inst_id).execute().data
            curr_f_ids = {f['id'] for f in curr_factors}
            
            incoming_f_ids = set()
            for f in data:
                incoming_f_ids.add(f['id'])
                # Upsert Factor
                try:
                    supabase.table('factors').upsert({
                        "id": f['id'], "number": f['number'], "name": f['name'], 
                        "weight": f.get('weight', 0), "inst_id": inst_id,
                        "leader_id": f.get('leader_id') or None
                    }).execute()
                except Exception:
                    supabase.table('factors').upsert({
                        "id": f['id'], "number": f['number'], "name": f['name'], 
                        "weight": f.get('weight', 0), "inst_id": inst_id
                    }).execute()
                
                for c in f.get('characteristics', []):
                    supabase.table('characteristics').upsert({
                        "id": c['id'], "factor_id": f['id'], "number": c['number'], 
                        "name": c['name'], "weight": c.get('weight', 0)
                    }).execute()
                    
                    for a in c.get('aspects', []):
                        supabase.table('aspects').upsert({
                            "id": a['id'], "char_id": c['id'], "text": a['text']
                        }).execute()
            
            # Delete factors (cascades) not in incoming
            diff_f = curr_f_ids - incoming_f_ids
            if diff_f:
                supabase.table('factors').delete().in_("id", list(diff_f)).eq("inst_id", inst_id).execute()

            return jsonify({"status": "success", "message": "Modelo sincronizado para institución " + str(inst_id)})
        except Exception as e:
            print(f"Error during sync: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    try:
        try:
            res = supabase.table('factors').select("*, characteristics(*, aspects(*)), leader_id").eq("inst_id", inst_id).execute()
        except Exception:
            res = supabase.table('factors').select("*, characteristics(*, aspects(*))").eq("inst_id", inst_id).execute()
            
        sorted_data = sorted(res.data, key=lambda x: float(x['number']))
        return jsonify(sorted_data)
    except Exception as e:
        print(f"Error fetching model: {e}")
        return jsonify([])

@app.route('/api/evaluations', methods=['GET', 'POST'])
def handle_evaluations():
    inst_id = request.args.get('inst_id', 1, type=int)
    if request.method == 'POST':
        data = request.json
        if isinstance(data, dict) and "char_id" in data:
            supabase.table('evaluations').upsert({
                "char_id": data['char_id'], "rating": data['rating'], 
                "just": data['just'], "inst_id": inst_id
            }).execute()
        else:
            for char_id, eval_data in data.items():
                supabase.table('evaluations').upsert({
                    "char_id": char_id, "rating": eval_data.get('rating', 0), 
                    "just": eval_data.get('just', ''), "inst_id": inst_id
                }).execute()
        return jsonify({"status": "success"})

    try:
        evals = supabase.table('evaluations').select("*").eq("inst_id", inst_id).execute()
        eval_dict = {e['char_id']: {"rating": e['rating'], "just": e['just']} for e in evals.data}
        return jsonify(eval_dict)
    except:
        return jsonify({})

@app.route('/api/estadisticas', methods=['GET', 'POST'])
def handle_stats():
    inst_id = request.args.get('inst_id', 1, type=int)
    if request.method == 'POST':
        data = request.json
        for table_id, rows in data.items():
            supabase.table('statistics').upsert({
                "table_id": table_id, "data_json": json.dumps(rows), "inst_id": inst_id
            }).execute()
        return jsonify({"status": "success"})

    try:
        stats = supabase.table('statistics').select("*").eq("inst_id", inst_id).execute()
        result = {s['table_id']: json.loads(s['data_json']) for s in stats.data}
        return jsonify(result)
    except:
        return jsonify({})

@app.route('/api/institutions', methods=['GET', 'POST'])
def handle_all_institutions():
    if request.method == 'POST':
        data = request.json
        try:
            res = supabase.table('institution').insert({
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

@app.route('/api/institution', methods=['GET', 'POST'])
def handle_institution():
    inst_id = request.args.get('inst_id', 1, type=int)
    if request.method == 'POST':
        data = request.json
        try:
            supabase.table('institution').upsert({
                "id": inst_id,
                "name": data.get('name'),
                "logo_url": data.get('logo_url'),
                "description": data.get('program', ''),
                "code": data.get('period', '')
            }).execute()
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
        if check_password_hash(user['password_hash'], password):
            return jsonify({
                "status": "success",
                "user": { 
                    "email": user['email'], 
                    "role": user['role'],
                    "inst_id": user['inst_id']
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
        res = supabase.table('users').select("*").eq("email", "admin@siacredit.edu.co").execute()
        if not res.data:
            admin_hash = generate_password_hash("admin123")
            supabase.table('users').insert({
                "email": "admin@siacredit.edu.co",
                "password_hash": admin_hash,
                "role": "admin",
                "inst_id": 1
            }).execute()
            return jsonify({"status": "success", "message": "Admin inicializado"})
        return jsonify({"status": "info", "message": "Admin ya existe"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Gestión de Usuarios por Institución ---

@app.route('/api/users', methods=['GET', 'POST'])
def handle_users():
    inst_id = request.args.get('inst_id', 1, type=int)
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
                res = supabase.table('users').insert({
                    "email": email,
                    "password_hash": password_hash,
                    "role": data.get('role', 'lider'),
                    "inst_id": inst_id,
                    "name": data.get('name', email.split('@')[0])
                }).execute()
            except Exception:
                # Fallback without name column
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
        query = supabase.table('users').select("id, email, role, name, inst_id")
        # Super-admin can see all users or filter by inst
        if inst_id != 0:
            query = query.eq("inst_id", inst_id)
        try:
            res = query.execute()
        except Exception:
            # Fallback if 'name' column doesn't exist yet
            query2 = supabase.table('users').select("id, email, role, inst_id")
            if inst_id != 0:
                query2 = query2.eq("inst_id", inst_id)
            res = query2.execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/users/<int:user_id>/reset-password', methods=['POST'])
def reset_user_password(user_id):
    data = request.json
    new_password = data.get('new_password', 'SIACTemp2025!')
    try:
        new_hash = generate_password_hash(new_password)
        supabase.table('users').update({"password_hash": new_hash}).eq("id", user_id).execute()
        return jsonify({"status": "success", "temp_password": new_password})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        supabase.table('users').delete().eq("id", user_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --- Dashboard Stats ---

@app.route('/api/dashboard/stats')
def dashboard_stats():
    inst_id = request.args.get('inst_id', 1, type=int)
    try:
        evidences = supabase.table('evidences').select("id, status").eq("inst_id", inst_id).execute().data
        factors = supabase.table('factors').select("id").eq("inst_id", inst_id).execute().data
        evals = supabase.table('evaluations').select("char_id, rating").eq("inst_id", inst_id).execute().data
        users_count = supabase.table('users').select("id").eq("inst_id", inst_id).execute().data

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
    try:
        factors = supabase.table('factors').select("*, characteristics(id, weight)").eq("inst_id", inst_id).execute().data
        evals = supabase.table('evaluations').select("char_id, rating").eq("inst_id", inst_id).execute().data
        eval_map = {e['char_id']: e['rating'] for e in evals}
        
        summary = []
        for f in factors:
            factor_score = 0
            for c in f.get('characteristics', []):
                rating = eval_map.get(c['id'], 0)
                weight = c.get('weight', 0)
                factor_score += rating * (weight / 100)
            
            summary.append({
                "name": f"Factor {f['number']}: {f['name']}",
                "avg": round(factor_score, 2),
                "cumplimiento": round((factor_score / 5) * 100, 1) if factor_score > 0 else 0
            })
        return jsonify(summary)
    except Exception as e:
        print(f"Error in summary: {e}")
        return jsonify([])

@app.route('/api/analyze', methods=['POST'])
def analyze_stats():
    req_data = request.json
    table_id = req_data.get('table_id')
    analysis = ["**Análisis por API:** Datos procesados correctamente."]
    if table_id == 'table_estudiantes':
        analysis.append("Se observa tendencia estable en la matrícula.")
    return jsonify({"analysis": analysis})
    
@app.route('/api/upload', methods=['POST'])
def upload_file():
    inst_id = request.form.get('inst_id', 1, type=int)
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    aspect_id = request.form.get('aspect_id')
    email = request.form.get('email')
    dependency = request.form.get('dependency', 'General')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = f"inst_{inst_id}/{aspect_id}/{file.filename}"
    try:
        file_content = file.read()
        supabase.storage.from_('evidencias').upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": file.content_type}
        )
        file_url = supabase.storage.from_('evidencias').get_public_url(file_path)
        supabase.table('evidences').insert({
            "aspect_id": aspect_id,
            "name": file.filename,
            "file_url": file_url,
            "user_email": email,
            "dependency": dependency,
            "status": "pendiente",
            "inst_id": inst_id
        }).execute()
        return jsonify({"status": "success", "url": file_url})
    except Exception as e:
        print(f"Error uploading: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/evidences', methods=['GET'])
def get_evidences():
    inst_id = request.args.get('inst_id', 1, type=int)
    aspect_id = request.args.get('aspect_id')
    query = supabase.table('evidences').select("*").eq("inst_id", inst_id)
    if aspect_id:
        query = query.eq("aspect_id", aspect_id)
    res = query.execute()
    return jsonify(res.data)

@app.route('/api/evidences/<int:evidence_id>', methods=['DELETE'])
def delete_evidence(evidence_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    try:
        supabase.table('evidences').delete().eq("id", evidence_id).eq("inst_id", inst_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/evidences/status', methods=['POST'])
def update_evidence_status():
    data = request.json
    inst_id = request.args.get('inst_id', 1, type=int)
    supabase.table('evidences').update({
        "status": data['status']
    }).eq("id", data['id']).eq("inst_id", inst_id).execute()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)

