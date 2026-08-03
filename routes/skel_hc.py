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

@skel_hc_bp.route('/empresa/<empresa_id>/colaboradores', methods=['GET', 'POST'])
def get_colaboradores(empresa_id):
    try:
        sb = get_supabase()
        if request.method == 'GET':
            res = sb.table('skel_colaboradores').select('*, skel_cargos(nombre), skel_areas(nombre)').eq('empresa_id', empresa_id).execute()
            return jsonify({"status": "success", "data": res.data}), 200
            
        elif request.method == 'POST':
            data = request.json
            
            # Helper para buscar o crear area/cargo
            def get_or_create(table, nombre):
                if not nombre: return None
                exist = sb.table(table).select('id').eq('empresa_id', empresa_id).eq('nombre', nombre).execute().data
                if exist: return exist[0]['id']
                res = sb.table(table).insert({"empresa_id": empresa_id, "nombre": nombre}).execute()
                return res.data[0]['id'] if res.data else None
                
            cargo_id = get_or_create('skel_cargos', data.get('cargo'))
            area_id = get_or_create('skel_areas', data.get('area'))
            
            insert_data = {
                "empresa_id": empresa_id,
                "nombres": data.get('nombres', ''),
                "apellidos": data.get('apellidos', ''),
                "documento": data.get('documento', ''),
                "email": data.get('email', ''),
                "cargo_id": cargo_id,
                "area_id": area_id
            }
            sb.table('skel_colaboradores').insert(insert_data).execute()
            return jsonify({"status": "success", "message": "Colaborador creado"}), 200
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/colaborador/<colab_id>', methods=['PUT', 'DELETE'])
def manage_colaborador(colab_id):
    try:
        sb = get_supabase()
        if request.method == 'DELETE':
            sb.table('skel_colaboradores').delete().eq('id', colab_id).execute()
            return jsonify({"status": "success", "message": "Colaborador eliminado"}), 200
            
        elif request.method == 'PUT':
            data = request.json
            empresa_id = data.get('empresa_id')
            
            def get_or_create(table, nombre):
                if not nombre: return None
                exist = sb.table(table).select('id').eq('empresa_id', empresa_id).eq('nombre', nombre).execute().data
                if exist: return exist[0]['id']
                res = sb.table(table).insert({"empresa_id": empresa_id, "nombre": nombre}).execute()
                return res.data[0]['id'] if res.data else None
                
            cargo_id = get_or_create('skel_cargos', data.get('cargo'))
            area_id = get_or_create('skel_areas', data.get('area'))
            
            update_data = {
                "nombres": data.get('nombres', ''),
                "apellidos": data.get('apellidos', ''),
                "documento": data.get('documento', ''),
                "email": data.get('email', ''),
                "cargo_id": cargo_id,
                "area_id": area_id
            }
            sb.table('skel_colaboradores').update(update_data).eq('id', colab_id).execute()
            return jsonify({"status": "success", "message": "Colaborador actualizado"}), 200
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/empresa/<empresa_id>/perfiles/matriz', methods=['POST'])
def gestionar_perfiles_matriz(empresa_id):
    try:
        sb = get_supabase()
        data = request.json
        asignaciones = data.get('asignaciones', [])
        
        # Eliminar TODAS las asignaciones de todos los cargos de esta empresa para hacer sync
        cargos = sb.table('skel_cargos').select('id').eq('empresa_id', empresa_id).execute().data
        cargo_ids = [c['id'] for c in cargos]
        if cargo_ids:
            # Delete in chunks or one by one if there's no IN operator easily available for delete
            # supabase-py supports in_ for delete!
            sb.table('skel_cargos_diccionario').delete().in_('cargo_id', cargo_ids).execute()
            
            # Preparar las nuevas inserciones
            inserts = []
            for asig in asignaciones:
                c_id = asig.get('cargo_id')
                comps = asig.get('competencias', [])
                if c_id in cargo_ids:
                    for comp in comps:
                        inserts.append({
                            "cargo_id": c_id,
                            "competencia_id": comp
                        })
            
            if inserts:
                sb.table('skel_cargos_diccionario').insert(inserts).execute()
                
        return jsonify({"status": "success", "message": "Matriz guardada con éxito"}), 200
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

@skel_hc_bp.route('/empresa/<empresa_id>/resultados', methods=['GET'])
def get_resultados_empresa(empresa_id):
    try:
        sb = get_supabase()
        
        # 1. Obtener todas las evaluaciones de la empresa
        evals = sb.table('skel_evaluaciones').select('id').eq('empresa_id', empresa_id).execute().data
        if not evals:
            return jsonify({"status": "success", "data": []}), 200
            
        eval_ids = [e['id'] for e in evals]
        
        # 2. Obtener respuestas
        respuestas = sb.table('skel_360_respuestas').select('*, skel_diccionario_comportamientos(competencia_id, descripcion)').in_('evaluacion_id', eval_ids).execute().data
        
        # 3. Obtener colaboradores
        colabs = sb.table('skel_colaboradores').select('id, nombres, apellidos').eq('empresa_id', empresa_id).execute().data
        colabs_dict = {c['id']: f"{c.get('nombres','')} {c.get('apellidos','')}".strip() for c in colabs}
        
        # 4. Obtener competencias
        comps = sb.table('skel_diccionario_competencias').select('id, nombre').execute().data
        comps_dict = {c['id']: c['nombre'] for c in comps}
        
        # 5. Agrupar resultados
        agrupados = {}
        for r in respuestas:
            colab_id = r['evaluado_id']
            if colab_id not in agrupados:
                agrupados[colab_id] = {"nombre": colabs_dict.get(colab_id, "Desconocido"), "competencias_raw": {}, "total_pts": 0, "total_items": 0}
            
            comp_id = r.get('skel_diccionario_comportamientos', {}).get('competencia_id')
            puntaje = r.get('puntaje', 0)
            
            if comp_id:
                comp_name = comps_dict.get(comp_id, "General")
                if comp_name not in agrupados[colab_id]["competencias_raw"]:
                    agrupados[colab_id]["competencias_raw"][comp_name] = {"pts": 0, "count": 0}
                agrupados[colab_id]["competencias_raw"][comp_name]["pts"] += puntaje
                agrupados[colab_id]["competencias_raw"][comp_name]["count"] += 1
                
            agrupados[colab_id]["total_pts"] += puntaje
            agrupados[colab_id]["total_items"] += 1
            
        # Formatear
        resultados_finales = []
        for colab_id, data in agrupados.items():
            prom_global = round(data["total_pts"] / data["total_items"], 1) if data["total_items"] > 0 else 0
            comps_promedios = {}
            for c_name, c_data in data["competencias_raw"].items():
                comps_promedios[c_name] = round(c_data["pts"] / c_data["count"], 1) if c_data["count"] > 0 else 0
                
            resultados_finales.append({
                "colaborador_id": colab_id,
                "colaborador_nombre": data["nombre"],
                "promedio_global": prom_global,
                "competencias": comps_promedios
            })
            
        return jsonify({"status": "success", "data": resultados_finales}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

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
            
        colabs_dict = {c['id']: f"{c.get('nombres','')} {c.get('apellidos','')}".strip() for c in colabs}
        
        # 3. Obtener Red 360
        red_360 = sb.table('skel_360_red').select('*').eq('empresa_id', empresa_id).execute().data
        
        # 4. Generar Tokens
        tokens_to_insert = []
        for colab in colabs:
            # Autoevaluación siempre
            tokens_to_insert.append({
                "empresa_id": empresa_id,
                "colaborador_id": colab['id'],
                "evaluado_id": colab['id'],
                "evaluacion_id": evaluacion_id,
                "tipo": "Autoevaluación",
                "estado": "Generado"
            })
            
            # Evaluadores adicionales
            evaluadores = [r for r in red_360 if r['evaluado_id'] == colab['id']]
            for ev in evaluadores:
                tokens_to_insert.append({
                    "empresa_id": empresa_id,
                    "colaborador_id": ev['evaluador_id'], # Quien llena la encuesta
                    "evaluado_id": colab['id'],           # A quien están evaluando
                    "evaluacion_id": evaluacion_id,
                    "tipo": ev['relacion'],
                    "estado": "Generado"
                })
            
        inserted_tokens = []
        if tokens_to_insert:
            res = sb.table('skel_tokens_acceso').insert(tokens_to_insert).execute()
            inserted_tokens = res.data
            
        # Construir listado de links para mostrar
        links = []
        for t in inserted_tokens:
            evaluado_nombre = colabs_dict.get(t['evaluado_id'], "Desconocido")
            evaluador_nombre = colabs_dict.get(t['colaborador_id'], "Desconocido")
            
            links.append({
                "colaborador_nombre": evaluador_nombre,  # A quien se le manda el link
                "tipo": t['tipo'],
                "evaluando_a": evaluado_nombre,          # A quien van a evaluar
                "link": f"https://www.skel360.online/evaluar?token={t['id']}"
            })
            
        return jsonify({"status": "success", "message": f"Se lanzaron {len(inserted_tokens)} encuestas.", "links": links}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ==============================================================================
# Módulo 06: Formulario Público de Evaluación
# ==============================================================================
@skel_hc_bp.route('/empresa/<empresa_id>/red360', methods=['GET', 'POST'])
def gestionar_red360(empresa_id):
    try:
        sb = get_supabase()
        if request.method == 'GET':
            red = sb.table('skel_360_red').select('*').eq('empresa_id', empresa_id).execute().data
            return jsonify({"status": "success", "data": red}), 200
            
        elif request.method == 'POST':
            data = request.json
            asignaciones = data.get('asignaciones', [])
            
            # Borrar la red existente
            sb.table('skel_360_red').delete().eq('empresa_id', empresa_id).execute()
            
            # Insertar nueva red
            if asignaciones:
                # Cada asig: { evaluado_id, evaluador_id, relacion }
                inserts = []
                for a in asignaciones:
                    inserts.append({
                        "empresa_id": empresa_id,
                        "evaluado_id": a['evaluado_id'],
                        "evaluador_id": a['evaluador_id'],
                        "relacion": a['relacion']
                    })
                sb.table('skel_360_red').insert(inserts).execute()
                
            return jsonify({"status": "success", "message": "Red 360 actualizada"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/evaluar/<token>', methods=['GET'])
def get_evaluacion_publica(token):
    try:
        sb = get_supabase()
        # 1. Validar Token
        token_res = sb.table('skel_tokens_acceso').select('*, skel_colaboradores(*)').eq('id', token).execute().data
        if not token_res:
            return jsonify({"status": "error", "message": "Token inválido o expirado"}), 404
            
        t_data = token_res[0]
        if t_data.get('estado') == 'Completado':
            return jsonify({"status": "error", "message": "Esta evaluación ya fue completada"}), 400
            
        # 1. Obtener Colaborador (El que es evaluado)
        evaluado_id = t_data.get('evaluado_id') or t_data.get('colaborador_id')
        colab = sb.table('skel_colaboradores').select('cargo_id, nombres, apellidos, email, skel_cargos(nombre)').eq('id', evaluado_id).execute().data[0]
        
        # 2. Obtener Perfil del Evaluado
        cargo_id = colab['cargo_id']
        
        # 3. Obtener competencias asignadas a su cargo
        asignaciones = sb.table('skel_cargos_diccionario').select('competencia_id').eq('cargo_id', cargo_id).execute().data
        
        # Fallback para cargos duplicados por error de subida de Excel
        if not asignaciones:
            cargo_nombre = colab.get('skel_cargos', {}).get('nombre') if colab.get('skel_cargos') else None
            if cargo_nombre:
                otros_cargos = sb.table('skel_cargos').select('id').eq('empresa_id', t_data['empresa_id']).eq('nombre', cargo_nombre).execute().data
                otros_ids = [c['id'] for c in otros_cargos]
                if otros_ids:
                    asignaciones = sb.table('skel_cargos_diccionario').select('competencia_id').in_('cargo_id', otros_ids).execute().data
                    
        if not asignaciones:
            return jsonify({"status": "error", "message": "No hay competencias asignadas a tu cargo"}), 404
            
        comp_ids = [a['competencia_id'] for a in asignaciones]
        
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
            "tipo": t_data.get('tipo', 'Autoevaluación'),
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
        token_res = sb.table('skel_tokens_acceso').select('*').eq('id', token).execute().data
        if not token_res or token_res[0].get('estado') == 'Completado':
            return jsonify({"status": "error", "message": "Token inválido"}), 400
            
        t_data = token_res[0]
        evaluacion_id = t_data.get('evaluacion_id')
        evaluador_id = t_data.get('colaborador_id') # Quien responde
        evaluado_id = t_data.get('evaluado_id') or evaluador_id # A quien evaluan
        
        data = request.json
        respuestas = data.get('respuestas', {}) # { comp_id: puntaje }
        
        # 2. Insertar respuestas
        inserts = []
        for comp_id, puntaje in respuestas.items():
            inserts.append({
                "evaluacion_id": evaluacion_id,
                "evaluado_id": evaluado_id,
                "evaluador_id": evaluador_id,
                "comportamiento_id": comp_id,
                "puntaje": int(puntaje)
            })
            
        if inserts:
            sb.table('skel_360_respuestas').insert(inserts).execute()
            
        # 3. Invalidar Token
        sb.table('skel_tokens_acceso').update({"estado": "Completado"}).eq('id', token).execute()
        
        return jsonify({"status": "success", "message": "Evaluación guardada con éxito"}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ==============================================================================
# Fase 4: Reporte Individual 360 y Brechas
# ==============================================================================

@skel_hc_bp.route('/reporte/individual/<evaluado_id>', methods=['GET'])
def get_reporte_individual(evaluado_id):
    try:
        sb = get_supabase()
        
        # 1. Info del Colaborador y Empresa
        res_colab = sb.table('skel_colaboradores').select('*, skel_cargos(nombre)').eq('id', evaluado_id).execute()
        if not res_colab.data:
            return jsonify({"status": "error", "message": "Colaborador no encontrado"}), 404
        colab = res_colab.data[0]
        empresa_id = colab['empresa_id']
        
        # 2. Obtener la Red (quiénes lo evaluaron) para cruzar relaciones
        res_red = sb.table('skel_360_red').select('*').eq('evaluado_id', evaluado_id).execute()
        red = { r['evaluador_id']: r['relacion'] for r in res_red.data }
        # Añadir a la red a sí mismo
        red[evaluado_id] = "Autoevaluación"
        
        # 3. Obtener Respuestas
        res_resp = sb.table('skel_360_respuestas').select('*, skel_diccionario_comportamientos(competencia_id)').eq('evaluado_id', evaluado_id).execute()
        respuestas = res_resp.data
        
        # 4. Agrupar por Competencia y Relación
        comps_data = {}
        
        res_comps = sb.table('skel_diccionario_competencias').select('*').execute()
        comp_map = { c['id']: {"nombre": c['nombre'], "nivel_esperado": 4.0} for c in res_comps.data }
        
        for r in respuestas:
            if not r.get('skel_diccionario_comportamientos'):
                continue
            comp_id = r['skel_diccionario_comportamientos']['competencia_id']
            if comp_id not in comps_data:
                comps_data[comp_id] = {
                    "id": comp_id,
                    "nombre": comp_map.get(comp_id, {}).get("nombre", "Desconocida"),
                    "nivel_esperado": comp_map.get(comp_id, {}).get("nivel_esperado", 4.0),
                    "puntajes": {"Autoevaluación": [], "Jefe": [], "Pares": [], "Subordinados": []}
                }
            
            evaluador = r['evaluador_id']
            # Mapear "Par" a "Pares", "Subordinado" a "Subordinados" si es necesario
            relacion_raw = red.get(evaluador, "Pares")
            if relacion_raw == "Par": relacion_raw = "Pares"
            if relacion_raw == "Subordinado": relacion_raw = "Subordinados"
            if relacion_raw not in comps_data[comp_id]["puntajes"]:
                comps_data[comp_id]["puntajes"][relacion_raw] = []
                
            comps_data[comp_id]["puntajes"][relacion_raw].append(r['puntaje'])
        
        # 5. Calcular promedios
        resultados = []
        for comp_id, data in comps_data.items():
            promedios = {}
            total_sum = 0
            total_count = 0
            for rel, pts in data["puntajes"].items():
                if pts:
                    prom = sum(pts) / len(pts)
                    promedios[rel] = round(prom, 2)
                    if rel != "Autoevaluación":
                        total_sum += sum(pts)
                        total_count += len(pts)
                else:
                    promedios[rel] = 0
            
            # Promedio 360: promedio de evaluadores externos (sin autoevaluación), si no hay externos, usa autoeval
            promedio_360 = round(total_sum / total_count, 2) if total_count > 0 else promedios.get("Autoevaluación", 0)
            brecha = round(promedio_360 - data["nivel_esperado"], 2)
            
            resultados.append({
                "competencia_id": comp_id,
                "nombre": data["nombre"],
                "nivel_esperado": data["nivel_esperado"],
                "promedios": promedios,
                "promedio_360": promedio_360,
                "brecha": brecha
            })
            
        return jsonify({
            "status": "success",
            "colaborador": {
                "nombres": colab.get("nombres", ""),
                "apellidos": colab.get("apellidos", ""),
                "cargo": colab.get("skel_cargos", {}).get("nombre", "N/A")
            },
            "resultados": resultados
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/reporte/ia', methods=['POST'])
def generar_plan_ia():
    try:
        data = request.json
        resultados = data.get('resultados', [])
        
        if not resultados:
            return jsonify({"status": "error", "message": "No hay resultados de competencias para analizar"}), 400
            
        prompt = "Actúa como un experto en Recursos Humanos y desarrollo organizacional. "
        prompt += "A continuación te presento los resultados de una evaluación de desempeño 360 de un colaborador, "
        prompt += "indicando la competencia, su nivel esperado y la brecha (un valor negativo indica que está por debajo de lo esperado):\n\n"
        
        for r in resultados:
            prompt += f"- {r.get('nombre', 'Competencia')}: Esperado {r.get('nivel_esperado', 4)}, Obtenido {r.get('promedio_360', 0)} (Brecha: {r.get('brecha', 0)})\n"
            
        prompt += "\nGenera un 'Plan de Acción' muy conciso y directo (en texto plano o viñetas simples, no uses markdown complejo). Sugiere 2 a 3 acciones prácticas y concretas que el colaborador debe tomar a corto plazo para cerrar las brechas más críticas."
        
        # Llamar a AI
        try:
            from routes.ai_generator import generar_informe_ia_base
            texto_ia = generar_informe_ia_base(prompt)
        except Exception as ai_e:
            print("Error IA:", ai_e)
            texto_ia = "Plan sugerido (Fallback IA no disponible):\n\n1. Identificar cursos en la plataforma correspondientes a las competencias con mayor brecha.\n2. Establecer reuniones periódicas con el Jefe Directo para seguimiento.\n3. Solicitar feedback continuo a pares para mejorar habilidades interpersonales."
            
        return jsonify({"status": "success", "plan": texto_ia})
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
