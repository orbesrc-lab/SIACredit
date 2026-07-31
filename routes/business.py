import os
from flask import Blueprint, jsonify, request
from utils.db import supabase
from routes.ai import call_ai
import json

business_bp = Blueprint('business', __name__)

@business_bp.route('/api/business/matrix/<matrix_type>', methods=['GET'])
def get_matrix(matrix_type):
    try:
        inst_id = request.args.get('inst_id')
        if not inst_id:
            return jsonify({'error': 'inst_id is required'}), 400
            
        res = supabase.table('business_matrices').select('*').eq('inst_id', inst_id).eq('matrix_type', matrix_type.upper()).execute()
        if res.data:
            return jsonify(res.data[0])
        else:
            return jsonify({'data': {}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@business_bp.route('/api/business/matrix/<matrix_type>', methods=['POST'])
def save_matrix(matrix_type):
    try:
        payload = request.json
        inst_id = payload.get('inst_id')
        data = payload.get('data')
        results = payload.get('results')
        user_id = payload.get('user_id')
        
        import uuid
        
        user_id = payload.get('user_id')
        if user_id:
            try:
                # Validar que sea un UUID
                uuid.UUID(str(user_id))
            except ValueError:
                user_id = None
                
        if not inst_id:
            return jsonify({'error': 'inst_id is required'}), 400
            
        res = supabase.table('business_matrices').select('id').eq('inst_id', inst_id).eq('matrix_type', matrix_type.upper()).execute()
        
        if res.data:
            db_id = res.data[0]['id']
            update_res = supabase.table('business_matrices').update({
                'data': data,
                'results': results,
                'updated_at': 'now()'
            }).eq('id', db_id).execute()
            return jsonify({'status': 'success', 'message': 'Matrix updated'})
        else:
            insert_res = supabase.table('business_matrices').insert({
                'inst_id': inst_id,
                'matrix_type': matrix_type.upper(),
                'data': data,
                'results': results,
                'created_by': user_id
            }).execute()
            return jsonify({'status': 'success', 'message': 'Matrix created'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@business_bp.route('/api/business/ai_dofa', methods=['POST'])
def generate_ai_dofa():
    try:
        payload = request.json
        inst_id = payload.get('inst_id')
        
        if not inst_id:
            return jsonify({'error': 'inst_id is required'}), 400
            
        # Fetch MEFI and MEFE
        mefi_res = supabase.table('business_matrices').select('data').eq('inst_id', inst_id).eq('matrix_type', 'MEFI').execute()
        mefe_res = supabase.table('business_matrices').select('data').eq('inst_id', inst_id).eq('matrix_type', 'MEFE').execute()
        
        if not mefi_res.data or not mefe_res.data:
            return jsonify({'error': 'Las matrices MEFI y MEFE deben estar guardadas previamente.'}), 400
            
        mefi_data = mefi_res.data[0].get('data', {}).get('factors', [])
        mefe_data = mefe_res.data[0].get('data', {}).get('factors', [])
        
        fortalezas = [f"{f['factor']} (Peso: {f['weight']}, Calificación: {f['rating']})" for f in mefi_data if f['type'] == 'fortaleza']
        debilidades = [f"{f['factor']} (Peso: {f['weight']}, Calificación: {f['rating']})" for f in mefi_data if f['type'] == 'debilidad']
        oportunidades = [f"{f['factor']} (Peso: {f['weight']}, Calificación: {f['rating']})" for f in mefe_data if f['type'] == 'oportunidad']
        amenazas = [f"{f['factor']} (Peso: {f['weight']}, Calificación: {f['rating']})" for f in mefe_data if f['type'] == 'amenaza']
        
        system_prompt = "Eres un consultor estratégico experto (nivel McKinsey/BCG). Tu tarea es tomar matrices MEFI y MEFE empresariales y generar una Matriz DOFA Cruzada (TOWS) con estrategias accionables de alto impacto."
        user_prompt = f"""
Basado en los siguientes factores de la empresa:

FORTALEZAS:
{chr(10).join(fortalezas) if fortalezas else 'Ninguna registrada'}

DEBILIDADES:
{chr(10).join(debilidades) if debilidades else 'Ninguna registrada'}

OPORTUNIDADES:
{chr(10).join(oportunidades) if oportunidades else 'Ninguna registrada'}

AMENAZAS:
{chr(10).join(amenazas) if amenazas else 'Ninguna registrada'}

Por favor genera un reporte estructurado en Markdown que incluya:
1. Resumen Diagnóstico (1 párrafo)
2. Estrategias FO (Fortalezas + Oportunidades): Cómo usar fortalezas para aprovechar oportunidades.
3. Estrategias DO (Debilidades + Oportunidades): Cómo superar debilidades aprovechando oportunidades.
4. Estrategias FA (Fortalezas + Amenazas): Cómo usar fortalezas para evitar amenazas.
5. Estrategias DA (Debilidades + Amenazas): Tácticas defensivas.
6. Recomendación Estratégica Principal.

Usa un tono profesional, directivo y altamente estratégico.
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        ai_response = call_ai(messages, max_tokens=2000, inst_id=inst_id)
        
        return jsonify({'status': 'success', 'analysis': ai_response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@business_bp.route('/api/business/auto-populate-matrices', methods=['POST'])
def auto_populate_matrices():
    try:
        payload = request.json
        inst_id = payload.get('inst_id')
        program_id = payload.get('program_id', 0)
        
        if not inst_id:
            return jsonify({'error': 'inst_id is required'}), 400
            
        # 1. Fetch current Autoevaluacion data
        factors = supabase.table('factors').select("*, characteristics(id, name, weight)").eq("inst_id", inst_id).execute().data if not program_id or int(program_id) == 0 else supabase.table('factors').select("*, characteristics(id, name, weight)").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        evals = supabase.table('evaluations').select("char_id, rating").eq("inst_id", inst_id).execute().data if not program_id or int(program_id) == 0 else supabase.table('evaluations').select("char_id, rating").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        eval_map = {e['char_id']: e['rating'] for e in evals}
        
        if not factors:
            return jsonify({'error': 'No hay factores de autoevaluación registrados para analizar.'}), 404
            
        # 2. Build the MEFI matrix deterministically (Autoevaluacion is mostly Internal)
        # We will map them directly without using AI to save tokens.
        
        fortalezas = []
        debilidades = []
        
        # To calculate relative weights properly
        total_items = 0
        
        for f in factors:
            for c in f.get('characteristics', []):
                rating = eval_map.get(c['id'], 0)
                if rating > 0:
                    total_items += 1
                    
        if total_items == 0:
            return jsonify({'error': 'No hay características evaluadas aún.'}), 404
            
        base_weight = round(1.0 / total_items, 2)
        
        for f in factors:
            for c in f.get('characteristics', []):
                rating = eval_map.get(c['id'], 0)
                if rating > 0:
                    char_name = c.get('name', 'Desconocido')
                    # Scale 1-5 to 1-4 for matrix
                    # 5 -> 4, 4 -> 3, 3 -> 2, 1-2 -> 1
                    matrix_rating = 1
                    if rating >= 4.5:
                        matrix_rating = 4
                    elif rating >= 3.5:
                        matrix_rating = 3
                    elif rating >= 2.5:
                        matrix_rating = 2
                    else:
                        matrix_rating = 1
                        
                    item = {
                        "name": char_name,
                        "weight": base_weight,
                        "rating": matrix_rating
                    }
                    
                    if rating >= 3.5:
                        fortalezas.append(item)
                    else:
                        debilidades.append(item)
                        
        # 3. Return the JSON structure directly
        parsed_data = {
            "mefi": {
                "fortalezas": fortalezas,
                "debilidades": debilidades
            },
            "mefe": {
                "oportunidades": [],
                "amenazas": []
            }
        }
        
        return jsonify(parsed_data)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@business_bp.route('/api/business/populate-from-dofa-pesta', methods=['POST'])
def populate_from_dofa_pesta():
    try:
        payload = request.json
        inst_id = payload.get('inst_id')
        program_id = payload.get('program_id', 0)
        
        if not inst_id:
            return jsonify({'error': 'inst_id is required'}), 400
            
        # 1. Fetch DOFA_INTERNAL
        dofa_int_res = supabase.table('statistics').select('data_json').eq('table_id', 'DOFA_INTERNAL').eq('inst_id', inst_id).order('id', desc=True).limit(1).execute()
        
        # 2. Fetch DOFA_EXTERNAL (PESTA)
        dofa_ext_res = supabase.table('statistics').select('data_json').eq('table_id', 'DOFA_EXTERNAL').eq('inst_id', inst_id).order('id', desc=True).limit(1).execute()
        
        if not dofa_int_res.data and not dofa_ext_res.data:
            return jsonify({'error': 'No se encontraron diagnósticos previos (DOFA o PESTA) para esta institución.'}), 404
            
        fortalezas = []
        debilidades = []
        oportunidades = []
        amenazas = []
        
        # Parse DOFA INTERNAL (Fortalezas y Debilidades)
        if dofa_int_res.data:
            dofa_data = dofa_int_res.data[0].get('data_json', {})
            if isinstance(dofa_data, str):
                dofa_data = json.loads(dofa_data)
                
            forts = dofa_data.get('fortalezas', [])
            debs = dofa_data.get('debilidades', [])
            
            # Asignar peso equitativo base
            total_int = len(forts) + len(debs)
            peso_int = round(1.0 / total_int, 2) if total_int > 0 else 0
            
            for item in forts:
                # Si item es un string o dict
                name = item if isinstance(item, str) else item.get('description', str(item))
                fortalezas.append({"name": name, "weight": peso_int, "rating": 3}) # rating default 3 o 4 (fuerte)
                
            for item in debs:
                name = item if isinstance(item, str) else item.get('description', str(item))
                debilidades.append({"name": name, "weight": peso_int, "rating": 2}) # rating default 1 o 2 (débil)
                
        # Parse DOFA EXTERNAL / PESTA (Oportunidades y Amenazas)
        if dofa_ext_res.data:
            pesta_data = dofa_ext_res.data[0].get('data_json', {})
            if isinstance(pesta_data, str):
                pesta_data = json.loads(pesta_data)
                
            opts = pesta_data.get('oportunidades', [])
            ams = pesta_data.get('amenazas', [])
            
            total_ext = len(opts) + len(ams)
            peso_ext = round(1.0 / total_ext, 2) if total_ext > 0 else 0
            
            for item in opts:
                name = item if isinstance(item, str) else item.get('description', item.get('factor', str(item)))
                oportunidades.append({"name": name, "weight": peso_ext, "rating": 3})
                
            for item in ams:
                name = item if isinstance(item, str) else item.get('description', item.get('factor', str(item)))
                amenazas.append({"name": name, "weight": peso_ext, "rating": 2})

        parsed_data = {
            "mefi": {
                "fortalezas": fortalezas,
                "debilidades": debilidades
            },
            "mefe": {
                "oportunidades": oportunidades,
                "amenazas": amenazas
            }
        }
        
        return jsonify(parsed_data)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@business_bp.route('/api/business/ai_informe_gerencial', methods=['POST'])
def ai_informe_gerencial():
    try:
        data = request.json
        inst_id = data.get('inst_id')
        
        # Load all matrices
        def get_matrix(table_id):
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT data FROM statistics 
                WHERE inst_id = %s AND table_id = %s
                ORDER BY created_at DESC LIMIT 1
            ''', (inst_id, table_id))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row['data'] if row else None
            
        mefi = get_matrix('MEFI')
        mefe = get_matrix('MEFE')
        porter = get_matrix('PORTER')
        riesgos = get_matrix('RIESGOS')
        stakeholders = get_matrix('STAKEHOLDERS')
        
        # Compile prompt context
        context_parts = []
        
        if mefi and 'factors' in mefi:
            context_parts.append("FACTORES INTERNOS (MEFI):\n" + "\n".join([f"- {f.get('type')}: {f.get('factor')} (Ponderado: {float(f.get('weight', 0))*float(f.get('rating', 0))})" for f in mefi['factors']]))
            
        if mefe and 'factors' in mefe:
            context_parts.append("FACTORES EXTERNOS (MEFE):\n" + "\n".join([f"- {f.get('type')}: {f.get('factor')} (Ponderado: {float(f.get('weight', 0))*float(f.get('rating', 0))})" for f in mefe['factors']]))
            
        if porter and 'analysis' in porter and 'scores' in porter['analysis']:
            context_parts.append("ANALISIS COMPETITIVO (PORTER):\n" + "\n".join([f"- {s.get('force')}: Presión {s.get('score')}/10 - {s.get('description')}" for s in porter['analysis']['scores']]))
            
        if riesgos and 'risks' in riesgos:
            context_parts.append("RIESGOS ESTRATEGICOS:\n" + "\n".join([f"- {r.get('categoria')}: {r.get('descripcion')} (Impacto {r.get('impacto')}, Probabilidad {r.get('probabilidad')})" for r in riesgos['risks']]))
            
        if stakeholders and 'stakeholders' in stakeholders:
            context_parts.append("STAKEHOLDERS CLAVE:\n" + "\n".join([f"- {s.get('nombre')}: Poder {s.get('poder')}, Interés {s.get('interes')} - {s.get('estrategia')}" for s in stakeholders['stakeholders']]))
            
        if not context_parts:
            return jsonify({'status': 'error', 'error': 'No hay datos suficientes de las herramientas para generar el informe.'})
            
        full_context = "\n\n".join(context_parts)
        
        prompt = f'''
Actúa como un Consultor Estratégico Senior.
Analiza la siguiente información extraída de múltiples herramientas de diagnóstico de una organización:

{full_context}

Tu objetivo es generar el **Informe Gerencial de Evaluación Organizacional** consolidado.
Debe ser formal, directo y estar estructurado en formato Markdown.

Estructura obligatoria:
# 1. Resumen Ejecutivo Integrado
# 2. Diagnóstico del Entorno Competitivo y Riesgos
# 3. Alineación de Grupos de Interés (Stakeholders)
# 4. Estrategia Global Recomendada (Combinando todos los hallazgos)
'''
        
        # We assume get_gemini_response exists in business.py
        ai_response = get_gemini_response(prompt)
        
        return jsonify({'status': 'success', 'analysis': ai_response})
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

