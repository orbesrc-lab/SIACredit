from utils.mail import send_email
from flask import Flask, render_template, request, jsonify, session, Response, send_from_directory, redirect
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import urllib.request
from dotenv import load_dotenv
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

from routes.frontend import frontend_bp
app.register_blueprint(frontend_bp)

from routes.backup import backup_bp
app.register_blueprint(backup_bp)

from routes.ai import ai_bp, call_ai
app.register_blueprint(ai_bp)

from routes.surveys import surveys_bp
app.register_blueprint(surveys_bp)

from routes.ai_generator import ai_generator_bp
app.register_blueprint(ai_generator_bp)

from routes.planning import planning_bp
app.register_blueprint(planning_bp)

from routes.export import export_bp
app.register_blueprint(export_bp)

from routes.skel_hc import skel_hc_bp
app.register_blueprint(skel_hc_bp)

from routes.skel_evaluations import skel_evaluaciones_bp
app.register_blueprint(skel_evaluaciones_bp)

from routes.core import core_bp
from routes.reports import reports_bp
from routes.prospects import prospects_bp
from routes.business import business_bp
from routes.compliance import compliance_bp
app.register_blueprint(core_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(prospects_bp)
app.register_blueprint(business_bp)
app.register_blueprint(compliance_bp)
from routes.registro_calificado import registro_calificado_bp
app.register_blueprint(registro_calificado_bp)








@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self' data: blob: https:; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.googletagmanager.com https://meet.jit.si; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
        "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "connect-src 'self' https://*.supabase.co https://ftpkhueqooyqvwliifzb.supabase.co wss://*.supabase.co https://*.google-analytics.com; "
        "img-src 'self' data: https: blob:; "
        "frame-src 'self' https: data: blob:; "
        "object-src 'none';"
    )
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Cache-Control para máximo rendimiento e inmediatez absoluta
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    elif request.path.startswith('/static/') or any(request.path.endswith(ext) for ext in ['.css', '.js', '.webp', '.png', '.jpg', '.svg', '.woff2', '.ttf']):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    else:
        # Páginas HTML: no cachear en CDN para evitar servir respuestas con errores
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

    return response

# El cliente Supabase se importa desde utils.db (ya inicializado ahí)
from utils.db import supabase, get_active_inst_id

# Nota: Las configuraciones se leen bajo demanda sin bloquear el arranque serverless

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
