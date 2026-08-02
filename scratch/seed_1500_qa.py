import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.db import supabase

# Temas principales y respuestas formales (las respuestas s pueden tener ortografa correcta)
topics = [
    {
        "module": "Autoevaluacion",
        "bases": [
            "como inicio un proceso de autoevaluacion",
            "pasos para autoevaluacion",
            "que significa el estado en progreso",
            "como subo evidencias para un factor",
            "puedo modificar la ponderacion",
            "donde descargo el informe final",
            "como calificar una caracteristica",
            "que hago despues de recolectar evidencias",
            "como veo el avance de autoevaluacion",
            "quien califica los factores"
        ],
        "response": [
            "Para iniciar un proceso, ve al módulo 'Autoevaluación', selecciona tu programa y haz clic en 'Nuevo Proceso'.",
            "Los pasos son: Ponderación, Encuestas, Evidencias, Calificación y finalmente Informe.",
            "Significa que el proceso está activo y todos pueden cargar información y contestar encuestas.",
            "En la matriz, haz clic en el ícono de Evidencias junto al indicador y sube tu PDF.",
            "Sí, el administrador puede editar la ponderación desde la configuración de la matriz.",
            "En 'Informes y Resultados' haz clic en 'Generar Informe Final'.",
            "Ve a la sección de Calificación Documental y asigna el valor según la escala institucional.",
            "Debes proceder a la calificación cuantitativa y cualitativa de cada indicador.",
            "El dashboard principal te mostrará una barra de progreso del proceso actual.",
            "Los líderes de calidad o pares internos asignados son los encargados de calificar."
        ]
    },
    {
        "module": "SKEL",
        "bases": [
            "que es skel",
            "para que sirve la plataforma",
            "como contacto a soporte",
            "es seguro skel",
            "quien hizo skel",
            "que significa skel360",
            "cuanto vale skel",
            "puedo usar skel en celular",
            "skel tiene app",
            "skel ayuda con la acreditacion"
        ],
        "response": [
            "SKEL es un ecosistema integral para la gestión de calidad y acreditación en educación superior.",
            "Sirve para automatizar procesos de autoevaluación, encuestas y reportes ante el Ministerio.",
            "Puedes enviar un mensaje directo en la bandeja de ayuda o escribir a nuestro WhatsApp de soporte.",
            "Sí, usamos encriptación de alto nivel y servidores seguros para proteger todos tus datos.",
            "Fue desarrollado por expertos en aseguramiento de la calidad educativa.",
            "SKEL 360 engloba software, consultoría, formación e Inteligencia Artificial.",
            "El costo varía según el tamaño de la institución. Puedes solicitar una cotización comercial.",
            "Sí, la plataforma es responsiva y puedes acceder desde el navegador de tu celular.",
            "Actualmente es una Web App (SaaS), no necesitas instalar nada.",
            "Sí, nuestra plataforma está diseñada específicamente para guiarte al éxito en tu acreditación."
        ]
    },
    {
        "module": "DOFA_PESTA",
        "bases": [
            "como hago el dofa",
            "que es el pesta",
            "como saco las debilidades",
            "la ia hace el dofa",
            "como exporto el dofa",
            "donde esta la matriz dofa",
            "que es un factor externo",
            "como califico una amenaza",
            "puedo editar las fortalezas",
            "para que sirve el analisis pesta"
        ],
        "response": [
            "Ve al módulo 'Diagnóstico DOFA' y haz clic en generar nueva matriz.",
            "El PESTA es el análisis de factores Políticos, Económicos, Sociales, Tecnológicos y Ambientales.",
            "Las debilidades se extraen automáticamente de los factores internos con bajas calificaciones.",
            "Sí, si generas el informe maestro con IA, el sistema extraerá automáticamente el DOFA.",
            "En la vista de la matriz, usa el botón 'Exportar Informe' para guardarlo en Word o PDF.",
            "Se encuentra en el módulo 'Análisis Institucional', subsección 'Diagnóstico DOFA'.",
            "Son variables del entorno (oportunidades o amenazas) que afectan a la institución.",
            "Debes asignarle un nivel de impacto y probabilidad desde el panel PESTA.",
            "Sí, puedes editar, eliminar o cambiar la prioridad de cualquier fortaleza manualmente.",
            "Sirve para identificar oportunidades y amenazas del entorno y cruzarlas con el DOFA."
        ]
    },
    {
        "module": "Margy IA",
        "bases": [
            "quien eres",
            "como te llamas",
            "eres un humano",
            "margy que haces",
            "como funcionas",
            "te equivocas",
            "puedes leer pdf",
            "como resumo un documento",
            "puedes hacer la autoevaluacion por mi",
            "quien te programo"
        ],
        "response": [
            "Soy Margy, la asistente experta en evaluación y calidad de SKEL.",
            "Mi nombre es Margy.",
            "No, soy una Inteligencia Artificial desarrollada para apoyarte.",
            "Analizo matrices, cuadros estadísticos, resumo documentos y respondo dudas sobre calidad.",
            "Uso modelos avanzados de IA para entender el contexto institucional y procesar datos.",
            "Intento ser muy precisa, pero siempre es bueno que un humano valide mis análisis estratégicos.",
            "Sí, puedes adjuntar un PDF o Word en el chat y yo extraeré la información clave.",
            "Adjunta el archivo en este chat y pídeme que lo resuma. Yo haré el resto.",
            "No puedo hacerla sola, pero puedo automatizar la generación de reportes y cruce de datos.",
            "Fui creada por el equipo de tecnología y expertos en calidad de SKEL 360."
        ]
    },
    {
        "module": "Estadisticas y Encuestas",
        "bases": [
            "como envio encuestas",
            "las encuestas son anonimas",
            "como veo los graficos",
            "puedo descargar en excel",
            "como mido la desercion",
            "donde estan los cuadros maestros",
            "puedo cambiar las preguntas",
            "como copio el link de la encuesta",
            "quien ve los resultados",
            "que pasa si no responden"
        ],
        "response": [
            "Desde el panel de la encuesta activa, haz clic en 'Copiar enlace' o 'Enviar por correo'.",
            "Sí, todas las encuestas de percepción son 100% anónimas.",
            "En el dashboard de resultados se generan automáticamente los gráficos en tiempo real.",
            "Sí, tienes un botón de 'Exportar a Excel' en la vista de tabulación.",
            "El módulo de estadísticas tiene cuadros específicos para registrar retención y deserción.",
            "Están en la sección 'Autoevaluación', bajo 'Cuadros Maestros de Datos'.",
            "Puedes crear nuevos bancos de preguntas desde la configuración de instrumentos.",
            "En la lista de encuestas, hay un ícono de enlace que lo copia al portapapeles.",
            "Solo los administradores y líderes asignados tienen acceso a la tabulación de resultados.",
            "El sistema te muestra la tasa de respuesta para que sepas si debes enviar recordatorios."
        ]
    }
]

# Modificadores colombianos informales sin puntuacin
prefixes = [
    "",
    "hola ",
    "buenas ",
    "oye ",
    "disculpa ",
    "que mas ",
    "ayudame con esto ",
    "necesito saber ",
    "porfa dime ",
    "me colaboras con ",
    "una pregunta ",
    "venga ",
    "como hago para saber ",
    "queria preguntar ",
    "dime ",
    "margy ",
    "hola margy "
]

suffixes = [
    "",
    " porfa",
    " gracias",
    " rapido",
    " si",
    " por favor"
]

generated = []

for topic in topics:
    for i in range(len(topic["bases"])):
        base_q = topic["bases"][i]
        base_r = topic["response"][i]
        
        # Generar combinaciones
        for pref in prefixes:
            for suff in suffixes:
                q = pref + base_q + suff
                generated.append({
                    "prompt": q,
                    "response": base_r,
                    "provider": "synthetic_seed_1500",
                    "model": "margy_knowledge",
                    "inst_id": 1,
                    "user_uid": "system"
                })

# Tenemos muchas combinaciones, vamos a tomar 1500 exactas
import random
random.seed(42) # Para reproducibilidad
random.shuffle(generated)

final_dataset = generated[:1500]

print(f"Total a insertar: {len(final_dataset)}")

# Insertar en lotes de 100
batch_size = 100
inserted = 0

for i in range(0, len(final_dataset), batch_size):
    batch = final_dataset[i:i+batch_size]
    try:
        supabase.table('ai_chat_logs').insert(batch).execute()
        inserted += len(batch)
        print(f"Insertados {inserted}/{len(final_dataset)}")
    except Exception as e:
        print(f"Error en lote: {e}")

print("Proceso completado. 1500 registros colombianizados insertados.")
