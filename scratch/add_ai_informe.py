import os

route_code = """
@business_bp.route('/api/business/ai_informe_gerencial', methods=['POST'])
def ai_informe_gerencial():
    try:
        data = request.json
        inst_id = data.get('inst_id')
        
        # Load all matrices
        def get_matrix(table_id):
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT data FROM statistics 
                WHERE inst_id = %s AND table_id = %s
                ORDER BY created_at DESC LIMIT 1
            ''', (inst_id, table_id))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row['data'] if row else None
            
        mefi = get_matrix('MEFI')
        mefe = get_matrix('MEFE')
        porter = get_matrix('PORTER')
        riesgos = get_matrix('RIESGOS')
        stakeholders = get_matrix('STAKEHOLDERS')
        
        # Compile prompt context
        context_parts = []
        
        if mefi and 'factors' in mefi:
            context_parts.append("FACTORES INTERNOS (MEFI):\\n" + "\\n".join([f"- {f.get('type')}: {f.get('factor')} (Ponderado: {float(f.get('weight', 0))*float(f.get('rating', 0))})" for f in mefi['factors']]))
            
        if mefe and 'factors' in mefe:
            context_parts.append("FACTORES EXTERNOS (MEFE):\\n" + "\\n".join([f"- {f.get('type')}: {f.get('factor')} (Ponderado: {float(f.get('weight', 0))*float(f.get('rating', 0))})" for f in mefe['factors']]))
            
        if porter and 'analysis' in porter and 'scores' in porter['analysis']:
            context_parts.append("ANALISIS COMPETITIVO (PORTER):\\n" + "\\n".join([f"- {s.get('force')}: Presión {s.get('score')}/10 - {s.get('description')}" for s in porter['analysis']['scores']]))
            
        if riesgos and 'risks' in riesgos:
            context_parts.append("RIESGOS ESTRATEGICOS:\\n" + "\\n".join([f"- {r.get('categoria')}: {r.get('descripcion')} (Impacto {r.get('impacto')}, Probabilidad {r.get('probabilidad')})" for r in riesgos['risks']]))
            
        if stakeholders and 'stakeholders' in stakeholders:
            context_parts.append("STAKEHOLDERS CLAVE:\\n" + "\\n".join([f"- {s.get('nombre')}: Poder {s.get('poder')}, Interés {s.get('interes')} - {s.get('estrategia')}" for s in stakeholders['stakeholders']]))
            
        if not context_parts:
            return jsonify({'status': 'error', 'error': 'No hay datos suficientes de las herramientas para generar el informe.'})
            
        full_context = "\\n\\n".join(context_parts)
        
        prompt = f'''
Actúa como un Consultor Estratégico Senior.
Analiza la siguiente información extraída de múltiples herramientas de diagnóstico de una organización:

{full_context}

Tu objetivo es generar el **Informe Gerencial de Evaluación Organizacional** consolidado.
Debe ser formal, directo y estar estructurado en formato Markdown.

Estructura obligatoria:
# 1. Resumen Ejecutivo Integrado
# 2. Diagnóstico del Entorno Competitivo y Riesgos
# 3. Alineación de Grupos de Interés (Stakeholders)
# 4. Estrategia Global Recomendada (Combinando todos los hallazgos)
'''
        
        # We assume get_gemini_response exists in business.py
        ai_response = get_gemini_response(prompt)
        
        return jsonify({'status': 'success', 'analysis': ai_response})
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500
"""

target = r'c:\SIAC\routes\business.py'
with open(target, 'r', encoding='utf-8') as f:
    content = f.read()

# Append if not exists
if 'def ai_informe_gerencial():' not in content:
    with open(target, 'a', encoding='utf-8') as f:
        f.write('\n' + route_code + '\n')
    print("Added ai_informe_gerencial route.")
else:
    print("Route already exists.")
