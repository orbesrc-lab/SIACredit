import codecs

with codecs.open('c:/SIAC/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1
text = text.replace(
    "Actúa como par académico del CNA. Analiza los siguientes datos estadísticos del cuadro '{table_id}' e identifica tendencias, fortalezas o aspectos críticos. Responde directamente con el análisis en formato Markdown. Datos: {data_context}",
    "Actúa como un evaluador experto y consultor académico de alto nivel. Analiza de manera formal y rigurosa los siguientes datos estadísticos del cuadro '{table_id}' e identifica tendencias, fortalezas o aspectos críticos. Emplea lenguaje técnico y académico. Responde directamente con el análisis en formato Markdown. Datos: {data_context}"
)

# 2
text = text.replace(
    "Actúa como par académico del CNA. Analiza de manera integral los siguientes cuadros de datos estadísticos institucionales. Resalta los aspectos más importantes, tendencias globales y posibles oportunidades de mejora. Responde directamente con el análisis en formato Markdown. Datos: {data_context}",
    "Actúa como un evaluador experto y consultor académico de alto nivel. Analiza de manera formal, integral y rigurosa los siguientes cuadros de datos estadísticos. Resalta los aspectos más importantes, tendencias globales y posibles oportunidades de mejora. Emplea lenguaje técnico y académico. Responde directamente con el análisis en formato Markdown. Datos: {data_context}"
)

# 3
old_sys1 = """            "Te llamas Margy. Eres una asistente experta en acreditación de alta calidad para "
            "instituciones de educación superior en Colombia (CNA) desarrollada por SKEL. "
            "Responde de manera concisa, profesional y analítica basándote en estándares de "
            "calidad académica. Si te preguntan cómo te llamas o quién eres, responde que te llamas "
            "Margy, la asistente de acreditación de SKEL." """
old_sys1 = old_sys1.strip()
new_sys1 = """            "Te llamas Margy. Eres una asistente experta en evaluación y aseguramiento de alta calidad "
            "para instituciones organizacionales y educativas, desarrollada por SKEL. "
            "Responde de manera formal, académica, profesional y analítica basándote en altos estándares "
            "de calidad organizacional. Si te preguntan cómo te llamas o quién eres, responde que te llamas "
            "Margy, la asistente de evaluación de SKEL." """
new_sys1 = new_sys1.strip()
text = text.replace(old_sys1, new_sys1)

# 4
old_prompt1 = """        Actúa como un Par Académico experto del Consejo Nacional de Acreditación (CNA) de Colombia.
        A continuación se te provee un JSON con la información de la autoevaluación de un programa académico."""
new_prompt1 = """        Actúa como un evaluador experto y consultor analítico de alto nivel.
        A continuación se te provee un JSON con la información de la evaluación de la entidad o programa."""
text = text.replace(old_prompt1, new_prompt1)

# 5
old_sys2 = """            "Eres un experto en aseguramiento de la calidad en educación superior (Ministerio de Educación "
            "Nacional de Colombia y CNA). Dominas el modelo de acreditación CESU (Acuerdo 01/2025), el "
            "Decreto 1330 de 2019 y el Decreto 529 de 2024. Tu función es generar el SOPORTE DOCUMENTAL "
            "de Renovación de Registro Calificado articulando las 9 condiciones de calidad con los 55 "
            "indicadores comunes del proceso de autoevaluación." """
old_sys2 = old_sys2.strip()
new_sys2 = """            "Eres un evaluador experto y consultor analítico de alto nivel en aseguramiento de la calidad. "
            "Dominas estándares normativos y de evaluación de alto rigor académico y organizacional. "
            "Tu función es generar un SOPORTE DOCUMENTAL formal, técnico y estrictamente analítico "
            "articulando los criterios de calidad con los indicadores evaluados." """
new_sys2 = new_sys2.strip()
text = text.replace(old_sys2, new_sys2)

with codecs.open('c:/SIAC/app.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done!')
