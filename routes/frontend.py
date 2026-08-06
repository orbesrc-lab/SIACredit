from flask import Blueprint, render_template, request, send_from_directory
from utils.db import supabase
import json
from flask import current_app

frontend_bp = Blueprint('frontend', __name__)

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
        res = supabase.table('statistics').select("data_json").eq("table_id", "GLOBAL_CONFIG").order("id", desc=True).limit(1).execute()
        config = json.loads(res.data[0]['data_json']) if res.data else {"theme": "dark"}
    except Exception:
        config = {"theme": "dark"}
    return render_template('index.html', theme=config.get('theme', 'dark'), config=config)

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

@frontend_bp.route('/empresa_dashboard.html')
def empresa_dashboard():
    return render_template('empresa_dashboard.html')

@frontend_bp.route('/empresa_matrices.html')
def empresa_matrices():
    return render_template('empresa_matrices.html')

@frontend_bp.route('/empresa_porter.html')
def empresa_porter():
    return render_template('empresa_porter.html')

@frontend_bp.route('/empresa_riesgos.html')
def empresa_riesgos():
    return render_template('empresa_riesgos.html')

@frontend_bp.route('/empresa_stakeholders.html')
def empresa_stakeholders():
    return render_template('empresa_stakeholders.html')

@frontend_bp.route('/empresa_comunicacion.html')
def empresa_comunicacion():
    return render_template('empresa_comunicacion.html')

@frontend_bp.route('/empresa_informe_gerencial.html')
def empresa_informe_gerencial():
    return render_template('empresa_informe_gerencial.html')

@frontend_bp.route('/empresa_iso.html')
def empresa_iso():
    return render_template('empresa_iso.html')

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

@frontend_bp.route('/normatividad.html')
def normatividad():
    return render_template('normatividad.html')

@frontend_bp.route('/skel360.html')
def skel360():
    return render_template('skel360.html')

@frontend_bp.route('/skel360_portal.html')
def skel360_portal():
    return render_template('skel360_portal.html')

@frontend_bp.route('/skel360/diccionario')
def skel360_diccionario():
    return render_template('skel_diccionario.html')

@frontend_bp.route('/skel360/empresa/<id>')
def skel360_empresa(id):
    return render_template('skel_empresa_dashboard.html', empresa_id=id)

@frontend_bp.route('/skel360/empresa/<empresa_id>/resultados')
def skel_empresa_resultados(empresa_id):
    return render_template('skel_empresa_resultados.html', empresa_id=empresa_id)

@frontend_bp.route('/evaluar')
def evaluar_publico():
    return render_template('skel_evaluar.html')

@frontend_bp.route('/skel360/reporte/individual')
def skel360_reporte_individual():
    return render_template('reporte_individual_360.html')

@frontend_bp.route('/skel360/empresa/<empresa_id>/plan-formacion')
def skel_empresa_plan_formacion(empresa_id):
    return render_template('skel_empresa_plan_formacion.html', empresa_id=empresa_id)

