from flask import Blueprint, jsonify, request, current_app
import traceback
import json

# Para este proyecto, app.py inicializa supabase globalmente.
# Usaremos un intento de import local o fallback
try:
    from utils.db import supabase
except ImportError:
    supabase = None

skel_hc_bp = Blueprint('skel_hc', __name__, url_prefix='/api/skel360')

def get_supabase():
    global supabase
    if supabase is None:
        from app import supabase as app_supabase
        supabase = app_supabase
    return supabase

# ==============================================================================
# Módulo 01: Administración General - Empresas (Tenants)
# ==============================================================================

@skel_hc_bp.route('/empresas', methods=['GET'])
def get_empresas():
    try:
        sb = get_supabase()
        res = sb.table('skel_empresas').select('*').execute()
        return jsonify({"status": "success", "data": res.data})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/empresas', methods=['POST'])
def create_empresa():
    try:
        data = request.json
        sb = get_supabase()
        res = sb.table('skel_empresas').insert({
            "nombre": data.get('nombre'),
            "nit": data.get('nit'),
            "sector": data.get('sector'),
            "pais": data.get('pais'),
            "ciudad": data.get('ciudad')
        }).execute()
        return jsonify({"status": "success", "data": res.data}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ==============================================================================
# Módulo 02: Gestión Organizacional - Cargos
# ==============================================================================

@skel_hc_bp.route('/empresas/<empresa_id>/cargos', methods=['GET'])
def get_cargos(empresa_id):
    try:
        sb = get_supabase()
        res = sb.table('skel_cargos').select('*').eq('empresa_id', empresa_id).execute()
        return jsonify({"status": "success", "data": res.data})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/empresas/<empresa_id>/cargos', methods=['POST'])
def create_cargo(empresa_id):
    try:
        data = request.json
        sb = get_supabase()
        res = sb.table('skel_cargos').insert({
            "empresa_id": empresa_id,
            "nombre": data.get('nombre'),
            "nivel_jerarquico": data.get('nivel_jerarquico'),
            "mision_cargo": data.get('mision_cargo')
        }).execute()
        return jsonify({"status": "success", "data": res.data}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ==============================================================================
# Módulo 04: Diccionario de Competencias (Global)
# ==============================================================================

@skel_hc_bp.route('/diccionario', methods=['GET'])
def get_diccionario():
    try:
        sb = get_supabase()
        res_comp = sb.table('skel_diccionario_competencias').select('*').execute()
        res_comp_comportamientos = sb.table('skel_diccionario_comportamientos').select('*').execute()
        
        comps = res_comp.data
        comps_dict = {c['id']: {**c, 'comportamientos': []} for c in comps}
        for comp in res_comp_comportamientos.data:
            if comp['competencia_id'] in comps_dict:
                comps_dict[comp['competencia_id']]['comportamientos'].append(comp)
                
        return jsonify({"status": "success", "data": list(comps_dict.values())})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/diccionario/seed', methods=['POST'])
def seed_diccionario():
    try:
        sb = get_supabase()
        # Seed basic dictionary if empty
        existing = sb.table('skel_diccionario_competencias').select('id').limit(1).execute()
        if existing.data and len(existing.data) > 0:
            return jsonify({"status": "success", "message": "Ya existen datos"}), 200
        
        # Inserciones por defecto
        comp_res = sb.table('skel_diccionario_competencias').insert([
            {"nombre": "Trabajo en Equipo", "descripcion": "Capacidad para colaborar", "tipo": "Blanda"},
            {"nombre": "Liderazgo", "descripcion": "Capacidad para guiar e inspirar", "tipo": "Blanda"}
        ]).execute()
        
        for comp in comp_res.data:
            if comp['nombre'] == "Trabajo en Equipo":
                sb.table('skel_diccionario_comportamientos').insert([
                    {"competencia_id": comp['id'], "descripcion": "¿Ayuda activamente a sus compañeros cuando tienen carga alta de trabajo?"},
                    {"competencia_id": comp['id'], "descripcion": "¿Mantiene una comunicación abierta y respetuosa con el equipo?"}
                ]).execute()
            else:
                sb.table('skel_diccionario_comportamientos').insert([
                    {"competencia_id": comp['id'], "descripcion": "¿Inspira a otros a alcanzar sus metas?"},
                    {"competencia_id": comp['id'], "descripcion": "¿Toma decisiones difíciles asumiendo la responsabilidad?"}
                ]).execute()
                
        return jsonify({"status": "success", "message": "Diccionario inicializado"}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ==============================================================================
# Módulo 05: Carga Masiva (Estructura y Logística)
# ==============================================================================

@skel_hc_bp.route('/empresa/<empresa_id>/carga-masiva', methods=['POST'])
def carga_masiva_empresa(empresa_id):
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No se encontró el archivo"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "Archivo inválido"}), 400
            
        import pandas as pd
        df = pd.read_excel(file)
        
        sb = get_supabase()
        
        # Procesar de forma básica (crear áreas y colaboradores)
        # Por seguridad y simplicidad en el MVP, creamos una sede por defecto
        sede_res = sb.table('skel_sedes').insert({"empresa_id": empresa_id, "nombre": "Sede Principal"}).execute()
        sede_id = sede_res.data[0]['id'] if sede_res.data else None
        
        # Agrupar áreas
        areas_unicas = df['Área'].dropna().unique()
        areas_dict = {}
        for area in areas_unicas:
            res = sb.table('skel_areas').insert({"empresa_id": empresa_id, "sede_id": sede_id, "nombre": str(area)}).execute()
            if res.data:
                areas_dict[str(area)] = res.data[0]['id']
                
        # Agrupar cargos
        cargos_unicos = df['Cargo'].dropna().unique()
        cargos_dict = {}
        for cargo in cargos_unicos:
            res = sb.table('skel_cargos').insert({"empresa_id": empresa_id, "nombre": str(cargo), "nivel_jerarquico": 1}).execute()
            if res.data:
                cargos_dict[str(cargo)] = res.data[0]['id']
                
        # Insertar colaboradores
        colabs = []
        for index, row in df.iterrows():
            area_id = areas_dict.get(str(row.get('Área')))
            cargo_id = cargos_dict.get(str(row.get('Cargo')))
            colabs.append({
                "empresa_id": empresa_id,
                "cargo_id": cargo_id,
                "area_id": area_id,
                "nombres": str(row.get('Nombre')),
                "apellidos": "",
                "identificacion": str(row.get('Cédula')),
                "correo": str(row.get('Correo')),
                "estado": "Activo"
            })
            
        if colabs:
            sb.table('skel_colaboradores').insert(colabs).execute()
            
        return jsonify({"status": "success", "message": f"Se procesaron {len(colabs)} colaboradores."}), 201
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
