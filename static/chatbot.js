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
        keywords: ["que es skel", "que es", "de que trata", "que hacen", "para que sirve", "software", "plataforma", "aplicativo", "herramienta"],
        response: "SKEL 360 es el **software líder** para la gestión de Calidad, Autoevaluación, Registros Calificados y Acreditación de programas de Educación Superior. Ayudamos a las IES a centralizar sus evidencias y automatizar la generación de reportes."
    },
    {
        // Beneficios y Bondades
        keywords: ["bondad", "bondades", "ventaja", "ventajas", "beneficio", "beneficios", "por que usar", "fortaleza", "fortalezas", "mejor", "diferencia", "diferenciador", "utilidad"],
        response: `Entre nuestras principales bondades destacan:<br>
        ✅ <b>Centralización:</b> Todas las evidencias en un solo lugar.<br>
        ✅ <b>Automatización:</b> Generación de informes en 1 clic.<br>
        ✅ <b>Inteligencia Artificial:</b> Nuestro asistente 'Margy' redacta y analiza por ti.<br>
        ✅ <b>Trazabilidad:</b> Seguimiento al plan de mejoramiento e indicadores.<br>
        ✅ <b>Ahorro de Tiempo:</b> Reduce en un 70% el trabajo operativo.`
    },
    {
        // Costos y Precios
        keywords: ["precio", "precios", "costo", "costos", "cuanto vale", "cuanto cuesta", "planes", "gratis", "cotizar", "cotizacion", "valor"],
        response: `El costo de SKEL 360 depende del tamaño de la institución y el número de programas académicos. <br><br>Ofrecemos un <b>diagnóstico gratuito</b> para evaluar tus necesidades. <a href="${SKEL_WHATSAPP}" target="_blank">¡Escríbenos al WhatsApp para cotizar!</a>`
    },
    {
        // IA (Margy)
        keywords: ["inteligencia artificial", "ia", "margy", "robot", "automatico", "chatgpt", "gemini", "anthropic", "redactar"],
        response: "¡Sí! SKEL 360 integra su propia IA llamada **Margy**. Ella puede analizar datos, redactar informes de autoevaluación, analizar debilidades y sugerir planes de mejora automáticamente."
    },
    {
        // Evidencias
        keywords: ["evidencia", "evidencias", "documentos", "archivos", "subir", "almacenamiento", "nube", "guardar", "repositorio"],
        response: "Nuestro módulo de Evidencias permite organizar todos los documentos, actas y resoluciones por factores, características e indicadores, con potentes motores de búsqueda."
    },
    {
        // Informes y Reportes
        keywords: ["informe", "informes", "reporte", "reportes", "documento maestro", "autoevaluacion", "imprimir", "pdf", "word", "exportar"],
        response: "SKEL 360 consolida toda la información y te permite generar tu **Documento Maestro** o **Informe de Autoevaluación** completo (en PDF) a un solo clic, cumpliendo la normativa del CNA."
    },
    {
        // Encuestas
        keywords: ["encuesta", "encuestas", "preguntas", "estudiantes", "docentes", "egresados", "formulario", "formularios", "resultados", "graficas"],
        response: "Contamos con un módulo de encuestas dinámico para evaluar la percepción de estudiantes, docentes, egresados y administrativos. Las gráficas y estadísticas se generan en tiempo real."
    },
    {
        // Planes de Mejoramiento (DOFA)
        keywords: ["dofa", "foda", "plan de mejoramiento", "plan de mejora", "mejora continua", "estrategias", "debilidades", "fortalezas"],
        response: "El módulo DOFA permite cruzar tus Fortalezas y Debilidades para construir automáticamente el Plan de Mejoramiento, asignar responsables y hacer seguimiento a su cumplimiento."
    },
    {
        // Soporte, Contacto y Humano
        keywords: ["contacto", "telefono", "hablar", "humano", "asesor", "whatsapp", "llamar", "ayuda", "soporte", "comunicarme", "numero", "celular", "correo"],
        response: `¡Claro! Nuestro equipo está listo para ayudarte. Puedes hablar directamente con un asesor a través de nuestro <a href="${SKEL_WHATSAPP}" target="_blank">WhatsApp oficial dando clic aquí</a>.`
    },
    {
        // Modulos Generales
        keywords: ["modulo", "modulos", "funciones", "que tiene", "caracteristica", "aula", "crm", "formacion", "cursos"],
        response: "SKEL 360 incluye módulos de: Gestión Documental (Evidencias), Encuestas, Planes de Mejoramiento (DOFA), Estadísticas, Aula Virtual de Formación, y Reportes Automáticos con IA."
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
