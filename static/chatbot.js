// SKEL 360 Offline Chatbot
// Basado puramente en JavaScript sin consumo de API

const SKEL_WHATSAPP = "https://wa.me/573165167661?text=Hola,%20me%20gustar%C3%ADa%20hablar%20con%20un%20asesor%20sobre%20SKEL360";

// Dataset de intenciones y respuestas
// Cada bloque contiene 'keywords' (palabras clave) y la 'response' (respuesta en HTML)
const botDataset = [
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
];

// Fallback por defecto si no entiende (Con número de WhatsApp directo)
const FALLBACK_RESPONSE = `No estoy seguro de entender tu pregunta, pero te aseguro que SKEL 360 es la plataforma ideal para tu proceso de acreditación.<br><br>Para una atención personalizada, <b><a href="${SKEL_WHATSAPP}" target="_blank">contáctanos por WhatsApp (+57 316 516 7661)</a></b> y un experto te atenderá de inmediato.`;

// Estado del Chat
let isChatOpen = false;

// Inicialización de la UI
function initSkelBot() {
    // 1. Crear el HTML y agregarlo al body
    const botHTML = `
        <!-- Botón flotante -->
        <button id="skelBotFab" class="skel-bot-fab" onclick="toggleSkelChat()">
            <svg viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 5.806 2 10.5c0 2.68 1.458 5.074 3.738 6.643l-1.077 3.23a1 1 0 001.26 1.26l3.23-1.077C10.074 20.806 11.02 21 12 21c5.523 0 10-3.806 10-8.5S17.523 2 12 2zm0 17c-.822 0-1.616-.118-2.368-.334a1 1 0 00-.632.052l-2.073.69-.69-2.072a1 1 0 00-.472-.519C4.167 15.534 3 13.11 3 10.5 3 6.916 7.037 4 12 4s9 2.916 9 6.5-4.037 6.5-9 6.5z"/></svg>
        </button>

        <!-- Ventana del Chat -->
        <div id="skelChatWindow" class="skel-chat-window">
            <div class="skel-chat-header">
                <div class="title">
                    <span class="status-dot"></span>
                    SKEL Bot
                </div>
                <button class="skel-chat-close" onclick="toggleSkelChat()">×</button>
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
        
        const botBubble = document.createElement('div');
        botBubble.className = 'skel-message bot';
        botBubble.innerHTML = reply;
        messagesContainer.appendChild(botBubble);
        
        // Auto-scroll
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 400 + Math.random() * 400);
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initSkelBot);
