import json
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Chunk 1
target1 = """            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/institutions', methods=['GET', 'POST'])"""

replacement1 = """            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/programs/metadata', methods=['GET', 'POST'])
def handle_program_metadata():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    table_id = f"PROGRAM_METADATA_{program_id}"
    
    if request.method == 'POST':
        data = request.json
        try:
            existing = supabase.table('statistics').select("id").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", table_id).execute()
            if existing.data:
                supabase.table('statistics').update({
                    "data_json": json.dumps(data)
                }).eq("id", existing.data[0]['id']).execute()
            else:
                supabase.table('statistics').insert({
                    "inst_id": inst_id,
                    "program_id": program_id,
                    "table_id": table_id,
                    "data_json": json.dumps(data)
                }).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            print("Error saving program metadata:", e)
            return jsonify({"status": "error", "message": str(e)}), 500
    
    try:
        res = supabase.table('statistics').select("data_json").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", table_id).execute()
        if res.data:
            return jsonify(json.loads(res.data[0]['data_json']))
        return jsonify({})
    except Exception as e:
        return jsonify({})

@app.route('/api/institutions', methods=['GET', 'POST'])"""

if target1 in content:
    content = content.replace(target1, replacement1)
    print("Replaced chunk 1")
else:
    print("Target 1 not found")

# Chunk 2
target2 = """    data = request.json
    inst_id    = data.get('inst_id', 1)
    program_id = data.get('program_id', 0)
    condiciones_data = data.get('condiciones', {})   # Ya mapeadas desde el frontend
    program_name     = data.get('program_name', 'Programa Académico')
    inst_name        = data.get('inst_name', 'Institución de Educación Superior')

    try:
        # Serializar datos de condiciones, limitando el tamaño
        data_str = json.dumps(condiciones_data, ensure_ascii=False)
        if len(data_str) > 28000:
            data_str = data_str[:28000] + "... [datos truncados]"

        system_prompt = (
            "Eres un experto en evaluación de condiciones de calidad para el Ministerio de Educación "
            "Nacional de Colombia (MEN). Dominas a profundidad el Decreto 1330 de 2019, la Resolución "
            "0529 del MEN y los lineamientos para la Renovación de Registro Calificado (RRC) de programas "
            "de educación superior. Tu rol es redactar texto de soporte académico-normativo riguroso, "
            "propositivo y basado estrictamente en los datos del programa."
        )

        prompt = f\"\"\"
Se te entrega la información de autoevaluación del programa académico **{program_name}** 
de la institución **{inst_name}**, mapeada a las 9 condiciones de calidad del Decreto 1330 de 2019 
y la Resolución 0529 del MEN.

Datos por condición:
{data_str}

Redacta el SOPORTE DOCUMENTAL para el proceso de Renovación de Registro Calificado.
Para CADA UNA de las 9 condiciones debes generar:

1. **Análisis de cumplimiento**: descripción de cómo el programa evidencia el cumplimiento 
   de la condición, apoyándote en los datos e indicadores provistos.
2. **Indicadores normativos cubiertos**: lista los aspectos de la Resolución 0529 que tienen soporte.
3. **Aspectos por fortalecer**: señala brevemente los indicadores que requieren mayor documentación 
   o que están en proceso de consolidación.
4. **Calificación estimada**: Cumple plenamente / Cumple en alto grado / Cumple aceptablemente / 
   En proceso de cumplimiento, según los datos.

Usa formato Markdown estricto:
## Condición [N]: [Nombre]
### Análisis de Cumplimiento
### Indicadores con Soporte
### Aspectos por Fortalecer  
### Estimación de Cumplimiento

Al final agrega:
## Resumen Ejecutivo RRC
Con tabla de las 9 condiciones y su estimación.

Sé riguroso, formal y propositivo. Cita las normas cuando sea pertinente.
\"\"\""""

replacement2 = """    data = request.json
    inst_id    = data.get('inst_id', 1)
    program_id = data.get('program_id', 0)
    condiciones_data = data.get('condiciones', {})   # Ya mapeadas desde el frontend
    program_name     = data.get('program_name', 'Programa Académico')
    inst_name        = data.get('inst_name', 'Institución de Educación Superior')
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
            justification_str = f"\\nEvidencia de Justificación/Estudio de Oferta adjunta: {justification_url}. EXIGENCIA: Analizar obligatoriamente el contexto territorial en la Condición 2 basándose en este estudio."

        # Serializar datos de condiciones, limitando el tamaño
        data_str = json.dumps(condiciones_data, ensure_ascii=False)
        if len(data_str) > 28000:
            data_str = data_str[:28000] + "... [datos truncados]"

        system_prompt = (
            "Eres un experto en aseguramiento de la calidad en educación superior (Ministerio de Educación "
            "Nacional de Colombia y CNA). Dominas el modelo de acreditación CESU (Acuerdo 01/2025), el "
            "Decreto 1330 de 2019 y el Decreto 529 de 2024. Tu función es generar el SOPORTE DOCUMENTAL "
            "de Renovación de Registro Calificado articulando las 9 condiciones de calidad con los 55 "
            "indicadores comunes del proceso de autoevaluación."
        )

        prompt = f\"\"\"
Basado en el documento 'Indicadores Comunes del Modelo de Autoevaluación CESU (Decretos 1330/2019 y 529/2024)', 
analiza la información de autoevaluación del programa académico **{program_name}** de la institución **{inst_name}**.{meta_str}{justification_str}

Datos por condición:
{data_str}

INSTRUCCIÓN CRÍTICA: Debes obligatoriamente referenciar de forma explícita los nombres de las *evidencias documentales* que soporten la condición, y argumentar basándote en los *cuadros estadísticos* (tasas, promedios) descritos en la información entregada para demostrar una verdadera trayectoria de mejoramiento y autorregulación. NO produzcas un texto puramente descriptivo sin datos.

Redacta el SOPORTE DOCUMENTAL para el proceso de Renovación de Registro Calificado.
Para CADA UNA de las 9 condiciones debes generar:

1. **Análisis de cumplimiento**: descripción de cómo el programa evidencia el cumplimiento de la condición, apoyándote en los datos e indicadores provistos.
2. **Indicadores normativos cubiertos**: lista los aspectos de la Resolución 0529 que tienen soporte.
3. **Aspectos por fortalecer**: señala brevemente los indicadores que requieren mayor documentación o que están en proceso de consolidación.
4. **Calificación estimada**: Cumple plenamente / Cumple en alto grado / Cumple aceptablemente / En proceso de cumplimiento, según los datos.

Usa formato Markdown estricto:
## Condición [N]: [Nombre]
### Análisis de Cumplimiento
### Indicadores con Soporte
### Aspectos por Fortalecer  
### Estimación de Cumplimiento

Al final agrega:
## Resumen Ejecutivo RRC
Con tabla de las 9 condiciones y su estimación.

Sé riguroso, formal y propositivo. Cita las normas cuando sea pertinente.
\"\"\""""

if target2 in content:
    content = content.replace(target2, replacement2)
    print("Replaced chunk 2")
else:
    print("Target 2 not found")

# Chunk 3
target3 = """    except Exception as e:
        print(f"Error AI Generar RRC: {e}")
        return jsonify({"error": str(e)}), 500


# --- Rutas del Módulo de Encuestas de Autoevaluación ---"""

replacement3 = """    except Exception as e:
        print(f"Error AI Generar RRC: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/rrc/report', methods=['GET', 'POST'])
def handle_rrc_report():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    table_id = f"RRC_REPORT_PROGRAM_{program_id}"
    
    if request.method == 'POST':
        data = request.json
        try:
            existing = supabase.table('statistics').select("id").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", table_id).execute()
            if existing.data:
                supabase.table('statistics').update({
                    "data_json": json.dumps({"report": data.get('report')})
                }).eq("id", existing.data[0]['id']).execute()
            else:
                supabase.table('statistics').insert({
                    "inst_id": inst_id,
                    "program_id": program_id,
                    "table_id": table_id,
                    "data_json": json.dumps({"report": data.get('report')})
                }).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            print("Error saving RRC report:", e)
            return jsonify({"status": "error", "message": str(e)}), 500
    
    try:
        res = supabase.table('statistics').select("data_json").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", table_id).execute()
        if res.data:
            return jsonify(json.loads(res.data[0]['data_json']))
        return jsonify({})
    except Exception as e:
        print("Error fetching RRC report:", e)
        return jsonify({})

# --- Rutas del Módulo de Encuestas de Autoevaluación ---"""

if target3 in content:
    content = content.replace(target3, replacement3)
    print("Replaced chunk 3")
else:
    print("Target 3 not found")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
