from flask import Blueprint, request, jsonify
from routes.ai import call_ai
import json

ai_generator_bp = Blueprint('ai_generator', __name__)

def extract_json_from_response(text):
    import re
    import json
    text = text.strip()
    
    # Extract markdown block if present
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1).strip()
        
    # Find start of JSON
    start_idx = -1
    for i, char in enumerate(text):
        if char in ('{', '['):
            start_idx = i
            break
            
    if start_idx == -1:
        return text
        
    text = text[start_idx:]
    
    try:
        # Fix common JSON errors like trailing commas
        text = re.sub(r',\s*([\]}])', r'\1', text)
        # raw_decode(strict=False) allows unescaped control characters like literal newlines inside strings
        obj, end = json.JSONDecoder(strict=False).raw_decode(text)
        return json.dumps(obj)
    except Exception:
        # Fallback if raw_decode fails
        end_obj = text.rfind("}")
        end_arr = text.rfind("]")
        end_idx = max(end_obj, end_arr)
        if end_idx != -1:
            return text[:end_idx+1]
        return text

def generar_informe_ia_base(prompt, max_tokens=4500):
    """Wrapper para usar en endpoints internos sin necesidad de petición HTTP."""
    messages = [
        {"role": "system", "content": "Eres un experto asesor y gurú en Recursos Humanos y desarrollo de habilidades institucionales."},
        {"role": "user", "content": prompt}
    ]
    # Llama a call_ai y devuelve el texto directamente
    return call_ai(messages, max_tokens=max_tokens)

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

CRÍTICO PARA EL JSON: Asegúrate de que el resultado sea un JSON ESTRÍCTAMENTE VÁLIDO. Todas las propiedades deben estar entre comillas dobles ("). Si necesitas usar comillas dentro del contenido de texto, usa comillas simples ('). No dejes comas al final de las listas.

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
        return jsonify({"status": "success", "data": json.loads(json_str, strict=False)})
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
5. Imágenes: NO INTENTES GENERAR IMÁGENES NI PONER ENLACES A IMÁGENES. En su lugar, cuando consideres que una imagen sería útil, escribe un "PROMPT DE IMAGEN" dentro del contenido (ej. [PROMPT SUGERIDO PARA IMAGEN: 'Un diagrama mostrando la relación entre X y Y']). Esto permitirá al profesor generarla externamente después.
6. Formato: Utiliza formato HTML semántico para estructurar el contenido (usa <h3>, <h4>, <p>, <ul>, <strong>, <em>, <blockquote>, etc.). No uses <html>, <head> o <body>.
7. CRÍTICO PARA EL JSON: Asegúrate de que el resultado sea un JSON ESTRÍCTAMENTE VÁLIDO. Todas las propiedades (llaves) deben estar entre comillas dobles ("). NUNCA uses comillas dobles (") dentro del contenido HTML ni en los textos, ya que esto ROMPE EL JSON. Usa comillas simples (') para atributos HTML (ej. <h3 class='title'>) y para cualquier cita en el texto. Asegúrate de no dejar comas al final de las listas.
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
        return jsonify({"status": "success", "data": json.loads(json_str, strict=False)})
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

CRÍTICO PARA EL JSON: Asegúrate de que el resultado sea un JSON ESTRÍCTAMENTE VÁLIDO. Todas las propiedades deben estar entre comillas dobles ("). Si necesitas usar comillas dentro del contenido de texto, usa comillas simples ('). No dejes comas al final de las listas.

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
        return jsonify({"status": "success", "data": json.loads(json_str, strict=False)})
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

CRÍTICO PARA EL JSON: Asegúrate de que el resultado sea un JSON ESTRÍCTAMENTE VÁLIDO. Todas las propiedades deben estar entre comillas dobles ("). Si necesitas usar comillas dentro del contenido de texto, usa comillas simples ('). No dejes comas al final de las listas.

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
        return jsonify({"status": "success", "data": json.loads(json_str, strict=False)})
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
        return jsonify({"status": "success", "data": json.loads(json_str, strict=False)})
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
        return jsonify({"status": "success", "data": json.loads(json_str, strict=False)})
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


# =========================================================================
# NUEVOS ENDPOINTS: AUDITORÍA DE CONTENIDOS, AUTO-COMPLETADO Y PROMPTS NOTEBOOKLM
# =========================================================================

@ai_generator_bp.route('/api/ai/course/audit', methods=['POST'])
def audit_course_content():
    """Audita el contenido de todas las unidades del curso e identifica temas vacíos o inconclusos."""
    import formacion_storage
    data = request.json or {}
    course_id = data.get('course_id')
    inst_id = data.get('inst_id') or 1
    
    course = data.get('course')
    if not course and course_id:
        course = formacion_storage.load_course(course_id)
        
    if not course:
        return jsonify({"status": "error", "message": "Curso no encontrado"}), 404
        
    units = course.get('units', [])
    if isinstance(units, dict):
        units = list(units.values())
        
    audit_units = []
    total_topics = 0
    completed_topics = 0
    missing_topics = 0
    
    for u_idx, unit in enumerate(units):
        u_name = unit.get('name') or unit.get('title') or f"Unidad {u_idx+1}"
        topics = unit.get('topics', [])
        if isinstance(topics, dict):
            topics = list(topics.values())
            
        unit_topics = []
        for t_idx, raw_t in enumerate(topics):
            total_topics += 1
            if isinstance(raw_t, str):
                t_obj = {"id": f"t_{t_idx}", "title": raw_t, "content": "", "type": "text"}
            else:
                t_obj = raw_t
                
            title = t_obj.get('title') or f"Tema {t_idx+1}"
            content = t_obj.get('content') or ""
            content_len = len(content.strip())
            
            # Un tema se considera completo si tiene más de 250 caracteres
            is_complete = content_len > 250
            if is_complete:
                completed_topics += 1
                status = "completed"
            else:
                missing_topics += 1
                status = "missing"
                
            unit_topics.append({
                "unit_idx": u_idx,
                "topic_idx": t_idx,
                "id": t_obj.get('id', f"t_{t_idx}"),
                "title": title,
                "status": status,
                "content_len": content_len,
                "word_count": len(content.split()) if content else 0
            })
            
        audit_units.append({
            "unit_idx": u_idx,
            "unit_name": u_name,
            "total_topics": len(unit_topics),
            "completed": sum(1 for t in unit_topics if t['status'] == 'completed'),
            "missing": sum(1 for t in unit_topics if t['status'] == 'missing'),
            "topics": unit_topics
        })
        
    pct = round((completed_topics / total_topics * 100), 1) if total_topics > 0 else 0
    
    return jsonify({
        "status": "success",
        "data": {
            "course_id": course.get('id'),
            "course_title": course.get('title'),
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "missing_topics": missing_topics,
            "completeness_percentage": pct,
            "units": audit_units
        }
    })


@ai_generator_bp.route('/api/ai/course/develop_topic', methods=['POST'])
def develop_topic_content():
    """Genera clase magistral explicativa, ejemplarizante y argumentativa con IA para un tema específico."""
    import formacion_storage
    data = request.json or {}
    course_id = data.get('course_id')
    unit_idx = data.get('unit_idx')
    topic_idx = data.get('topic_idx')
    course_name = data.get('course_name') or 'Programa de Formación'
    unit_name = data.get('unit_name') or f'Unidad {int(unit_idx)+1 if unit_idx is not None else ""}'
    topic_title = data.get('topic_title') or 'Tema Principal'
    inst_id = data.get('inst_id') or 1
    program_id = data.get('program_id') or 0
    custom_instructions = data.get('custom_instructions') or ''
    
    prompt = f"""Actúa como un PROFESOR CATEDRÁTICO TITULAR, DOCTOR EN EL ÁREA Y EVALUADOR PAR ACADÉMICO de posgrados y alta gerencia.
Estás dictando la clase magistral correspondiente al tema:
📘 TEMA: "{topic_title}"
📚 UNIDAD: "{unit_name}"
🎓 CURSO / PROGRAMA: "{course_name}"

TU MISIÓN:
Escribe una CLASE MAGISTRAL ESCRITA EXHAUSTIVA, EXTENSA, PROFUNDAMENTE EXPLICATIVA, ARGUMENTATIVA Y EJEMPLARIZANTE en formato HTML enriquecido para que el estudiante domine a la perfección este tema.

ESTRUCTURA OBLIGATORIA DEL CONTENIDO EN HTML:
1. <h3>{topic_title}</h3>
2. <div style="background:#f1f5f9; border-left:4px solid #1e3a8a; padding:15px; margin:15px 0; border-radius:0 8px 8px 0;">
   <p><strong>Contextualización y Relevancia:</strong> Introducción profunda que explique por qué este tema es neurálgico en la práctica institucional/profesional contemporánea, desafíos actuales y brechas comunes.</p>
</div>
3. <h4>I. Fundamentación Teórica y Conceptual Rigurosa</h4>
   <p>Desarrollo conceptual exhaustivo (al menos 3 a 4 párrafos sustantivos) explicando principios, definiciones clave, modelos de referencia y estándares (ej. marcos normativos colombianos como CESU Acuerdo 01/2025, Decreto 1330/2019, lineamientos CNA, estándares ISO o directrices internacionales según el campo disciplinar).</p>
4. <h4>II. Desarrollo Argumentativo y Mecanismos de Aplicación</h4>
   <p>Argumentación profunda sobre el 'cómo', el 'por qué' y los puntos críticos de control en la gestión o implementación.</p>
5. <h4>III. Casos de Estudio Aplicados y Ejemplos Prácticos Reales</h4>
   <div style="background:#f8fafc; border-left:4px solid #3b82f6; padding:15px; margin:15px 0; border-radius:0 8px 8px 0;">
      <p><strong>Caso Real / Simulación Institucional:</strong> Presenta una situación real o caso de estudio detallado con cifras, dilemas, toma de decisiones y lecciones aprendidas paso a paso.</p>
   </div>
6. <h4>IV. Matriz Metodológica de Indicadores y Puntos de Control</h4>
   <table style="width:100%; border-collapse:collapse; margin:15px 0; font-size:0.9rem;">
      <thead>
         <tr style="background:#1e3a8a; color:white;">
            <th style="padding:10px; border:1px solid #cbd5e1;">Dimensión / Criterio</th>
            <th style="padding:10px; border:1px solid #cbd5e1;">Indicador / Evidencia Clave</th>
            <th style="padding:10px; border:1px solid #cbd5e1;">Impacto en la Calidad</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td style="padding:8px; border:1px solid #cbd5e1;">Dimensión Conceptual</td>
            <td style="padding:8px; border:1px solid #cbd5e1;">Indicador medible de adopción</td>
            <td style="padding:8px; border:1px solid #cbd5e1;">Alineación estratégica</td>
         </tr>
         <tr>
            <td style="padding:8px; border:1px solid #cbd5e1;">Dimensión Operativa</td>
            <td style="padding:8px; border:1px solid #cbd5e1;">Tasa de cumplimiento / Seguimiento</td>
            <td style="padding:8px; border:1px solid #cbd5e1;">Sostenibilidad institucional</td>
         </tr>
      </tbody>
   </table>
7. <h4>V. Conclusiones y Claves de Éxito</h4>
   <p>Síntesis directiva con recomendaciones estratégicas indispensables.</p>
8. <h4>Referencias Bibliográficas (Norma APA 7ma Edición)</h4>
   <p style="font-size:0.85rem; color:#64748b;">Referencias representativas y actualizadas al campo.</p>

{f"INSTRUCCIONES ESPECIALES DEL DOCENTE: {custom_instructions}" if custom_instructions else ""}

REGLAS DE FORMATO:
- Responde ÚNICAMENTE con el código HTML interno (usa <h3>, <h4>, <p>, <ul>, <li>, <strong>, <em>, <table>, <div>).
- NO incluyas <html>, <head>, <body> ni bloques de markdown (evita ```html).
- Extensión sustantiva: mínimo 800 a 1400 palabras de contenido docente denso y valioso.
"""
    try:
        response_text = call_ai([
            {"role": "system", "content": "Eres un prestigioso catedrático universitario y redactor pedagógico de alto nivel."},
            {"role": "user", "content": prompt}
        ], max_tokens=4000, temperature=0.5)
        
        cleaned_html = response_text.strip()
        if cleaned_html.startswith("```html"):
            cleaned_html = cleaned_html[7:]
        elif cleaned_html.startswith("```"):
            cleaned_html = cleaned_html[3:]
        if cleaned_html.endswith("```"):
            cleaned_html = cleaned_html[:-3]
        cleaned_html = cleaned_html.strip()
        
        # Persistir automáticamente en el curso si se suministraron los índices
        saved_in_db = False
        if course_id is not None and unit_idx is not None and topic_idx is not None:
            course = formacion_storage.load_course(course_id)
            if course:
                u_i = int(unit_idx)
                t_i = int(topic_idx)
                units = course.get('units', [])
                if isinstance(units, dict):
                    units = list(units.values())
                    course['units'] = units
                
                if 0 <= u_i < len(units):
                    topics = units[u_i].get('topics', [])
                    if isinstance(topics, dict):
                        topics = list(topics.values())
                        units[u_i]['topics'] = topics
                        
                    if 0 <= t_i < len(topics):
                        raw_t = topics[t_i]
                        t_obj = {"id": f"t_{t_i}", "title": topic_title, "type": "text"} if isinstance(raw_t, str) else raw_t
                        t_obj['content'] = cleaned_html
                        topics[t_i] = t_obj
                        
                        formacion_storage.save_course(inst_id, course.get('program_id', program_id), course)
                        saved_in_db = True
                        
        return jsonify({
            "status": "success",
            "data": {
                "html_content": cleaned_html,
                "saved_in_db": saved_in_db,
                "topic_title": topic_title,
                "word_count": len(cleaned_html.split())
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@ai_generator_bp.route('/api/ai/course/prompts', methods=['POST'])
def generate_course_prompts():
    """Genera los prompts listos para copiar y pegar en ChatGPT/Claude y en NotebookLM."""
    data = request.json or {}
    course_name = data.get('course_name') or 'Curso Especializado'
    unit_name = data.get('unit_name') or 'Unidad Temática'
    topic_title = data.get('topic_title') or 'Tema Específico'
    topics_list = data.get('topics_list') or [topic_title]
    topics_formatted = "\n".join([f"  - {t}" for t in topics_list]) if isinstance(topics_list, list) else str(topics_list)

    # 1. Prompt de Redacción Docente Experta (para ChatGPT / Claude / Gemini Web)
    prompt_redaccion = f"""Actúa como un CATEDRÁTICO UNIVERSITARIO TITULAR, INVESTIGADOR SENIOR Y EVALUADOR PAR ACADÉMICO.
Eres el autor principal del curso "{course_name}".

Tu tarea es redactar el contenido académico completo, magistral, explicativo, argumentativo y ejemplarizante para el siguiente tema/unidad:
- CURSO: {course_name}
- UNIDAD: {unit_name}
- TEMA PRINCIPAL: {topic_title}
- TEMARIO DE LA UNIDAD:
{topics_formatted}

INSTRUCCIONES METODOLÓGICAS DE REDACCIÓN:
1. TONO Y LENGUAJE: Docente experto, analítico, persuasivo y didáctico. No utilices resúmenes telegráficos ni viñetas superficiales; desarrolla párrafos profundos y argumentativos que guíen al estudiante como en una clase doctoral o de alta dirección.
2. FUNDAMENTACIÓN TEÓRICA Y NORMATIVA: Articula los conceptos teóricos con el marco regulatorio y estándares contemporáneos (ej. Acuerdo 01 de 2025 CESU, Decreto 1330 de 2019, guías del CNA, normas ISO o buenas prácticas internacionales según la disciplina).
3. CASOS REALES Y EJEMPLOS APLICADOS: Incluye de manera obligatoria al menos un caso de estudio o situación problemática real con datos simulados, análisis de causas, toma de decisiones y lecciones aprendidas.
4. TABLAS Y MATRICES: Incorpora una matriz comparativa o tabla de indicadores/criterios de éxito en formato HTML.
5. REFERENCIAS: Finaliza con un listado bibliográfico representativo en formato APA (7ma edición).
6. FORMATO DE ENTREGA: Escribe directamente en código HTML semántico (<h3>, <h4>, <p>, <ul>, <li>, <strong>, <em>, <table>, <div> con estilos inline elegantes). No uses etiquetas <html>, <head> o <body> ni bloques de markdown con comillas triples."""

    # 2. Prompt Maestro para Google NotebookLM (Audio Overview / Video Podcast Contextualizado)
    prompt_notebooklm = f"""[INSTRUCCIONES MAESTRAS PARA NOTEBOOKLM - DEEP DIVE AUDIO / VIDEO OVERVIEW]

Por favor, actúa como los dos anfitriones académicos expertos de Google NotebookLM para generar un Deep Dive Audio Overview / Video Podcast altamente contextualizado, coherente y dinámico sobre la siguiente unidad académica:

🎙️ CURSO: {course_name}
📑 UNIDAD TEMÁTICA: {unit_name}
🎯 TEMAS CLAVE ABORDADOS:
{topics_formatted}

DIRECTRICES PARA LA GENERACIÓN DEL PODCAST / VIDEO AUDIO:
1. ROLES DE LOS ANFITRIONES:
   - Anfitrión 1 (El Catedrático / Experto Técnico): Lidera el rigor conceptual, cita los marcos regulatorios (ej. CESU, CNA, lineamientos institucionales), explica la arquitectura de los datos e indicadores, y plantea los principios metodológicos.
   - Anfitrión 2 (El Estratega / Consultor de Campo): Plantea preguntas provocadoras, contraejemplos prácticos, anécdotas de lo que ocurre en la vida real en las universidades o empresas, desmitifica errores comunes y traduce las teorías en acciones cotidianas.
2. DINÁMICA DE CONVERSACIÓN:
   - Inicien con un "gancho" directo: un dilema o pregunta crítica sobre {topic_title} que cualquier directivo, docente o estudiante se ha enfrentado.
   - Desarrollen un diálogo ágil, con entusiasmo profesional, analogías memorables y debate constructivo (eviten monólogos planos o lecturas textuales).
   - Analicen cómo esta unidad se conecta directamente con los resultados de aprendizaje y la transformación institucional de calidad.
3. CIERRE DE ALTO IMPACTO:
   - Finalicen con una síntesis de tres lecciones clave "para llevar a la práctica mañana mismo" y una pregunta detonante para que la audiencia reflexione en el foro del curso.

(Instrucciones de uso: Abre https://notebooklm.google.com, sube los documentos o el texto del tema como Fuente 'Source', y en la sección de Audio Overview / Studio personaliza las instrucciones pegando este texto)."""

    return jsonify({
        "status": "success",
        "data": {
            "course_name": course_name,
            "unit_name": unit_name,
            "topic_title": topic_title,
            "prompt_redaccion": prompt_redaccion,
            "prompt_notebooklm": prompt_notebooklm
        }
    })


