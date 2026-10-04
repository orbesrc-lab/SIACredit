import os
import json
import uuid

SYSTEM_QUESTION_BANK = [
    # ==================================================
    # MODELO: AUTOEVALUACIÓN DE PROGRAMA (CNA 2025 / CESU)
    # ==================================================
    # Factor 1: Proyecto Educativo del Programa e Identidad Institucional
    {
        "id": "bank_prog_f1_q1",
        "model_type": "programa",
        "text": "¿Qué tanto conoce y se identifica con la Misión, Visión y el Proyecto Educativo del Programa (PEP)?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "transversal",
        "factor_number": 1,
        "factor_name": "Factor 1: Proyecto educativo del programa e identidad institucional",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_prog_f1_q2",
        "text": "¿El perfil de egreso y los resultados de aprendizaje definidos en el programa responden a las necesidades del contexto regional y nacional?",
        "type": "likert",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 1,
        "factor_name": "Factor 1: Proyecto educativo del programa e identidad institucional",
        "options": [],
        "is_system": True
    },

    # Factor 2: Comunidad de Estudiantes
    {
        "id": "bank_prog_f2_q1",
        "text": "¿Los criterios de admisión, selección, nivelación y transferencia de estudiantes son transparentes y equitativos?",
        "type": "likert",
        "aspect_type": "factual",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 2,
        "factor_name": "Factor 2: Comunidad de estudiantes",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_prog_f2_q2",
        "text": "¿Cómo evalúa el acompañamiento pedagógico, tutorías docentes y estímulos al mérito académico recibidos en el programa?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 2,
        "factor_name": "Factor 2: Comunidad de estudiantes",
        "options": [],
        "is_system": True
    },

    # Factor 3: Comunidad de Profesores
    {
        "id": "bank_prog_f3_q1",
        "text": "¿Cómo califica la idoneidad profesional, formación académica (maestría/doctorado) y dominio pedagógico de sus profesores?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 3,
        "factor_name": "Factor 3: Comunidad de profesores",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_prog_f3_q2",
        "text": "¿La institución y la facultad otorgan apoyos e incentivos efectivos para la cualificación docente y el desarrollo profesional continuo?",
        "type": "likert",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 3,
        "factor_name": "Factor 3: Comunidad de profesores",
        "options": [],
        "is_system": True
    },

    # Factor 4: Comunidad de Egresados
    {
        "id": "bank_prog_f4_q1",
        "text": "¿En qué medida la formación académica recibida le ha permitido desempeñarse exitosamente en su ejercicio profesional?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "egresados",
        "factor_number": 4,
        "factor_name": "Factor 4: Comunidad de egresados",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_prog_f4_q2",
        "text": "¿El programa mantiene canales fluidos de comunicación, seguimiento laboral y ofertas de educación continuada para los graduados?",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "egresados",
        "factor_number": 4,
        "factor_name": "Factor 4: Comunidad de egresados",
        "options": [],
        "is_system": True
    },

    # Factor 5: Aspectos Académicos y Evaluación
    {
        "id": "bank_prog_f5_q1",
        "text": "¿Cómo evalúa la pertinencia, actualización, flexibilidad e interdisciplinariedad del Plan de Estudios del programa?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "transversal",
        "factor_number": 5,
        "factor_name": "Factor 5: Aspectos académicos y evaluación",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_prog_f5_q2",
        "text": "¿Las metodologías de enseñanza y las evaluaciones aplicadas permiten verificar con claridad el logro de los Resultados de Aprendizaje?",
        "type": "likert",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 5,
        "factor_name": "Factor 5: Aspectos académicos y evaluación",
        "options": [],
        "is_system": True
    },

    # Factor 6: Permanencia y Graduación
    {
        "id": "bank_prog_f6_q1",
        "text": "¿Cómo valora las estrategias e intervenciones institucionales orientadas a prevenir la deserción y favorecer la graduación oportuna?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "transversal",
        "factor_number": 6,
        "factor_name": "Factor 6: Permanencia y graduación",
        "options": [],
        "is_system": True
    },

    # Factor 7: Proyección e Interacción con el Entorno
    {
        "id": "bank_prog_f7_q1",
        "text": "¿Cómo califica el desempeño ético, resolutivo y la capacidad técnica de los graduados de este programa en su empresa u organización?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "empleadores",
        "factor_number": 7,
        "factor_name": "Factor 7: Proyección e interacción con el entorno",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_prog_f7_q2",
        "text": "¿El programa promueve proyectos de extensión, prácticas profesionales y servicio social con impacto real en la comunidad?",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 7,
        "factor_name": "Factor 7: Proyección e interacción con el entorno",
        "options": [],
        "is_system": True
    },

    # Factor 8: Investigación, Innovación y Creación
    {
        "id": "bank_prog_f8_q1",
        "text": "¿El programa fomenta activamente la investigación formativa, semilleros, desarrollo tecnológico o creación artística?",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 8,
        "factor_name": "Factor 8: Investigación, innovación y creación",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_prog_f8_q2",
        "text": "¿Los docentes cuentan con horas asignadas, convocatorias y presupuesto adecuado para la producción científica en grupos reconocidos?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 8,
        "factor_name": "Factor 8: Investigación, innovación y creación",
        "options": [],
        "is_system": True
    },

    # Factor 9: Bienestar de la Comunidad Académica
    {
        "id": "bank_prog_f9_q1",
        "text": "¿Los servicios de salud, desarrollo humano, cultura, deporte y orientación psicosocial responden a las necesidades del estamento?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "transversal",
        "factor_number": 9,
        "factor_name": "Factor 9: Bienestar de la comunidad académica",
        "options": [],
        "is_system": True
    },

    # Factor 10: Recursos y Ambientes de Aprendizaje
    {
        "id": "bank_prog_f10_q1",
        "text": "¿Las aulas, laboratorios, talleres, licencias de software y bibliotecas físicas y digitales responden con suficiencia y calidad?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "transversal",
        "factor_number": 10,
        "factor_name": "Factor 10: Recursos y ambientes de aprendizaje",
        "options": [],
        "is_system": True
    },

    # Factor 11: Organización, Administración y Financiación
    {
        "id": "bank_prog_f11_q1",
        "text": "¿La gestión administrativa y financiera de la facultad garantiza el cumplimiento oportuno de las metas de inversión del programa?",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "unidad",
        "target": "administrativos",
        "factor_number": 11,
        "factor_name": "Factor 11: Organización, administración y financiación",
        "options": [],
        "is_system": True
    },

    # Factor 12: Aseguramiento de la Alta Calidad
    {
        "id": "bank_prog_f12_q1",
        "text": "¿Cómo evalúa la cultura de autorregulación y la efectividad de los Planes de Mejoramiento implementados en el programa?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "transversal",
        "factor_number": 12,
        "factor_name": "Factor 12: Aseguramiento de la alta calidad",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # MODELO: AUTOEVALUACIÓN INSTITUCIONAL (CNA)
    # ==================================================
    {
        "id": "bank_inst_f1_q1",
        "model_type": "institucional",
        "text": "¿La gobernanza institucional promueve decisiones participativas, transparentes y orientadas a la excelencia académica?",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "directivos",
        "factor_number": 1,
        "factor_name": "Gobierno y Gobernanza Institucional",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_inst_f2_q1",
        "model_type": "institucional",
        "text": "¿Los planes de desarrollo físico y financiero garantizan la sostenibilidad económica de la institución a largo plazo?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "institucional",
        "target": "directivos",
        "factor_number": 2,
        "factor_name": "Sostenibilidad Financiera e Infraestructura",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # MODELO: REGISTRO CALIFICADO (DECRETO 1330 / ACUERDO 02/2020)
    # ==================================================
    {
        "id": "bank_rc_cond1_q1",
        "model_type": "registro_calificado",
        "text": "¿La denominación del programa y la justificación del mismo responden explícitamente a las tendencias y necesidades del sector?",
        "type": "likert",
        "aspect_type": "factual",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 1,
        "factor_name": "Condición 1: Denominación y Justificación del Programa",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_rc_cond2_q1",
        "model_type": "registro_calificado",
        "text": "¿La fundamentación teórica y la organización de las actividades académicas garantizan el logro de los contenidos curriculares?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 2,
        "factor_name": "Condición 2: Contenidos Curriculares y Organización",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_rc_cond3_q1",
        "model_type": "registro_calificado",
        "text": "¿La oferta de medios educativos (plataformas, laboratorios, talleres) garantiza el aprendizaje práctico en todas las sedes?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 3,
        "factor_name": "Condición 3: Medios Educativos e Infraestructura",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # MODELO: CAMBIO DE CARÁCTER INSTITUCIONAL (ITP a IU)
    # ==================================================
    {
        "id": "bank_cc_f1_q1",
        "model_type": "cambio_caracter",
        "text": "¿La institución demuestra capacidad técnica e investigativa para dar el salto cualitativo hacia el nuevo carácter académico?",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "directivos",
        "factor_number": 1,
        "factor_name": "Capacidad Institucional para Cambio de Carácter",
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
                nq['model_type'] = nq.get('model_type') or 'programa'
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
