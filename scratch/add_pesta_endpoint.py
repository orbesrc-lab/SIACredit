import codecs
with codecs.open('c:/SIAC/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# We look for the end of `ai_generate_dofa`
search_marker = """        print(f"Error AI Generate DOFA: {e}")
        return jsonify({"error": str(e)}), 500
"""

pesta_code = """
@app.route('/api/ai/generate_pesta', methods=['POST'])
def ai_generate_pesta():
    data = request.json
    inst_id = data.get('inst_id')
    program_id = data.get('program_id')
    contexto_espacial = data.get('contexto', 'Colombia')
    
    try:
        # Cargar metadatos del programa para el contexto
        meta_table = f"PROGRAM_METADATA_{program_id}"
        meta_res = supabase.table('statistics').select("data_json").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", meta_table).execute()
        meta_str = ""
        if meta_res.data:
            meta_str = "Metadatos del programa/institución: " + str(meta_res.data[0]['data_json'])

        prompt = f'''
        Actúa como un experto en planeación estratégica institucional.
        Debes realizar un barrido referencial y análisis PESTA (Político, Económico, Social, Tecnológico, Ambiental) para la institución y su respectivo campo disciplinar.
        
        Contexto espacial de evaluación: {contexto_espacial} (si se pide regional o internacional, enfócate en ese alcance geográfico).
        Información y contexto disciplinar del programa:
        {meta_str}
        
        Tu tarea es generar un informe PESTA secuencial enfocado en las tendencias del sector educativo/organizacional y disciplinar.
        A partir de este análisis PESTA, debes extraer y listar claramente las Oportunidades (O) y Amenazas (A) que afectan directamente a la institución.
        
        Debes devolver tu respuesta ESTRICTAMENTE en formato JSON válido, con la siguiente estructura:
        {{
            "informe_pesta": "# Análisis PESTA y Barrido Referencial\\n\\n## Político\\n...\\n\\n## Económico\\n...",
            "oportunidades": [
                {{"id": "O1", "descripcion": "Descripción concisa...", "importancia": 1}}
            ],
            "amenazas": [
                {{"id": "A1", "descripcion": "Descripción concisa...", "importancia": 1}}
            ]
        }}
        Prioriza los factores en 'importancia' de 1 a N, siendo 1 el más crítico.
        Asegúrate de escapar correctamente los saltos de línea (\\\\n) dentro del campo string 'informe_pesta' para que el JSON sea válido.
        Devuelve únicamente el texto JSON y NADA MÁS.
        '''
        
        pesta_res = call_ai(
            messages=[
                {"role": "system", "content": "Eres un asistente experto que solo devuelve estructuras JSON puras y válidas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=4000
        )
        
        # Limpieza básica
        pesta_res = pesta_res.replace('```json', '').replace('```', '').strip()
        
        try:
            pesta_json = json.loads(pesta_res)
        except Exception as e_json:
            print("Error parsing PESTA JSON:", str(e_json), "Raw Output:", pesta_res[:200])
            pesta_json = {"informe_pesta": "# Error\\nNo se pudo generar el formato correcto.", "oportunidades": [], "amenazas": [], "error_parseo": "El formato generado no fue un JSON válido."}
            
        return jsonify({"status": "success", "pesta": pesta_json})
    except Exception as e:
        print(f"Error AI Generate PESTA: {e}")
        return jsonify({"error": str(e)}), 500
"""

if search_marker in text:
    new_text = text.replace(search_marker, search_marker + pesta_code)
    with codecs.open('c:/SIAC/app.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Endpoint added successfully.")
else:
    print("Search marker not found in app.py!")
