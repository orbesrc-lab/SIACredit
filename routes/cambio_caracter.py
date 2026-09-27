import os
import PyPDF2
import docx2txt
import io
from routes.ai import call_ai
import json
import datetime
import uuid
from flask import Blueprint, jsonify, request, render_template
from utils.db import supabase, get_active_inst_id
from utils.auth import require_permission

cambio_caracter_bp = Blueprint('cambio_caracter', __name__)

# Requisitos combinados de Ley 749 y Decreto 2038
import os
import json
req_path = os.path.join(os.path.dirname(__file__), 'requisitos_cc.json')
with open(req_path, 'r', encoding='utf-8') as f:
    REQUISITOS = json.load(f)

def get_cc_project(inst_id):
    table_id = f"CC_PROJ_{inst_id}"
    try:
        res = supabase.table('statistics').select('data_json').eq('table_id', table_id).execute()
        if res.data:
            return json.loads(res.data[0]['data_json'])
    except Exception as e:
        print(f"[CC] Error fetch: {e}")
    
    # Crear proyecto por defecto si no existe
    return {
        "inst_id": inst_id,
        "created_at": datetime.datetime.now().isoformat(),
        "requisitos": {req["id"]: {"status": "Pendiente", "notes": "", "evidences": []} for req in REQUISITOS}
    }

def save_cc_project(inst_id, data):
    table_id = f"CC_PROJ_{inst_id}"
    data_json = json.dumps(data, ensure_ascii=False)
    try:
        check = supabase.table('statistics').select('id').eq('table_id', table_id).execute()
        if check.data:
            supabase.table('statistics').update({'data_json': data_json}).eq('table_id', table_id).execute()
        else:
            supabase.table('statistics').insert({
                'table_id': table_id,
                'inst_id': inst_id,
                'data_json': data_json
            }).execute()
        return True
    except Exception as e:
        print(f"[CC] Error save: {e}")
        return False

@cambio_caracter_bp.route('/cambio_caracter', methods=['GET'])
def render_cambio_caracter():
    inst_id = get_active_inst_id()
    return render_template('cambio_caracter.html', inst_id=inst_id, requisitos=REQUISITOS)

@cambio_caracter_bp.route('/api/cambio_caracter/data', methods=['GET', 'POST'])
def api_cambio_caracter_data():
    inst_id = request.args.get('inst_id', get_active_inst_id(), type=int)
    
    if request.method == 'POST':
        data = request.json
        if save_cc_project(inst_id, data):
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "Error saving data"}), 500
        
    project = get_cc_project(inst_id)
    return jsonify({"status": "success", "data": project})

@cambio_caracter_bp.route('/api/cambio_caracter/upload', methods=['POST'])
def api_cambio_caracter_upload():
    try:
        inst_id = request.form.get('inst_id', get_active_inst_id())
        req_id = request.form.get('req_id')
        file = request.files.get('file')
        
        if not file or not req_id:
            return jsonify({"status": "error", "message": "Falta archivo o req_id"}), 400
            
        ext = os.path.splitext(file.filename)[1].lower()
        new_filename = f"{uuid.uuid4()}{ext}"
        path = f"inst_{inst_id}/cambio_caracter/{req_id}/{new_filename}"
        
        file_bytes = file.read()
        res = supabase.storage.from_('evidencias').upload(path, file_bytes)
        
        public_url = supabase.storage.from_('evidencias').get_public_url(path)
        
        return jsonify({"status": "success", "url": public_url, "name": file.filename, "path": path})
    except Exception as e:
        print(f"[CC] Upload error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@cambio_caracter_bp.route('/api/cambio_caracter/delete_file', methods=['POST'])
def api_cambio_caracter_delete_file():
    try:
        path = request.json.get('path')
        if path:
            supabase.storage.from_('evidencias').remove([path])
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@cambio_caracter_bp.route('/api/cambio_caracter/ai_gap_analysis', methods=['POST'])
def api_cc_ai_gap_analysis():
    try:
        inst_id = request.form.get('inst_id', get_active_inst_id())
        file = request.files.get('file')
        
        if not file:
            return jsonify({"status": "error", "message": "No file uploaded"}), 400
            
        ext = os.path.splitext(file.filename)[1].lower()
        file_bytes = file.read()
        
        # Save document to storage for record-keeping
        new_filename = f"base_doc_{uuid.uuid4()}{ext}"
        path = f"inst_{inst_id}/cambio_caracter/base_documents/{new_filename}"
        supabase.storage.from_('evidencias').upload(path, file_bytes)
        
        text = ""
        if ext == '.pdf':
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        elif ext in ['.docx', '.doc']:
            text = docx2txt.process(io.BytesIO(file_bytes))
        else:
            return jsonify({"status": "error", "message": "Formato no soportado para análisis IA. Sube PDF o Word."}), 400
            
        if not text.strip():
            return jsonify({"status": "error", "message": "No se pudo extraer texto del documento."}), 400
            
        # Limit text length to avoid token limits
        text = text[:40000]
        
        prompt = f"""
Eres un experto del Ministerio de Educación Nacional de Colombia (MEN). 
La institución quiere cambiar su carácter académico a 'Institución Universitaria' según la Ley 749 de 2002 y el Decreto 2038 de 2023.
A continuación te presento el texto extraído de su documento base actual (PEI, Proyecto Institucional o similar).

Tu tarea es analizar este documento e identificar las BRECHAS (lo que falta o no cumple plenamente) frente a los 13 requisitos normativos exigidos para el cambio de carácter.
Genera un 'Checklist de Mejoramiento' que le indique a la institución exactamente qué debe construir o mejorar en cada uno de los 13 requisitos para presentarse con éxito ante el MEN.

Requisitos a evaluar:
1. Misión Institucional.
2. Proyecto Educativo Institucional (PEI).
3. Políticas Académicas (docencia, investigación, extensión).
4. Diseños Curriculares (pertinencia social y académica).
5. Estructura Físico-Académica.
6. Recursos de Apoyo académico.
7. Consolidación Financiera.
8. Organización Administrativa.
9. Autoevaluación permanente.
10. Plan Estratégico (Proyección).
11. Reglamentos Ajustados (Dec. 2038).
12. Interacción con Entorno (Dec. 2038).
13. Plan de Desarrollo (Dec. 2038).

Devuelve tu respuesta estructurada en texto plano con formato Markdown (usando -, *, #). Esto se cargará en un editor de texto para que el usuario pueda ir completando y redactando su documento final. No uses etiquetas HTML.

DOCUMENTO BASE EXTRAÍDO:
{text}
"""
        
        prompt = "Eres un asesor experto del MEN en Colombia, especialista en Cambio de Carácter (Ley 749 de 2002).\n\n" + prompt
        ai_response = call_ai(prompt)
        
        return jsonify({"status": "success", "analysis_html": ai_response, "saved_path": path})
    except Exception as e:
        print(f"[CC AI] Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
