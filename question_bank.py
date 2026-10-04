import os
import json
import uuid

SYSTEM_QUESTION_BANK = [
    # ==================================================
    # FACTOR 1: MISIÓN, PEI Y PROYECTO EDUCATIVO
    # ==================================================
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
        "text": "¿El Proyecto Educativo del Programa (PEP) orienta de forma clara, explícita y coherente el perfil de egreso y los resultados de aprendizaje esperados?",
        "type": "likert",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 1,
        "factor_name": "Factor 1: Misión, PEI y Proyecto Educativo",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f1_q3",
        "text": "¿Considera que los principios institucionales de inclusión, ética y sostenibilidad se ven reflejados en la vida cotidiana del programa?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "estudiantes",
        "factor_number": 1,
        "factor_name": "Factor 1: Misión, PEI y Proyecto Educativo",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f1_q4",
        "text": "Comentarios u observaciones sobre la apropiación del Proyecto Educativo Institucional en los procesos curriculares del programa.",
        "type": "text",
        "aspect_type": "factual",
        "scope": "programa",
        "target": "directivos",
        "factor_number": 1,
        "factor_name": "Factor 1: Misión, PEI y Proyecto Educativo",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # FACTOR 2: GOBIERNO INSTITUCIONAL, ORGANIZACIÓN Y GESTIÓN
    # ==================================================
    {
        "id": "bank_f2_q1",
        "text": "¿Cómo evalúa la transparencia, efectividad y oportunidad en la toma de decisiones por parte de los órganos de gobierno institucionales?",
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
        "text": "¿La estructura administrativa de la Facultad/Unidad brinda un soporte oportuno y eficiente para los trámites académicos y laborales?",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "unidad",
        "target": "administrativos",
        "factor_number": 2,
        "factor_name": "Factor 2: Gobierno Institucional y Organización",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f2_q3",
        "text": "¿Los canales formales de comunicación institucional son claros y permiten una fluida rendición de cuentas a la comunidad?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "institucional",
        "target": "profesores",
        "factor_number": 2,
        "factor_name": "Factor 2: Gobierno Institucional y Organización",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f2_q4",
        "text": "¿Existen mecanismos efectivos para garantizar la representación y participación activa de estudiantes y profesores en los consejos directivos?",
        "type": "boolean",
        "aspect_type": "factual",
        "scope": "institucional",
        "target": "transversal",
        "factor_number": 2,
        "factor_name": "Factor 2: Gobierno Institucional y Organización",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # FACTOR 3: ESTUDIANTES (ADMISIÓN, TUTORÍAS Y PERMANENCIA)
    # ==================================================
    {
        "id": "bank_f3_q1",
        "text": "¿Los criterios de admisión, selección y homologación de asignaturas del programa son transparentes, equitativos y de conocimiento público?",
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
        "text": "¿Cómo valora la eficacia de los programas de acompañamiento, tutorías académicas y consejería en su adaptación y nivelación universitaria?",
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
        "text": "¿Qué acciones o estrategias considera prioritarias para fortalecer la permanencia y reducir la deserción en los primeros semestres académicos?",
        "type": "text",
        "aspect_type": "factual",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 3,
        "factor_name": "Factor 3: Estudiantes",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f3_q4",
        "text": "¿El programa fomenta un ambiente propicio para el desarrollo integral, el estímulo al mérito académico y la participación estudiantil?",
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
        "id": "bank_f3_q5",
        "text": "¿Ha hecho uso de las becas, descuentos o apoyos socioeconómicos ofrecidos por la institución?",
        "type": "boolean",
        "aspect_type": "factual",
        "scope": "institucional",
        "target": "estudiantes",
        "factor_number": 3,
        "factor_name": "Factor 3: Estudiantes",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # FACTOR 4: PROFESORES Y CUERPO DOCENTE
    # ==================================================
    {
        "id": "bank_f4_q1",
        "text": "¿Cómo califica la idoneidad profesional, preparación pedagógica, actualización disciplinar y puntualidad del equipo docente del programa?",
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
        "text": "¿La institución otorga incentivos y apoyos suficientes para la cualificación académica avanzada (maestrías, doctorados y publicaciones)?",
        "type": "likert",
        "aspect_type": "rating",
        "scope": "institucional",
        "target": "profesores",
        "factor_number": 4,
        "factor_name": "Factor 4: Profesores",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f4_q3",
        "text": "¿La asignación de la carga académica (docencia, investigación, extensión y gestión) responde a criterios razonables y equilibrados?",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "unidad",
        "target": "profesores",
        "factor_number": 4,
        "factor_name": "Factor 4: Profesores",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f4_q4",
        "text": "¿Cómo evalúa los procedimientos de selección, vinculación, evaluación del desempeño y escalafón docente institucional?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "institucional",
        "target": "profesores",
        "factor_number": 4,
        "factor_name": "Factor 4: Profesores",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # FACTOR 5: ASPECTOS ACADÉMICOS Y RESULTADOS DE APRENDIZAJE
    # ==================================================
    {
        "id": "bank_f5_q1",
        "text": "¿Cómo evalúa la pertinencia, estructura y actualización del Plan de Estudios para responder a las exigencias del entorno profesional?",
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
        "text": "¿Las metodologías de enseñanza y las estrategias de evaluación formativa garantizan la verificación efectiva de los Resultados de Aprendizaje?",
        "type": "likert",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 5,
        "factor_name": "Factor 5: Aspectos Académicos y Resultados de Aprendizaje",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f5_q3",
        "text": "¿El programa promueve efectivamente la flexibilidad curricular, electividad, homologación y las asignaturas interdisciplinares?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 5,
        "factor_name": "Factor 5: Aspectos Académicos y Resultados de Aprendizaje",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f5_q4",
        "text": "¿En qué medida las actividades formativas potencian el desarrollo de la competencia en segunda lengua (inglés) y las competencias digitales?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 5,
        "factor_name": "Factor 5: Aspectos Académicos y Resultados de Aprendizaje",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f5_q5",
        "text": "Sugerencias específicas de adición o modificación de temáticas, asignaturas o prácticas profesionales en la currícula del programa.",
        "type": "text",
        "aspect_type": "factual",
        "scope": "programa",
        "target": "transversal",
        "factor_number": 5,
        "factor_name": "Factor 5: Aspectos Académicos y Resultados de Aprendizaje",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # FACTOR 6: INVESTIGACIÓN, INNOVACIÓN Y CREACIÓN ARTÍSTICA
    # ==================================================
    {
        "id": "bank_f6_q1",
        "text": "¿El programa fomenta el desarrollo del pensamiento crítico y la investigación formativa (semilleros, proyectos de aula y trabajos de grado)?",
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
        "text": "¿Cómo califica los recursos financieros, convocatorias internas y apoyos para proyectos de los grupos de investigación clasificados?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "institucional",
        "target": "profesores",
        "factor_number": 6,
        "factor_name": "Factor 6: Investigación y Creación Artística",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f6_q3",
        "text": "¿La producción científica y aplicada del programa (artículos, patentes, productos de creación) impacta positivamente el entorno social?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 6,
        "factor_name": "Factor 6: Investigación y Creación Artística",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f6_q4",
        "text": "¿Ha participado como integrante o ponente en semilleros, ponencias o eventos de investigación académica durante su carrera?",
        "type": "boolean",
        "aspect_type": "factual",
        "scope": "programa",
        "target": "estudiantes",
        "factor_number": 6,
        "factor_name": "Factor 6: Investigación y Creación Artística",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # FACTOR 7: PERTINENCIA, IMPACTO SOCIAL Y EGRESADOS
    # ==================================================
    {
        "id": "bank_f7_q1",
        "text": "¿En qué medida la formación recibida le permitió desenvolverse con solidez técnica y ética en el mercado laboral profesional?",
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
        "text": "¿Cómo califica la capacidad de resolución de problemas, liderazgo, ética profesional y trabajo en equipo de los graduados del programa en su organización?",
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
        "text": "¿En cuánto tiempo logró vincularse laboralmente en un cargo acorde a su área de formación tras obtener el grado académico?",
        "type": "select",
        "aspect_type": "factual",
        "scope": "programa",
        "target": "egresados",
        "factor_number": 7,
        "factor_name": "Factor 7: Pertinencia, Impacto Social y Egresados",
        "options": ["Antes de graduarme", "Menos de 6 meses", "6 a 12 meses", "Más de 1 año", "Aún no ubicado"],
        "is_system": True
    },
    {
        "id": "bank_f7_q4",
        "text": "¿La institución mantiene vínculos permanentes con los egresados mediante bolsas de empleo, eventos de actualización y educación continuada?",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "egresados",
        "factor_number": 7,
        "factor_name": "Factor 7: Pertinencia, Impacto Social y Egresados",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f7_q5",
        "text": "¿Recomendaría o continuaría contratando profesionales formados en este programa académico para su empresa u organización?",
        "type": "boolean",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "empleadores",
        "factor_number": 7,
        "factor_name": "Factor 7: Pertinencia, Impacto Social y Egresados",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # FACTOR 8: BIENESTAR UNIVERSITARIO Y CLIMA INSTITUCIONAL
    # ==================================================
    {
        "id": "bank_f8_q1",
        "text": "¿Cómo evalúa los servicios de salud, orientación psicológica, deporte, desarrollo humano y cultura prestados por Bienestar Universitario?",
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
        "text": "El ambiente de trabajo y estudio fomenta valores sustantivos de inclusión, respeto por la diversidad, equidad de género y convivencia pacífica.",
        "type": "likert",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "transversal",
        "factor_number": 8,
        "factor_name": "Factor 8: Bienestar Universitario",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f8_q3",
        "text": "¿Considera que los programas de apoyo socioeconómico (subsidios de alimentación, transporte, becas) llegan oportunamente a los estudiantes vulnerables?",
        "type": "rating",
        "aspect_type": "rating",
        "scope": "institucional",
        "target": "estudiantes",
        "factor_number": 8,
        "factor_name": "Factor 8: Bienestar Universitario",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # FACTOR 9: RECURSOS BIBLIOGRÁFICOS Y TECNOLÓGICOS
    # ==================================================
    {
        "id": "bank_f9_q1",
        "text": "¿Cómo califica la suficiencia, actualidad y disponibilidad de las bases de datos bibliográficas digitales, libros físicos y revistas científicas?",
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
        "text": "¿La plataforma de campus virtual, conectividad wifi y licencias de software especializado responden satisfactoriamente a las exigencias académicas?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "transversal",
        "factor_number": 9,
        "factor_name": "Factor 9: Recursos Bibliográficos y Tecnológicos",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f9_q3",
        "text": "¿Ha recibido capacitación o inducción adecuada para la búsqueda de información científica en las bases de datos institucionales?",
        "type": "boolean",
        "aspect_type": "factual",
        "scope": "institucional",
        "target": "estudiantes",
        "factor_number": 9,
        "factor_name": "Factor 9: Recursos Bibliográficos y Tecnológicos",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # FACTOR 10: INFRAESTRUCTURA FÍSICA Y FINANCIERA
    # ==================================================
    {
        "id": "bank_f10_q1",
        "text": "¿Las aulas de clase, auditorios, laboratorios, talleres y áreas de estudio cuentan con condiciones óptimas de iluminación, ventilación y mantenimiento?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "institucional",
        "target": "transversal",
        "factor_number": 10,
        "factor_name": "Factor 10: Infraestructura Física y Financiera",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f10_q2",
        "text": "¿Los espacios físicos de la institución cuentan con condiciones adecuadas de accesibilidad para personas con movilidad reducida o discapacidad?",
        "type": "likert",
        "aspect_type": "factual",
        "scope": "institucional",
        "target": "transversal",
        "factor_number": 10,
        "factor_name": "Factor 10: Infraestructura Física y Financiera",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f10_q3",
        "text": "¿La gestión financiera institucional garantiza la sostenibilidad económica y el cumplimiento de las metas de inversión del programa?",
        "type": "likert",
        "aspect_type": "rating",
        "scope": "institucional",
        "target": "directivos",
        "factor_number": 10,
        "factor_name": "Factor 10: Infraestructura Física y Financiera",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # FACTOR 11: AUTORREGULACIÓN Y CULTURA DE CALIDAD
    # ==================================================
    {
        "id": "bank_f11_q1",
        "text": "¿Cómo evalúa el nivel de compromiso y participación de los estamentos en los procesos de Autoevaluación, Autorregulación y Acreditación?",
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
        "text": "¿Los Planes de Mejoramiento formulados e implementados se traducen en acciones concretas que fortalecen la calidad del programa?",
        "type": "likert",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 11,
        "factor_name": "Factor 11: Procesos de Autorregulación y Calidad",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f11_q3",
        "text": "Describa qué oportunidad de mejora estratégica considera urgente incorporar en el Plan de Mejoramiento Institucional o del Programa.",
        "type": "text",
        "aspect_type": "factual",
        "scope": "programa",
        "target": "transversal",
        "factor_number": 11,
        "factor_name": "Factor 11: Procesos de Autorregulación y Calidad",
        "options": [],
        "is_system": True
    },

    # ==================================================
    # FACTOR 12: INTERNACIONALIZACIÓN Y RELACIONES INTERINSTITUCIONALES
    # ==================================================
    {
        "id": "bank_f12_q1",
        "text": "¿Cómo califica las oportunidades y convenios de movilidad académica (pasantías, intercambio, doble titulación) nacionales e internacionales?",
        "type": "rating",
        "aspect_type": "opinion",
        "scope": "programa",
        "target": "transversal",
        "factor_number": 12,
        "factor_name": "Factor 12: Internacionalización e Interacción con el Entorno",
        "options": [],
        "is_system": True
    },
    {
        "id": "bank_f12_q2",
        "text": "¿El programa promueve activamente la participación de estudiantes y profesores en redes de conocimiento, eventos internacionales o COIL?",
        "type": "likert",
        "aspect_type": "rating",
        "scope": "programa",
        "target": "profesores",
        "factor_number": 12,
        "factor_name": "Factor 12: Internacionalización e Interacción con el Entorno",
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
