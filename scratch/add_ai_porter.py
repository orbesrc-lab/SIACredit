import os
import re

file_path = r'c:\SIAC\routes\business.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

ai_porter_route = """
@business_bp.route('/api/business/ai_porter', methods=['POST'])
def ai_porter_analysis():
    try:
        payload = request.json
        forces = payload.get('forces', {})
        
        prompt = f'''
        Actúa como un experto en estrategia corporativa y Análisis de las 5 Fuerzas de Porter.
        Evalúa la siguiente industria/empresa según las descripciones proporcionadas para cada fuerza.
        Si alguna fuerza está vacía, asume un escenario estándar o deduce la presión basada en el contexto general.
        
        1. Rivalidad: {forces.get('rivalidad', '')}
        2. Proveedores: {forces.get('proveedores', '')}
        3. Clientes: {forces.get('clientes', '')}
        4. Entrantes: {forces.get('entrantes', '')}
        5. Sustitutos: {forces.get('sustitutos', '')}
        
        Debes devolver un análisis estructurado estrictamente en formato JSON con la siguiente estructura (y nada más que el JSON puro, sin backticks de markdown):
        {{
            "scores": {{
                "Rivalidad": <número 1-10>,
                "Poder Proveedores": <número 1-10>,
                "Poder Clientes": <número 1-10>,
                "Nuevos Entrantes": <número 1-10>,
                "Sustitutos": <número 1-10>
            }},
            "strategic_advice": "Una conclusión estratégica de máximo 3 párrafos sobre cómo la empresa debería posicionarse ante estas fuerzas."
        }}
        Recuerda: 10 significa máxima presión/amenaza, 1 significa mínima presión/amenaza.
        '''
        
        import google.generativeai as genai
        import json
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        result = json.loads(text)
        
        return jsonify({'status': 'success', 'analysis': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
"""

if "def ai_porter_analysis" not in content:
    content += "\n" + ai_porter_route
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("ai_porter route added")
