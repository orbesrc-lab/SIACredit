import os, json, re

# Definición de Checklist oficial extraído del documento ISO_9001_2015_Requisitos_Auditoria_Evidencias_SGC.pdf (Capítulo 11)
CHECKLIST_DEFAULT = [
    {
        "id": "chk_4_1",
        "clausula": "4.1",
        "clausula_nombre": "Contexto de la Organización",
        "pregunta": "¿Existe un análisis documentado de cuestiones externas e internas?",
        "criterio": "Documento de contexto (PESTEL / Diagnóstico Interno) disponible y actualizado (máx 12 meses).",
        "estado": "Cumple", # Cumple / En Progreso / No Cumple
        "evidencia": "Matriz PESTEL y diagnóstico institucional.",
        "responsable": "Alta Dirección / Calidad",
        "hallazgos": ""
    },
    {
        "id": "chk_4_2",
        "clausula": "4.2",
        "clausula_nombre": "Partes Interesadas",
        "pregunta": "¿Se han identificado partes interesadas y sus requisitos pertinentes?",
        "criterio": "Matriz de Partes Interesadas con requisitos, nivel de influencia e impacto en el SGC.",
        "estado": "Cumple",
        "evidencia": "Matriz de Partes Interesadas actualizada.",
        "responsable": "Alta Dirección / Calidad",
        "hallazgos": ""
    },
    {
        "id": "chk_4_3",
        "clausula": "4.3",
        "clausula_nombre": "Alcance del SGC",
        "pregunta": "¿Está definido, documentado y justificado el alcance del SGC?",
        "criterio": "Documento de alcance con límites, productos/servicios y justificación de exclusiones.",
        "estado": "Cumple",
        "evidencia": "Declaración formal de alcance del SGC en manual.",
        "responsable": "Calidad",
        "hallazgos": ""
    },
    {
        "id": "chk_4_4",
        "clausula": "4.4",
        "clausula_nombre": "Sistema y Procesos",
        "pregunta": "¿Existe mapa de procesos con secuencia, interacción y caracterizaciones?",
        "criterio": "Mapa de procesos visual y fichas SIPOC por cada proceso estratégico, misional y de apoyo.",
        "estado": "Cumple",
        "evidencia": "Mapa de procesos interactivo y fichas SIPOC.",
        "responsable": "Dueños de Proceso / Calidad",
        "hallazgos": ""
    },
    {
        "id": "chk_5_1",
        "clausula": "5.1",
        "clausula_nombre": "Liderazgo y Compromiso",
        "pregunta": "¿Demuestra la alta dirección liderazgo y compromiso con el SGC?",
        "criterio": "Actas de comité, asignación presupuestal y comunicaciones formales de calidad.",
        "estado": "Cumple",
        "evidencia": "Actas de consejo y presupuesto asignado al SGC.",
        "responsable": "Alta Dirección",
        "hallazgos": ""
    },
    {
        "id": "chk_5_2",
        "clausula": "5.2",
        "clausula_nombre": "Política de Calidad",
        "pregunta": "¿La política de calidad está comunicada, entendida y revisada?",
        "criterio": "Política firmada, publicada en puntos visibles y alineada al propósito institucional.",
        "estado": "Cumple",
        "evidencia": "Política de Calidad en plataforma y carteleras.",
        "responsable": "Alta Dirección",
        "hallazgos": ""
    },
    {
        "id": "chk_5_3",
        "clausula": "5.3",
        "clausula_nombre": "Roles y Autoridades",
        "pregunta": "¿Están asignadas y comunicadas las responsabilidades y autoridades del SGC?",
        "criterio": "Organigrama, matrices de roles/responsabilidades (RACI) y perfiles de cargo.",
        "estado": "Cumple",
        "evidencia": "Perfiles de cargo y asignación de líderes.",
        "responsable": "Gestión Humana / Calidad",
        "hallazgos": ""
    },
    {
        "id": "chk_6_1",
        "clausula": "6.1",
        "clausula_nombre": "Riesgos y Oportunidades",
        "pregunta": "¿Existe matriz de riesgos y oportunidades con acciones planificadas?",
        "criterio": "Matriz de riesgos con evaluación de probabilidad/impacto, mitigación y seguimiento.",
        "estado": "Cumple",
        "evidencia": "Matriz de riesgos por proceso con semáforos.",
        "responsable": "Comité de Riesgos / Calidad",
        "hallazgos": ""
    },
    {
        "id": "chk_6_2",
        "clausula": "6.2",
        "clausula_nombre": "Objetivos de Calidad",
        "pregunta": "¿Existen objetivos de calidad medibles (SMART) con seguimiento?",
        "criterio": "Plan de objetivos con indicadores, metas, periodicidad y responsables definidos.",
        "estado": "Cumple",
        "evidencia": "Objetivos de calidad y Banco de Indicadores.",
        "responsable": "Calidad / Líderes",
        "hallazgos": ""
    },
    {
        "id": "chk_6_3",
        "clausula": "6.3",
        "clausula_nombre": "Planificación de Cambios",
        "pregunta": "¿Los cambios al SGC se planifican de manera sistemática?",
        "criterio": "Evaluaciones de impacto previas a cambios significativos y control de cambios en fichas.",
        "estado": "Cumple",
        "evidencia": "Histórico de control de cambios por proceso.",
        "responsable": "Calidad",
        "hallazgos": ""
    },
    {
        "id": "chk_7_1",
        "clausula": "7.1",
        "clausula_nombre": "Recursos e Infraestructura",
        "pregunta": "¿Se proporcionan y mantienen los recursos necesarios para el SGC?",
        "criterio": "Mantenimiento preventivo de infraestructura, tecnología y calibración de equipos.",
        "estado": "Cumple",
        "evidencia": "Planes de mantenimiento e inventario tecnológico.",
        "responsable": "Infraestructura / TI",
        "hallazgos": ""
    },
    {
        "id": "chk_7_2",
        "clausula": "7.2",
        "clausula_nombre": "Competencia del Personal",
        "pregunta": "¿Se demuestra la competencia y formación continua del personal?",
        "criterio": "Registros de capacitaciones, evaluaciones de desempeño y perfiles de competencias.",
        "estado": "Cumple",
        "evidencia": "Planes de capacitación y evaluaciones de desempeño 360.",
        "responsable": "Gestión Humana",
        "hallazgos": ""
    },
    {
        "id": "chk_7_3",
        "clausula": "7.3",
        "clausula_nombre": "Toma de Conciencia",
        "pregunta": "¿El personal es consciente de su aporte a la calidad y del impacto del incumplimiento?",
        "criterio": "Registros de inducciones, charlas de calidad y campañas de sensibilización.",
        "estado": "Cumple",
        "evidencia": "Actas de socialización de política y objetivos.",
        "responsable": "Calidad / Gestión Humana",
        "hallazgos": ""
    },
    {
        "id": "chk_7_4",
        "clausula": "7.4",
        "clausula_nombre": "Comunicación",
        "pregunta": "¿Están determinados los canales y planes de comunicación interna y externa?",
        "criterio": "Plan de comunicación institucional con matriz de qué, cuándo, a quién y cómo comunicar.",
        "estado": "Cumple",
        "evidencia": "Matriz y canales oficiales de comunicación.",
        "responsable": "Comunicaciones",
        "hallazgos": ""
    },
    {
        "id": "chk_7_5",
        "clausula": "7.5",
        "clausula_nombre": "Información Documentada",
        "pregunta": "¿La información documentada está controlada, aprobada y protegida?",
        "criterio": "Listado maestro de documentos, control de versiones y políticas de respaldo/seguridad.",
        "estado": "Cumple",
        "evidencia": "Listado maestro de procedimientos y políticas.",
        "responsable": "Calidad / TI",
        "hallazgos": ""
    },
    {
        "id": "chk_8_1",
        "clausula": "8.1",
        "clausula_nombre": "Control Operacional",
        "pregunta": "¿Los procesos operativos se planifican y ejecutan bajo condiciones controladas?",
        "criterio": "Planes de control operacional, procedimientos ejecutados y registros de cumplimiento.",
        "estado": "Cumple",
        "evidencia": "Fichas PHVA operativas y guías de servicio.",
        "responsable": "Líderes de Procesos Misionales",
        "hallazgos": ""
    },
    {
        "id": "chk_8_2",
        "clausula": "8.2",
        "clausula_nombre": "Requisitos del Cliente",
        "pregunta": "¿Se revisan y confirman los requisitos del servicio antes de comprometerse?",
        "criterio": "Registros de revisión de solicitudes, contratos y atención a requerimientos.",
        "estado": "Cumple",
        "evidencia": "Contratos, acuerdos de servicio y registros de matrícula/admisión.",
        "responsable": "Admisiones / Comercial",
        "hallazgos": ""
    },
    {
        "id": "chk_8_4",
        "clausula": "8.4",
        "clausula_nombre": "Control de Proveedores",
        "pregunta": "¿Los proveedores externos son evaluados, seleccionados y monitoreados?",
        "criterio": "Listado de proveedores aprobados con criterios de evaluación y seguimiento.",
        "estado": "Cumple",
        "evidencia": "Evaluación periódica de proveedores críticos.",
        "responsable": "Compras / Adquisiciones",
        "hallazgos": ""
    },
    {
        "id": "chk_8_5",
        "clausula": "8.5",
        "clausula_nombre": "Prestación del Servicio",
        "pregunta": "¿La prestación del servicio cuenta con trazabilidad, preservación e instrucciones?",
        "criterio": "Instrucciones de trabajo disponibles en puntos de uso y trazabilidad de registros.",
        "estado": "Cumple",
        "evidencia": "Formatos y registros de servicio prestado.",
        "responsable": "Operaciones / Docencia",
        "hallazgos": ""
    },
    {
        "id": "chk_8_6",
        "clausula": "8.6",
        "clausula_nombre": "Liberación del Servicio",
        "pregunta": "¿Se verifica el cumplimiento de requisitos antes de la liberación final del servicio?",
        "criterio": "Registros de verificación y firmas de aprobación de cumplimiento.",
        "estado": "Cumple",
        "evidencia": "Actas de grado, certificaciones o entrega de servicios.",
        "responsable": "Registro y Control / Calidad",
        "hallazgos": ""
    },
    {
        "id": "chk_9_1",
        "clausula": "9.1",
        "clausula_nombre": "Satisfacción del Cliente",
        "pregunta": "¿Se mide y analiza sistemáticamente la percepción y satisfacción del usuario?",
        "criterio": "Encuestas periódicas de satisfacción, análisis de PQRS y tendencias estadísticas.",
        "estado": "Cumple",
        "evidencia": "Reportes de encuestas y Banco de Indicadores de satisfacción.",
        "responsable": "Calidad / Servicio al Cliente",
        "hallazgos": ""
    },
    {
        "id": "chk_9_2",
        "clausula": "9.2",
        "clausula_nombre": "Análisis y Evaluación",
        "pregunta": "¿Se analizan los datos de desempeño, indicadores y eficacia del SGC?",
        "criterio": "Informes periódicos con gráficas de tendencia y toma de decisiones basada en evidencia.",
        "estado": "Cumple",
        "evidencia": "Tableros de control con semáforos e histórico de indicadores.",
        "responsable": "Calidad / Dirección",
        "hallazgos": ""
    },
    {
        "id": "chk_9_3",
        "clausula": "9.3",
        "clausula_nombre": "Auditoría Interna",
        "pregunta": "¿Se realizan auditorías internas periódicas con informes y seguimiento a hallazgos?",
        "criterio": "Programa anual de auditoría, auditores competentes, informes de visita y seguimiento a no conformidades.",
        "estado": "Cumple",
        "evidencia": "Módulo de Auditorías periódicas e informes de hallazgos.",
        "responsable": "Líder de Auditoría / Calidad",
        "hallazgos": ""
    },
    {
        "id": "chk_9_4",
        "clausula": "9.4",
        "clausula_nombre": "Revisión por la Dirección",
        "pregunta": "¿La alta dirección revisa el SGC a intervalos planificados con todas las entradas?",
        "criterio": "Actas formales de revisión con análisis de entradas requeridas y decisiones estratégicas.",
        "estado": "Cumple",
        "evidencia": "Acta anual de revisión por la dirección.",
        "responsable": "Alta Dirección",
        "hallazgos": ""
    },
    {
        "id": "chk_10_2",
        "clausula": "10.2",
        "clausula_nombre": "No Conformidad y Acción Correctiva",
        "pregunta": "¿Las no conformidades se gestionan con contención, causa raíz y verificación de eficacia?",
        "criterio": "Registro de NC (Menores/Mayores), método de causa raíz (5 Porqués/Ishikawa), ACC y cierre formal.",
        "estado": "Cumple",
        "evidencia": "Matriz y bandeja de No Conformidades con trazabilidad completa.",
        "responsable": "Calidad / Responsables de ACC",
        "hallazgos": ""
    },
    {
        "id": "chk_10_3",
        "clausula": "10.3",
        "clausula_nombre": "Mejora Continua",
        "pregunta": "¿Existen evidencias tangibles de mejora continua en la eficacia del SGC?",
        "criterio": "Planes de mejora ejecutados, proyectos Kaizen/PDCA y evolución positiva de indicadores.",
        "estado": "Cumple",
        "evidencia": "Planes de mejoramiento institucional y metas superadas.",
        "responsable": "Calidad / Alta Dirección",
        "hallazgos": ""
    }
]

print(f"Checklist estructurado con {len(CHECKLIST_DEFAULT)} preguntas normativas oficiales.")
