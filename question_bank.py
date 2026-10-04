import os
import json
import uuid

SYSTEM_QUESTION_BANK = [
    # FACTOR 1: PEI, Misión y Proyecto Educativo
    {
        "id": "bank_f1_q1",
        "text": "¿Qué tanto conoce y se identifica con la Misión, Visión y Objetivos del Proyecto Educativo Institucional (PEI)?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "transversal",
        "factor_number": 1,
        "factor_name": "Factor 1: Misión, PEI y Proyecto Educativo",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f1_q2",
        "text": "¿El Proyecto Educativo del Programa (PEP) orienta de forma clara y coherente el perfil de egreso y las competencias profesionales?",
        "type": "likert",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 1,
        "factor_name": "Factor 1: Misión, PEI y Proyecto Educativo",
        "options": [],
        "is_system": True
    },
    
    # FACTOR 2: Gobierno Institucional y Organización
    {
        "id": "bank_f2_q1",
        "text": "¿Cómo evalúa la transparencia, efectividad y oportunidad en la toma de decisiones de los órganos de gobierno institucionales?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "transversal",
        "factor_number": 2,
        "factor_name": "Factor 2: Gobierno Institucional y Organización",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f2_q2",
        "text": "¿La estructura administrativa de la Facultad/Unidad brinda un soporte eficiente y oportuno para la gestión académica?",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "unidad",
        "target": "administrativos",
        "factor_number": 2,
        "factor_name": "Factor 2: Gobierno Institucional y Organización",
        "options": [],
        "is_system": True
    },

    # FACTOR 3: Estudiantes
    {
        "id": "bank_f3_q1",
        "text": "¿Los criterios de admisión, selección y transferencia de estudiantes son claros, equitativos y de conocimiento público?",
        "type": "likert",
        "aspect_type": "factual",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 3,
        "factor_name": "Factor 3: Estudiantes",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f3_q2",
        "text": "¿Cómo valora la eficacia de los programas de inducción, tutorías académicas y consejería en su adaptación universitaria?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 3,
        "factor_name": "Factor 3: Estudiantes",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f3_q3",
        "text": "¿Qué acciones o estrategias considera prioritarias para mitigar el riesgo de deserción en los primeros semestres académicos?",
        "type": "text",
        "aspect_type": "factual",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 3,
        "factor_name": "Factor 3: Estudiantes",
        "options": [],
        "is_system": True
    },

    # FACTOR 4: Profesores y Cuerpo Docente
    {
        "id": "bank_f4_q1",
        "text": "¿Cómo califica la idoneidad académica, nivel de maestría/doctorado y capacidad pedagógica de los profesores del programa?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 4,
        "factor_name": "Factor 4: Profesores",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f4_q2",
        "text": "¿La institución impulsa de manera efectiva el desarrollo profesional docente mediante apoyos para posgrados y eventos científicos?",
        "type": "likert",
        "aspect_type": "rating",
        "scope": "institucional",
        "target": "profesores",
        "factor_number": 4,
        "factor_name": "Factor 4: Profesores",
        "options": [],
        "is_system": True
    },

    # FACTOR 5: Plan de Estudios y Aspectos Académicos
    {
        "id": "bank_f5_q1",
        "text": "¿Cómo evalúa la actualidad, flexibilidad e interdisciplinariedad del Plan de Estudios frente a las demandas de la profesión?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "transversal",
        "factor_number": 5,
        "factor_name": "Factor 5: Aspectos Académicos y Resultados de Aprendizaje",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f5_q2",
        "text": "¿Las estrategias de enseñanza y los métodos de evaluación garantizan la verificación rigurosa de los Resultados de Aprendizaje?",
        "type": "likert",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 5,
        "factor_name": "Factor 5: Aspectos Académicos y Resultados de Aprendizaje",
        "options": [],
        "is_system": True
    },

    # FACTOR 6: Investigación, Innovación y Creación Artística
    {
        "id": "bank_f6_q1",
        "text": "¿El programa fomenta el desarrollo del pensamiento científico y la investigación formativa (semilleros, proyectos y publicaciones)?",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 6,
        "factor_name": "Factor 6: Investigación y Creación Artística",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f6_q2",
        "text": "¿Cómo califica las convocatorias internas, los presupuestos asignados y los estímulos para grupos de investigación reconocidos?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "institucional",
        "target": "profesores",
        "factor_number": 6,
        "factor_name": "Factor 6: Investigación y Creación Artística",
        "options": [],
        "is_system": True
    },

    # FACTOR 7: Pertinencia, Impacto Social y Egresados
    {
        "id": "bank_f7_q1",
        "text": "¿En qué medida la formación académica recibida le ha permitido desenvolverse con éxito en el mercado laboral profesional?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "egresados",
        "factor_number": 7,
        "factor_name": "Factor 7: Pertinencia, Impacto Social y Egresados",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f7_q2",
        "text": "¿Cómo califica el desempeño ético, resolutivo, liderazgo y adaptación tecnológica de los graduados en su empresa u organización?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "empleadores",
        "factor_number": 7,
        "factor_name": "Factor 7: Pertinencia, Impacto Social y Egresados",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f7_q3",
        "text": "¿En cuánto tiempo logró vincularse laboralmente en un cargo afín a su perfil profesional tras obtener el grado académico?",
        "type": "select",
        "aspect_type": "factual",
        "scope": "programa",
        "target": "egresados",
        "factor_number": 7,
        "factor_name": "Factor 7: Pertinencia, Impacto Social y Egresados",
        "options": ["Antes de graduarme", "Menos de 6 meses", "6 a 12 meses", "Más de 1 año", "Aún no ubicado"],
        "is_system": True
    },

    # FACTOR 8: Bienestar Universitario
    {
        "id": "bank_f8_q1",
        "text": "¿Cómo evalúa los servicios de salud, orientación psicológica, deporte, cultura y desarrollo humano de Bienestar Universitario?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "transversal",
        "factor_number": 8,
        "factor_name": "Factor 8: Bienestar Universitario",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f8_q2",
        "text": "El clima académico e institucional promueve valores de equidad de género, inclusión, diversidad y prevención del acoso.",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "transversal",
        "factor_number": 8,
        "factor_name": "Factor 8: Bienestar Universitario",
        "options": [],
        "is_system": True
    },

    # FACTOR 9: Recursos Bibliográficos y Tecnológicos
    {
        "id": "bank_f9_q1",
        "text": "¿Cómo califica la cobertura, actualidad y facilidad de acceso a las bases de datos bibliográficas especializadas e e-books?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "institucional",
        "target": "transversal",
        "factor_number": 9,
        "factor_name": "Factor 9: Recursos Bibliográficos y Tecnológicos",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f9_q2",
        "text": "¿La infraestructura tecnológica (redes wifi, aulas virtuales, software especializado) responde satisfactoriamente a las labores académicas?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "transversal",
        "factor_number": 9,
        "factor_name": "Factor 9: Recursos Bibliográficos y Tecnológicos",
        "options": [],
        "is_system": True
    },

    # FACTOR 10: Infraestructura Física y Servicios
    {
        "id": "bank_f10_q1",
        "text": "¿Las aulas de clase, salas de estudio, auditorios y zonas comunes ofrecen un nivel adecuado de confort, limpieza y bioseguridad?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "transversal",
        "factor_number": 10,
        "factor_name": "Factor 10: Infraestructura Física y Financiera",
        "options": [],
        "is_system": True
    },

    # FACTOR 11: Autorregulación y Cultura de Calidad
    {
        "id": "bank_f11_q1",
        "text": "¿Cómo valora la participación y comunicación transparente de los avances en el proceso de Autoevaluación y Acreditación?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "transversal",
        "factor_number": 11,
        "factor_name": "Factor 11: Procesos de Autorregulación y Calidad",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f11_q2",
        "text": "Describa brevemente qué oportunidad de mejora considera urgente que el equipo de autoevaluación incorpore en el Plan de Mejoramiento.",
        "type": "text",
        "aspect_type": "factual",
        "scope": "programa",
        "target": "transversal",
        "factor_number": 11,
        "factor_name": "Factor 11: Procesos de Autorregulación y Calidad",
        "options": [],
        "is_system": True
    }
]

IS_VERCEL = os.environ.get("VERCEL") == "1"
if IS_VERCEL:
    CUSTOM_BANK_FILE = "/tmp/custom_question_bank.json"
else:
    CUSTOM_BANK_FILE = os.path.join("instance", "custom_question_bank.json")

def load_custom_questions(inst_id):
    if not os.path.exists(CUSTOM_BANK_FILE):
        return []
    try:
        with open(CUSTOM_BANK_FILE, 'r', encoding='utf-8') as f:
            all_custom = json.load(f)
        target_inst = int(inst_id) if str(inst_id).isdigit() else inst_id
        return [
            q for q in all_custom
            if q.get('inst_id') == target_inst or str(q.get('inst_id')) == str(target_inst) or target_inst in (0, None, '0')
        ]
    except Exception as e:
        print(f"Error loading custom question bank: {e}")
        return []

def save_custom_questions(inst_id, new_questions):
    try:
        if not IS_VERCEL:
            os.makedirs("instance", exist_ok=True)
            
        all_custom = []
        if os.path.exists(CUSTOM_BANK_FILE):
            try:
                with open(CUSTOM_BANK_FILE, 'r', encoding='utf-8') as f:
                    all_custom = json.load(f)
            except Exception: pass

        target_inst = int(inst_id) if str(inst_id).isdigit() else inst_id
        
        # Deduplicate by text
        existing_texts = {q.get('text', '').strip().lower() for q in (SYSTEM_QUESTION_BANK + all_custom)}
        
        added_count = 0
        for nq in new_questions:
            t = nq.get('text', '').strip().lower()
            if t and t not in existing_texts:
                nq['id'] = nq.get('id') or f"bank_custom_{uuid.uuid4().hex[:8]}"
                nq['inst_id'] = target_inst
                nq['is_system'] = False
                all_custom.append(nq)
                existing_texts.add(t)
                added_count += 1
                
        with open(CUSTOM_BANK_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_custom, f, indent=2, ensure_ascii=False)
            
        return added_count
    except Exception as e:
        print(f"Error saving custom question bank: {e}")
        return 0

def get_full_question_bank(inst_id=1):
    custom = load_custom_questions(inst_id)
    return SYSTEM_QUESTION_BANK + custom
