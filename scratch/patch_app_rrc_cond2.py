import re

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_route = """

@app.route('/api/ai/generar_rrc_condicion', methods=['POST'])
def ai_generar_rrc_condicion():
    \"\"\"
    Genera el soporte documental para una sola condición de RRC.
    \"\"\"
    data = request.json
    inst_id    = data.get('inst_id', 1)
    program_id = data.get('program_id', 0)
    condicion_num = data.get('condicion_num', '1')
    condicion_data = data.get('condicion_data', {})
    program_name   = data.get('program_name', 'Programa Académico')
    inst_name      = data.get('inst_name', 'Institución de Educación Superior')
    justification_url = data.get('justification_url', '')

    try:
        # Cargar metadatos
        meta_table = f"PROGRAM_METADATA_{program_id}"
        meta_res = supabase.table('statistics').select("data_json").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", meta_table).execute()
        meta_str = ""
        if meta_res.data:
            meta_str = "\\nMetadatos de Denominación: " + str(meta_res.data[0]['data_json'])

        justification_str = ""
        if justification_url:
            justification_str = f"\\n\\nEVIDENCIA PRINCIPAL OBLIGATORIA ADJUNTA PARA LA CONDICIÓN {condicion_num}: {justification_url}\\nEXIGENCIA CRÍTICA: Debes analizar exhaustivamente este documento y basar la argumentación de la Condición {condicion_num} en los hallazgos de este soporte documental."

        data_str = json.dumps(condicion_data, ensure_ascii=False)

        system_prompt = (
            "Eres un evaluador experto y consultor analítico de alto nivel en aseguramiento de la calidad. "
            "Tu función es generar un SOPORTE DOCUMENTAL formal, técnico y estrictamente analítico "
            f"articulando de forma rigurosa los criterios de calidad con los indicadores evaluados, exclusivamente para la Condición {condicion_num}."
        )

        prompt = f\"\"\"
Basado en el documento 'Indicadores Comunes del Modelo de Autoevaluación CESU', 
analiza la información de autoevaluación del programa académico **{program_name}** de la institución **{inst_name}**.{meta_str}{justification_str}

Datos específicos de la Condición {condicion_num}:
{data_str}

INSTRUCCIÓN CRÍTICA: Debes obligatoriamente referenciar de forma explícita los nombres de las *evidencias documentales* que soporten la condición, y argumentar basándote en los *cuadros estadísticos* (tasas, promedios). NO produzcas un texto puramente descriptivo sin datos.

Redacta el SOPORTE DOCUMENTAL exclusivamente para la Condición {condicion_num}.

Debes generar:
1. **Análisis de cumplimiento**: descripción de cómo el programa evidencia el cumplimiento de la condición.
2. **Indicadores normativos cubiertos**.
3. **Aspectos por fortalecer**.
4. **Estimación de Cumplimiento**: Cumple plenamente / Cumple en alto grado / Cumple aceptablemente / En proceso de cumplimiento.

IMPORTANTE: No uses el título principal `## Condición {condicion_num}: ...`, porque el contenedor visual ya lo tiene.
Simplemente devuelve el contenido interno con esta estructura de subtítulos en Markdown:
### Análisis de Cumplimiento
[texto]
### Indicadores con Soporte
[texto]
### Aspectos por Fortalecer  
[texto]
### Estimación de Cumplimiento
[texto]
\"\"\"

        rrc_text = call_ai(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return jsonify({'status': 'success', 'report': rrc_text})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/rrc/report', methods=['GET', 'POST'])
"""

content = content.replace("@app.route('/api/rrc/report', methods=['GET', 'POST'])", new_route)

with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch 2 applied to app.py")
