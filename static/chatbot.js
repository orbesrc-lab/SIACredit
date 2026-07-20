// SKEL 360 Offline Chatbot
// Basado puramente en JavaScript sin consumo de API

const SKEL_WHATSAPP = "https://wa.me/573165167661?text=Hola,%20me%20gustar%C3%ADa%20hablar%20con%20un%20asesor%20sobre%20SKEL360";

// Dataset de intenciones y respuestas
// Cada bloque contiene 'keywords' (palabras clave) y la 'response' (respuesta en HTML)
let botDataset = [
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
    },
    {
        keywords: ["consultoria cna", "asesoria cna", "ayuda cna", "proceso cna", "tramite cna", "pares cna", "consejeros cna", "apoyo cna"],
        response: "Nuestra Consultoría CNA te acompaña desde el diagnóstico inicial hasta la visita de pares, asegurando que cumplas estrictamente con el modelo de acreditación."
    },
    {
        keywords: ["que hace el cna", "quien evalua", "consejo nacional de acreditacion", "criterios cna"],
        response: "El CNA (Consejo Nacional de Acreditación) es la entidad que evalúa la alta calidad. En SKEL conocemos a fondo sus 12 factores y te preparamos para superar su evaluación."
    },
    {
        keywords: ["como es el diagnostico", "que evalua el diagnostico", "diagnostico gratis", "diagnostico inicial", "evaluacion previa", "auditoria inicial"],
        response: "En el Diagnóstico Institucional analizamos las fortalezas y brechas de tu programa frente a la normativa, entregándote un reporte claro de qué falta para la acreditación."
    },
    {
        keywords: ["cuanto dura el diagnostico", "tiempo diagnostico", "demora diagnostico"],
        response: "Nuestro diagnóstico inicial es rápido y eficiente. Contáctanos por WhatsApp para agendar una sesión y evaluar tu estado actual sin costo."
    },
    {
        keywords: ["capacitacion de lideres", "entrenar equipo", "formar docentes", "capacitar administrativos", "curso de acreditacion"],
        response: "A través de SKEL Academy capacitamos a tus líderes de factor. Aprenden a recolectar evidencias, redactar justificaciones y manejar la plataforma SIAC autónomamente."
    },
    {
        keywords: ["tienen cursos", "dictan cursos", "diplomados", "seminarios acreditacion"],
        response: "Sí, SKEL Academy ofrece microlearning asincrónico en Liderazgo Ágil, Inteligencia Artificial aplicada a IES, y Gestión de Calidad Universitaria."
    },
    {
        keywords: ["certifican", "dan certificado", "entregan diploma", "certificado de curso"],
        response: "¡Por supuesto! Todos los cursos de SKEL Academy otorgan certificación inmediata que fortalece la hoja de vida de tus docentes y directivos."
    },
    {
        keywords: ["revision de informes", "revisar documento maestro", "correccion de autoevaluacion", "corregir informe", "auditar informe"],
        response: "Si ya tienes tu informe redactado, nuestros expertos ofrecen el servicio de Revisión de Informes, asegurando que la narrativa y las evidencias coincidan perfectamente antes de enviarlo al MEN."
    },
    {
        keywords: ["como genera el informe", "el sistema hace el informe", "descargar informe", "exportar autoevaluacion"],
        response: "SKEL SIAC consolida las calificaciones y justificaciones de todos los factores, generando tu Informe de Autoevaluación en PDF con un solo clic."
    },
    {
        keywords: ["quien redacta", "me ayudan a escribir", "redaccion de informe", "escribir documento maestro", "escribir autoevaluacion"],
        response: "Puedes redactarlo tú mismo en la plataforma, o dejar que 'Margy' (nuestra IA) genere borradores automáticamente basándose en las evidencias subidas."
    },
    {
        keywords: ["condiciones institucionales", "condicion institucional", "que son las condiciones", "requisitos previos institucionales"],
        response: "Las Condiciones Institucionales son requisitos previos del MEN. Te asesoramos en la estructura administrativa, financiera y de bienestar requerida para operar y ofertar programas."
    },
    {
        keywords: ["renovar condiciones", "vencen condiciones", "vencimiento condiciones institucionales"],
        response: "Si tus Condiciones Institucionales están por vencer, en SKEL estructuramos todo el documento de renovación asegurando que la IES demuestre su evolución y sostenibilidad."
    },
    {
        keywords: ["registro calificado", "obtener registro", "sacar registro calificado", "decreto 1330", "ley 1330", "norma 1330"],
        response: "Gestionamos la obtención y renovación de Registros Calificados bajo los parámetros del Decreto 1330, garantizando el cumplimiento de las condiciones de calidad del programa."
    },
    {
        keywords: ["renovar registro", "renovacion registro", "se vence el registro", "ampliar registro calificado"],
        response: "La renovación del Registro Calificado debe planearse con meses de anticipación. SKEL organiza tus evidencias de los últimos 7 años para asegurar una renovación exitosa."
    },
    {
        keywords: ["modificacion de registro", "modificar registro", "cambiar plan de estudios", "ampliar cupos"],
        response: "Te acompañamos en las solicitudes de modificación de Registro Calificado (cambios en plan de estudios, número de créditos, cupos o sedes)."
    },
    {
        keywords: ["cambio de caracter", "pasar de tecnica a universitaria", "institucion universitaria", "universidad", "cambiar caracter"],
        response: "El Cambio de Carácter (ej. de Institución Tecnológica a Universitaria) es un proceso riguroso. SKEL te diseña la ruta estratégica y académica para lograr la aprobación del MEN."
    },
    {
        keywords: ["redefinicion", "redefinicion institucional", "cambio de estatutos", "reforma estatutaria"],
        response: "Te apoyamos en procesos de Redefinición Institucional para actualizar tu misión, visión y estructura, alineándote con las nuevas demandas de la educación superior."
    },
    {
        keywords: ["como funciona la ia", "como es margy", "como ayuda la ia", "inteligencia artificial skel", "funciones de margy"],
        response: "Nuestra IA 'Margy' lee tus evidencias, analiza si cumplen con el indicador del CNA y detecta debilidades ocultas, ahorrando miles de horas de lectura manual."
    },
    {
        keywords: ["la ia es segura", "seguridad ia", "privacidad de datos", "me roban la informacion"],
        response: "Totalmente segura. SKEL utiliza modelos predictivos en entornos cerrados. La información de tu universidad es 100% confidencial y nunca se usa para entrenar modelos públicos."
    },
    {
        keywords: ["prediccion de riesgos", "ia predictiva", "predecir riesgos", "alerta temprana"],
        response: "SKEL AI detecta patrones en tus estadísticas y emite Alertas Tempranas si un factor (ej. deserción o investigación) tiene un rendimiento riesgoso que podría costar la acreditación."
    },
    {
        keywords: ["cuanto espacio tengo", "capacidad de almacenamiento", "limite de archivos", "peso de evidencias", "cuanto puedo subir"],
        response: "Ofrecemos almacenamiento escalable en la nube (AWS). Dependiendo del plan de tu IES, puedes almacenar miles de documentos, actas y videos sin preocuparte por el límite."
    },
    {
        keywords: ["como busco un documento", "buscador de evidencias", "encontrar acta", "buscar archivo"],
        response: "SKEL SIAC tiene un potente motor de búsqueda con filtros por Fecha, Factor, Característica, Tipo de Documento y Líder responsable. Encuentras cualquier acta en segundos."
    },
    {
        keywords: ["se borran los documentos", "copias de seguridad", "backup", "respaldo de evidencias"],
        response: "Tu información es sagrada. Realizamos copias de seguridad (backups) automáticos diarios para garantizar que nunca pierdas el trabajo de tu proceso de autoevaluación."
    },
    {
        keywords: ["quien hace las encuestas", "como mando la encuesta", "encuesta a estudiantes", "encuesta a egresados", "encuesta docentes"],
        response: "SKEL SIAC genera enlaces públicos (URLs) de las encuestas para que los compartas por correo o WhatsApp con tus estudiantes, docentes y egresados."
    },
    {
        keywords: ["graficas de encuestas", "resultados de encuestas", "tabulacion", "analisis de resultados"],
        response: "A medida que los usuarios responden las encuestas, la plataforma tabula y genera gráficos en tiempo real, listos para anexar al Informe de Autoevaluación."
    },
    {
        keywords: ["como hago el dofa", "matriz dofa", "matriz foda", "generar dofa"],
        response: "El módulo DOFA se alimenta automáticamente. Cada vez que calificas mal una característica, se vuelve una Debilidad; si la calificas alto, es Fortaleza. SKEL cruza todo automáticamente."
    },
    {
        keywords: ["seguimiento al plan de mejora", "medir avances", "indicadores de mejora", "cumplimiento del plan"],
        response: "Puedes asignar responsables y fechas límite a las estrategias del Plan de Mejoramiento. SKEL envía alertas y grafica el porcentaje de cumplimiento de cada meta."
    },
    {
        keywords: ["puedo tener varios programas", "varios registros", "multiples carreras", "multiples programas"],
        response: "Sí, SKEL es multi-programa. Desde un panel principal de Vicerrectoría puedes monitorear el avance de Ingeniería, Derecho, Medicina, etc., por separado."
    },
    {
        keywords: ["cuantos usuarios", "limite de usuarios", "licencias de usuario", "crear mas profesores"],
        response: "Dependiendo del plan adquirido, puedes crear cuentas ilimitadas para Líderes de Factor y Operativos, centralizando a toda tu comunidad académica."
    },
    {
        keywords: ["como ingreso", "como iniciar sesion", "olvide mi clave", "restablecer contraseña"],
        response: "Los usuarios acceden a la plataforma SIAC con su correo y contraseña. Si olvidas tu clave, puedes usar la opción 'Olvidé mi contraseña' en la pantalla de ingreso."
    },
    {
        keywords: ["funciona en mac", "funciona en celular", "app movil", "descargar app", "requerimientos de sistema"],
        response: "SKEL es 100% web (SaaS). Funciona perfectamente en Windows, Mac, Tablets y Celulares sin necesidad de instalar nada. Solo requieres conexión a internet."
    },
    {
        keywords: ["caidas del sistema", "el sistema se cae", "disponibilidad", "garantia de servicio"],
        response: "Garantizamos un 'uptime' del 99.9%. Nuestra infraestructura en la nube está diseñada para soportar picos de tráfico sin lentitud ni caídas."
    },
    {
        keywords: ["donde estan ubicados", "de donde son", "oficinas", "direccion fisica", "sede"],
        response: "Somos expertos a nivel nacional en Colombia. Atendemos a Instituciones de Educación Superior en cualquier ciudad a través de nuestros canales digitales y visitas in situ."
    },
    {
        keywords: ["tienen experiencia", "casos de exito", "han acreditado", "universidades acreditadas"],
        response: "¡Por supuesto! Contamos con casos de éxito comprobados. Hemos acompañado a múltiples ETDH e IES en otorgamiento de registros y acreditaciones de alta calidad."
    },
    {
        keywords: ["quien es john orbes", "director skel", "john orbes gomez"],
        response: "John Orbes es nuestro experto y director. Especialista en aseguramiento de la calidad en Educación Superior, con años de trayectoria liderando procesos ante el MEN y el CNA."
    },
    {
        keywords: ["como pago", "medios de pago", "transferencia", "facturacion electronica"],
        response: "Manejamos facturación electrónica y pagos institucionales (transferencia bancaria). Nos adaptamos a los procesos de compras de tu Universidad."
    },
    {
        keywords: ["dan soporte tecnico", "si tengo un problema", "mesa de ayuda", "horario de atencion"],
        response: "Incluimos Soporte Técnico especializado. Nuestro equipo atiende tus requerimientos de plataforma de lunes a viernes, asegurando que tu proceso no se detenga jamás."
    },
    {
        keywords: ["pregunta frecuente 1", "duda especifica 1", "servicio de consultoria avanzada 1", "variante de skel 1"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #1)</a>"
    },
    {
        keywords: ["pregunta frecuente 2", "duda especifica 2", "servicio de consultoria avanzada 2", "variante de skel 2"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #2)</a>"
    },
    {
        keywords: ["pregunta frecuente 3", "duda especifica 3", "servicio de consultoria avanzada 3", "variante de skel 3"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #3)</a>"
    },
    {
        keywords: ["pregunta frecuente 4", "duda especifica 4", "servicio de consultoria avanzada 4", "variante de skel 4"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #4)</a>"
    },
    {
        keywords: ["pregunta frecuente 5", "duda especifica 5", "servicio de consultoria avanzada 5", "variante de skel 5"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #5)</a>"
    },
    {
        keywords: ["pregunta frecuente 6", "duda especifica 6", "servicio de consultoria avanzada 6", "variante de skel 6"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #6)</a>"
    },
    {
        keywords: ["pregunta frecuente 7", "duda especifica 7", "servicio de consultoria avanzada 7", "variante de skel 7"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #7)</a>"
    },
    {
        keywords: ["pregunta frecuente 8", "duda especifica 8", "servicio de consultoria avanzada 8", "variante de skel 8"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #8)</a>"
    },
    {
        keywords: ["pregunta frecuente 9", "duda especifica 9", "servicio de consultoria avanzada 9", "variante de skel 9"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #9)</a>"
    },
    {
        keywords: ["pregunta frecuente 10", "duda especifica 10", "servicio de consultoria avanzada 10", "variante de skel 10"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #10)</a>"
    },
    {
        keywords: ["pregunta frecuente 11", "duda especifica 11", "servicio de consultoria avanzada 11", "variante de skel 11"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #11)</a>"
    },
    {
        keywords: ["pregunta frecuente 12", "duda especifica 12", "servicio de consultoria avanzada 12", "variante de skel 12"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #12)</a>"
    },
    {
        keywords: ["pregunta frecuente 13", "duda especifica 13", "servicio de consultoria avanzada 13", "variante de skel 13"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #13)</a>"
    },
    {
        keywords: ["pregunta frecuente 14", "duda especifica 14", "servicio de consultoria avanzada 14", "variante de skel 14"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #14)</a>"
    },
    {
        keywords: ["pregunta frecuente 15", "duda especifica 15", "servicio de consultoria avanzada 15", "variante de skel 15"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #15)</a>"
    },
    {
        keywords: ["pregunta frecuente 16", "duda especifica 16", "servicio de consultoria avanzada 16", "variante de skel 16"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #16)</a>"
    },
    {
        keywords: ["pregunta frecuente 17", "duda especifica 17", "servicio de consultoria avanzada 17", "variante de skel 17"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #17)</a>"
    },
    {
        keywords: ["pregunta frecuente 18", "duda especifica 18", "servicio de consultoria avanzada 18", "variante de skel 18"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #18)</a>"
    },
    {
        keywords: ["pregunta frecuente 19", "duda especifica 19", "servicio de consultoria avanzada 19", "variante de skel 19"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #19)</a>"
    },
    {
        keywords: ["pregunta frecuente 20", "duda especifica 20", "servicio de consultoria avanzada 20", "variante de skel 20"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #20)</a>"
    },
    {
        keywords: ["pregunta frecuente 21", "duda especifica 21", "servicio de consultoria avanzada 21", "variante de skel 21"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #21)</a>"
    },
    {
        keywords: ["pregunta frecuente 22", "duda especifica 22", "servicio de consultoria avanzada 22", "variante de skel 22"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #22)</a>"
    },
    {
        keywords: ["pregunta frecuente 23", "duda especifica 23", "servicio de consultoria avanzada 23", "variante de skel 23"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #23)</a>"
    },
    {
        keywords: ["pregunta frecuente 24", "duda especifica 24", "servicio de consultoria avanzada 24", "variante de skel 24"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #24)</a>"
    },
    {
        keywords: ["pregunta frecuente 25", "duda especifica 25", "servicio de consultoria avanzada 25", "variante de skel 25"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #25)</a>"
    },
    {
        keywords: ["pregunta frecuente 26", "duda especifica 26", "servicio de consultoria avanzada 26", "variante de skel 26"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #26)</a>"
    },
    {
        keywords: ["pregunta frecuente 27", "duda especifica 27", "servicio de consultoria avanzada 27", "variante de skel 27"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #27)</a>"
    },
    {
        keywords: ["pregunta frecuente 28", "duda especifica 28", "servicio de consultoria avanzada 28", "variante de skel 28"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #28)</a>"
    },
    {
        keywords: ["pregunta frecuente 29", "duda especifica 29", "servicio de consultoria avanzada 29", "variante de skel 29"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #29)</a>"
    },
    {
        keywords: ["pregunta frecuente 30", "duda especifica 30", "servicio de consultoria avanzada 30", "variante de skel 30"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #30)</a>"
    },
    {
        keywords: ["pregunta frecuente 31", "duda especifica 31", "servicio de consultoria avanzada 31", "variante de skel 31"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #31)</a>"
    },
    {
        keywords: ["pregunta frecuente 32", "duda especifica 32", "servicio de consultoria avanzada 32", "variante de skel 32"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #32)</a>"
    },
    {
        keywords: ["pregunta frecuente 33", "duda especifica 33", "servicio de consultoria avanzada 33", "variante de skel 33"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #33)</a>"
    },
    {
        keywords: ["pregunta frecuente 34", "duda especifica 34", "servicio de consultoria avanzada 34", "variante de skel 34"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #34)</a>"
    },
    {
        keywords: ["pregunta frecuente 35", "duda especifica 35", "servicio de consultoria avanzada 35", "variante de skel 35"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #35)</a>"
    },
    {
        keywords: ["pregunta frecuente 36", "duda especifica 36", "servicio de consultoria avanzada 36", "variante de skel 36"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #36)</a>"
    },
    {
        keywords: ["pregunta frecuente 37", "duda especifica 37", "servicio de consultoria avanzada 37", "variante de skel 37"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #37)</a>"
    },
    {
        keywords: ["pregunta frecuente 38", "duda especifica 38", "servicio de consultoria avanzada 38", "variante de skel 38"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #38)</a>"
    },
    {
        keywords: ["pregunta frecuente 39", "duda especifica 39", "servicio de consultoria avanzada 39", "variante de skel 39"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #39)</a>"
    },
    {
        keywords: ["pregunta frecuente 40", "duda especifica 40", "servicio de consultoria avanzada 40", "variante de skel 40"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #40)</a>"
    },
    {
        keywords: ["pregunta frecuente 41", "duda especifica 41", "servicio de consultoria avanzada 41", "variante de skel 41"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #41)</a>"
    },
    {
        keywords: ["pregunta frecuente 42", "duda especifica 42", "servicio de consultoria avanzada 42", "variante de skel 42"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #42)</a>"
    },
    {
        keywords: ["pregunta frecuente 43", "duda especifica 43", "servicio de consultoria avanzada 43", "variante de skel 43"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #43)</a>"
    },
    {
        keywords: ["pregunta frecuente 44", "duda especifica 44", "servicio de consultoria avanzada 44", "variante de skel 44"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #44)</a>"
    },
    {
        keywords: ["pregunta frecuente 45", "duda especifica 45", "servicio de consultoria avanzada 45", "variante de skel 45"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #45)</a>"
    },
    {
        keywords: ["pregunta frecuente 46", "duda especifica 46", "servicio de consultoria avanzada 46", "variante de skel 46"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #46)</a>"
    },
    {
        keywords: ["pregunta frecuente 47", "duda especifica 47", "servicio de consultoria avanzada 47", "variante de skel 47"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #47)</a>"
    },
    {
        keywords: ["pregunta frecuente 48", "duda especifica 48", "servicio de consultoria avanzada 48", "variante de skel 48"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #48)</a>"
    },
    {
        keywords: ["pregunta frecuente 49", "duda especifica 49", "servicio de consultoria avanzada 49", "variante de skel 49"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #49)</a>"
    },
    {
        keywords: ["pregunta frecuente 50", "duda especifica 50", "servicio de consultoria avanzada 50", "variante de skel 50"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #50)</a>"
    },
    {
        keywords: ["pregunta frecuente 51", "duda especifica 51", "servicio de consultoria avanzada 51", "variante de skel 51"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #51)</a>"
    },
    {
        keywords: ["pregunta frecuente 52", "duda especifica 52", "servicio de consultoria avanzada 52", "variante de skel 52"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #52)</a>"
    },
    {
        keywords: ["pregunta frecuente 53", "duda especifica 53", "servicio de consultoria avanzada 53", "variante de skel 53"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #53)</a>"
    },
    {
        keywords: ["pregunta frecuente 54", "duda especifica 54", "servicio de consultoria avanzada 54", "variante de skel 54"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #54)</a>"
    },
    {
        keywords: ["pregunta frecuente 55", "duda especifica 55", "servicio de consultoria avanzada 55", "variante de skel 55"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #55)</a>"
    },
    {
        keywords: ["pregunta frecuente 56", "duda especifica 56", "servicio de consultoria avanzada 56", "variante de skel 56"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #56)</a>"
    },
    {
        keywords: ["pregunta frecuente 57", "duda especifica 57", "servicio de consultoria avanzada 57", "variante de skel 57"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #57)</a>"
    },
    {
        keywords: ["pregunta frecuente 58", "duda especifica 58", "servicio de consultoria avanzada 58", "variante de skel 58"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #58)</a>"
    },
    {
        keywords: ["pregunta frecuente 59", "duda especifica 59", "servicio de consultoria avanzada 59", "variante de skel 59"],
        response: "En SKEL estamos preparados para resolver cualquier desafío de acreditación. Nuestro Ecosistema cubre todas tus necesidades normativas. <a href='https://wa.me/573165167661' target='_blank'>Habla con nosotros (Soporte Especializado #59)</a>"
    },

];

// Fallback por defecto si no entiende (Con número de WhatsApp directo)
const FALLBACK_RESPONSE = `No estoy seguro de entender tu pregunta, pero te aseguro que SKEL 360 es la plataforma ideal para tu proceso de acreditación.<br><br>Para una atención personalizada, <b><a href="${SKEL_WHATSAPP}" target="_blank">contáctanos por WhatsApp (+57 316 516 7661)</a></b> y un experto te atenderá de inmediato.`;

// Estado del Chat
let isChatOpen = false;
let voiceEnabled = false;
let useColombianVoice = false;


window.toggleSkelVoice = function() {
    voiceEnabled = !voiceEnabled;
    const btn = document.getElementById('skelVoiceBtn');
    if(voiceEnabled) {
        btn.style.color = '#10b981'; // Green
        btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>';
    } else {
        btn.style.color = 'white';
        btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>';
        window.speechSynthesis.cancel();
    }
}

function speakSkelText(htmlText) {
    if (!voiceEnabled) return;
    
    // Convert HTML to plain text
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = htmlText;
    const plainText = tempDiv.textContent || tempDiv.innerText || "";
    
    // Stop any ongoing speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(plainText);
    utterance.lang = useColombianVoice ? 'es-CO' : 'es-ES'; // Spanish
    utterance.rate = 1.0;     // Normal speed
    
    // Look for a nice voice
    const voices = window.speechSynthesis.getVoices();
    let selectedVoice = null;
    
    if (useColombianVoice) {
        selectedVoice = voices.find(v => v.lang === 'es-CO' && (v.name.includes('Google') || v.name.includes('Microsoft')));
        if (!selectedVoice) selectedVoice = voices.find(v => v.lang === 'es-CO');
    }
    
    if (!selectedVoice) {
        selectedVoice = voices.find(v => v.lang.startsWith('es') && (v.name.includes('Google') || v.name.includes('Microsoft') || v.name.includes('Siri')));
    }
    
    if (selectedVoice) utterance.voice = selectedVoice;

    
    window.speechSynthesis.speak(utterance);
}

// Inicialización de la UI
async function initSkelBot() {
    // Intentar cargar config para ver si debe usar voz colombiana
    try {
        const res = await fetch('/api/global-settings?t=' + Date.now());
        if (res.ok) {
            const data = await res.json();
            if (data.ai_voice_colombia) {
                useColombianVoice = true;
                voiceEnabled = true;
                
                // Actualizar UI del botón de voz
                setTimeout(() => {
                    const btn = document.getElementById('skelVoiceBtn');
                    if(btn) {
                        btn.style.color = '#10b981';
                        btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>';
                    }
                }, 500);

                // Pre-cargar voces para evitar bloqueos
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
                    window.speechSynthesis.getVoices();
                }
            }
        }
    } catch (e) {
        console.log("No se pudo cargar config de voz para chatbot");
    }
    
    if (document.getElementById('skelChatWidget')) return; // Ya existe
    try {
        const res = await fetch('/api/bot/dataset');
        if (res.ok) {
            const data = await res.json();
            if (data.status === 'success' && data.data) {
                botDataset.push(...data.data);
            }
        }
    } catch(e) {
        console.log('Error fetching dynamic bot dataset', e);
    }

    // 2. Crear el HTML y agregarlo al body
    const botHTML = `
        <!-- Botón flotante -->
        <button id="skelBotFab" class="skel-bot-fab" onclick="toggleSkelChat()">
            <svg viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 5.806 2 10.5c0 2.68 1.458 5.074 3.738 6.643l-1.077 3.23a1 1 0 001.26 1.26l3.23-1.077C10.074 20.806 11.02 21 12 21c5.523 0 10-3.806 10-8.5S17.523 2 12 2zm0 17c-.822 0-1.616-.118-2.368-.334a1 1 0 00-.632.052l-2.073.69-.69-2.072a1 1 0 00-.472-.519C4.167 15.534 3 13.11 3 10.5 3 6.916 7.037 4 12 4s9 2.916 9 6.5-4.037 6.5-9 6.5z"/></svg>
        </button>

        <div id="skelChatWindow" class="skel-chat-window">
            <div class="skel-chat-header">
                <div class="title">
                    <span class="status-dot"></span>
                    SKEL Bot
                </div>
                <div style="display:flex; gap:10px;">
                    <button id="skelVoiceBtn" onclick="toggleSkelVoice()" style="background:none; border:none; color:white; cursor:pointer;" title="Activar Voz">
                        <svg viewBox="0 0 24 24" style="width:20px;height:20px;fill:currentColor;"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>
                    </button>
                    <button class="skel-chat-close" onclick="toggleSkelChat()">×</button>
                </div>
            </div>
            <div id="skelChatMessages" class="skel-chat-messages">
                <div class="skel-message bot">
                    ¡Hola! 👋 Soy el asistente virtual de SKEL 360. ¿En qué te puedo colaborar hoy?
                </div>
            </div>
            <div class="skel-chat-input-area">
                <input type="text" id="skelChatInput" placeholder="Escribe tu mensaje aquí..." onkeypress="handleSkelEnter(event)">
                <button onclick="sendSkelMessage()">
                    <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                </button>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', botHTML);
}

// Abrir/Cerrar Chat
window.toggleSkelChat = function() {
    isChatOpen = !isChatOpen;
    const chatWindow = document.getElementById('skelChatWindow');
    if (isChatOpen) {
        chatWindow.classList.add('active');
        document.getElementById('skelChatInput').focus();
    } else {
        chatWindow.classList.remove('active');
    }
}

// Manejar Enter en el input
window.handleSkelEnter = function(e) {
    if (e.key === 'Enter') {
        sendSkelMessage();
    }
}

// Función principal de limpieza de texto
function normalizeText(text) {
    return text.toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "") // Quitar tildes
        .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?"']/g, "") // Quitar puntuación
        .trim();
}

// Evaluar la intención del usuario
function getBotResponse(userMsg) {
    const cleanMsg = normalizeText(userMsg);
    if (!cleanMsg) return null;

    let bestMatchScore = 0;
    let response = FALLBACK_RESPONSE;

    // Buscar en el dataset
    for (const intent of botDataset) {
        for (const keyword of intent.keywords) {
            const cleanKeyword = normalizeText(keyword);
            
            // Verificamos si el mensaje del usuario incluye la keyword, o si la keyword incluye el mensaje (si es muy corto)
            if (cleanMsg.includes(cleanKeyword)) {
                // Dar mayor peso a palabras clave más largas
                if (cleanKeyword.length > bestMatchScore) {
                    bestMatchScore = cleanKeyword.length;
                    response = intent.response;
                }
            }
        }
    }

    return response;
}

// Enviar mensaje
window.sendSkelMessage = function() {
    const input = document.getElementById('skelChatInput');
    const msg = input.value.trim();
    if (!msg) return;

    if (voiceEnabled && ('speechSynthesis' in window)) {
        // Unlock browser speech synthesis
        window.speechSynthesis.speak(new SpeechSynthesisUtterance(''));
    }

    input.value = '';
    
    const messagesContainer = document.getElementById('skelChatMessages');

    // 1. Mostrar mensaje del usuario
    const userBubble = document.createElement('div');
    userBubble.className = 'skel-message user';
    userBubble.textContent = msg;
    messagesContainer.appendChild(userBubble);
    
    // Auto-scroll
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // 2. Simular tiempo de "escribiendo" (300ms a 600ms)
    setTimeout(() => {
        const reply = getBotResponse(msg);
        
        // Si no se encontró respuesta, enviar al servidor para registro
        if (reply === FALLBACK_RESPONSE) {
            fetch('/api/bot/unanswered', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: msg })
            }).catch(e => console.log("Error registrando log:", e));
        }
        
        const botBubble = document.createElement('div');
        botBubble.className = 'skel-message bot';
        speakSkelText(reply);
        botBubble.innerHTML = reply;
        messagesContainer.appendChild(botBubble);
        
        // Auto-scroll
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 400 + Math.random() * 400);
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initSkelBot);
