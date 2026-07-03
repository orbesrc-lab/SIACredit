from flask import Blueprint, render_template, request, send_from_directory
from utils.db import supabase
import json

frontend_bp = Blueprint('frontend', __name__)

from flask import current_app

# --- Rutas para SEO (Indexación) ---
@frontend_bp.route('/robots.txt')
def static_from_root_robots():
    return send_from_directory(current_app.static_folder, request.path[1:])

@frontend_bp.route('/sitemap.xml')
def static_from_root_sitemap():
    return send_from_directory(current_app.static_folder, request.path[1:])

@frontend_bp.route('/google3bc9f2eb5c06c742.html')
def static_from_root_google_verification():
    return send_from_directory(current_app.static_folder, request.path[1:])

# --- Rutas para servir las páginas HTML ---
@frontend_bp.route('/')
@frontend_bp.route('/index.html')
def index():
    try:
        # Fetch sin eq("inst_id", 0) porque ya no usamos 0
        res = supabase.table('statistics').select("data_json").eq("table_id", "GLOBAL_CONFIG").execute()
        config = json.loads(res.data[0]['data_json']) if res.data else {"theme": "dark"}
    except Exception:
        config = {"theme": "dark"}
    return render_template('index.html', theme=config.get('theme', 'dark'))

@frontend_bp.route('/login.html')
@frontend_bp.route('/login')
def login():
    return render_template('login.html')

@frontend_bp.route('/registro.html')
@frontend_bp.route('/registro')
def registro():
    return render_template('registro.html')

@frontend_bp.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@frontend_bp.route('/evidencias.html')
def evidencias():
    return render_template('evidencias.html')

@frontend_bp.route('/autoevaluacion.html')
def autoevaluacion():
    return render_template('autoevaluacion.html')

@frontend_bp.route('/informes.html')
def informes():
    return render_template('informes.html')

@frontend_bp.route('/dofa.html')
def dofa():
    return render_template('dofa.html')

@frontend_bp.route('/estadisticas.html')
def estadisticas():
    return render_template('estadisticas.html')

@frontend_bp.route('/configuracion.html')
def configuracion():
    return render_template('configuracion.html')

@frontend_bp.route('/formacion.html')
def formacion():
    return render_template('formacion.html')

@frontend_bp.route('/biblioteca.html')
def biblioteca():
    return render_template('biblioteca.html')

