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
            "ciudad": data.get('ciudad'),
            "contacto_email": data.get('contacto_email'),
            "contacto_telefono": data.get('contacto_telefono'),
            "num_empleados": data.get('num_empleados'),
            "num_departamentos": data.get('num_departamentos'),
            "mision": data.get('mision'),
            "vision": data.get('vision'),
            "logo_url": data.get('logo_url'),
            "logo_institucion_evaluadora": data.get('logo_institucion_evaluadora')
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

@skel_hc_bp.route('/diccionario', methods=['POST'])
def create_competencia_manual():
    try:
        data = request.json
        sb = get_supabase()
        
        # 1. Crear la competencia
        comp_res = sb.table('skel_diccionario_competencias').insert({
            "nombre": data.get('nombre'),
            "descripcion": data.get('descripcion', ''),
            "tipo": data.get('tipo', 'Blanda')
        }).execute()
        
        nueva_comp = comp_res.data[0]
        
        # 2. Agregar preguntas/comportamientos
        comportamientos = data.get('comportamientos', [])
        if comportamientos:
            insert_data = [
                {"competencia_id": nueva_comp['id'], "descripcion": comp}
                for comp in comportamientos if comp.strip()
            ]
            if insert_data:
                sb.table('skel_diccionario_comportamientos').insert(insert_data).execute()
                
        return jsonify({"status": "success", "data": nueva_comp}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ==============================================================================
# Módulo 05: Carga Masiva (Estructura y Logística)
# ==============================================================================

def deduplicate_cargos_empresa(sb, empresa_id):
    """
    Agrupa los cargos de una empresa por nombre normalizado (sin espacios extras, ignorando mayúsculas/minúsculas y plurales).
    Consolida las asignaciones de competencias y migra los colaboradores al cargo principal que posee las competencias.
    """
    try:
        import re
        cargos = sb.table('skel_cargos').select('*').eq('empresa_id', empresa_id).execute().data
        if not cargos:
            return

        def norm(n):
            s = n.strip().lower()
            return re.sub(r's$', '', s)

        groups = {}
        for c in cargos:
            k = norm(c['nombre'])
            if k not in groups:
                groups[k] = []
            groups[k].append(c)

        for k, list_cargos in groups.items():
            if len(list_cargos) > 1:
                survivor = None
                for c in list_cargos:
                    asig = sb.table('skel_cargos_diccionario').select('id').eq('cargo_id', c['id']).execute().data
                    if asig and not survivor:
                        survivor = c
                if not survivor:
                    survivor = list_cargos[0]

                for c in list_cargos:
                    if c['id'] != survivor['id']:
                        sb.table('skel_colaboradores').update({'cargo_id': survivor['id']}).eq('cargo_id', c['id']).execute()
                        asigs_dup = sb.table('skel_cargos_diccionario').select('*').eq('cargo_id', c['id']).execute().data
                        for a in asigs_dup:
                            exist = sb.table('skel_cargos_diccionario').select('id').eq('cargo_id', survivor['id']).eq('competencia_id', a['competencia_id']).execute().data
                            if not exist:
                                sb.table('skel_cargos_diccionario').insert({
                                    'cargo_id': survivor['id'],
                                    'competencia_id': a['competencia_id'],
                                    'nivel_requerido': a.get('nivel_requerido', 5)
                                }).execute()
                        sb.table('skel_cargos_diccionario').delete().eq('cargo_id', c['id']).execute()
                        try:
                            sb.table('skel_cargos').delete().eq('id', c['id']).execute()
                        except Exception: pass
    except Exception as e:
        print(f"Error deduplicando cargos: {e}")

@skel_hc_bp.route('/empresa/<empresa_id>/carga-masiva', methods=['POST'])
def carga_masiva_colaboradores(empresa_id):
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No se encontró el archivo"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "Archivo inválido"}), 400
            
        import pandas as pd
        df = pd.read_excel(file)
        
        sb = get_supabase()
        
        # Sede por defecto
        sede_res = sb.table('skel_sedes').insert({"empresa_id": empresa_id, "nombre": "Sede Principal"}).execute()
        sede_id = sede_res.data[0]['id'] if sede_res.data else None
        
        # Agrupar áreas con verificación inteligente de existentes
        areas_unicas = df['Área'].dropna().unique()
        areas_dict = {}
        areas_existentes = sb.table('skel_areas').select('*').eq('empresa_id', empresa_id).execute().data
        
        def find_existing_area(nombre):
            n_clean = str(nombre).strip().lower()
            for ex in areas_existentes:
                if ex['nombre'].strip().lower() == n_clean:
                    return ex['id']
            return None

        for area in areas_unicas:
            a_str = str(area).strip()
            found_id = find_existing_area(a_str)
            if found_id:
                areas_dict[a_str] = found_id
            else:
                res = sb.table('skel_areas').insert({"empresa_id": empresa_id, "sede_id": sede_id, "nombre": a_str}).execute()
                if res.data:
                    areas_dict[a_str] = res.data[0]['id']
                    areas_existentes.append(res.data[0])
                
        # Agrupar cargos con verificación inteligente de existentes
        cargos_unicos = df['Cargo'].dropna().unique()
        cargos_dict = {}
        cargos_existentes = sb.table('skel_cargos').select('*').eq('empresa_id', empresa_id).execute().data
        
        def find_existing_cargo(nombre):
            n_clean = str(nombre).strip().lower().rstrip('s')
            for ex in cargos_existentes:
                ex_clean = ex['nombre'].strip().lower().rstrip('s')
                if ex_clean == n_clean:
                    return ex['id']
            return None

        for cargo in cargos_unicos:
            c_str = str(cargo).strip()
            found_id = find_existing_cargo(c_str)
            if found_id:
                cargos_dict[c_str] = found_id
            else:
                res = sb.table('skel_cargos').insert({"empresa_id": empresa_id, "nombre": c_str, "nivel_jerarquico": 1}).execute()
                if res.data:
                    cargos_dict[c_str] = res.data[0]['id']
                    cargos_existentes.append(res.data[0])
                
        # Insertar colaboradores
        colabs = []
        for index, row in df.iterrows():
            area_id = areas_dict.get(str(row.get('Área')).strip())
            cargo_id = cargos_dict.get(str(row.get('Cargo')).strip())
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
            
        # Ejecutar auto-limpieza de cargos
        deduplicate_cargos_empresa(sb, empresa_id)
            
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
            # 1. Desvincular como jefe de otros colaboradores
            try:
                sb.table('skel_colaboradores').update({'jefe_id': None}).eq('jefe_id', colab_id).execute()
            except Exception: pass

            # 2. Eliminar respuestas de evaluaciones asociadas
            for tbl in ['skel_360_respuestas', 'skel_evaluaciones_respuestas']:
                try:
                    sb.table(tbl).delete().eq('evaluador_id', colab_id).execute()
                    sb.table(tbl).delete().eq('evaluado_id', colab_id).execute()
                except Exception: pass

            # 3. Eliminar tokens y red 360
            try:
                sb.table('skel_tokens_acceso').delete().eq('colaborador_id', colab_id).execute()
                sb.table('skel_tokens_acceso').delete().eq('evaluado_id', colab_id).execute()
            except Exception: pass

            try:
                sb.table('skel_360_red').delete().eq('evaluador_id', colab_id).execute()
                sb.table('skel_360_red').delete().eq('evaluado_id', colab_id).execute()
            except Exception: pass

            # 4. Eliminar el colaborador finalmente
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
                
        # Auto-limpieza de cargos duplicados al guardar la matriz
        deduplicate_cargos_empresa(sb, empresa_id)

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
            
        colabs_dict = {c['id']: {"nombre": f"{c.get('nombres','')} {c.get('apellidos','')}".strip(), "email": c.get('email', '')} for c in colabs}
        
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
            evaluado_info = colabs_dict.get(t['evaluado_id'], {"nombre": "Desconocido", "email": ""})
            evaluador_info = colabs_dict.get(t['colaborador_id'], {"nombre": "Desconocido", "email": ""})
            
            links.append({
                "id": t['id'],
                "nombre": f"{evaluador_info['nombre']} ({t['tipo']})",  # A quien se le manda el link
                "correo": evaluador_info['email'],
                "colaborador_nombre": evaluador_info['nombre'],
                "tipo": t['tipo'],
                "evaluando_a": evaluado_info['nombre'],          # A quien van a evaluar
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
        token_res = sb.table('skel_tokens_acceso').select('*').eq('id', token).execute().data
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
        
        # Fallback para cargos duplicados por diferencias de espacios o plurales
        if not asignaciones:
            cargo_nombre = colab.get('skel_cargos', {}).get('nombre') if colab.get('skel_cargos') else None
            if cargo_nombre:
                # Extraer la raíz limpia del nombre del cargo
                base_clean = cargo_nombre.strip()
                if base_clean.endswith('s') or base_clean.endswith('S'):
                    base_clean = base_clean[:-1]
                
                otros_cargos = sb.table('skel_cargos').select('id').eq('empresa_id', t_data['empresa_id']).ilike('nombre', f"%{base_clean}%").execute().data
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
            
        # 6. Fetch saved individual plan and comments
        saved_plan = ""
        saved_comments = ""
        table_id = f"SKEL_PLAN_INDIVIDUAL_{evaluado_id}"
        plan_check = sb.table('statistics').select('data_json').eq('table_id', table_id).execute().data
        if plan_check:
            import json
            try:
                saved_data = json.loads(plan_check[0]['data_json'])
                saved_plan = saved_data.get('plan', '')
                saved_comments = saved_data.get('comentarios', '')
            except:
                pass

        return jsonify({
            "status": "success",
            "colaborador": {
                "nombres": colab.get("nombres", ""),
                "apellidos": colab.get("apellidos", ""),
                "cargo": colab.get("skel_cargos", {}).get("nombre", "N/A")
            },
            "resultados": resultados,
            "saved_plan": saved_plan,
            "saved_comments": saved_comments
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/reporte/individual/<evaluado_id>/plan_accion', methods=['POST'])
def save_plan_accion_individual(evaluado_id):
    try:
        data = request.json
        plan = data.get('plan', '')
        comentarios = data.get('comentarios', '')
        
        import json
        sb = get_supabase()
        
        table_id = f"SKEL_PLAN_INDIVIDUAL_{evaluado_id}"
        # Delete any previous record
        sb.table('statistics').delete().eq('table_id', table_id).execute()
        # Insert new record
        sb.table('statistics').insert({
            'table_id': table_id,
            'data_json': json.dumps({
                "plan": plan,
                "comentarios": comentarios
            })
        }).execute()
        return jsonify({"status": "success", "message": "Plan guardado correctamente"})
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
            
        prompt = f"""Actúa como Consultor Senior en Desarrollo Organizacional y Evaluación 360°.
Realiza un Análisis de Competencias Gerencial y Diagnóstico de Sesgos de Percepción exhaustivo, riguroso y de alto nivel ejecutivo para el colaborador.

DATOS CONSOLIDADOS DE LA EVALUACIÓN 360°:
"""
        for r in resultados:
            auto = r.get('autoevaluacion', 'N/A')
            jefe = r.get('jefe', 'N/A')
            pares = r.get('pares', 'N/A')
            sub = r.get('subordinados', 'N/A')
            esp = r.get('nivel_esperado', 4)
            p_360 = r.get('promedio_360', 0)
            brecha = r.get('brecha', 0)
            
            prompt += f"- Competencia: {r.get('nombre')}\n"
            prompt += f"  Nivel Requerido: {esp} | Promedio 360 Obtenido: {p_360} | Brecha: {brecha:+}\n"
            prompt += f"  Desglose -> Autoevaluación: {auto} | Jefe: {jefe} | Pares: {pares} | Subordinados: {sub}\n\n"

        prompt += """INSTRUCCIONES DE ESTRUCTURA Y ANÁLISIS:
Genera un informe gerencial estructurado en las siguientes 3 secciones en español profesional, claro y enriquecedor (usa viñetas o numeración simple, NO uses símbolos de código o asteriscos extraños):

1. DIAGNÓSTICO DE SESGOS Y PERCEPCIÓN 360°:
- Analiza si existe un Sesgo de Sobreestimación (la autoevaluación es marcadamente superior a la mirada externa de pares/jefe) o de Subestimación (el entorno valora al colaborador por encima de su propia autopercepción).
- Compara la convergencia o divergencia entre la visión del Jefe, los Pares y los Subordinados.

2. FORTALEZAS Y COMPETENCIAS CRÍTICAS A INTERVENIR:
- Detalla las 2 competencias de mayor fortaleza estratégica y cómo apalancarlas.
- Detalla las 2 competencias con brecha crítica negativa y su impacto específico en los objetivos del rol.

3. PLAN DE ACCIÓN Y COMPROMISOS GERENCIALES:
- Presenta 3 compromisos prácticos, medibles y concretos organizados con metas a 30, 60 y 90 días para cerrar las brechas identificadas.
"""
        
        # Llamar a AI
        try:
            from routes.ai_generator import generar_informe_ia_base
            texto_ia = generar_informe_ia_base(prompt)
        except Exception as ai_e:
            print("Error IA:", ai_e)
            texto_ia = "⚠️ Análisis IA no disponible. Por favor, verifica la llave de Inteligencia Artificial en la configuración."
            
        return jsonify({"status": "success", "plan": texto_ia})
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ==============================================================================
# Módulo 07: Plan de Capacitación Institucional
# ==============================================================================

@skel_hc_bp.route('/empresa/<empresa_id>/plan_formacion', methods=['GET'])
def get_plan_formacion_empresa(empresa_id):
    try:
        sb = get_supabase()
        
        # 1. Traer todas las evaluaciones de la empresa
        evals = sb.table('skel_evaluaciones').select('id').eq('empresa_id', empresa_id).execute().data
        if not evals:
            return jsonify({"status": "success", "data": []})
            
        eval_ids = [e['id'] for e in evals]
        
        # 2. Traer respuestas de esas evaluaciones, unidas con la competencia
        # Obtenemos directamente las competencias
        res_comps = sb.table('skel_diccionario_competencias').select('*').execute().data
        comp_map = {c['id']: c for c in res_comps}
        
        # Traer respuestas
        resp_res = sb.table('skel_360_respuestas').select('*, skel_diccionario_comportamientos(competencia_id)').in_('evaluacion_id', eval_ids).execute().data
        
        # 3. Agrupar puntajes por competencia a nivel empresa
        comps_data = {}
        for r in resp_res:
            if not r.get('skel_diccionario_comportamientos'): continue
            comp_id = r['skel_diccionario_comportamientos']['competencia_id']
            if comp_id not in comps_data:
                info = comp_map.get(comp_id, {})
                comps_data[comp_id] = {
                    "id": comp_id,
                    "nombre": info.get('nombre', 'Desconocida'),
                    "tipo": info.get('tipo', 'Blanda'),
                    "nivel_esperado": 4.0,
                    "sum_pts": 0,
                    "count": 0
                }
            comps_data[comp_id]["sum_pts"] += r.get('puntaje', 0)
            comps_data[comp_id]["count"] += 1
            
        # 4. Calcular promedios y brechas
        resultados = []
        for c_id, dat in comps_data.items():
            promedio = round(dat["sum_pts"] / dat["count"], 1) if dat["count"] > 0 else 0
            brecha = round(promedio - dat["nivel_esperado"], 1)
            resultados.append({
                "id": c_id,
                "nombre": dat["nombre"],
                "tipo": dat["tipo"],
                "nivel_esperado": dat["nivel_esperado"],
                "promedio_empresa": promedio,
                "brecha": brecha
            })
            
        # Ordenar por brecha (de más negativa a más positiva)
        resultados.sort(key=lambda x: x["brecha"])
        
        # 5. Fetch saved AI Plan (if any)
        saved_plan = None
        table_id = f"SKEL_PLAN_IA_{empresa_id}"
        plan_check = sb.table('statistics').select('data_json').eq('table_id', table_id).execute().data
        if plan_check:
            import json
            try:
                saved_data = json.loads(plan_check[0]['data_json'])
                saved_plan = saved_data.get('plan')
            except:
                pass
        
        return jsonify({"status": "success", "data": resultados, "saved_plan": saved_plan})
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@skel_hc_bp.route('/empresa/<empresa_id>/plan_formacion/ia', methods=['POST'])
def generar_plan_formacion_ia(empresa_id):
    try:
        data = request.json
        resultados = data.get('resultados', [])
        
        if not resultados:
            return jsonify({"status": "error", "message": "No hay resultados para analizar"}), 400
            
        prompt = "Actúa como Consultor en Desarrollo Organizacional. "
        prompt += "A continuación tienes los resultados consolidados de todas las evaluaciones 360 de una empresa, "
        prompt += "identificando las brechas en competencias (valores negativos = urgencia de capacitación):\n\n"
        
        for r in resultados:
            prompt += f"- {r['nombre']} ({r['tipo']}): Brecha {r['brecha']}\n"
            
        prompt += "\nBasado en esto, redacta un 'Plan Maestro de Capacitación Institucional'. "
        prompt += "Agrupa las necesidades por prioridad. Sé ejecutivo, usa formato HTML (usando <ul>, <li>, <h3>, <p>, <strong>, etc.) "
        prompt += "para que se vea directamente en la plataforma.\n"
        prompt += "CRÍTICO: Para cada curso propuesto (sugiere 3 a 5 cursos para las áreas más urgentes), DEBES incluir explícitamente:\n"
        prompt += "1. Nombre del curso.\n"
        prompt += "2. Horas estimadas.\n"
        prompt += "3. Contenidos principales del curso.\n"
        prompt += "4. Promesa de valor (qué se espera lograr o cómo impactará si los colaboradores toman ese curso)."
        
        try:
            from routes.ai_generator import generar_informe_ia_base
            texto_ia = generar_informe_ia_base(prompt)
            
            # Guardar el plan generado en la base de datos
            import json
            sb = get_supabase()
            table_id = f"SKEL_PLAN_IA_{empresa_id}"
            # Delete any previous plan for this company
            sb.table('statistics').delete().eq('table_id', table_id).execute()
            # Insert the new plan
            sb.table('statistics').insert({
                'table_id': table_id,
                'data_json': json.dumps({"plan": texto_ia})
            }).execute()
            
        except Exception as ai_e:
            texto_ia = """
            <div style="background-color: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 15px; border-radius: 4px;">
                <h3 style="color: #ef4444; margin-top: 0; display: flex; align-items: center; gap: 8px;">
                    ⚠️ Análisis IA no disponible
                </h3>
                <p style="margin-bottom: 0;">El sistema no pudo generar el plan maestro personalizado porque la <strong>llave API de Inteligencia Artificial es inválida o no está configurada</strong>. Por favor, ingresa una API Key válida en el panel de <strong>Configuración Global</strong> para habilitar los insights generativos.</p>
            </div>
            """
            
        return jsonify({"status": "success", "plan": texto_ia})
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@skel_hc_bp.route('/empresas/<empresa_id>', methods=['DELETE'])
def delete_empresa(empresa_id):
    try:
        sb = get_supabase()
        # Eliminar las estadísticas asociadas
        sb.table('statistics').delete().like('table_id', f'%_{empresa_id}').execute()
        
        # Safe cascade delete
        colabs = sb.table('skel_colaboradores').select('id').eq('empresa_id', empresa_id).execute().data
        colab_ids = [c['id'] for c in colabs]
        if colab_ids:
            sb.table('skel_360_respuestas').delete().in_('evaluado_id', colab_ids).execute()
            sb.table('skel_360_red').delete().in_('evaluado_id', colab_ids).execute()
            sb.table('skel_tokens_acceso').delete().in_('colaborador_id', colab_ids).execute()
            
        sb.table('skel_evaluaciones').delete().eq('empresa_id', empresa_id).execute()
        
        cargos = sb.table('skel_cargos').select('id').eq('empresa_id', empresa_id).execute().data
        if cargos:
            cargo_ids = [ca['id'] for ca in cargos]
            sb.table('skel_cargos_competencias').delete().in_('cargo_id', cargo_ids).execute()
            
        sb.table('skel_colaboradores').delete().eq('empresa_id', empresa_id).execute()
        sb.table('skel_cargos').delete().eq('empresa_id', empresa_id).execute()
        sb.table('skel_areas').delete().eq('empresa_id', empresa_id).execute()
        
        # Eliminar la empresa
        sb.table('skel_empresas').delete().eq('id', empresa_id).execute()
        return jsonify({"status": "success", "message": "Empresa eliminada correctamente"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/empresas/<empresa_id>/estado', methods=['PATCH'])
def toggle_estado_empresa(empresa_id):
    try:
        data = request.json
        nuevo_estado = data.get('estado')
        sb = get_supabase()
        sb.table('skel_empresas').update({'estado': nuevo_estado}).eq('id', empresa_id).execute()
        return jsonify({"status": "success", "message": "Estado actualizado"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@skel_hc_bp.route('/empresa/<empresa_id>/enviar-correo', methods=['POST'])
def enviar_correo_evaluacion(empresa_id):
    try:
        from utils.mail import send_email
        sb = get_supabase()
        data = request.json or {}
        token_id = data.get('token_id')
        
        query = sb.table('skel_tokens_acceso').select('*').eq('empresa_id', empresa_id)
        if token_id:
            query = query.eq('id', token_id)
        else:
            query = query.eq('estado', 'Generado')
            
        tokens = query.execute().data
        if not tokens:
            return jsonify({"status": "error", "message": "No se encontraron tokens pendientes de envío"}), 404
            
        colabs = sb.table('skel_colaboradores').select('id, nombres, apellidos, email').eq('empresa_id', empresa_id).execute().data
        colabs_dict = {c['id']: c for c in colabs}
        
        enviados = 0
        fallidos = 0
        
        for t in tokens:
            evaluador = colabs_dict.get(t['colaborador_id'], {})
            evaluado = colabs_dict.get(t['evaluado_id'], {})
            
            destinatario = evaluador.get('email')
            if not destinatario or '@' not in destinatario:
                fallidos += 1
                continue
                
            evaluador_nombre = f"{evaluador.get('nombres','')} {evaluador.get('apellidos','')}".strip() or "Colaborador"
            evaluado_nombre = f"{evaluado.get('nombres','')} {evaluado.get('apellidos','')}".strip() or "Colaborador"
            tipo_eval = t.get('tipo', 'Evaluación')
            link = f"https://www.skel360.online/evaluar?token={t['id']}"
            
            asunto = f"Invitación a proceso de Evaluación 360° - {tipo_eval}"
            html_content = f"""
            <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
                <div style="text-align: center; margin-bottom: 20px; border-bottom: 2px solid #3b82f6; padding-bottom: 15px;">
                    <h2 style="color: #1e293b; margin: 0;">SKEL Human Capital 360</h2>
                    <p style="color: #64748b; font-size: 0.9rem; margin-top: 5px;">Proceso de Evaluación del Desempeño</p>
                </div>
                <div style="color: #334155; font-size: 1rem; line-height: 1.6;">
                    <p>Hola, <strong>{evaluador_nombre}</strong> 👋</p>
                    <p>Has sido asignado(a) para participar en el proceso de <strong>Evaluación 360°</strong> de la institución.</p>
                    <div style="background: #f8fafc; border-left: 4px solid #3b82f6; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        <p style="margin: 0; font-weight: 600; color: #1e3a8a;">📋 Detalle de la Asignación:</p>
                        <ul style="margin: 10px 0 0 20px; padding: 0; color: #475569;">
                            <li><strong>Tipo de Evaluación:</strong> {tipo_eval}</li>
                            <li><strong>Evaluando a:</strong> {evaluado_nombre}</li>
                        </ul>
                    </div>
                    <p>El propósito de esta evaluación es identificar fortalezas y oportunidades de mejora para impulsar el desarrollo profesional continuo. Tus respuestas son totalmente confidenciales.</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{link}" target="_blank" style="background-color: #10b981; color: white; padding: 14px 28px; font-weight: bold; border-radius: 8px; text-decoration: none; display: inline-block; font-size: 1rem; box-shadow: 0 4px 6px rgba(16,185,129,0.2);">
                            🚀 Iniciar Evaluación Ahora
                        </a>
                    </div>
                    <p style="font-size: 0.85rem; color: #94a3b8; text-align: center;">Si el botón no funciona, ingresa a este enlace:<br><a href="{link}" style="color: #3b82f6;">{link}</a></p>
                </div>
                <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #f1f5f9; text-align: center; font-size: 0.8rem; color: #94a3b8;">
                    Este es un mensaje automático generado por el sistema SKEL HC 360.
                </div>
            </div>
            """
            
            res_envio = send_email(destinatario, asunto, html_content)
            if res_envio:
                enviados += 1
            else:
                fallidos += 1
                
        return jsonify({
            "status": "success", 
            "message": f"Proceso finalizado. Enviados: {enviados}, Fallidos/Sin correo: {fallidos}",
            "enviados": enviados,
            "fallidos": fallidos
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
