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
                "documento": str(row.get('Cédula')),
                "email": str(row.get('Correo')),
                "estado": "Activo"
            })
            
        if colabs:
            sb.table('skel_colaboradores').insert(colabs).execute()
            
        return jsonify({"status": "success", "message": f"Se procesaron {len(colabs)} colaboradores."}), 201
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/empresa/<empresa_id>/colaboradores', methods=['GET'])
def get_colaboradores(empresa_id):
    try:
        sb = get_supabase()
        res = sb.table('skel_colaboradores').select('*, skel_cargos(nombre), skel_areas(nombre)').eq('empresa_id', empresa_id).execute()
        return jsonify({"status": "success", "data": res.data}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/empresa/<empresa_id>/perfiles', methods=['GET', 'POST'])
def gestionar_perfiles(empresa_id):
    try:
        sb = get_supabase()
        if request.method == 'GET':
            # Obtener cargos y sus competencias asignadas
            cargos = sb.table('skel_cargos').select('*').eq('empresa_id', empresa_id).execute().data
            asignaciones = sb.table('skel_cargos_diccionario').select('*').execute().data
            
            cargos_list = []
            for c in cargos:
                c_asig = [a['competencia_id'] for a in asignaciones if a['cargo_id'] == c['id']]
                cargos_list.append({"id": c['id'], "nombre": c['nombre'], "competencias": c_asig})
                
            return jsonify({"status": "success", "data": cargos_list}), 200
            
        elif request.method == 'POST':
            # Guardar asignación de competencias
            data = request.json
            cargo_id = data.get('cargo_id')
            competencia_ids = data.get('competencias', [])
            
            # Borrar las anteriores
            sb.table('skel_cargos_diccionario').delete().eq('cargo_id', cargo_id).execute()
            
            # Insertar las nuevas
            if competencia_ids:
                inserts = [{"cargo_id": cargo_id, "competencia_id": comp_id, "nivel_esperado": 3} for comp_id in competencia_ids]
                sb.table('skel_cargos_diccionario').insert(inserts).execute()
                
            return jsonify({"status": "success", "message": "Perfiles actualizados"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

import uuid

@skel_hc_bp.route('/empresa/<empresa_id>/lanzar', methods=['POST'])
def lanzar_encuestas(empresa_id):
    try:
        sb = get_supabase()
        
        # 1. Crear la Evaluación
        eval_res = sb.table('skel_evaluaciones').insert({
            "empresa_id": empresa_id,
            "nombre": "Evaluación 360",
            "descripcion": "Ciclo de evaluación automático",
            "estado": "Activa"
        }).execute()
        
        if not eval_res.data:
            return jsonify({"status": "error", "message": "No se pudo crear la evaluación"}), 500
            
        evaluacion_id = eval_res.data[0]['id']
        
        # 2. Obtener Colaboradores
        colabs = sb.table('skel_colaboradores').select('*').eq('empresa_id', empresa_id).execute().data
        
        if not colabs:
            return jsonify({"status": "error", "message": "No hay colaboradores para lanzar"}), 400
            
        # 3. Generar Tokens
        tokens = []
        for colab in colabs:
            token = str(uuid.uuid4())
            tokens.append({
                "colaborador_id": colab['id'],
                "evaluacion_id": evaluacion_id,
                "token": token,
                "estado": "Generado"
            })
            
        if tokens:
            sb.table('skel_tokens_acceso').insert(tokens).execute()
            
        # Construir listado de links para mostrar
        links = []
        for t, c in zip(tokens, colabs):
            links.append({
                "nombre": f"{c.get('nombres')} {c.get('apellidos')}".strip(),
                "correo": c.get('email'),
                "link": f"https://skel360.online/evaluar?token={t['token']}"
            })
            
        return jsonify({"status": "success", "message": f"Se lanzaron {len(tokens)} encuestas.", "links": links}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ==============================================================================
# Módulo 06: Formulario Público de Evaluación
# ==============================================================================

@skel_hc_bp.route('/evaluar/<token>', methods=['GET'])
def get_evaluacion_publica(token):
    try:
        sb = get_supabase()
        # 1. Validar Token
        token_res = sb.table('skel_tokens_acceso').select('*, skel_colaboradores(*)').eq('token', token).execute().data
        if not token_res:
            return jsonify({"status": "error", "message": "Token inválido o expirado"}), 404
            
        t_data = token_res[0]
        if t_data.get('estado') == 'Completado':
            return jsonify({"status": "error", "message": "Esta evaluación ya fue completada"}), 400
            
        colab = t_data.get('skel_colaboradores', {})
        cargo_id = colab.get('cargo_id')
        
        # 2. Buscar Competencias asignadas al Cargo
        asig = sb.table('skel_cargos_diccionario').select('competencia_id').eq('cargo_id', cargo_id).execute().data
        if not asig:
            return jsonify({"status": "error", "message": "No hay competencias asignadas a tu cargo"}), 404
            
        comp_ids = [a['competencia_id'] for a in asig]
        
        # 3. Traer detalles del diccionario
        comps = sb.table('skel_diccionario_competencias').select('*').in_('id', comp_ids).execute().data
        comports = sb.table('skel_diccionario_comportamientos').select('*').in_('competencia_id', comp_ids).execute().data
        
        # Agrupar
        comps_dict = {c['id']: {**c, 'comportamientos': []} for c in comps}
        for comp in comports:
            if comp['competencia_id'] in comps_dict:
                comps_dict[comp['competencia_id']]['comportamientos'].append(comp)
                
        return jsonify({
            "status": "success",
            "empleado": f"{colab.get('nombres')} {colab.get('apellidos')}".strip(),
            "evaluacion_id": t_data.get('evaluacion_id'),
            "evaluado_id": colab.get('id'),
            "data": list(comps_dict.values())
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/evaluar/<token>/submit', methods=['POST'])
def submit_evaluacion(token):
    try:
        sb = get_supabase()
        # 1. Validar Token
        token_res = sb.table('skel_tokens_acceso').select('*').eq('token', token).execute().data
        if not token_res or token_res[0].get('estado') == 'Completado':
            return jsonify({"status": "error", "message": "Token inválido"}), 400
            
        t_data = token_res[0]
        evaluacion_id = t_data.get('evaluacion_id')
        evaluador_id = t_data.get('colaborador_id')
        
        data = request.json
        respuestas = data.get('respuestas', {}) # { comp_id: puntaje }
        
        # 2. Insertar respuestas
        inserts = []
        for comp_id, puntaje in respuestas.items():
            inserts.append({
                "evaluacion_id": evaluacion_id,
                "evaluado_id": evaluador_id,
                "evaluador_id": evaluador_id,
                "comportamiento_id": comp_id,
                "puntaje": int(puntaje)
            })
            
        if inserts:
            sb.table('skel_360_respuestas').insert(inserts).execute()
            
        # 3. Invalidar Token
        sb.table('skel_tokens_acceso').update({"estado": "Completado"}).eq('token', token).execute()
        
        return jsonify({"status": "success", "message": "Evaluación guardada con éxito"}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
