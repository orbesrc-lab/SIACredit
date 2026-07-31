import os

file_path = r'c:\SIAC\routes\business.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

iso_route_code = """
@business_bp.route('/api/business/iso9001_generate', methods=['POST'])
def generate_iso9001_ai():
    try:
        payload = request.json
        inst_id = payload.get('inst_id')
        action_type = payload.get('action_type', 'all') # 'all', 'policy', 'sipoc', 'act'
        process_name = payload.get('process_name', '')
        
        # 1. Fetch DOFA & Porter for strategic context
        dofa_res = supabase.table('statistics').select('data_json').eq('table_id', 'DOFA_MATRIX').eq('inst_id', inst_id).order('id', desc=True).limit(1).execute()
        porter_res = supabase.table('statistics').select('data_json').eq('table_id', 'PORTER').eq('inst_id', inst_id).order('id', desc=True).limit(1).execute()
        
        context_text = ""
        if dofa_res.data:
            context_text += "DOFA Context: " + str(dofa_res.data[0]['data_json']) + "\\n"
        if porter_res.data:
            context_text += "Porter Context: " + str(porter_res.data[0]['data_json']) + "\\n"
            
        import google.generativeai as genai
        import json
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if action_type == 'policy':
            prompt = f'''
            Actúa como Auditor Líder ISO 9001:2015.
            Basándote en el siguiente contexto estratégico organizacional:
            {context_text}
            
            Redacta:
            1. Una Política de Calidad formal, comprometiéndose con la satisfacción del cliente y la mejora continua.
            2. 4 Objetivos de Calidad medibles y alineados con la política.
            
            Responde ÚNICAMENTE en JSON estructurado (sin backticks de markdown):
            {{
                "politica": "Texto de la política...",
                "objetivos": ["Objetivo 1...", "Objetivo 2...", "Objetivo 3...", "Objetivo 4..."]
            }}
            '''
        elif action_type == 'act':
            prompt = f'''
            Actúa como Auditor Líder ISO 9001:2015.
            Evalúa el proceso '{process_name}' bajo el ciclo PHVA con los siguientes datos:
            {payload.get('process_data', {})}
            
            Genera un informe de evaluación de auditoría y propone 3 Acciones de Mejora Correctivas/Preventivas (ISO 9001 Cláusula 10).
            
            Responde ÚNICAMENTE en JSON estructurado (sin backticks):
            {{
                "evaluacion_auditor": "Diagnóstico de cumplimiento del proceso...",
                "acciones_mejora": [
                    {{"accion": "...", "causa_raiz": "...", "responsable": "...", "plazo": "..."}},
                    {{"accion": "...", "causa_raiz": "...", "responsable": "...", "plazo": "..."}}
                ]
            }}
            '''
        else:
            prompt = f'''
            Actúa como Auditor Líder ISO 9001:2015.
            Basándote en el contexto estratégico: {context_text}
            Genera la estructura de un Sistema de Gestión de Calidad ISO 9001:
            - Política de Calidad
            - 4 Objetivos de Calidad
            - Mapa de Procesos (Estratégicos, Misionales, Apoyo)
            
            Responde ÚNICAMENTE en JSON estructurado (sin backticks):
            {{
                "politica": "...",
                "objetivos": ["..."],
                "procesos": {{
                    "estrategicos": ["Gestión de la Dirección", "Aseguramiento de Calidad y Riesgos"],
                    "misionales": ["Gestión Académica y Docencia", "Investigación e Innovación", "Proyección Social y Extensión"],
                    "apoyo": ["Gestión del Talento Humano", "Tecnología y Sistemas (TI)", "Gestión Financiera", "Infraestructura"]
                }}
            }}
            '''
            
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        result = json.loads(text)
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
"""

if "def generate_iso9001_ai" not in content:
    content += "\n" + iso_route_code

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("iso9001_generate AI backend route added to business.py")
