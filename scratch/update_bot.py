import re

new_dataset = """const botDataset = [
    {
        // Saludos
        keywords: ["hola", "buenos dias", "buenas tardes", "buenas noches", "saludos", "que tal", "buenas", "hey", "hello", "holis"],
        response: "¡Hola! 👋 Soy el asistente virtual de SKEL 360. ¿En qué te puedo colaborar hoy?"
    },
    {
        // Despedidas
        keywords: ["adios", "chao", "hasta luego", "nos vemos", "bye", "hasta pronto", "gracias"],
        response: "¡Con mucho gusto! Si necesitas algo más, aquí estaré. ¡Que tengas un excelente día!"
    },
    {
        // Qué es SKEL
        keywords: ["que es skel", "que es", "de que trata", "que hacen", "para que sirve", "software", "plataforma", "aplicativo", "herramienta", "quienes son"],
        response: "SKEL 360 es mucho más que un software. Somos el **único ecosistema integral para educación superior**. Combinamos consultoría experta, una plataforma SaaS (SIAC), academia de formación y tecnología predictiva con IA para asegurar tu acreditación."
    },
    {
        // SKEL Consulting (Consultoría)
        keywords: ["consultoria", "asesoria", "consultores", "expertos", "acompañamiento", "metodologia", "consulting", "acreditacion garantizada"],
        response: "**SKEL Consulting:** Ofrecemos acompañamiento metodológico probado por expertos para garantizar el cumplimiento normativo ante el CNA y el MEN, sin ensayos ni errores. Construimos tu ruta clara de acreditación."
    },
    {
        // SKEL SIAC (SaaS)
        keywords: ["saas", "siac", "plataforma digital", "piloto automatico", "digital", "sistema"],
        response: "**SKEL SIAC (SaaS):** Es tu piloto automático. Nuestra plataforma propia organiza evidencias, automatiza informes y elimina el caos documental de tu institución en la nube."
    },
    {
        // SKEL Academy (Formación)
        keywords: ["academy", "formacion", "capacitacion", "academia", "cursos", "aprender", "certificacion", "certificar", "estudiar", "microlearning", "asincronico"],
        response: "**SKEL Academy:** Capacitamos a tu equipo con formación 100% online, asincrónica y de alto impacto (microlearning) para que lideren los procesos de calidad con total autonomía y confianza."
    },
    {
        // SKEL AI (Inteligencia Predictiva)
        keywords: ["ai", "inteligencia predictiva", "riesgos", "prediccion", "analisis avanzado", "margy"],
        response: "**SKEL AI:** Integramos inteligencia artificial predictiva (Margy). Nuestro modelo anticipa riesgos antes de que sean problemas graves, dándote visibilidad absoluta sobre tus factores de calidad."
    },
    {
        // Acreditación y Registros Calificados
        keywords: ["acreditacion", "registro calificado", "cna", "men", "ministerio", "renovacion", "1330", "decreto 1330", "alta calidad"],
        response: "Te acompañamos en procesos de **Acreditación de Alta Calidad** y en la obtención o renovación de **Registros Calificados** (Decreto 1330), guiándote en la construcción y organización de las evidencias."
    },
    {
        // Condiciones Institucionales y Cambio de Carácter
        keywords: ["condiciones institucionales", "cambio de caracter", "redefinicion", "requisitos previos", "transito", "nivel academico"],
        response: "Te ayudamos con el cumplimiento de **Condiciones Institucionales** indispensables y ofrecemos acompañamiento estratégico para el **Cambio de Carácter y Redefinición** de tu IES."
    },
    {
        // Diagnóstico Inicial
        keywords: ["diagnostico", "estado actual", "ruta", "evaluacion inicial", "analisis inicial", "gratis"],
        response: "El primer paso es nuestro **Diagnóstico Institucional Gratuito**. Evaluamos el estado actual de tu programa frente a los 12 factores del CNA para definir tu hoja de ruta. <a href='https://wa.me/573165167661' target='_blank'>¡Agéndalo aquí!</a>"
    },
    {
        // Gestión de Evidencias
        keywords: ["evidencia", "evidencias", "documentos", "archivos", "subir", "almacenamiento", "repositorio", "carpetas"],
        response: "Olvídate de las 800 carpetas dispersas. Con SIAC puedes subir, organizar y clasificar documentos directamente por Factor, Característica y Aspecto del CNA."
    },
    {
        // Autoevaluación y Calificación
        keywords: ["autoevaluacion", "calificar", "calificacion", "justificacion", "evaluar", "12 factores", "factores"],
        response: "Realiza tu Autoevaluación Online. Califica cada característica, registra justificaciones colaborativamente con los líderes de factor y visualiza las estadísticas en tiempo real."
    },
    {
        // Informes y Reportes Automáticos
        keywords: ["informe", "informes", "reporte", "reportes", "documento maestro", "imprimir", "pdf", "exportar"],
        response: "Reduce el trabajo de semanas a horas. SKEL SIAC genera tu **Documento de Autoevaluación** completo automáticamente en un clic, con todas las evidencias enlazadas."
    },
    {
        // Planes de Mejoramiento (DOFA)
        keywords: ["dofa", "foda", "plan de mejoramiento", "plan de mejora", "mejora continua", "estrategias", "debilidades", "fortalezas"],
        response: "El módulo DOFA cruza tus Fortalezas y Debilidades automáticamente para construir el Plan de Mejoramiento, asignar responsables y visualizar estadísticas de avance."
    },
    {
        // Estadísticas y Dashboards
        keywords: ["estadistica", "estadisticas", "dashboard", "graficas", "avance", "progreso", "tablero"],
        response: "Nuestra plataforma te brinda Dashboards interactivos en tiempo real con el avance por factor, pesos ponderados y alertas tempranas de cumplimiento."
    },
    {
        // Roles y Usuarios
        keywords: ["usuario", "usuarios", "roles", "administrador", "lider de factor", "operativo", "acceso", "multi institucion"],
        response: "SIAC cuenta con acceso Multi-Usuario (Administrador, Líder de Factor, Operativo) y capacidad Multi-Institución, permitiendo gestionar varias universidades y programas desde una cuenta central."
    },
    {
        // Beneficios y Bondades
        keywords: ["bondad", "bondades", "ventaja", "ventajas", "beneficio", "beneficios", "por que usar", "fortaleza", "mejor", "diferencia", "utilidad"],
        response: "Las ventajas de SKEL360 incluyen:<br>✅ Ahorro del 70% de tiempo operativo.<br>✅ Visibilidad total de procesos.<br>✅ Metodología garantizada.<br>✅ IA predictiva.<br>✅ Cero caos de documentos."
    },
    {
        // Encuestas
        keywords: ["encuesta", "encuestas", "preguntas", "estudiantes", "docentes", "egresados", "formulario", "formularios", "resultados"],
        response: "Tenemos un sistema de encuestas dinámico integrado. Evalúa la percepción de estudiantes, docentes y egresados, y obtén tabulaciones y gráficas de inmediato."
    },
    {
        // Costos y Precios
        keywords: ["precio", "precios", "costo", "costos", "cuanto vale", "cuanto cuesta", "planes", "cotizar", "cotizacion", "valor"],
        response: "El costo se ajusta a las necesidades, tamaño de la institución y cantidad de programas. <a href='https://wa.me/573165167661' target='_blank'>Contáctanos por WhatsApp para recibir una cotización a medida.</a>"
    },
    {
        // Soporte, Contacto y Humano
        keywords: ["contacto", "telefono", "hablar", "humano", "asesor", "whatsapp", "llamar", "ayuda", "soporte", "comunicarme", "numero", "celular", "correo"],
        response: "¡Estamos aquí para ayudarte! Habla directamente con John Orbes o uno de nuestros expertos haciendo <a href='https://wa.me/573165167661' target='_blank'>clic aquí para ir a WhatsApp</a> (o escribe al +57 316 516 7661)."
    }
];"""

with open('c:/SIAC/static/chatbot.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'const botDataset = \[.*?\];', new_dataset, content, flags=re.DOTALL)

with open('c:/SIAC/static/chatbot.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('Dataset expanded in chatbot.js')
