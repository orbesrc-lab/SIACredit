from flask import Blueprint, jsonify, request, current_app
import traceback
import json
from datetime import datetime

try:
    from utils.db import supabase
except ImportError:
    supabase = None

skel_evaluaciones_bp = Blueprint('skel_evaluaciones', __name__, url_prefix='/api/skel360/evaluaciones')

def get_supabase():
    global supabase
    if supabase is None:
        from app import supabase as app_supabase
        supabase = app_supabase
    return supabase

# ==============================================================================
# Endpoint 1: Obtener Formulario Dinámico (Matriz Cruzada con Cargo)
# ==============================================================================

@skel_evaluaciones_bp.route('/<version_id>/colaborador/<colaborador_id>/formulario', methods=['GET'])
def get_formulario_dinamico(version_id, colaborador_id):
    """
    Este endpoint devuelve el formulario completo. 
    Para la sección de "Matriz de Competencias", solo devuelve las competencias
    asociadas al cargo del colaborador.
    """
    try:
        sb = get_supabase()
        
        # 1. Obtener datos del colaborador y su cargo
        res_col = sb.table('skel_colaboradores').select('cargo_id').eq('id', colaborador_id).execute()
        if not res_col.data:
            return jsonify({"status": "error", "message": "Colaborador no encontrado"}), 404
            
        cargo_id = res_col.data[0]['cargo_id']
        
        # 2. Obtener las secciones de esta versión
        res_secciones = sb.table('skel_secciones_evaluacion').select('*').eq('version_id', version_id).order('orden').execute()
        secciones = res_secciones.data
        
        # 3. Obtener competencias asignadas a este cargo (Para la Matriz Integral)
        # Esto reduce el tiempo de respuesta del colaborador mostrando solo lo relevante
        res_comps = sb.table('skel_cargos_competencias').select('competencia_id, skel_competencias(*)').eq('cargo_id', cargo_id).execute()
        competencias_cargo = res_comps.data

        # 4. Obtener las preguntas estándar
        res_pregs = sb.table('skel_seccion_preguntas').select('*, skel_preguntas(*)').in_('seccion_id', [s['id'] for s in secciones]).order('orden').execute()

        # Armar el payload
        payload = {
            "version_id": version_id,
            "colaborador_id": colaborador_id,
            "secciones": []
        }
        
        for sec in secciones:
            sec_data = {
                "id": sec['id'],
                "nombre": sec['nombre'],
                "tipo": sec['tipo'],
                "preguntas": []
            }
            
            if sec['tipo'] == 'MatrizCompetencias':
                sec_data['competencias'] = [c['skel_competencias'] for c in competencias_cargo if c['skel_competencias']]
            else:
                sec_data['preguntas'] = [p['skel_preguntas'] for p in res_pregs.data if p['seccion_id'] == sec['id']]
                
            payload['secciones'].append(sec_data)

        return jsonify({"status": "success", "data": payload})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ==============================================================================
# Endpoint 2: Guardar Respuestas de la Matriz Integral
# ==============================================================================

@skel_evaluaciones_bp.route('/<version_id>/colaborador/<colaborador_id>/respuestas_matriz', methods=['POST'])
def save_respuestas_matriz(version_id, colaborador_id):
    """
    Recibe las respuestas de las 5 dimensiones de la Matriz Integral de Competencias
    y las almacena en la tabla especializada con fecha histórica.
    """
    try:
        data = request.json
        respuestas = data.get('respuestas', []) # Lista de diccionarios
        sb = get_supabase()
        
        insert_data = []
        fecha_actual = datetime.utcnow().isoformat()
        
        for r in respuestas:
            # Cálculo de brecha: Importancia (lo que se requiere) - Nivel actual
            # (Ej: Si cargo exige Importancia 5 y Nivel Actual es 2 -> Brecha = 3)
            imp = int(r.get('importancia', 0))
            niv = int(r.get('nivel_actual', 0))
            brecha = max(0, imp - niv) 
            
            insert_data.append({
                "colaborador_id": colaborador_id,
                "version_id": version_id,
                "competencia_id": r.get('competencia_id'),
                "fecha": fecha_actual,
                "importancia": imp,
                "nivel_actual": niv,
                "frecuencia_uso": int(r.get('frecuencia_uso', 0)),
                "impacto_mejora": int(r.get('impacto_mejora', 0)),
                "prioridad_capacitacion": int(r.get('prioridad_capacitacion', 0)),
                "brecha_competencia": brecha
                # El índice IPF se puede calcular aquí o dejar a la base de datos/motor analítico
            })
            
        res = sb.table('skel_respuestas_matriz_competencias').insert(insert_data).execute()
        return jsonify({"status": "success", "message": "Respuestas de matriz guardadas exitosamente", "data": res.data}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ==============================================================================
# Endpoint 3: Motor Analítico e IA (Fases 5 y 6)
# ==============================================================================

@skel_evaluaciones_bp.route('/empresa/<empresa_id>/informe-ia', methods=['GET'])
def generar_informe_ia(empresa_id):
    """
    Este endpoint representa el Motor Analítico y de IA.
    1. Extrae todas las respuestas de la matriz de la empresa.
    2. Calcula el IPF (Índice de Prioridad de Formación).
    3. Construye un prompt avanzado y llama a la IA para generar el informe justificado.
    """
    try:
        from routes.ai import call_ai
        sb = get_supabase()
        
        # 1. Obtener colaboradores de la empresa
        res_colabs = sb.table('skel_colaboradores').select('id, nombre').eq('empresa_id', empresa_id).execute()
        if not res_colabs.data:
            return jsonify({"status": "error", "message": "La empresa no tiene colaboradores registrados."}), 404
            
        colab_ids = [c['id'] for c in res_colabs.data]
        
        # 2. Obtener las respuestas de la matriz para estos colaboradores
        res_resp = sb.table('skel_respuestas_matriz_competencias').select('*, skel_competencias(nombre, bloque)').in_('colaborador_id', colab_ids).execute()
        
        if not res_resp.data:
            return jsonify({"status": "error", "message": "No hay datos de evaluaciones (respuestas) para generar el informe."}), 404

        # 3. MOTOR ANALÍTICO: Procesar datos y calcular IPF (Índice de Prioridad de Formación)
        analisis_competencias = {}
        for r in res_resp.data:
            comp_id = r['competencia_id']
            comp_nombre = r['skel_competencias']['nombre']
            bloque = r['skel_competencias']['bloque']
            
            brecha = r.get('brecha_competencia', 0)
            frecuencia = r.get('frecuencia_uso', 1)
            impacto = r.get('impacto_mejora', 1)
            prioridad_colab = r.get('prioridad_capacitacion', 1)
            
            # Fórmula matemática para IPF
            ipf = brecha * frecuencia * impacto * prioridad_colab
            
            if comp_id not in analisis_competencias:
                analisis_competencias[comp_id] = {
                    "nombre": comp_nombre,
                    "bloque": bloque,
                    "total_ipf": 0,
                    "conteo": 0,
                    "brecha_promedio": 0
                }
            
            analisis_competencias[comp_id]['total_ipf'] += ipf
            analisis_competencias[comp_id]['brecha_promedio'] += brecha
            analisis_competencias[comp_id]['conteo'] += 1
            
        # Calcular promedios para ordenar
        resultados_finales = []
        for c_id, data in analisis_competencias.items():
            if data['conteo'] > 0:
                ipf_promedio = data['total_ipf'] / data['conteo']
                brecha_prom = data['brecha_promedio'] / data['conteo']
                if brecha_prom > 0: # Solo si hay brecha real
                    resultados_finales.append({
                        "competencia": data['nombre'],
                        "bloque": data['bloque'],
                        "ipf": round(ipf_promedio, 2),
                        "brecha": round(brecha_prom, 2)
                    })
                    
        # Ordenar por el IPF de mayor a menor (Las mayores necesidades primero)
        resultados_finales.sort(key=lambda x: x['ipf'], reverse=True)
        top_brechas = resultados_finales[:10] # Tomar el Top 10 crítico
        
        # 4. MOTOR DE IA: Preparar el Prompt
        datos_json = json.dumps(top_brechas, ensure_ascii=False)
        
        prompt_system = (
            "Eres el Consultor Experto en Capital Humano de SKEL Human Capital 360. "
            "Tu objetivo es analizar un reporte matemático de brechas de competencias de una empresa "
            "y redactar un INFORME GERENCIAL altamente justificado y persuasivo. "
            "El informe debe explicar el riesgo de estas brechas, cómo impactan en la productividad, y "
            "debe concluir recomendando de manera convincente los SERVICIOS DE CONSULTORÍA Y FORMACIÓN DE SKEL "
            "como la solución ideal para cerrar estas brechas y optimizar sus labores."
        )
        
        prompt_user = f"Aquí están las 10 competencias más críticas calculadas mediante el Índice de Prioridad de Formación (IPF):\n{datos_json}\n\nPor favor, genera el informe justificado."
        
        messages = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user}
        ]
        
        # 5. Llamar a la IA
        informe_generado = call_ai(messages)
        
        # 6. Guardar en Base de Datos (Opcional, para historial en una tabla futura)
        # Por ahora lo retornamos al frontend para su visualización.
        
        return jsonify({
            "status": "success", 
            "data": {
                "top_brechas": top_brechas,
                "informe_ia": informe_generado
            }
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ==============================================================================
# Endpoint 4: Logística - Generación de Magic Links (Lanzamiento)
# ==============================================================================

@skel_evaluaciones_bp.route('/empresa/<empresa_id>/evaluacion/<evaluacion_id>/lanzar', methods=['POST'])
def lanzar_encuestas(empresa_id, evaluacion_id):
    try:
        sb = get_supabase()
        empresa_res = sb.table('skel_empresas').select('habilitar_magic_links').eq('id', empresa_id).execute()
        if not empresa_res.data or not empresa_res.data[0].get('habilitar_magic_links'):
            return jsonify({'status': 'error', 'message': 'La empresa no tiene habilitados los Magic Links.'}), 403

        colabs_res = sb.table('skel_colaboradores').select('id, email').eq('empresa_id', empresa_id).execute()
        if not colabs_res.data:
            return jsonify({'status': 'error', 'message': 'No hay colaboradores registrados.'}), 404

        insert_data = []
        for c in colabs_res.data:
            insert_data.append({
                'empresa_id': empresa_id,
                'colaborador_id': c['id'],
                'evaluacion_id': evaluacion_id,
                'tipo': 'MagicLink',
                'estado': 'Pendiente'
            })
            
        tokens_res = sb.table('skel_tokens_acceso').insert(insert_data).execute()
        
        return jsonify({
            'status': 'success', 
            'message': f'Se generaron {len(insert_data)} Magic Links exitosamente.',
            'data': tokens_res.data
        }), 201
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==============================================================================
# Endpoint 5: Logística - Login de Kiosco (Por Cédula)
# ==============================================================================

@skel_evaluaciones_bp.route('/kiosco/login', methods=['POST'])
def kiosco_login():
    try:
        data = request.json
        empresa_id = data.get('empresa_id')
        documento = data.get('documento')
        evaluacion_id = data.get('evaluacion_id')
        
        if not empresa_id or not documento or not evaluacion_id:
            return jsonify({'status': 'error', 'message': 'Faltan datos obligatorios.'}), 400
            
        sb = get_supabase()
        
        empresa_res = sb.table('skel_empresas').select('habilitar_kiosco_qr').eq('id', empresa_id).execute()
        if not empresa_res.data or not empresa_res.data[0].get('habilitar_kiosco_qr'):
            return jsonify({'status': 'error', 'message': 'El modo Kiosco no está habilitado.'}), 403

        colabs_res = sb.table('skel_colaboradores').select('id, nombre').eq('empresa_id', empresa_id).eq('documento_identidad', documento).execute()
        
        if hasattr(colabs_res, 'message') and 'documento_identidad' in str(colabs_res.message):
            return jsonify({'status': 'error', 'message': 'Actualizar esquema DB con documento_identidad.'}), 400

        if not colabs_res.data:
            return jsonify({'status': 'error', 'message': 'Identificación no encontrada.'}), 404
            
        colaborador_id = colabs_res.data[0]['id']
        
        token_data = {
            'empresa_id': empresa_id,
            'colaborador_id': colaborador_id,
            'evaluacion_id': evaluacion_id,
            'tipo': 'KioscoSession',
            'estado': 'En Progreso'
        }
        
        tokens_res = sb.table('skel_tokens_acceso').insert(token_data).execute()
        
        return jsonify({
            'status': 'success', 
            'message': f'Bienvenido, {colabs_res.data[0]["nombre"]}',
            'token': tokens_res.data[0]['id']
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500
