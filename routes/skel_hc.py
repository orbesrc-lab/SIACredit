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
# Módulo 04: Diccionario de Competencias
# ==============================================================================

@skel_hc_bp.route('/empresas/<empresa_id>/competencias', methods=['GET'])
def get_competencias(empresa_id):
    try:
        sb = get_supabase()
        # Obtiene competencias de la empresa, usando inner join con familia
        res = sb.table('skel_competencias').select('*, skel_familias_competencias!inner(empresa_id)').eq('skel_familias_competencias.empresa_id', empresa_id).execute()
        return jsonify({"status": "success", "data": res.data})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
