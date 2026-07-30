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
        factors = supabase.table('factors').select("*, characteristics(id, name, weight)").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        evals = supabase.table('evaluations').select("char_id, rating").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        eval_map = {e['char_id']: e['rating'] for e in evals}
        
        if not factors:
            return jsonify({'error': 'No hay factores de autoevaluación registrados para analizar.'}), 404
            
        # 2. Build the context string for the AI
        context_lines = []
        for f in factors:
            factor_name = f.get('name', 'Desconocido')
            context_lines.append(f"FACTOR: {factor_name}")
            for c in f.get('characteristics', []):
                char_name = c.get('name', 'Desconocido')
                rating = eval_map.get(c['id'], 0)
                if rating > 0:
                    context_lines.append(f" - CARACTERISTICA: {char_name} (Calificación: {rating}/5)")
                    
        evaluation_text = "\n".join(context_lines)
        if not evaluation_text.strip():
            return jsonify({'error': 'No hay características evaluadas aún.'}), 404
            
        # 3. Prompt for Gemini
        prompt = f'''
Actúa como un Consultor Estratégico Senior B2B experto en análisis organizacional.
A continuación te presento los resultados de la autoevaluación de una organización. Los factores y características tienen calificaciones de 1 a 5 (donde 5 es excelente y 1 es crítico).

DATOS DE AUTOEVALUACIÓN:
{evaluation_text}

Tu objetivo es clasificar estas características en los cuadrantes de las matrices MEFI y MEFE.
Reglas estrictas:
1. INTERNAL vs EXTERNAL: Clasifica cada característica como Interna (bajo el control de la empresa, ej. Talento Humano, Procesos, Finanzas) o Externa (fuera del control directo, ej. Competencia, Mercado, Regulaciones, Macroeconomía).
2. STRENGTH vs WEAKNESS (Para Internas): Si la calificación original es de 3.5 o superior, es Fortaleza. Si es menor a 3.5, es Debilidad.
3. OPPORTUNITY vs THREAT (Para Externas): Si la calificación original es 3.5 o superior, es Oportunidad. Si es menor, es Amenaza.
4. CALIFICACIÓN (1-4): Convierte la nota original (1-5) a la escala de matrices (1-4).
   - Para Fortalezas: 4 (Mayor), 3 (Menor).
   - Para Debilidades: 1 (Mayor), 2 (Menor).
   - Para Oportunidades: 4 (Mayor), 3 (Menor).
   - Para Amenazas: 1 (Mayor), 2 (Menor).
5. PESO: Asigna un peso (ponderación) lógico a cada ítem de 0 a 1 (ej. 0.15). La suma de los pesos de MEFI (Fortalezas + Debilidades) DEBE SER EXACTAMENTE 1.0. La suma de los pesos de MEFE (Oportunidades + Amenazas) DEBE SER EXACTAMENTE 1.0.

Responde ÚNICAMENTE con un JSON válido con esta estructura estricta (no agregues texto fuera del JSON, ni markdown de bloques de código si puedes evitarlo, solo el JSON puro):
{{
  "mefi": {{
    "fortalezas": [
      {{"name": "nombre resumido", "weight": 0.15, "rating": 4}}, ...
    ],
    "debilidades": [
      {{"name": "nombre resumido", "weight": 0.1, "rating": 1}}, ...
    ]
  }},
  "mefe": {{
    "oportunidades": [
      {{"name": "nombre resumido", "weight": 0.2, "rating": 4}}, ...
    ],
    "amenazas": [
      {{"name": "nombre resumido", "weight": 0.1, "rating": 2}}, ...
    ]
  }}
}}
'''
        # 4. Call AI
        ai_response = call_ai(prompt)
        
        # Clean potential markdown formatting
        cleaned_response = ai_response.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]
            
        parsed_data = json.loads(cleaned_response.strip())
        
        return jsonify(parsed_data)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
