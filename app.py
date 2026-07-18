from utils.mail import send_email
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

from routes.core import core_bp
from routes.reports import reports_bp
from routes.prospects import prospects_bp
app.register_blueprint(core_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(prospects_bp)








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
