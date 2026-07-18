from flask import Blueprint, request, jsonify
from routes.ai import call_ai
import json

ai_generator_bp = Blueprint('ai_generator', __name__)

def extract_json_from_response(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    start = text.find("{")
    if start == -1:
        start = text.find("[")
    end = text.rfind("}")
    if end == -1:
        end = text.rfind("]")
    if start != -1 and end != -1:
        return text[start:end+1]
    return text

@ai_generator_bp.route('/api/ai/course/structure', methods=['POST'])
def generate_course_structure():
    data = request.json
    prompt = f"""Eres un Diseñador Instruccional Experto y Especialista en Currículo. 
Tu tarea es estructurar un {data.get('type', 'curso')} titulado "{data.get('name')}".
Modalidad: {data.get('modality', 'Virtual')} | Nivel: {data.get('level', 'Intermedio')} | Horas: {data.get('duration')}
Descripción general: {data.get('description')}
Competencia General: {data.get('general_competence')}
Competencias Específicas: {', '.join(data.get('specific_competencies', []))}

Genera la estructura de UNIDADES TEMÁTICAS y sus respectivos TEMAS. Debes determinar el número adecuado de unidades, su nombre, distribución de horas, y los temas principales (3 a 5 temas por unidad).
La suma de horas debe ser igual a {data.get('duration')}.

Responde ÚNICAMENTE con un JSON válido con este formato:
{{
  "units": [
    {{
      "name": "Nombre de la unidad",
      "hours": 10,
      "topics": [
        "Título del Tema 1",
        "Título del Tema 2",
        "Título del Tema 3"
      ]
    }}
  ]
}}
"""
    try:
        response_text = call_ai([{"role": "system", "content": "You are a helpful JSON generator AI."}, {"role": "user", "content": prompt}], max_tokens=1500)
        json_str = extract_json_from_response(response_text)
        return jsonify({"status": "success", "data": json.loads(json_str)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@ai_generator_bp.route('/api/ai/course/unit_content', methods=['POST'])
def generate_unit_content():
    data = request.json
    unit_info = data.get('unit_info', {})
    topics_list = unit_info.get('topics', ['Desarrollo Temático Principal'])
    
    prompt = f"""Eres un Experto Disciplinar y Doctor en Educación. 
Estás escribiendo el contenido académico detallado para la unidad "{unit_info.get('name')}" del curso "{data.get('course_name')}".

La unidad contiene los siguientes temas que debes desarrollar extensamente:
{', '.join(topics_list)}

Instrucciones de redacción para CADA TEMA:
- No escribas simples listas. Desarrolla el contenido académico de forma completa, profunda y pedagógica.
- Explica cada concepto detalladamente. Agrega ejemplos prácticos, casos de estudio o aplicaciones reales.
- Utiliza formato HTML para estructurar el contenido (usa <h3>, <h4>, <p>, <ul>, <strong>, <em>, etc.). No uses <html>, <head> o <body>.

Responde ÚNICAMENTE con un JSON válido con este formato:
{{
  "topics": [
    {{
      "title": "Nombre exacto del tema",
      "html_content": "<p>Contenido extenso en HTML...</p>"
    }}
  ]
}}
"""
    try:
        response_text = call_ai([{"role": "system", "content": "You are a helpful JSON generator AI."}, {"role": "user", "content": prompt}], max_tokens=6000)
        json_str = extract_json_from_response(response_text)
        return jsonify({"status": "success", "data": json.loads(json_str)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@ai_generator_bp.route('/api/ai/course/unit_activities', methods=['POST'])
def generate_unit_activities():
    data = request.json
    unit_info = data.get('unit_info', {})
    prompt = f"""Eres un Especialista en Aprendizaje por Competencias.
Diseña actividades de aprendizaje para la unidad "{unit_info.get('name')}" del curso "{data.get('course_name')}".
Crea exactamente 2 actividades variadas (ej. Actividad individual, Foro, Caso, Taller, Proyecto).

Responde ÚNICAMENTE en JSON con el formato:
{{
  "activities": [
    {{
      "name": "Nombre de la actividad",
      "description": "Instrucciones detalladas de la actividad, qué se debe entregar y cómo desarrollarlo.",
      "points": 15,
      "due_date": "2026-10-15"
    }}
  ]
}}
"""
    try:
        response_text = call_ai([{"role": "system", "content": "You are a JSON generator API."}, {"role": "user", "content": prompt}], max_tokens=1500)
        json_str = extract_json_from_response(response_text)
        return jsonify({"status": "success", "data": json.loads(json_str)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@ai_generator_bp.route('/api/ai/course/unit_evaluations', methods=['POST'])
def generate_unit_evaluations():
    data = request.json
    unit_info = data.get('unit_info', {})
    prompt = f"""Eres un Experto en Resultados de Aprendizaje y Taxonomía de Bloom.
Diseña 1 evaluación (Cuestionario o Examen o Rúbrica) para la unidad "{unit_info.get('name')}" del curso "{data.get('course_name')}".

Responde ÚNICAMENTE en JSON con el formato:
{{
  "evaluations": [
    {{
      "name": "Nombre de la evaluación",
      "description": "Descripción de la evaluación (qué evalúa, criterios).",
      "points": 20,
      "due_date": "2026-10-20"
    }}
  ]
}}
"""
    try:
        response_text = call_ai([{"role": "system", "content": "You are a JSON generator API."}, {"role": "user", "content": prompt}], max_tokens=1500)
        json_str = extract_json_from_response(response_text)
        return jsonify({"status": "success", "data": json.loads(json_str)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@ai_generator_bp.route('/api/ai/course/unit_resources', methods=['POST'])
def generate_unit_resources():
    data = request.json
    unit_info = data.get('unit_info', {})
    prompt = f"""Eres un Bibliotecario y Especialista en Educación Virtual.
Sugiéreme 3 recursos didácticos (artículos, videos, libros) para la unidad "{unit_info.get('name')}" del curso "{data.get('course_name')}".

REGLA CRÍTICA DE ORO: NUNCA inventes URLs directas a PDFs o sitios que no conoces, ya que suelen estar rotos o bloqueados por paywalls (cobro). 
DEBES proveer únicamente URLs reales, abiertas y gratuitas (Open Access). 
Para asegurar esto, genera enlaces de BÚSQUEDA automatizada que siempre funcionarán, por ejemplo:
- Para videos: usa https://www.youtube.com/results?search_query=PALABRAS+CLAVE
- Para artículos: usa https://scholar.google.com/scholar?q=PALABRAS+CLAVE
- O enlaces a enciclopedias públicas como Wikipedia.

Responde ÚNICAMENTE en JSON con el formato:
{{
  "resources": [
    {{
      "name": "Título descriptivo del recurso (ej. Video: Introducción a...)",
      "url": "https://www.youtube.com/results?search_query=...",
      "type": "video" 
    }}
  ]
}}
Los tipos permitidos son: video, audio, document, link.
"""
    try:
        response_text = call_ai([{"role": "system", "content": "You are a JSON generator API."}, {"role": "user", "content": prompt}], max_tokens=1500)
        json_str = extract_json_from_response(response_text)
        return jsonify({"status": "success", "data": json.loads(json_str)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@ai_generator_bp.route('/api/ai/course/unit_glossary', methods=['POST'])
def generate_unit_glossary():
    data = request.json
    unit_info = data.get('unit_info', {})
    prompt = f"""Crea un glosario breve y palabras clave para la unidad "{unit_info.get('name')}" del curso "{data.get('course_name')}".

Responde ÚNICAMENTE en JSON con el formato:
{{
  "topics": ["Palabra clave 1", "Palabra clave 2", "Palabra clave 3"],
  "glossary": [
    {{ "term": "Término 1", "definition": "Definición 1" }}
  ]
}}
"""
    try:
        response_text = call_ai([{"role": "system", "content": "You are a JSON generator API."}, {"role": "user", "content": prompt}], max_tokens=1500)
        json_str = extract_json_from_response(response_text)
        return jsonify({"status": "success", "data": json.loads(json_str)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@ai_generator_bp.route('/api/ai/course/improve', methods=['POST'])
def improve_content():
    data = request.json
    action = data.get('action') # 'improve', 'expand', 'simplify', 'examples'
    content = data.get('content')
    
    actions = {
        'improve': 'Mejora académicamente el siguiente texto, corrigiendo estilo y claridad.',
        'expand': 'Expande y profundiza el siguiente texto académico, añadiendo más detalles y explicaciones rigurosas.',
        'simplify': 'Simplifica el siguiente texto académico para que sea fácil de entender por un principiante.',
        'examples': 'Agrega ejemplos prácticos y casos ilustrativos al siguiente concepto.'
    }
    
    prompt = f"{actions.get(action, 'Mejora este texto')}:\n\n{content}\n\nResponde únicamente con el texto HTML resultante."
    
    try:
        response_text = call_ai([{"role": "system", "content": "Eres un editor académico experto."}, {"role": "user", "content": prompt}], max_tokens=2000)
        if response_text.startswith("```html"): response_text = response_text[7:]
        if response_text.endswith("```"): response_text = response_text[:-3]
        return jsonify({"status": "success", "data": response_text.strip()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

