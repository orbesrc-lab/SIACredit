import os

filepath = "c:/SIAC/routes/business.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_endpoint = """
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
                    
        evaluation_text = "\\n".join(context_lines)
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
"""

if "def auto_populate_matrices():" not in content:
    content = content + "\n" + new_endpoint
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Added auto_populate_matrices to routes/business.py")
else:
    print("Endpoint already exists")
