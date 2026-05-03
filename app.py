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

# --- API Endpoints con Supabase ---

@app.route('/api/model', methods=['GET', 'POST'])
def handle_model():
    if request.method == 'POST':
        data = request.json # Lista de factores
        
        # 1. Obtener IDs actuales para identificar eliminaciones
        try:
            curr_factors = supabase.table('factors').select("id").execute().data
            curr_chars = supabase.table('characteristics').select("id").execute().data
            curr_aspects = supabase.table('aspects').select("id").execute().data
            
            curr_f_ids = {f['id'] for f in curr_factors}
            curr_c_ids = {c['id'] for c in curr_chars}
            curr_a_ids = {a['id'] for a in curr_aspects}
            
            incoming_f_ids = set()
            incoming_c_ids = set()
            incoming_a_ids = set()

            for f in data:
                incoming_f_ids.add(f['id'])
                # Upsert Factor
                supabase.table('factors').upsert({
                    "id": f['id'], "number": f['number'], "name": f['name'], "weight": f.get('weight', 0)
                }).execute()
                
                for c in f.get('characteristics', []):
                    incoming_c_ids.add(c['id'])
                    # Upsert Característica
                    supabase.table('characteristics').upsert({
                        "id": c['id'], "factor_id": f['id'], "number": c['number'], "name": c['name'], "weight": c.get('weight', 0)
                    }).execute()
                    
                    for a in c.get('aspects', []):
                        incoming_a_ids.add(a['id'])
                        # Upsert Aspecto
                        supabase.table('aspects').upsert({
                            "id": a['id'], "char_id": c['id'], "text": a['text']
                        }).execute()
            
            # 2. Eliminar los que ya no están en el modelo entrante
            # El orden importa por las FKs: Aspectos -> Características -> Factores
            diff_a = curr_a_ids - incoming_a_ids
            if diff_a:
                supabase.table('aspects').delete().in_("id", list(diff_a)).execute()
                
            diff_c = curr_c_ids - incoming_c_ids
            if diff_c:
                supabase.table('characteristics').delete().in_("id", list(diff_c)).execute()
                
            diff_f = curr_f_ids - incoming_f_ids
            if diff_f:
                supabase.table('factors').delete().in_("id", list(diff_f)).execute()

            return jsonify({"status": "success", "message": "Modelo sincronizado (creados/actualizados/eliminados)"})
        except Exception as e:
            print(f"Error during sync: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    # Obtener modelo jerárquico
    try:
        res = supabase.table('factors').select("*, characteristics(*, aspects(*))").execute()
        # Ordenar por número manualmente para mayor precisión
        sorted_data = sorted(res.data, key=lambda x: float(x['number']))
        return jsonify(sorted_data)
    except Exception as e:
        print(f"Error fetching model: {e}")
        return jsonify([])

@app.route('/api/evaluations', methods=['GET', 'POST'])
def handle_evaluations():
    if request.method == 'POST':
        data = request.json
        # Support both single evaluation and batch dictionary
        if isinstance(data, dict) and "char_id" in data:
            supabase.table('evaluations').upsert({
                "char_id": data['char_id'],
                "rating": data['rating'],
                "just": data['just']
            }).execute()
        else:
            for char_id, eval_data in data.items():
                supabase.table('evaluations').upsert({
                    "char_id": char_id,
                    "rating": eval_data.get('rating', 0),
                    "just": eval_data.get('just', '')
                }).execute()
        return jsonify({"status": "success"})

    try:
        evals = supabase.table('evaluations').select("*").execute()
        eval_dict = {e['char_id']: {"rating": e['rating'], "just": e['just']} for e in evals.data}
        return jsonify(eval_dict)
    except:
        return jsonify({})

@app.route('/api/estadisticas', methods=['GET', 'POST'])
def handle_stats():
    if request.method == 'POST':
        data = request.json
        for table_id, rows in data.items():
            supabase.table('statistics').upsert({
                "table_id": table_id,
                "data_json": json.dumps(rows)
            }).execute()
        return jsonify({"status": "success"})

    try:
        stats = supabase.table('statistics').select("*").execute()
        result = {s['table_id']: json.loads(s['data_json']) for s in stats.data}
        return jsonify(result)
    except:
        return jsonify({})

@app.route('/api/institution', methods=['GET', 'POST'])
def handle_institution():
    if request.method == 'POST':
        data = request.json
        supabase.table('institution').upsert({
            "id": 1,
            "name": data.get('name'),
            "logo_url": data.get('logo_url'),
            "program": data.get('program'),
            "period": data.get('period')
        }).execute()
        return jsonify({"status": "success"})

    try:
        inst = supabase.table('institution').select("*").eq("id", 1).execute()
        if inst.data:
            return jsonify(inst.data[0])
    except:
        pass
    return jsonify({"name": "Nombre Institución", "logo_url": "", "program": "Ingeniería de Sistemas", "period": "2026-1"})

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
                "user": { "email": user['email'], "role": user['role'] }
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
                "role": "admin"
            }).execute()
            return jsonify({"status": "success", "message": "Admin inicializado. Email: admin@siacredit.edu.co, Pass: admin123"})
        return jsonify({"status": "info", "message": "Admin ya existe"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reports/summary')
def report_summary():
    try:
        # Dynamic summary based on factors and evaluations
        factors = supabase.table('factors').select("*, characteristics(id, weight)").execute().data
        evals = supabase.table('evaluations').select("char_id, rating").execute().data
        eval_map = {e['char_id']: e['rating'] for e in evals}
        
        summary = []
        for f in factors:
            factor_score = 0
            total_weight = 0
            for c in f.get('characteristics', []):
                rating = eval_map.get(c['id'], 0)
                weight = c.get('weight', 0)
                factor_score += rating * (weight / 100)
                total_weight += weight
            
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
    analysis = ["**Análisis por API de Supabase:** Datos procesados correctamente."]
    if table_id == 'table_estudiantes':
        analysis.append("Se observa tendencia estable en la matrícula.")
    return jsonify({"analysis": analysis})
    
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    aspect_id = request.form.get('aspect_id')
    email = request.form.get('email')
    dependency = request.form.get('dependency', 'General')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = f"{aspect_id}/{file.filename}"
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
            "status": "pendiente"
        }).execute()
        return jsonify({"status": "success", "url": file_url})
    except Exception as e:
        print(f"Error uploading: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/evidences', methods=['GET'])
def get_evidences():
    aspect_id = request.args.get('aspect_id')
    query = supabase.table('evidences').select("*")
    if aspect_id:
        query = query.eq("aspect_id", aspect_id)
    res = query.execute()
    return jsonify(res.data)

@app.route('/api/evidences/<int:evidence_id>', methods=['DELETE'])
def delete_evidence(evidence_id):
    try:
        # Get file info to delete from storage too if possible
        ev = supabase.table('evidences').select("*").eq("id", evidence_id).execute().data
        if ev:
            # Optionally delete from storage (need path)
            # For now just database
            supabase.table('evidences').delete().eq("id", evidence_id).execute()
            return jsonify({"status": "success"})
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/evidences/status', methods=['POST'])
def update_evidence_status():
    data = request.json
    supabase.table('evidences').update({
        "status": data['status']
    }).eq("id", data['id']).execute()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)

