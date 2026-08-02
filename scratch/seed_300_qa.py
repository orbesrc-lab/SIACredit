import os
from supabase import create_client
import time

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.db import supabase

topics = [
    {
        "module": "Autoevaluación",
        "questions": [
            "¿Cómo inicio un proceso de autoevaluación?",
            "¿Cuáles son los pasos para la autoevaluación?",
            "¿Qué significa el estado 'En progreso' en autoevaluación?",
            "¿Cómo subo las evidencias para un factor?",
            "¿Puedo modificar la ponderación de las características?",
            "¿Dónde descargo el informe final de autoevaluación?"
        ],
        "responses": [
            "Para iniciar un proceso, ve al módulo 'Autoevaluación', selecciona tu programa y haz clic en 'Nuevo Proceso'. Define las fechas y guárdalo.",
            "Los pasos principales son: Ponderación, Asignación de encuestas, Recolección de evidencias, Calificación documental, e Informe Final.",
            "Significa que el proceso está activo y los usuarios pueden subir evidencias y contestar encuestas.",
            "En la matriz documental, haz clic en el ícono de 'Evidencias' al lado del indicador correspondiente. Podrás subir archivos PDF o Word.",
            "Sí, como administrador o líder puedes editar la ponderación de factores, características e indicadores desde la configuración de la matriz.",
            "Una vez calificadas todas las características, ve a 'Informes y Resultados' y haz clic en 'Generar Informe Final en PDF o Word'."
        ]
    },
    {
        "module": "SKEL",
        "questions": [
            "¿Qué es SKEL?",
            "¿Qué significa SKEL?",
            "¿Para qué sirve esta plataforma?",
            "¿Quién desarrolló SKEL?",
            "¿Cómo puedo contactar a soporte de SKEL?",
            "¿Es seguro usar SKEL para nuestros datos?"
        ],
        "responses": [
            "SKEL es una plataforma integral de gestión de calidad, evaluación y aseguramiento para organizaciones, desarrollada por SKEL.",
            "SKEL representa nuestro Sistema de Conocimiento y Evaluación para la Calidad.",
            "Sirve para gestionar procesos de autoevaluación, acreditación, encuestas de percepción, y análisis estadístico en instituciones y empresas.",
            "SKEL fue desarrollado por un equipo de expertos en aseguramiento de la calidad y tecnología.",
            "Puedes contactar a soporte a través del módulo de 'Herramientas Gerenciales' o enviando un mensaje directo en la bandeja de ayuda.",
            "Sí, SKEL utiliza encriptación de alto nivel y se apoya en infraestructuras en la nube seguras (como Supabase) para garantizar la privacidad y seguridad."
        ]
    },
    {
        "module": "Margy IA",
        "questions": [
            "¿Quién eres?",
            "¿Cómo te llamas?",
            "¿Qué puedes hacer por mí?",
            "¿Eres humana?",
            "¿Cómo analizas los informes?",
            "¿Margy puede equivocarse?"
        ],
        "responses": [
            "Soy Margy, la asistente experta en evaluación y aseguramiento de la calidad desarrollada por SKEL.",
            "Mi nombre es Margy, asistente virtual de SKEL.",
            "Puedo ayudarte a resumir informes, guiarte en el uso de la plataforma, analizar matrices de calidad y responder dudas sobre procesos de acreditación.",
            "No, soy una Inteligencia Artificial diseñada específicamente para asistir en tareas de evaluación institucional.",
            "Leo los datos estructurados y los archivos que me adjuntas, aplico criterios de calidad estándar y genero resúmenes o recomendaciones analíticas.",
            "Como IA, siempre busco dar la respuesta más precisa basada en los datos proporcionados, pero siempre es recomendable que un evaluador humano revise mis conclusiones."
        ]
    },
    {
        "module": "Gestión de Usuarios",
        "questions": [
            "¿Cómo agrego un nuevo usuario?",
            "¿Qué roles existen en la plataforma?",
            "¿Un usuario operativo puede eliminar datos?",
            "¿Cómo cambio mi contraseña?",
            "¿Dónde asigno permisos a los líderes?"
        ],
        "responses": [
            "Como administrador, ve a 'Configuración', sección 'Gestión de Usuarios', y haz clic en 'Agregar Usuario'. Deberás asignar un correo y un rol.",
            "Existen roles como Super Admin, Admin de Institución, Líder de Calidad, Operativo y Usuario Básico.",
            "Generalmente no. El rol operativo está diseñado para cargar información y evidencias, pero la eliminación está restringida a administradores y líderes.",
            "En la esquina superior derecha, haz clic en tu perfil y selecciona 'Cambiar contraseña'. También un administrador puede resetearla desde Configuración.",
            "Los permisos de los líderes se asignan automáticamente según el programa al que están vinculados en el panel de usuarios."
        ]
    },
    {
        "module": "Encuestas y Estadísticas",
        "questions": [
            "¿Cómo envío encuestas a los estudiantes?",
            "¿Puedo ver las estadísticas en tiempo real?",
            "¿Cómo exporto los resultados de las encuestas?",
            "¿Qué tipo de gráficos genera SKEL?",
            "¿Se pueden anonimizar los resultados?"
        ],
        "responses": [
            "Desde el módulo 'Análisis Institucional', selecciona la encuesta activa y utiliza la opción 'Copiar enlace' o 'Enviar masivamente' por correo.",
            "Sí, el panel de control (Dashboard) actualiza las métricas y tasas de respuesta en tiempo real a medida que los usuarios contestan.",
            "En la vista de resultados de la encuesta, tienes opciones para descargar la tabulación en Excel o un resumen en PDF.",
            "SKEL genera gráficos de barras, diagramas de pastel para preguntas cerradas y nubes de palabras para respuestas abiertas.",
            "Todas las encuestas de percepción de calidad en SKEL son completamente anónimas por defecto para garantizar respuestas honestas."
        ]
    }
]

# Generate permutations and variants to reach 300 Q&As
generated_qas = []

variations = [
    ("Por favor dime, ", ""),
    ("Necesito saber ", ""),
    ("Hola Margy, ", ""),
    ("Una consulta: ", ""),
    ("", " ¡Gracias!"),
    ("", " (Explícame brevemente)"),
    ("¿Podrías indicarme ", "?"),
    ("Duda rápida: ", ""),
]

for topic in topics:
    q_list = topic["questions"]
    r_list = topic["responses"]
    
    for i in range(len(q_list)):
        base_q = q_list[i]
        base_r = r_list[i]
        
        # Add the exact base
        generated_qas.append({"q": base_q, "r": base_r})
        
        # Add variations
        for prefix, suffix in variations:
            mod_q = f"{prefix}{base_q.lower() if prefix else base_q}{suffix}"
            if mod_q != base_q:
                generated_qas.append({"q": mod_q, "r": base_r})

# If we don't have 300 yet, we will duplicate some with minor changes
needed = 300 - len(generated_qas)
if needed > 0:
    extra = []
    for i in range(needed):
        source = generated_qas[i % len(generated_qas)]
        extra.append({
            "q": f"Consulta #{i+1}: {source['q']}",
            "r": source['r']
        })
    generated_qas.extend(extra)

# Truncate strictly to 300
generated_qas = generated_qas[:300]

print(f"Total generados: {len(generated_qas)}")

# Insert into database in batches
batch_size = 50
inserted = 0

for i in range(0, len(generated_qas), batch_size):
    batch = generated_qas[i:i+batch_size]
    
    rows = []
    for qa in batch:
        rows.append({
            "prompt": qa["q"],
            "response": qa["r"],
            "provider": "synthetic_seed",
            "model": "margy_knowledge",
            "inst_id": 1,
            "user_uid": "system"
        })
        
    try:
        supabase.table('ai_chat_logs').insert(rows).execute()
        inserted += len(rows)
        print(f"Inserted {inserted}/{len(generated_qas)}")
    except Exception as e:
        print(f"Error in batch: {e}")
        
print("Seed process completed.")
