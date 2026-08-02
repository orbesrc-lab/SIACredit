import os

ROUTES_FILE = r'c:\SIAC\routes\business.py'

NEW_ROUTE = """
@business_bp.route('/api/business/ai_expert_improve', methods=['POST'])
def ai_expert_improve():
    try:
        data = request.json
        original_text = data.get('text', '')
        
        prompt = f'''Eres un experto Doctor en Dirección Administrativa y Gerencia Estratégica.
Se te proporciona una sección de un Informe Gerencial Integral. Tu tarea es analizar, mejorar y elevar el tono de este texto a un nivel altamente profesional y ejecutivo, sin perder los datos originales.
Texto original:
{original_text}

Devuelve únicamente el texto mejorado en formato HTML (puedes usar <strong>, <ul>, etc.) o texto plano si prefieres, pero preferiblemente HTML limpio. No uses markdown.'''

        model = get_gemini_model()
        if not model:
            return jsonify({'status': 'error', 'error': 'AI not configured'}), 500
            
        response = model.generate_content(prompt)
        return jsonify({'status': 'success', 'improved_text': response.text})
    except Exception as e:
        print(f"Error in ai_expert_improve: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500
"""

def update_routes():
    with open(ROUTES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'def ai_expert_improve():' not in content:
        content += "\n" + NEW_ROUTE
        with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully added ai_expert_improve endpoint.")
    else:
        print("Endpoint already exists.")

if __name__ == '__main__':
    update_routes()
