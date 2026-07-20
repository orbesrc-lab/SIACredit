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
Tu tarea es estructurar un evento de formación tipo "{data.get('type', 'curso')}" titulado "{data.get('name')}".
Modalidad: {data.get('modality', 'Virtual')} | Nivel: {data.get('level', 'Intermedio')} | Horas totales de duración: {data.get('duration')}
Descripción general: {data.get('description')}
Competencia General: {data.get('general_competence')}
Competencias Específicas: {', '.join(data.get('specific_competencies', []))}

INSTRUCCIÓN CRÍTICA:
Genera la estructura de UNIDADES TEMÁTICAS y sus respectivos TEMAS. El número de unidades, la cantidad de temas y el nivel de profundidad DEBEN SER ESTRICTAMENTE COHERENTES con las horas totales de duración y el tipo de evento (un taller corto de 4 horas no puede tener 10 unidades, mientras que un diplomado de 120 horas debe ser extenso y profundo). 
Distribuye las horas de forma lógica entre las unidades. La suma EXACTA de las horas de las unidades debe ser igual a {data.get('duration')}.
Además, genera un "forum_topic" (un mensaje o pregunta detonadora que servirá para abrir el Foro Principal de debate del curso).

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
  ],
  "forum_topic": "Pregunta o mensaje detonador para abrir el debate en el foro del curso."
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
    
    prompt = f"""Eres un Experto Disciplinar, Doctor en Educación y Diseñador Instruccional de alto nivel.
Estás escribiendo el contenido académico detallado para la unidad "{unit_info.get('name')}" del curso "{data.get('course_name')}".

La unidad contiene los siguientes temas que debes desarrollar MUY EXTENSAMENTE:
{', '.join(topics_list)}

Instrucciones CRÍTICAS de redacción para CADA TEMA:
1. Lenguaje y Tono: Escribe con un lenguaje docente, argumentativo, explicativo, claro y motivador. El texto debe guiar al estudiante como si fuera una clase magistral de alta calidad.
2. Extensión y Profundidad: PROHIBIDO reducirse a unas solas líneas o listas superficiales. Debes desarrollar cada tema de manera medianamente extensa, profunda y rigurosa, aportando contexto, fundamentos teóricos y análisis.
3. Ejemplos Prácticos: Es OBLIGATORIO incluir ejemplos claros, casos de estudio, analogías o aplicaciones reales para cada concepto abstracto que expliques.
4. Coherencia Evaluativa: Asegúrate de resaltar los conceptos clave que serán objeto de evaluación posteriormente.
5. Imágenes: NO INTENTES GENERAR IMÁGENES NI PONER ENLACES A IMÁGENES. En su lugar, cuando consideres que una imagen sería útil, escribe un "PROMPT DE IMAGEN" dentro del contenido (ej. [PROMPT SUGERIDO PARA IMAGEN: "Un diagrama mostrando la relación entre X y Y"]). Esto permitirá al profesor generarla externamente después.
6. Formato: Utiliza formato HTML semántico para estructurar el contenido (usa <h3>, <h4>, <p>, <ul>, <strong>, <em>, <blockquote>, etc.). No uses <html>, <head> o <body>.

Responde ÚNICAMENTE con un JSON válido con este formato:
{{
  "topics": [
    {{
      "title": "Nombre exacto del tema",
      "html_content": "<h3>Título del Tema</h3><p>Contenido explicativo, argumentativo y muy extenso en HTML, con al menos 3 a 5 párrafos bien desarrollados, seguidos de ejemplos claros y conclusiones. [PROMPT SUGERIDO PARA IMAGEN: '...']...</p>"
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
Crea exactamente 2 actividades prácticas (ej. Caso de estudio, Taller, Proyecto, Ejercicio práctico). 
CRÍTICO: NO crees Foros de debate como actividades (el foro tiene su propia sección separada).

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
    prompt = f"""Eres un Experto en Resultados de Aprendizaje, Taxonomía de Bloom y Evaluación Educativa.
Diseña 1 evaluación (Cuestionario, Examen o Rúbrica) para la unidad "{unit_info.get('name')}" del curso "{data.get('course_name')}".

CRÍTICO: La evaluación debe estar en ESTRICTA COHERENCIA con el contenido y los temas de la unidad. 
Describe detalladamente los criterios de evaluación, especificando qué habilidades, conceptos prácticos y teóricos se van a evaluar.

Responde ÚNICAMENTE en JSON con el formato:
{{
  "evaluations": [
    {{
      "name": "Nombre de la evaluación",
      "description": "Descripción extensa y argumentada de la evaluación. Detalla explícitamente cómo se conecta de forma coherente con el contenido de la unidad, qué tipo de preguntas o casos prácticos contendrá y cuáles son los criterios exactos que el estudiante debe cumplir.",
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

