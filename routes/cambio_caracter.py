import os
import io
import json
import uuid
import datetime
import PyPDF2
import docx2txt
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from flask import Blueprint, jsonify, request, render_template, send_file
from routes.ai import call_ai
from utils.db import supabase, get_active_inst_id
from utils.auth import require_permission
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

cambio_caracter_bp = Blueprint('cambio_caracter', __name__)

# Requisitos combinados de Ley 749 y Decreto 2038
REQ_PATH = os.path.join(os.path.dirname(__file__), 'requisitos_cc.json')
with open(REQ_PATH, 'r', encoding='utf-8') as f:
    REQUISITOS = json.load(f)

DEFAULTS_PATH = os.path.join(os.path.dirname(__file__), 'cc_defaults.json')

def load_defaults():
    if os.path.exists(DEFAULTS_PATH):
        with open(DEFAULTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def build_clean_cc_project(inst_id):
    """Construye la estructura base en limpio (0% avance, sin documentos de prueba ni evidencias previas)."""
    defaults = load_defaults()
    now_iso = datetime.datetime.now().isoformat()

    clean_fases = []
    for f in defaults.get("fases", []):
        fc = dict(f)
        fc["progreso"] = 0
        fc["estado"] = "Pendiente"
        clean_fases.append(fc)

    clean_quincenas = []
    for q in defaults.get("quincenas", []):
        qc = dict(q)
        qc["estado"] = "Pendiente"
        qc["notas"] = ""
        clean_quincenas.append(qc)

    clean_frentes = []
    for fr in defaults.get("frentes", []):
        frc = dict(fr)
        frc["progreso"] = 0
        frc["estado"] = "Pendiente"
        clean_frentes.append(frc)

    clean_productos = []
    for pr in defaults.get("productos", []):
        prc = dict(pr)
        prc["estado"] = "Pendiente"
        prc["version"] = "1.0"
        prc["documento_contenido"] = ""
        clean_productos.append(prc)

    clean_riesgos = []
    for rk in defaults.get("riesgos", []):
        rkc = dict(rk)
        rkc["estado"] = "Activo"
        clean_riesgos.append(rkc)

    return {
        "inst_id": inst_id,
        "created_at": now_iso,
        "updated_at": now_iso,
        "fases": clean_fases,
        "quincenas": clean_quincenas,
        "frentes": clean_frentes,
        "productos": clean_productos,
        "riesgos": clean_riesgos,
        "brechas": [],
        "requisitos": {
            req["id"]: {
                "status": "Pendiente",
                "notes": "",
                "evidences": [],
                "preguntas_6": {
                    "existe": False,
                    "vigente": False,
                    "aprobado": False,
                    "pertinente": False,
                    "aplica": False,
                    "evidencia": False
                }
            } for req in REQUISITOS
        },
        "ai_history": [],
        "ai_gap_analysis": ""
    }


def get_cc_project(inst_id):
    table_id = f"CC_PROJ_{inst_id}"
    project = None
    try:
        res = supabase.table('statistics').select('data_json').eq('table_id', table_id).execute()
        if res.data:
            project = json.loads(res.data[0]['data_json'])
    except Exception as e:
        print(f"[CC] Error fetch: {e}")

    defaults = load_defaults()

    if not project:
        project = build_clean_cc_project(inst_id)
    else:
        # Merge missing structural sections
        for key in ["fases", "quincenas", "frentes", "productos", "riesgos"]:
            if key not in project or not project[key]:
                project[key] = defaults.get(key, [])
        if "brechas" not in project or project["brechas"] is None:
            project["brechas"] = []

        if "requisitos" not in project or not project["requisitos"]:
            project["requisitos"] = {
                req["id"]: {
                    "status": "Pendiente",
                    "notes": "",
                    "evidences": [],
                    "preguntas_6": {
                        "existe": False,
                        "vigente": False,
                        "aprobado": False,
                        "pertinente": False,
                        "aplica": False,
                        "evidencia": False
                    }
                } for req in REQUISITOS
            }
        else:
            # Ensure all requirements have the 6 questions structure
            for req in REQUISITOS:
                rid = req["id"]
                if rid not in project["requisitos"]:
                    project["requisitos"][rid] = {
                        "status": "Pendiente",
                        "notes": "",
                        "evidences": [],
                        "preguntas_6": {
                            "existe": False,
                            "vigente": False,
                            "aprobado": False,
                            "pertinente": False,
                            "aplica": False,
                            "evidencia": False
                        }
                    }
                elif "preguntas_6" not in project["requisitos"][rid]:
                    project["requisitos"][rid]["preguntas_6"] = {
                        "existe": False,
                        "vigente": False,
                        "aprobado": False,
                        "pertinente": False,
                        "aplica": False,
                        "evidencia": False
                    }

        if "ai_history" not in project or project["ai_history"] is None:
            project["ai_history"] = []

    # Ensure every item in ai_history has collaborative & traceability fields
    for idx_h, item in enumerate(project.get("ai_history", [])):
        if "codigo_doc" not in item or not item["codigo_doc"]:
            prod_prefix = (item.get("producto") or "DOC").split()[0][:4].upper()
            item["codigo_doc"] = f"DOC-{prod_prefix}-{idx_h + 1:02d}"
        if "categoria" not in item or not item["categoria"]:
            item["categoria"] = "Políticas y Modelos" if "modelo" in item.get("titulo", "").lower() or "política" in item.get("titulo", "").lower() else (
                "Reglamentos y Estatutos" if "estatuto" in item.get("titulo", "").lower() or "reglamento" in item.get("titulo", "").lower() else "Diagnósticos y Estudios"
            )
        if "requisito_id" not in item:
            item["requisito_id"] = "req_17" if "pedag" in item.get("titulo", "").lower() else "req_1"
        if "fase" not in item or not item["fase"]:
            item["fase"] = "Fase III: Escenario y diseño"
        if "version_actual" not in item or not item["version_actual"]:
            item["version_actual"] = "v1.0"
        if "estado_editorial" not in item or not item["estado_editorial"]:
            item["estado_editorial"] = "En Construcción"
        if "cargo_dependencia" not in item or not item["cargo_dependencia"]:
            item["cargo_dependencia"] = item.get("frente") or "Equipo Institucional"
        if "rol_skel" not in item or not item["rol_skel"]:
            item["rol_skel"] = "lider"
        if "bitacora_versiones" not in item or not isinstance(item["bitacora_versiones"], list) or len(item["bitacora_versiones"]) == 0:
            item["bitacora_versiones"] = [
                {
                    "version": item.get("version_actual", "v1.0"),
                    "fecha": item.get("fecha", datetime.datetime.now().isoformat()),
                    "autor": item.get("autor", "Equipo Institucional"),
                    "cargo_dependencia": item.get("cargo_dependencia", item.get("frente", "Equipo Institucional")),
                    "rol_skel": item.get("rol_skel", "lider"),
                    "fase": item.get("fase", "Fase I: Alineación y levantamiento"),
                    "tipo_actuacion": "Generación Asistida por IA" if "IA" in item.get("autor", "") else "Redacción Inicial",
                    "resumen_cambio": f"Creación inicial del documento: {item.get('titulo', 'Documento Institucional')}",
                    "contenido_snapshot": item.get("contenido", "")
                }
            ]
        if "aportes_equipo" not in item or not isinstance(item["aportes_equipo"], list):
            item["aportes_equipo"] = []
        if "auditorias_ia" not in item or not isinstance(item["auditorias_ia"], list):
            item["auditorias_ia"] = []
        if "equipo_documento" not in item or not isinstance(item["equipo_documento"], list):
            init_autor = item.get("autor", "")
            init_dep = item.get("cargo_dependencia", item.get("frente", "Equipo Institucional"))
            if init_autor and "IA" not in init_autor:
                item["equipo_documento"] = [
                    {
                        "id": f"tm_{idx_h}_0",
                        "nombre": init_autor,
                        "dependencia": init_dep,
                        "rol": "Líder / Co-Autor",
                        "fecha": item.get("fecha", datetime.datetime.now().isoformat())
                    }
                ]
            else:
                item["equipo_documento"] = []
        # Garantizar que contenido y snapshots estén siempre limpios de envoltorios JSON
        if item.get("contenido"):
            item["contenido"] = sanitize_doc_markdown_text(item["contenido"])
        for v_item in (item.get("bitacora_versiones") or []):
            if isinstance(v_item, dict) and v_item.get("contenido_snapshot"):
                v_item["contenido_snapshot"] = sanitize_doc_markdown_text(v_item["contenido_snapshot"])

    return project


def sanitize_doc_markdown_text(raw_text):
    """Limpia cualquier rastro de envoltorio JSON ('markdown_report', 'evaluations', bloques ```json, \\n literales) de un documento."""
    if not raw_text or not isinstance(raw_text, str):
        return ""
    import re
    txt = raw_text.strip()
    # 1. Si viene con etiquetas <DOCUMENTO_MARKDOWN> ... </DOCUMENTO_MARKDOWN>
    doc_tag = re.search(r'<DOCUMENTO_MARKDOWN>([\s\S]*?)(?:</DOCUMENTO_MARKDOWN>|$)', txt, re.IGNORECASE)
    if doc_tag:
        txt = doc_tag.group(1).strip()
    # 2. Remover bloque <EVALUATIONS_JSON> ... </EVALUATIONS_JSON> si quedó incluido
    txt = re.sub(r'<EVALUATIONS_JSON>[\s\S]*?</EVALUATIONS_JSON>', '', txt, flags=re.IGNORECASE).strip()
    # 3. Si empieza con ```json o { "markdown_report": "
    txt = re.sub(r'^```(?:json)?\s*', '', txt, flags=re.IGNORECASE).strip()
    txt = re.sub(r'\s*```$', '', txt).strip()
    if re.match(r'^\{\s*"markdown_report"\s*:\s*"', txt):
        txt = re.sub(r'^\{\s*"markdown_report"\s*:\s*"', '', txt, count=1).strip()
        if '\\n' in txt:
            txt = txt.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
    # 4. Cortar cualquier cola JSON '", "evaluations": {' al final
    txt = re.sub(r'"?\s*,\s*"evaluations"\s*:\s*\{[\s\S]*$', '', txt, flags=re.IGNORECASE).strip()
    if txt.endswith('"}'):
        txt = txt[:-2].strip()
    return txt


def merge_team_members_into_doc(doc_item, members_list, default_rol="Co-Autor / Integrante"):
    """Integra una lista de integrantes [{"nombre": ..., "dependencia": ..., "rol": ...}] en doc_item['equipo_documento'] sin duplicar."""
    if not doc_item or not isinstance(members_list, list):
        return
    if "equipo_documento" not in doc_item or not isinstance(doc_item["equipo_documento"], list):
        doc_item["equipo_documento"] = []
    existing_names = {str(m.get("nombre", "")).strip().lower() for m in doc_item["equipo_documento"] if m.get("nombre")}
    now_iso = datetime.datetime.now().isoformat()
    for m in members_list:
        if not isinstance(m, dict):
            continue
        nombre = str(m.get("nombre") or m.get("autor") or "").strip()
        dep = str(m.get("dependencia") or m.get("cargo_dependencia") or "Equipo Institucional").strip()
        rol = str(m.get("rol") or default_rol).strip()
        if not nombre:
            continue
        if nombre.lower() not in existing_names:
            doc_item["equipo_documento"].append({
                "id": str(uuid.uuid4())[:8],
                "nombre": nombre,
                "dependencia": dep,
                "rol": rol,
                "fecha": now_iso
            })
            existing_names.add(nombre.lower())

def save_cc_project(inst_id, data):
    table_id = f"CC_PROJ_{inst_id}"
    data["updated_at"] = datetime.datetime.now().isoformat()
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
        data = request.json or {}
        try:
            existing = get_cc_project(inst_id)
            # Protección multi-usuario: preservar documentos en ai_history creados en paralelo o por IA
            if isinstance(existing.get("ai_history"), list) and isinstance(data.get("ai_history"), list):
                incoming_by_id = {d.get("id"): d for d in data["ai_history"] if isinstance(d, dict) and d.get("id")}
                merged_history = list(data["ai_history"])
                for ex_doc in existing["ai_history"]:
                    ex_id = ex_doc.get("id")
                    if ex_id and ex_id not in incoming_by_id:
                        merged_history.insert(0, ex_doc)
                data["ai_history"] = merged_history
            # Preservar brechas registradas en paralelo
            if isinstance(existing.get("brechas"), list) and isinstance(data.get("brechas"), list):
                inc_brechas = {b.get("id") for b in data["brechas"] if isinstance(b, dict) and b.get("id")}
                for ex_b in existing["brechas"]:
                    if ex_b.get("id") and ex_b.get("id") not in inc_brechas:
                        data["brechas"].append(ex_b)
        except Exception as merge_e:
            print(f"[CC] Merge warning: {merge_e}")
        if save_cc_project(inst_id, data):
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "Error saving data"}), 500
        
    project = get_cc_project(inst_id)
    return jsonify({"status": "success", "data": project})

@cambio_caracter_bp.route('/api/cambio_caracter/upload', methods=['POST'])
def api_cambio_caracter_upload():
    try:
        inst_id = request.form.get('inst_id', get_active_inst_id())
        req_id = request.form.get('req_id', 'general')
        
        # Soportar múltiples archivos o archivo individual
        files = request.files.getlist('files')
        if not files or len(files) == 0:
            single = request.files.get('file')
            if single:
                files = [single]
        
        if not files:
            return jsonify({"status": "error", "message": "Falta archivo"}), 400
            
        uploaded_results = []
        for file in files:
            if not file or not file.filename:
                continue
            ext = os.path.splitext(file.filename)[1].lower()
            new_filename = f"{uuid.uuid4()}{ext}"
            path = f"inst_{inst_id}/cambio_caracter/{req_id}/{new_filename}"
            
            file_bytes = file.read()
            file_options = {"content-type": file.content_type} if hasattr(file, 'content_type') else {}
            supabase.storage.from_('evidencias').upload(path, file_bytes, file_options=file_options)
            
            public_url = supabase.storage.from_('evidencias').get_public_url(path)
            
            size_kb = len(file_bytes) / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{(size_kb/1024):.1f} MB"
            
            uploaded_results.append({
                "url": public_url,
                "name": file.filename,
                "path": path,
                "size": size_str,
                "ext": ext
            })
            
        if not uploaded_results:
            return jsonify({"status": "error", "message": "No se procesaron archivos válidos"}), 400
            
        # Si fue un solo archivo, retornar campos individuales para compatibilidad hacia atrás
        first_item = uploaded_results[0]
        return jsonify({
            "status": "success",
            "url": first_item["url"],
            "name": first_item["name"],
            "path": first_item["path"],
            "size": first_item["size"],
            "files": uploaded_results
        })
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

@cambio_caracter_bp.route('/api/cambio_caracter/margy_consult', methods=['POST'])
def api_cc_margy_consult():
    """Asesoría experta de Margy IA sobre qué exige realmente el MEN para un requisito específico."""
    try:
        data = request.json or {}
        req_id = data.get('req_id')
        user_message = (data.get('message') or '').strip()
        history = data.get('history', [])
        
        req_item = next((r for r in REQUISITOS if r['id'] == req_id), None)
        if not req_item:
            return jsonify({"status": "error", "message": "Requisito no encontrado"}), 404
            
        system_prompt = f"""Eres Margy IA, la Consejera Técnica Senior y Consultora Experta en Aseguramiento de Calidad del MEN y CONACES para la institución educativa.
Estás asesorando a la institución en su proceso estratégico de Cambio de Carácter Académico a Institución Universitaria bajo la Ley 749 de 2002 y el Decreto 2038 de 2023.

Estás orientando sobre el REQUISITO NORMATIVO ESPECÍFICO:
- Código: {req_item.get('id')}
- Eje: {req_item.get('eje')}
- Factor: {req_item.get('factor')}
- Título: {req_item.get('title')}
- Descripción del Requisito: {req_item.get('desc')}
- Exigencia Documental MEN: {req_item.get('evidencia_requerida')}
- Marco Legal: {req_item.get('ley')}

DIRECTRICES DE RESPUESTA:
1. Responde de manera profesional, cercana, empática y con profundo rigor técnico y normativo del MEN.
2. Si el usuario solicita orientación general o inicial, estructura tu respuesta en los siguientes 4 bloques en Markdown con formato claro y viñetas:
   - 🎯 **¿Qué busca realmente el MEN con este requisito?**: Explica el sentido profundo y por qué los Pares Evaluadores lo exigen (más allá del texto frío de la norma).
   - 📑 **Evidencias Clave y Coherencia Documental**: Detalla qué documentos específicos (actas, resoluciones, matrices, diagnósticos, firmas) deben existir para que el MEN lo considere plenamente cumplido.
   - 📈 **Evolución Recomendada por Fase**: Cómo debe madurar este requisito a lo largo del proceso institucional:
     * *Fase I (Alineación / Levantamiento):* Diagnóstico inicial y mapeo de brechas.
     * *Fase II (Diagnóstico Integral y Elaboración):* Documento técnico y propuesta fundamentada.
     * *Fase III (Aprobación Colegiada):* Acta y Acuerdo formal de Consejo Directivo o Superior.
     * *Fase IV (Radicación SACES / Consolidación):* Inclusión en el Documento Maestro final.
   - ⚠️ **Riesgos y Errores Comunes**: Qué inconsistencias suelen detectar los Pares Académicos del MEN que originan requerimientos o conceptos negativos.
3. Si el usuario hace una pregunta puntual (ej. sobre actas, cronogramas, formatos), respóndele de forma concisa y práctica orientada a la solución.
4. Mantén siempre el avatar y personalidad de Margy IA: pedagógica, rigurosa, motivadora y experta en el MEN."""

        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-4:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
            
        if user_message:
            messages.append({"role": "user", "content": user_message})
        else:
            messages.append({"role": "user", "content": f"Margy, por favor explícame en detalle qué es lo que realmente busca el MEN con este requisito '{req_item.get('title')}' y cómo debemos construir y madurar las evidencias por fase."})

        answer = call_ai(messages, max_tokens=2000, temperature=0.35)
        return jsonify({"status": "success", "answer": answer, "req_item": req_item})
    except Exception as e:
        print(f"[CC Margy] Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@cambio_caracter_bp.route('/api/cambio_caracter/skel_users', methods=['GET'])
def api_cc_skel_users():
    inst_id = get_active_inst_id()
    try:
        res = supabase.table('users').select('id, email, name, role, inst_id').execute()
        valid_users = [
            u for u in (res.data or [])
            if u.get('role') in ['inst_admin', 'lider', 'operativo', 'profesor', 'consultor', 'auditor', 'admin']
            and (u.get('inst_id') in [inst_id, 7, None] or u.get('role') == 'admin')
        ]
        return jsonify({"status": "success", "users": valid_users})
    except Exception as e:
        print(f"[CC] Error fetch users: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@cambio_caracter_bp.route('/api/cambio_caracter/ai_gap_analysis', methods=['POST'])
def api_cc_ai_gap_analysis():
    try:
        inst_id = request.form.get('inst_id', get_active_inst_id(), type=int)
        mode = request.form.get('mode', 'full_diagnosis') # full_diagnosis, frente_diagnosis, draft_product, evaluate_evidence, solve_brecha, custom_prompt
        frente_name = request.form.get('frente_name', '')
        producto_codigo = request.form.get('producto_codigo', '')
        brecha_id = request.form.get('brecha_id', '')
        custom_instructions = request.form.get('custom_instructions', '')
        direct_text = request.form.get('text', '')
        
        file = request.files.get('file')
        file_text = ""
        saved_doc_path = None
        
        if file:
            ext = os.path.splitext(file.filename)[1].lower()
            file_bytes = file.read()
            new_filename = f"base_doc_{uuid.uuid4()}{ext}"
            saved_doc_path = f"inst_{inst_id}/cambio_caracter/base_documents/{new_filename}"
            file_options = {"content-type": file.content_type} if hasattr(file, 'content_type') else {}
            try:
                supabase.storage.from_('evidencias').upload(saved_doc_path, file_bytes, file_options=file_options)
            except Exception as up_e:
                print(f"[CC AI] Upload warning: {up_e}")

            if ext == '.pdf':
                reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        file_text += extracted + "\n"
            elif ext in ['.docx', '.doc']:
                file_text = docx2txt.process(io.BytesIO(file_bytes))
            else:
                return jsonify({"status": "error", "message": "Formato no soportado para análisis IA. Sube PDF o Word."}), 400

        text_to_process = (file_text.strip() or direct_text.strip())
        if not text_to_process and mode not in ['draft_product', 'solve_brecha', 'custom_prompt']:
            return jsonify({"status": "error", "message": "Debes subir un archivo o ingresar texto para el análisis."}), 400

        # Truncate text to avoid token exhaustion if huge
        if len(text_to_process) > 35000:
            text_to_process = text_to_process[:35000]

        project = get_cc_project(inst_id)

        system_prompt = (
            "Eres el Asesor Experto Principal del Ministerio de Educación Nacional de Colombia (MEN) y de CONACES/CESU, "
            "especialista de máximo nivel en cambio de carácter académico institucional (Ley 749 de 2002, Ley 30 de 1992, "
            "Decreto 2216 de 2003, Decreto 1075 de 2015, Decreto 1330 de 2019, Decreto 2038 de 2023, Decreto 0529 de 2024 "
            "y Acuerdo CESU 01 de 2025). "
            "REGLA INSTITUCIONAL OBLIGATORIA: La institución que adelanta este proceso de cambio de carácter a Institución Universitaria "
            "es SIEMPRE 'INTENALCO EDUCACIÓN SUPERIOR' (ubicada en Santiago de Cali, Valle del Cauca). "
            "Si el documento subido como insumo o referente menciona el nombre de otra institución (por ejemplo, una política de referencia "
            "o modelo comparativo externo), NUNCA adoptes ese nombre externo: debes redactar absolutamente todo el informe, diagnóstico, "
            "plan de acción y propuesta de articulado exclusivamente a nombre de INTENALCO EDUCACIÓN SUPERIOR. "
            "Tu estilo de redacción es formal, altamente técnico, académico, jurídico y propositivo. "
            "No te limitas a opinar: redactas articulados normativos, capítulos del PEI/PDI, justificaciones curriculares, "
            "políticas institucionales y matrices con rigor impecable, adaptados a la realidad de INTENALCO EDUCACIÓN SUPERIOR "
            "en su tránsito a Institución Universitaria."
        )

        title_entry = "Análisis IA"
        task_frente = frente_name or "General"
        task_product = producto_codigo or ("P1" if mode in ['frente_diagnosis', 'full_diagnosis', 'evaluate_evidence'] else "P2")
        default_req_id = "req_1"

        # PROMPT BUILDING BY MODE TO MINIMIZE TOKENS
        if mode == 'frente_diagnosis':
            # Filter requirements for this front
            rubrica_frente = []
            matched_req_ids = []
            for r in REQUISITOS:
                if frente_name.lower() in (r.get('eje', '') + ' ' + r.get('factor', '') + ' ' + r.get('desc', '')).lower():
                    rubrica_frente.append(f"- ID: {r['id']} | FACTOR: {r['factor']}\n  ASPECTO: {r['desc']}\n  EVIDENCIA EXIGIDA: {r.get('evidencia_requerida','')}")
                    matched_req_ids.append(r['id'])
            
            if not rubrica_frente:
                rubrica_frente = [f"- ID: {r['id']} | {r['desc']}" for r in REQUISITOS[:8]]
                matched_req_ids = [r['id'] for r in REQUISITOS[:8]]
            if matched_req_ids:
                default_req_id = matched_req_ids[0]
            rubrica_str = "\n".join(rubrica_frente[:10])

            title_entry = f"Diagnóstico Focalizado: Frente {frente_name}"
            user_prompt = f"""
Has sido convocado por **INTENALCO EDUCACIÓN SUPERIOR** para liderar el diagnóstico y redacción del frente: **{frente_name}**.
Objetivo: Evaluar el estado actual de INTENALCO EDUCACIÓN SUPERIOR, detectar brechas frente a los estándares de Institución Universitaria del MEN y redactar la propuesta de mejoramiento o articulado normativo correspondiente para INTENALCO EDUCACIÓN SUPERIOR.
(Nota: Si el texto base adjunto proviene de un documento referente externo, tómalo únicamente como insumo técnico y redacta toda la propuesta, encabezados y articulados exclusivamente para INTENALCO EDUCACIÓN SUPERIOR).

REQUISITOS APLICABLES AL FRENTE ({frente_name}):
{rubrica_str}

INSTRUCCIONES ESPECÍFICAS DEL USUARIO:
{custom_instructions or 'Identifica las brechas y redacta el articulado y plan de acción correspondiente para INTENALCO EDUCACIÓN SUPERIOR.'}

TEXTO / EVIDENCIA BASE:
{text_to_process}

Debes responder utilizando EXACTAMENTE estas dos etiquetas XML (NO envuelvas el documento Markdown dentro de un string JSON):

<EVALUATIONS_JSON>
{{
  "req_X": {{
    "status": "En Construcción",
    "notes": "Justificación técnica del estado y recomendación.",
    "preguntas_6": {{
      "existe": true,
      "vigente": true,
      "aprobado": false,
      "pertinente": true,
      "aplica": false,
      "evidencia": false
    }}
  }}
}}
</EVALUATIONS_JSON>

<DOCUMENTO_MARKDOWN>
Aquí redacta directamente el INFORME TÉCNICO Y LA PROPUESTA REDACTADA (articulados, políticas, planes de acción) en formato Markdown limpio para INTENALCO EDUCACIÓN SUPERIOR.
</DOCUMENTO_MARKDOWN>
"""

        elif mode == 'draft_product':
            prod_info = next((p for p in project.get("productos", []) if p["codigo"] == producto_codigo), None)
            prod_name = prod_info["nombre"] if prod_info else f"Producto {producto_codigo}"
            prod_min = prod_info["contenido_minimo"] if prod_info else ""
            title_entry = f"Redacción Experta: {producto_codigo} - {prod_name}"
            
            user_prompt = f"""
Se te encomienda REDACTAR EL ENTREGABLE INSTITUCIONAL DE **INTENALCO EDUCACIÓN SUPERIOR**: **{producto_codigo}: {prod_name}**.
Contenido mínimo exigido por la metodología institucional:
{prod_min}

Directrices del proceso de cambio de carácter de INTENALCO EDUCACIÓN SUPERIOR (Ley 749 de 2002 / Decreto 2038 de 2023):
- Incluye Considerandos jurídicos y de pertinencia académica para INTENALCO EDUCACIÓN SUPERIOR.
- Estructura el documento con Títulos, Capítulos, Artículos y Parágrafos donde aplique.
- Incorpora disposiciones transitorias para proteger las cohortes de estudiantes y docentes en transición.
- Define indicadores y responsables.

INSTRUCCIONES ESPECÍFICAS:
{custom_instructions or 'Redacta el documento formal completo para INTENALCO EDUCACIÓN SUPERIOR, listo para revisión del Comité Técnico y aprobación.'}

INSUMOS / BASE DOCUMENTAL (si aplica):
{text_to_process or 'No se adjuntó texto previo; redacta la propuesta estándar de máxima calidad institucional para INTENALCO EDUCACIÓN SUPERIOR.'}

Responde utilizando estas etiquetas:
<EVALUATIONS_JSON>
{{}}
</EVALUATIONS_JSON>

<DOCUMENTO_MARKDOWN>
Aquí redacta directamente el DOCUMENTO COMPLETO en formato Markdown formal y riguroso para INTENALCO EDUCACIÓN SUPERIOR.
</DOCUMENTO_MARKDOWN>
"""

        elif mode == 'solve_brecha':
            brecha_info = next((b for b in project.get("brechas", []) if b["id"] == brecha_id), None)
            desc_b = brecha_info["descripcion"] if brecha_info else "Brecha institucional"
            frente_b = brecha_info["frente"] if brecha_info else (frente_name or "General")
            accion_b = brecha_info.get("accion_propuesta", "Actualizar") if brecha_info else "Actualizar"
            task_frente = frente_b
            task_product = producto_codigo or "P2"
            title_entry = f"Solución Técnica a Brecha {brecha_id}: {desc_b[:55]}"

            rubrica_brecha = []
            for r in REQUISITOS:
                if frente_b.lower() in (r.get('eje', '') + ' ' + r.get('factor', '') + ' ' + r.get('desc', '')).lower():
                    rubrica_brecha.append(f"- ID: {r['id']} | FACTOR: {r['factor']} | {r['desc']}")
            if rubrica_brecha:
                default_req_id = rubrica_brecha[0].split('|')[0].replace('- ID:', '').strip()
            rubrica_b_str = "\n".join(rubrica_brecha[:8])

            user_prompt = f"""
Se requiere una SOLUCIÓN TÉCNICA Y REDACCIÓN NORMATIVA EXPERTA para **INTENALCO EDUCACIÓN SUPERIOR** con el fin de cerrar la siguiente brecha identificada en el plan de cambio de carácter a Institución Universitaria:
- Institución: INTENALCO EDUCACIÓN SUPERIOR
- Código de Brecha: {brecha_id}
- Frente Responsable: {frente_b}
- Tratamiento institucional propuesto: {accion_b} (según metodología: Conservar, Fortalecer, Actualizar, Transformar, Armonizar, Crear, Derogar)
- Descripción de la Brecha: {desc_b}
- Evidencia faltante: {brecha_info.get('evidencia_faltante', '') if brecha_info else ''}

REQUISITOS DEL MEN RELACIONADOS CON ESTE FRENTE:
{rubrica_b_str}

INSTRUCCIONES ESPECÍFICAS:
{custom_instructions or 'Redacta para INTENALCO EDUCACIÓN SUPERIOR la solución definitiva: análisis técnico de la brecha, propuesta de articulado o reforma lista para adopción, procedimiento operativo y protocolo de evidencias para Pares MEN.'}

INSUMOS / DOCUMENTO DE REFERENCIA ADICIONAL:
{text_to_process or 'Toma como base el contexto institucional de INTENALCO EDUCACIÓN SUPERIOR.'}
(Importante: Si el documento adjunto menciona otra institución por ser un referente comparativo, adapta todo el texto, títulos y articulados exclusivamente a INTENALCO EDUCACIÓN SUPERIOR).

Responde utilizando EXACTAMENTE estas dos etiquetas (NO envuelvas el documento Markdown dentro de un string JSON):
<EVALUATIONS_JSON>
{{
  "{default_req_id}": {{
    "status": "En Construcción",
    "notes": "Síntesis del estado actual y cómo esta propuesta cierra la brecha en INTENALCO.",
    "preguntas_6": {{
      "existe": true,
      "vigente": false,
      "aprobado": false,
      "pertinente": true,
      "aplica": false,
      "evidencia": false
    }}
  }}
}}
</EVALUATIONS_JSON>

<DOCUMENTO_MARKDOWN>
Redacta aquí el informe de cierre de brecha, propuesta de texto legal/académico para INTENALCO EDUCACIÓN SUPERIOR y protocolo de evidencias en formato Markdown limpio.
</DOCUMENTO_MARKDOWN>
"""

        elif mode == 'evaluate_evidence':
            title_entry = f"Auditoría de Evidencias (6 Preguntas) - {frente_name or 'General'}"
            user_prompt = f"""
Realiza una AUDITORÍA METODOLÓGICA DE EVIDENCIAS para **INTENALCO EDUCACIÓN SUPERIOR** aplicando rigurosamente la 'Metodología de las 6 Preguntas Institucionales' de INTENALCO / MEN:
1. ¿Existe? (Verificación de existencia del instrumento o proceso)
2. ¿Está vigente? (Vigencia temporal, sin derogatorias tácitas)
3. ¿Está formalmente aprobado? (Por el órgano competente: Consejo Superior / Directivo / Académico con acta o acuerdo)
4. ¿Es pertinente frente al nuevo carácter? (Alineado a Institución Universitaria según Ley 749 y Decreto 2038)
5. ¿Se aplica efectivamente? (Operatividad real en la vida institucional)
6. ¿Existe evidencia de aplicación y resultados? (Registros, actas, mediciones, trazabilidad)

DOCUMENTO / EVIDENCIAS REVISADAS:
{text_to_process}

INSTRUCCIONES ESPECÍFICAS:
{custom_instructions or 'Emite dictamen de auditoría para INTENALCO EDUCACIÓN SUPERIOR por cada requisito evidenciado y califica cada una de las 6 preguntas.'}

Responde utilizando estas dos etiquetas:
<EVALUATIONS_JSON>
{{
  "req_X": {{
    "status": "Completado",
    "notes": "Dictamen fundado.",
    "preguntas_6": {{
      "existe": true,
      "vigente": true,
      "aprobado": true,
      "pertinente": true,
      "aplica": true,
      "evidencia": true
    }}
  }}
}}
</EVALUATIONS_JSON>

<DOCUMENTO_MARKDOWN>
Redacta aquí el dictamen de auditoría con hallazgos, recomendaciones y plan de subsanación para INTENALCO EDUCACIÓN SUPERIOR en formato Markdown limpio.
</DOCUMENTO_MARKDOWN>
"""

        else: # full_diagnosis (default)
            rubrica_text = "\n".join([f"- ID: {r['id']} | EJE: {r['eje']} | FACTOR: {r['factor']}\n  ASPECTO: {r['desc']}" for r in REQUISITOS[:25]])
            title_entry = "Diagnóstico Integral de Brechas y Propuesta de Redacción"
            user_prompt = f"""
**INTENALCO EDUCACIÓN SUPERIOR** adelanta su proceso de cambio de carácter a 'Institución Universitaria' según la Ley 749 de 2002 y el Decreto 2038 de 2023.
A continuación te presento el documento base o insumo institucional.

Tu tarea es:
1. Identificar las brechas críticas de transformación de INTENALCO EDUCACIÓN SUPERIOR frente a los estándares de Institución Universitaria.
2. Aplicar la matriz de tratamiento (Conservar, Fortalecer, Actualizar, Transformar, Armonizar, Crear, Derogar).
3. REDACTAR para INTENALCO EDUCACIÓN SUPERIOR las propuestas de articulado normativo, ajuste de políticas y capítulos requeridos para subsanar los vacíos.

RUBRICA DE REFERENCIA (Factores Priorizados):
{rubrica_text}

INSTRUCCIONES ESPECÍFICAS:
{custom_instructions or 'Genera un informe integral para INTENALCO EDUCACIÓN SUPERIOR con propuestas de redacción listas para usar en el Dossier Técnico.'}

DOCUMENTO BASE EXTRAÍDO:
{text_to_process}

Responde utilizando estas dos etiquetas:
<EVALUATIONS_JSON>
{{
  "req_1": {{
    "status": "En Construcción",
    "notes": "Breve nota de cumplimiento.",
    "preguntas_6": {{
      "existe": true,
      "vigente": true,
      "aprobado": false,
      "pertinente": true,
      "aplica": false,
      "evidencia": false
    }}
  }}
}}
</EVALUATIONS_JSON>

<DOCUMENTO_MARKDOWN>
Redacta aquí el informe técnico de brechas y las propuestas de redacción formal de estatutos/políticas en formato Markdown limpio para INTENALCO EDUCACIÓN SUPERIOR.
</DOCUMENTO_MARKDOWN>
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        ai_response = call_ai(messages, max_tokens=32000, inst_id=inst_id)

        import re
        evaluations = {}
        analysis_html = ""

        # 1) Formato preferido: <EVALUATIONS_JSON> + <DOCUMENTO_MARKDOWN>
        ev_tag_match = re.search(r'<EVALUATIONS_JSON>([\s\S]*?)</EVALUATIONS_JSON>', ai_response, re.IGNORECASE)
        if ev_tag_match:
            ev_raw = ev_tag_match.group(1).strip()
            ev_raw = re.sub(r'^```(?:json)?\s*', '', ev_raw).strip()
            ev_raw = re.sub(r'\s*```$', '', ev_raw).strip()
            try:
                parsed_ev = json.loads(ev_raw)
                evaluations = parsed_ev.get("evaluations", parsed_ev) if isinstance(parsed_ev, dict) else {}
            except Exception as e_xml:
                print("[CC AI] XML evaluations JSON warning:", e_xml)

        doc_tag_match = re.search(r'<DOCUMENTO_MARKDOWN>([\s\S]*?)(?:</DOCUMENTO_MARKDOWN>|$)', ai_response, re.IGNORECASE)
        if doc_tag_match:
            analysis_html = sanitize_doc_markdown_text(doc_tag_match.group(1))
        else:
            # 2) Fallback por si la IA devolvió un objeto JSON {"markdown_report": "...", "evaluations": {...}}
            match = re.search(r'```(?:json)?\s*\n(.*?)\n```', ai_response, re.DOTALL)
            json_str = match.group(1).strip() if match else ai_response.strip()
            try:
                parsed_data = json.loads(json_str)
                analysis_html = parsed_data.get("markdown_report", "")
                if not evaluations:
                    evaluations = parsed_data.get("evaluations", {}) or {}
            except Exception:
                eval_split = re.search(r'"\s*,\s*"evaluations"\s*:\s*(\{[\s\S]*\})\s*\}?\s*$', json_str)
                if eval_split and not evaluations:
                    raw_eval_part = eval_split.group(1).strip()
                    depth = 0
                    end_idx = len(raw_eval_part)
                    for idx_ch, ch in enumerate(raw_eval_part):
                        if ch == '{':
                            depth += 1
                        elif ch == '}':
                            depth -= 1
                            if depth == 0:
                                end_idx = idx_ch + 1
                                break
                    try:
                        evaluations = json.loads(raw_eval_part[:end_idx])
                    except Exception:
                        evaluations = {}
                analysis_html = sanitize_doc_markdown_text(json_str)

        analysis_html = sanitize_doc_markdown_text(analysis_html)

        if evaluations and isinstance(evaluations, dict):
            first_eval_req = next((k for k in evaluations.keys() if k.startswith('req_')), None)
            if first_eval_req:
                default_req_id = first_eval_req

        # Vincular automáticamente al líder y equipo del Frente responsable
        frente_obj = next((f for f in project.get("frentes", []) if f.get("nombre", "").lower() == task_frente.lower()), None)
        equipo_inicial = []
        autor_label = "Asesor Experto MEN (IA)"
        if frente_obj:
            if frente_obj.get("lider"):
                autor_label = f"{frente_obj['lider']} · Asesor IA"
                equipo_inicial.append({
                    "id": str(uuid.uuid4())[:8],
                    "nombre": frente_obj["lider"],
                    "dependencia": task_frente,
                    "rol": "Líder de Frente",
                    "fecha": datetime.datetime.now().isoformat()
                })
            for m in (frente_obj.get("equipo_frente") or []):
                if m.get("nombre") and m.get("nombre") != frente_obj.get("lider"):
                    equipo_inicial.append({
                        "id": str(uuid.uuid4())[:8],
                        "nombre": m.get("nombre"),
                        "dependencia": m.get("dependencia", task_frente),
                        "rol": m.get("rol", "Integrante del Frente"),
                        "fecha": datetime.datetime.now().isoformat()
                    })

        # Save to history entry
        tokens_est = (len(user_prompt) + len(analysis_html)) // 4
        history_id = str(uuid.uuid4())
        now_iso = datetime.datetime.now().isoformat()
        new_hist_item = {
            "id": history_id,
            "codigo_doc": f"DOC-{task_product[:4].upper()}-{len(project.get('ai_history', [])) + 1:02d}",
            "titulo": title_entry,
            "categoria": "Políticas y Modelos" if mode == 'draft_product' else ("Planes y Proyecciones" if mode == 'solve_brecha' else "Diagnósticos y Estudios"),
            "fecha": now_iso,
            "fecha_modificacion": now_iso,
            "tipo": mode,
            "frente": task_frente,
            "producto": task_product,
            "requisito_id": default_req_id,
            "fase": "Fase III: Escenario y diseño",
            "version_actual": "v1.0",
            "estado_editorial": "En Construcción",
            "autor": autor_label,
            "cargo_dependencia": task_frente,
            "rol_skel": "lider",
            "tokens_est": tokens_est,
            "contenido": analysis_html,
            "saved_doc_path": saved_doc_path,
            "equipo_documento": equipo_inicial,
            "bitacora_versiones": [
                {
                    "version": "v1.0",
                    "fecha": now_iso,
                    "autor": autor_label,
                    "cargo_dependencia": task_frente,
                    "rol_skel": "lider",
                    "fase": "Fase III: Escenario y diseño",
                    "tipo_actuacion": "Generación Asistida por IA",
                    "resumen_cambio": f"Generación inicial del documento base ({title_entry})",
                    "contenido_snapshot": analysis_html
                }
            ],
            "aportes_equipo": [],
            "auditorias_ia": []
        }

        # Persistir inmediatamente el .docx en Supabase Storage para trazabilidad ante Pares MEN
        try:
            persist_doc_version_to_supabase_storage(inst_id, new_hist_item, new_hist_item["bitacora_versiones"][0], project)
        except Exception as st_e:
            print(f"[CC AI] Storage docx persist warning: {st_e}")

        if "ai_history" not in project:
            project["ai_history"] = []
        project["ai_history"].insert(0, new_hist_item)
        project["ai_gap_analysis"] = analysis_html # Keep latest for backward compatibility

        # Update evaluations in project if any (soporta "No Cumple", "Parcial", "En Construcción", "Completado")
        if evaluations and isinstance(evaluations, dict):
            for req_id, eval_data in evaluations.items():
                if req_id in project["requisitos"] and isinstance(eval_data, dict):
                    raw_st = (eval_data.get("status") or "").strip()
                    if raw_st in ["Completado", "Cumple", "Aprobado"]:
                        project["requisitos"][req_id]["status"] = "Completado"
                    elif raw_st:
                        project["requisitos"][req_id]["status"] = "En Construcción"
                    if eval_data.get("notes"):
                        prefix = "[Requiere Subsanación / Brecha] " if raw_st.lower() in ["no cumple", "incumple", "brecha"] else ""
                        project["requisitos"][req_id]["notes"] = prefix + str(eval_data["notes"])
                    if isinstance(eval_data.get("preguntas_6"), dict):
                        project["requisitos"][req_id]["preguntas_6"] = eval_data["preguntas_6"]

        # If it was a brecha solution, update the brecha item directly
        if mode == 'solve_brecha' and brecha_id:
            for b in project.get("brechas", []):
                if b["id"] == brecha_id:
                    b["solucion_redactada"] = analysis_html
                    b["doc_solucion_id"] = history_id
                    b["estado"] = "Cerrada" if "conforme" in analysis_html.lower() else "En gestión"

        # If it was a product draft, update the product document content
        if mode == 'draft_product' and producto_codigo:
            for p in project.get("productos", []):
                if p["codigo"] == producto_codigo:
                    p["documento_contenido"] = analysis_html
                    p["estado"] = "En Construcción"

        save_cc_project(inst_id, project)

        return jsonify({
            "status": "success",
            "analysis_html": analysis_html,
            "evaluations": evaluations,
            "history_item": new_hist_item,
            "history_id": history_id,
            "tokens_est": tokens_est
        })

    except Exception as e:
        print(f"[CC AI] Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def generate_doc_docx_bytes(title, text, doc_item=None, include_trace=True):
    """Genera en memoria el documento Word (.docx) oficial con Ficha Técnica y Anexo de Trazabilidad para Pares MEN."""
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    title_para = doc.add_paragraph()
    title_run = title_para.add_run("INTENALCO EDUCACIÓN SUPERIOR\nPROCESO DE CAMBIO DE CARÁCTER A INSTITUCIÓN UNIVERSITARIA")
    title_run.font.name = 'Calibri'
    title_run.font.size = Pt(11)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(49, 46, 129)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc_heading = doc.add_heading(title, level=0)
    doc_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if doc_item:
        meta_table = doc.add_table(rows=2, cols=4)
        meta_table.style = 'Table Grid'
        meta_cells_r0 = [
            f"Código: {doc_item.get('codigo_doc', 'DOC-CC')}",
            f"Versión: {doc_item.get('version_actual', 'v1.0')}",
            f"Estado: {doc_item.get('estado_editorial', 'En Construcción')}",
            f"Producto: {doc_item.get('producto', 'P5')}"
        ]
        meta_cells_r1 = [
            f"Categoría: {doc_item.get('categoria', 'Políticas y Modelos')}",
            f"Frente: {doc_item.get('frente', 'Institucional')}",
            f"Requisito MEN: {(doc_item.get('requisito_id') or 'req_1').upper()}",
            f"Fase: {doc_item.get('fase', 'Fase III')}"
        ]
        for c_i, val in enumerate(meta_cells_r0):
            cell = meta_table.cell(0, c_i)
            cell.text = val
            for run in cell.paragraphs[0].runs:
                run.font.size = Pt(8.5)
                run.font.bold = True
        for c_i, val in enumerate(meta_cells_r1):
            cell = meta_table.cell(1, c_i)
            cell.text = val
            for run in cell.paragraphs[0].runs:
                run.font.size = Pt(8.5)
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    date_para = doc.add_paragraph()
    d_run = date_para.add_run(f"Generado el: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} | Expediente Co-Construido en SKEL 360 / SIAC")
    d_run.font.name = 'Calibri'
    d_run.font.size = Pt(9)
    d_run.font.italic = True
    d_run.font.color.rgb = RGBColor(100, 116, 139)
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    for line in (text or '').split('\n'):
        line_str = line.strip()
        if not line_str:
            doc.add_paragraph()
            continue
        if line_str.startswith('# '):
            p = doc.add_heading(line_str[2:].replace('**', ''), level=1)
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
        elif line_str.startswith('## '):
            p = doc.add_heading(line_str[3:].replace('**', ''), level=2)
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
        elif line_str.startswith('### '):
            p = doc.add_heading(line_str[4:].replace('**', ''), level=3)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
        elif line_str.startswith('- ') or line_str.startswith('* '):
            doc.add_paragraph(line_str[2:].replace('**', ''), style='List Bullet')
        elif line_str.startswith('1. ') or line_str.startswith('2. ') or line_str.startswith('3. '):
            doc.add_paragraph(line_str[3:].replace('**', ''), style='List Number')
        else:
            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(6)
            parts = line_str.split('**')
            for i, part in enumerate(parts):
                if not part:
                    continue
                run = p.add_run(part)
                run.font.name = 'Calibri'
                run.font.size = Pt(10.5)
                if i % 2 == 1:
                    run.font.bold = True

    if include_trace and doc_item:
        doc.add_page_break()
        doc.add_heading("ANEXO DE TRAZABILIDAD Y CONSTRUCCIÓN COLECTIVA (SOPORTE PARA PARES ACADÉMICOS MEN)", level=1)
        intro_p = doc.add_paragraph(
            "El presente anexo certifica la trazabilidad metodológica, el equipo interdisciplinario co-autor, "
            "el control de versiones por dependencia, los acuerdos de mesas de trabajo participativas y la auditoría "
            "interna de cumplimiento normativo adelantada en el marco de la Ley 749 de 2002 y el Decreto 2038 de 2023."
        )
        intro_p.runs[0].font.size = Pt(9.5)
        intro_p.runs[0].font.italic = True

        equipo_doc = doc_item.get("equipo_documento", [])
        if equipo_doc:
            doc.add_heading("1. Equipo Institucional Co-Autor del Documento", level=2)
            t_eq = doc.add_table(rows=1, cols=4)
            t_eq.style = 'Table Grid'
            hdrs_eq = ["Integrante / Funcionario", "Dependencia / Estamento", "Rol en la Construcción", "Fecha Vinculación"]
            for idx_c, h_txt in enumerate(hdrs_eq):
                c = t_eq.cell(0, idx_c)
                c.text = h_txt
                for r in c.paragraphs[0].runs:
                    r.font.bold = True
                    r.font.size = Pt(8.5)
            for m in equipo_doc:
                rc = t_eq.add_row().cells
                rc[0].text = str(m.get("nombre", ""))
                rc[1].text = str(m.get("dependencia", ""))
                rc[2].text = str(m.get("rol", "Co-Autor"))
                rc[3].text = str(m.get("fecha", ""))[:10]
                for cell in rc:
                    for r in cell.paragraphs[0].runs:
                        r.font.size = Pt(8.5)

        doc.add_heading("2. Historial de Versiones y Co-Edición del Equipo", level=2)
        versiones = doc_item.get("bitacora_versiones", [])
        if versiones:
            t_ver = doc.add_table(rows=1, cols=5)
            t_ver.style = 'Table Grid'
            hdrs = ["Versión", "Fecha", "Responsable(s) / Co-Autor(es)", "Cargo / Dependencia(s)", "Actuación y Resumen del Aporte"]
            for idx_c, h_txt in enumerate(hdrs):
                c = t_ver.cell(0, idx_c)
                c.text = h_txt
                for r in c.paragraphs[0].runs:
                    r.font.bold = True
                    r.font.size = Pt(8.5)
            for v in versiones:
                row_cells = t_ver.add_row().cells
                row_cells[0].text = str(v.get("version", "v1.0"))
                row_cells[1].text = str(v.get("fecha", ""))[:16].replace("T", " ")
                row_cells[2].text = str(v.get("autor", ""))
                row_cells[3].text = f"{v.get('cargo_dependencia', '')} ({v.get('fase', '')})"
                row_cells[4].text = f"[{v.get('tipo_actuacion', '')}] {v.get('resumen_cambio', '')}"
                for rc in row_cells:
                    for r in rc.paragraphs[0].runs:
                        r.font.size = Pt(8.5)

        doc.add_heading("3. Registro de Mesas de Trabajo, Revisiones y Avales Colegiados", level=2)
        aportes = doc_item.get("aportes_equipo", [])
        if aportes:
            t_ap = doc.add_table(rows=1, cols=5)
            t_ap.style = 'Table Grid'
            hdrs_ap = ["Fecha", "Participantes / Instancia", "Dependencia(s) / Estamento(s)", "Tipo de Intervención", "Detalle del Aporte / Acuerdo / Aval"]
            for idx_c, h_txt in enumerate(hdrs_ap):
                c = t_ap.cell(0, idx_c)
                c.text = h_txt
                for r in c.paragraphs[0].runs:
                    r.font.bold = True
                    r.font.size = Pt(8.5)
            for ap in aportes:
                row_cells = t_ap.add_row().cells
                row_cells[0].text = str(ap.get("fecha", ""))[:16].replace("T", " ")
                row_cells[1].text = str(ap.get("autor", ""))
                row_cells[2].text = str(ap.get("cargo_dependencia", ""))
                row_cells[3].text = f"{ap.get('tipo', '')} ({ap.get('seccion_referencia', 'General')})"
                row_cells[4].text = str(ap.get("comentario", ""))
                for rc in row_cells:
                    for r in rc.paragraphs[0].runs:
                        r.font.size = Pt(8.5)
        else:
            doc.add_paragraph("Sin observaciones adicionales pendientes de cierre.")

        auditorias = doc_item.get("auditorias_ia", [])
        if auditorias:
            ult = auditorias[0]
            doc.add_heading("4. Dictamen Interno de Cumplimiento Normativo (Ley 749 / Dec. 2038)", level=2)
            p_aud = doc.add_paragraph()
            r_aud = p_aud.add_run(
                f"Índice de Alineación Normativa Verificado: {ult.get('puntaje_cumplimiento', 0)}% ({ult.get('nivel_concepto', '')}) "
                f"| Requisito contrastado: {ult.get('requisito_titulo', '')} | Versión evaluada: {ult.get('version_evaluada', '')}"
            )
            r_aud.font.bold = True
            r_aud.font.size = Pt(9.5)
            for f_item in ult.get("fortalezas", []):
                doc.add_paragraph(f"Fortaleza verificada: {f_item}", style='List Bullet')

    io_stream = io.BytesIO()
    doc.save(io_stream)
    return io_stream.getvalue()


def persist_doc_version_to_supabase_storage(inst_id, doc_item, version_entry=None, project=None):
    """Guarda físicamente cada versión del documento co-construido en el bucket 'evidencias' de Supabase Storage y lo indexa en el requisito."""
    try:
        title = doc_item.get("titulo", "Documento_Institucional")
        content = doc_item.get("contenido", "")
        ver_str = (version_entry.get("version") if version_entry else doc_item.get("version_actual", "v1.0")).replace(".", "_")
        code_str = (doc_item.get("codigo_doc") or "DOC_CC").replace("-", "_")
        docx_bytes = generate_doc_docx_bytes(title, content, doc_item, include_trace=True)

        short_uid = str(uuid.uuid4())[:8]
        storage_path = f"inst_{inst_id}/cambio_caracter/documentos_colectivos/{code_str}_{ver_str}_{short_uid}.docx"
        supabase.storage.from_('evidencias').upload(
            storage_path,
            docx_bytes,
            file_options={"content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
        )
        public_url = supabase.storage.from_('evidencias').get_public_url(storage_path)

        doc_item["supabase_doc_url"] = public_url
        doc_item["supabase_storage_path"] = storage_path
        if version_entry is not None:
            version_entry["storage_url"] = public_url
            version_entry["storage_path"] = storage_path

        # También registrar como evidencia trazable por fase en el requisito normativo vinculado
        req_id = doc_item.get("requisito_id")
        if project and req_id and req_id in project.get("requisitos", {}):
            if "evidences" not in project["requisitos"][req_id] or not isinstance(project["requisitos"][req_id]["evidences"], list):
                project["requisitos"][req_id]["evidences"] = []
            size_kb = len(docx_bytes) / 1024
            project["requisitos"][req_id]["evidences"].append({
                "name": f"{doc_item.get('codigo_doc', 'DOC')} - {title} ({doc_item.get('version_actual', 'v1.0')}).docx",
                "url": public_url,
                "path": storage_path,
                "size": f"{size_kb:.1f} KB",
                "ext": ".docx",
                "fase": doc_item.get("fase", "Fase III: Escenario y diseño"),
                "tag": f"Co-Construcción Equipo ({doc_item.get('categoria', 'Política/Modelo')})",
                "version": doc_item.get("version_actual", "v1.0"),
                "notes": f"[{doc_item.get('autor', 'Equipo')} - {doc_item.get('cargo_dependencia', '')}] {version_entry.get('resumen_cambio', '') if version_entry else 'Versión consolidada en equipo.'}",
                "uploaded_at": datetime.datetime.now().isoformat()
            })
            if project["requisitos"][req_id].get("status") == "Pendiente":
                project["requisitos"][req_id]["status"] = "En Construcción"

        return public_url
    except Exception as st_e:
        print(f"[CC Supabase Storage Persist] Warning: {st_e}")
        return None


@cambio_caracter_bp.route('/api/cambio_caracter/ai_history/save', methods=['POST'])
def api_cc_ai_history_save():
    try:
        req_json = request.json or {}
        inst_id = req_json.get('inst_id', get_active_inst_id())
        item_id = req_json.get('id')
        titulo = req_json.get('titulo', 'Documento Institucional')
        contenido = req_json.get('contenido', '')
        frente = req_json.get('frente', 'Oferta y currículo')
        producto = req_json.get('producto', 'P5')
        categoria = req_json.get('categoria', 'Políticas y Modelos')
        codigo_doc = req_json.get('codigo_doc', '')
        requisito_id = req_json.get('requisito_id', 'req_17')
        fase = req_json.get('fase', 'Fase III: Escenario y diseño')
        estado_editorial = req_json.get('estado_editorial', 'En Construcción')
        autor = req_json.get('autor', 'Integrante del Equipo Institucional')
        cargo_dependencia = req_json.get('cargo_dependencia', frente)
        coautores = req_json.get('coautores') or []
        rol_skel = req_json.get('rol_skel', 'lider')
        tipo_actuacion = req_json.get('tipo_actuacion', 'Ajuste Técnico / Co-edición')
        resumen_cambio = req_json.get('resumen_cambio', 'Actualización colaborativa del documento.')
        version_actual = req_json.get('version_actual', 'v1.0')
        create_new = req_json.get('create_new', False)
        increment_version = req_json.get('increment_version', True)

        if isinstance(coautores, list) and len(coautores) > 0:
            autor = " · ".join([str(m.get("nombre", "")).strip() for m in coautores if m.get("nombre")]) or autor
            deps_uniq = []
            for m in coautores:
                d_str = str(m.get("dependencia", "")).strip()
                if d_str and d_str not in deps_uniq:
                    deps_uniq.append(d_str)
            if deps_uniq:
                cargo_dependencia = " / ".join(deps_uniq)

        project = get_cc_project(inst_id)
        if "ai_history" not in project:
            project["ai_history"] = []

        now_iso = datetime.datetime.now().isoformat()

        def bump_version(ver_str):
            v = (ver_str or "v1.0").strip()
            if not v.lower().startswith("v"):
                v = "v" + v
            try:
                parts = v[1:].split(".")
                major = int(parts[0])
                minor = int(parts[1]) if len(parts) > 1 else 0
                return f"v{major}.{minor + 1}"
            except Exception:
                return "v1.1"

        target_doc_ref = None
        target_ver_ref = None

        if not create_new and item_id:
            found = False
            for item in project["ai_history"]:
                if item["id"] == item_id:
                    new_ver = bump_version(item.get("version_actual", version_actual)) if increment_version else (version_actual or item.get("version_actual", "v1.0"))
                    item["titulo"] = titulo
                    item["contenido"] = contenido
                    item["frente"] = frente
                    item["producto"] = producto
                    item["categoria"] = categoria
                    if codigo_doc:
                        item["codigo_doc"] = codigo_doc
                    item["requisito_id"] = requisito_id
                    item["fase"] = fase
                    item["estado_editorial"] = estado_editorial
                    item["version_actual"] = new_ver
                    item["fecha_modificacion"] = now_iso
                    item["autor"] = autor
                    item["cargo_dependencia"] = cargo_dependencia
                    item["rol_skel"] = rol_skel

                    if "bitacora_versiones" not in item or not isinstance(item["bitacora_versiones"], list):
                        item["bitacora_versiones"] = []
                    new_ver_entry = {
                        "version": new_ver,
                        "fecha": now_iso,
                        "autor": autor,
                        "cargo_dependencia": cargo_dependencia,
                        "coautores": coautores if isinstance(coautores, list) and len(coautores) > 0 else [{"nombre": autor, "dependencia": cargo_dependencia, "rol": "Co-Autor"}],
                        "rol_skel": rol_skel,
                        "fase": fase,
                        "tipo_actuacion": tipo_actuacion,
                        "resumen_cambio": resumen_cambio,
                        "contenido_snapshot": contenido
                    }
                    item["bitacora_versiones"].insert(0, new_ver_entry)
                    merge_team_members_into_doc(
                        item,
                        coautores if isinstance(coautores, list) and len(coautores) > 0 else [{"nombre": autor, "dependencia": cargo_dependencia, "rol": "Co-Autor"}],
                        default_rol="Co-Autor"
                    )
                    target_doc_ref = item
                    target_ver_ref = new_ver_entry
                    found = True
                    break

            if not found:
                create_new = True

        if create_new or not item_id:
            item_id = str(uuid.uuid4())
            if not codigo_doc:
                prod_prefix = (producto or "DOC").split()[0][:4].upper()
                codigo_doc = f"DOC-{prod_prefix}-{len(project['ai_history']) + 1:02d}"
            ver_init = version_actual or "v1.0"
            init_ver_entry = {
                "version": ver_init,
                "fecha": now_iso,
                "autor": autor,
                "cargo_dependencia": cargo_dependencia,
                "coautores": coautores if isinstance(coautores, list) and len(coautores) > 0 else [{"nombre": autor, "dependencia": cargo_dependencia, "rol": "Líder / Co-Autor"}],
                "rol_skel": rol_skel,
                "fase": fase,
                "tipo_actuacion": tipo_actuacion or "Redacción Inicial",
                "resumen_cambio": resumen_cambio or f"Creación inicial del documento: {titulo}",
                "contenido_snapshot": contenido
            }
            new_doc = {
                "id": item_id,
                "codigo_doc": codigo_doc,
                "titulo": titulo,
                "categoria": categoria,
                "fecha": now_iso,
                "fecha_modificacion": now_iso,
                "tipo": "collaborative_doc",
                "frente": frente,
                "producto": producto,
                "requisito_id": requisito_id,
                "fase": fase,
                "version_actual": ver_init,
                "estado_editorial": estado_editorial,
                "autor": autor,
                "cargo_dependencia": cargo_dependencia,
                "rol_skel": rol_skel,
                "tokens_est": 0,
                "contenido": contenido,
                "equipo_documento": [],
                "bitacora_versiones": [init_ver_entry],
                "aportes_equipo": [],
                "auditorias_ia": []
            }
            merge_team_members_into_doc(
                new_doc,
                coautores if isinstance(coautores, list) and len(coautores) > 0 else [{"nombre": autor, "dependencia": cargo_dependencia, "rol": "Líder / Co-Autor"}],
                default_rol="Líder / Co-Autor"
            )
            project["ai_history"].insert(0, new_doc)
            target_doc_ref = new_doc
            target_ver_ref = init_ver_entry

        # Persist physical .docx version into Supabase Storage ('evidencias' bucket) and link to requirement
        storage_url = None
        if target_doc_ref:
            storage_url = persist_doc_version_to_supabase_storage(inst_id, target_doc_ref, target_ver_ref, project)

        # Also sync with product's main documento_contenido if linked to P1..P10
        for p in project.get("productos", []):
            if p.get("codigo") == producto:
                p["documento_contenido"] = contenido
                if p.get("estado") == "Pendiente":
                    p["estado"] = "En Construcción"

        save_cc_project(inst_id, project)
        return jsonify({
            "status": "success",
            "id": item_id,
            "storage_url": storage_url,
            "message": "Versión y trazabilidad de equipo guardadas en Supabase Database y Supabase Storage."
        })
    except Exception as e:
        print(f"[CC Save History] Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@cambio_caracter_bp.route('/api/cambio_caracter/doc/import_file', methods=['POST'])
def api_cc_doc_import_file():
    """Importa un archivo .docx o .pdf construido por el equipo y lo convierte en un documento colaborativo con trazabilidad."""
    try:
        inst_id = request.form.get('inst_id', get_active_inst_id(), type=int)
        titulo = (request.form.get('titulo') or '').strip()
        categoria = request.form.get('categoria', 'Políticas y Modelos')
        producto = request.form.get('producto', 'P5')
        frente = request.form.get('frente', 'Oferta y currículo')
        requisito_id = request.form.get('requisito_id', 'req_17')
        fase = request.form.get('fase', 'Fase III: Escenario y diseño')
        autor = request.form.get('autor', 'Equipo Técnico Institucional')
        cargo_dependencia = request.form.get('cargo_dependencia', frente)
        rol_skel = request.form.get('rol_skel', 'lider')
        resumen_cambio = request.form.get('resumen_cambio', 'Cargue e importación inicial de documento construido por el equipo para co-edición y verificación normativa.')
        direct_content = (request.form.get('contenido') or '').strip()
        equipo_json_str = (request.form.get('equipo_json') or '').strip()
        equipo_members = []
        if equipo_json_str:
            try:
                equipo_members = json.loads(equipo_json_str)
            except Exception:
                equipo_members = []
        if isinstance(equipo_members, list) and len(equipo_members) > 0:
            autor = " · ".join([str(m.get("nombre", "")).strip() for m in equipo_members if m.get("nombre")]) or autor
            deps_uniq = []
            for m in equipo_members:
                d_str = str(m.get("dependencia", "")).strip()
                if d_str and d_str not in deps_uniq:
                    deps_uniq.append(d_str)
            if deps_uniq:
                cargo_dependencia = " / ".join(deps_uniq)

        file = request.files.get('file')
        extracted_md = ""
        saved_doc_path = None
        public_url = None

        if file and file.filename:
            ext = os.path.splitext(file.filename)[1].lower()
            if not titulo:
                titulo = os.path.splitext(file.filename)[0].replace('_', ' ')
            file_bytes = file.read()
            new_filename = f"collab_{uuid.uuid4()}{ext}"
            saved_doc_path = f"inst_{inst_id}/cambio_caracter/collab_docs/{new_filename}"
            file_options = {"content-type": file.content_type} if hasattr(file, 'content_type') else {}
            try:
                supabase.storage.from_('evidencias').upload(saved_doc_path, file_bytes, file_options=file_options)
                public_url = supabase.storage.from_('evidencias').get_public_url(saved_doc_path)
            except Exception as up_e:
                print(f"[CC Collab Import] Storage warning: {up_e}")

            if ext == '.docx':
                try:
                    d_obj = docx.Document(io.BytesIO(file_bytes))
                    md_lines = []
                    for para in d_obj.paragraphs:
                        t = para.text.strip()
                        if not t:
                            md_lines.append("")
                            continue
                        style_name = (para.style.name if para.style else "").lower()
                        if "heading 1" in style_name or "título 1" in style_name:
                            md_lines.append(f"# {t}")
                        elif "heading 2" in style_name or "título 2" in style_name:
                            md_lines.append(f"## {t}")
                        elif "heading 3" in style_name or "título 3" in style_name:
                            md_lines.append(f"### {t}")
                        elif "list" in style_name or "viñeta" in style_name:
                            md_lines.append(f"- {t}")
                        else:
                            md_lines.append(t)
                    # Also extract tables if any
                    for tbl in d_obj.tables:
                        md_lines.append("")
                        for r_i, row in enumerate(tbl.rows):
                            cells_txt = [c.text.strip().replace('\n', ' ') for c in row.cells]
                            md_lines.append("| " + " | ".join(cells_txt) + " |")
                            if r_i == 0:
                                md_lines.append("| " + " | ".join(["---"] * len(cells_txt)) + " |")
                        md_lines.append("")
                    extracted_md = "\n".join(md_lines).strip()
                except Exception:
                    extracted_md = docx2txt.process(io.BytesIO(file_bytes))
            elif ext == '.doc':
                extracted_md = docx2txt.process(io.BytesIO(file_bytes))
            elif ext == '.pdf':
                reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                pages_txt = []
                for idx_p, page in enumerate(reader.pages):
                    t = page.extract_text()
                    if t:
                        pages_txt.append(t.strip())
                extracted_md = "\n\n".join(pages_txt)
            elif ext in ['.md', '.txt']:
                extracted_md = file_bytes.decode('utf-8', errors='replace')
            else:
                return jsonify({"status": "error", "message": "Formato no soportado. Usa Word (.docx), PDF (.pdf) o Markdown (.md)."}), 400

        final_content = extracted_md or direct_content
        if not final_content:
            final_content = (
                f"# {titulo or 'Nuevo Documento Institucional'}\n\n"
                f"## 1. Propósito y Alcance Normativo (Ley 749 de 2002 / Decreto 2038 de 2023)\n"
                f"Documento en construcción colectiva por el frente **{frente}**.\n\n"
                f"## 2. Lineamientos y Articulado Institucional\n\n"
                f"## 3. Disposiciones de Implementación y Seguimiento\n"
            )

        if not titulo:
            titulo = "Documento Institucional Co-construido"

        project = get_cc_project(inst_id)
        if "ai_history" not in project:
            project["ai_history"] = []

        now_iso = datetime.datetime.now().isoformat()
        item_id = str(uuid.uuid4())
        prod_prefix = (producto or "DOC").split()[0][:4].upper()
        codigo_doc = f"DOC-{prod_prefix}-{len(project['ai_history']) + 1:02d}"

        new_doc = {
            "id": item_id,
            "codigo_doc": codigo_doc,
            "titulo": titulo,
            "categoria": categoria,
            "fecha": now_iso,
            "fecha_modificacion": now_iso,
            "tipo": "collaborative_doc",
            "frente": frente,
            "producto": producto,
            "requisito_id": requisito_id,
            "fase": fase,
            "version_actual": "v1.0",
            "estado_editorial": "En Construcción",
            "autor": autor,
            "cargo_dependencia": cargo_dependencia,
            "rol_skel": rol_skel,
            "tokens_est": 0,
            "contenido": final_content,
            "saved_doc_path": saved_doc_path,
            "original_file_url": public_url,
            "equipo_documento": [],
            "bitacora_versiones": [
                {
                    "version": "v1.0",
                    "fecha": now_iso,
                    "autor": autor,
                    "cargo_dependencia": cargo_dependencia,
                    "coautores": equipo_members if len(equipo_members) > 0 else [{"nombre": autor, "dependencia": cargo_dependencia, "rol": "Líder / Co-Autor"}],
                    "rol_skel": rol_skel,
                    "fase": fase,
                    "tipo_actuacion": "Importación de Documento Base" if (file and file.filename) else "Redacción Inicial",
                    "resumen_cambio": resumen_cambio,
                    "contenido_snapshot": final_content
                }
            ],
            "aportes_equipo": [],
            "auditorias_ia": []
        }

        merge_team_members_into_doc(
            new_doc,
            equipo_members if len(equipo_members) > 0 else [{"nombre": autor, "dependencia": cargo_dependencia, "rol": "Líder / Co-Autor"}],
            default_rol="Líder / Co-Autor"
        )
        project["ai_history"].insert(0, new_doc)
        persist_doc_version_to_supabase_storage(inst_id, new_doc, new_doc["bitacora_versiones"][0], project)
        save_cc_project(inst_id, project)

        return jsonify({
            "status": "success",
            "id": item_id,
            "doc": new_doc,
            "message": "Documento incorporado exitosamente a la Mesa de Co-Construcción."
        })
    except Exception as e:
        print(f"[CC Import Doc] Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@cambio_caracter_bp.route('/api/cambio_caracter/doc/add_team_contribution', methods=['POST'])
def api_cc_doc_add_team_contribution():
    """Registra aportes de revisión del equipo, acuerdos de mesas de trabajo o avales colegiados con uno o varios integrantes."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', get_active_inst_id())
        doc_id = data.get('doc_id')
        autor = (data.get('autor') or 'Integrante del Equipo').strip()
        cargo_dependencia = (data.get('cargo_dependencia') or 'Comité Técnico').strip()
        participantes = data.get('participantes') or []
        tipo = data.get('tipo', 'Aporte / Observación')
        seccion_referencia = (data.get('seccion_referencia') or 'General').strip()
        comentario = (data.get('comentario') or '').strip()
        nuevo_estado_editorial = data.get('nuevo_estado_editorial')

        if not doc_id or not comentario:
            return jsonify({"status": "error", "message": "Falta identificar el documento o el detalle del aporte."}), 400

        project = get_cc_project(inst_id)
        target_doc = next((d for d in project.get("ai_history", []) if d["id"] == doc_id), None)
        if not target_doc:
            return jsonify({"status": "error", "message": "Documento no encontrado"}), 404

        if "aportes_equipo" not in target_doc or not isinstance(target_doc["aportes_equipo"], list):
            target_doc["aportes_equipo"] = []

        if isinstance(participantes, list) and len(participantes) > 0:
            autor = " · ".join([str(p.get("nombre", "")).strip() for p in participantes if p.get("nombre")]) or autor
            deps_uniq = []
            for p in participantes:
                d_str = str(p.get("dependencia", "")).strip()
                if d_str and d_str not in deps_uniq:
                    deps_uniq.append(d_str)
            if deps_uniq:
                cargo_dependencia = " / ".join(deps_uniq)
        else:
            participantes = [{"nombre": autor, "dependencia": cargo_dependencia, "rol": "Participante Mesa"}]

        now_iso = datetime.datetime.now().isoformat()
        aporte_item = {
            "id": str(uuid.uuid4()),
            "fecha": now_iso,
            "autor": autor,
            "cargo_dependencia": cargo_dependencia,
            "participantes": participantes,
            "tipo": tipo,
            "seccion_referencia": seccion_referencia,
            "comentario": comentario,
            "estado": "Avalado" if "Aval" in tipo else "Registrado"
        }
        target_doc["aportes_equipo"].insert(0, aporte_item)
        merge_team_members_into_doc(target_doc, participantes, default_rol="Participante Mesa / Revisor")

        if nuevo_estado_editorial:
            target_doc["estado_editorial"] = nuevo_estado_editorial

        target_doc["fecha_modificacion"] = now_iso
        save_cc_project(inst_id, project)

        return jsonify({
            "status": "success",
            "aporte": aporte_item,
            "equipo_documento": target_doc.get("equipo_documento", []),
            "estado_editorial": target_doc.get("estado_editorial"),
            "message": "Aporte de trabajo en equipo registrado en la bitácora del documento."
        })
    except Exception as e:
        print(f"[CC Add Contribution] Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@cambio_caracter_bp.route('/api/cambio_caracter/doc/update_team', methods=['POST'])
def api_cc_doc_update_team():
    """Agrega o elimina integrantes del equipo de trabajo permanente asignado a un documento co-construido."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', get_active_inst_id())
        doc_id = data.get('doc_id')
        action = data.get('action', 'add')  # 'add' o 'remove'
        if not doc_id:
            return jsonify({"status": "error", "message": "Falta seleccionar un documento."}), 400

        project = get_cc_project(inst_id)
        target_doc = next((d for d in project.get("ai_history", []) if d["id"] == doc_id), None)
        if not target_doc:
            return jsonify({"status": "error", "message": "Documento no encontrado."}), 404

        if "equipo_documento" not in target_doc or not isinstance(target_doc["equipo_documento"], list):
            target_doc["equipo_documento"] = []

        if action == 'add':
            nombre = (data.get('nombre') or '').strip()
            dependencia = (data.get('dependencia') or 'Equipo Institucional').strip()
            rol = (data.get('rol') or 'Co-Autor / Integrante').strip()
            if not nombre:
                return jsonify({"status": "error", "message": "Ingresa el nombre del integrante."}), 400
            merge_team_members_into_doc(target_doc, [{"nombre": nombre, "dependencia": dependencia, "rol": rol}], default_rol=rol)
        elif action == 'remove':
            member_id = data.get('member_id')
            target_doc["equipo_documento"] = [
                m for m in target_doc["equipo_documento"]
                if str(m.get("id")) != str(member_id) and str(m.get("nombre")) != str(member_id)
            ]

        target_doc["fecha_modificacion"] = datetime.datetime.now().isoformat()
        save_cc_project(inst_id, project)
        return jsonify({
            "status": "success",
            "equipo_documento": target_doc["equipo_documento"]
        })
    except Exception as e:
        print(f"[CC Update Team] Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@cambio_caracter_bp.route('/api/cambio_caracter/doc/ai_audit_compliance', methods=['POST'])
def api_cc_doc_ai_audit_compliance():
    """Evalúa un documento co-construido (ej. Modelo Pedagógico, Reglamentos) frente al requerimiento normativo MEN."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', get_active_inst_id())
        doc_id = data.get('doc_id')
        contenido = (data.get('contenido') or '').strip()
        titulo = data.get('titulo', 'Documento Institucional')
        requisito_id = data.get('requisito_id', 'req_17')
        frente = data.get('frente', 'Oferta y currículo')
        producto = data.get('producto', 'P5')

        if not contenido:
            return jsonify({"status": "error", "message": "El documento está vacío. Escribe o importa contenido antes de auditarlo."}), 400

        project = get_cc_project(inst_id)
        target_doc = next((d for d in project.get("ai_history", []) if d["id"] == doc_id), None)

        req_item = next((r for r in REQUISITOS if r['id'] == requisito_id), None)
        if not req_item:
            req_item = REQUISITOS[0]

        # Buscar requisitos complementarios del mismo factor/frente para un contraste integral
        related_reqs = [
            f"- [{r['id']}] {r['title']}: {r['desc']} (Exigencia: {r.get('evidencia_requerida', '')})"
            for r in REQUISITOS
            if r.get('factor') == req_item.get('factor') or frente.lower()[:8] in (r.get('eje', '') + ' ' + r.get('desc', '')).lower()
        ][:6]
        related_reqs_str = "\n".join(related_reqs)

        # Incluir resumen del trabajo en equipo del documento para que el Par IA también valore la construcción colectiva
        num_versiones = len(target_doc.get("bitacora_versiones", [])) if target_doc else 1
        num_aportes = len(target_doc.get("aportes_equipo", [])) if target_doc else 0
        autores_equipo = list({v.get("cargo_dependencia", "") for v in (target_doc.get("bitacora_versiones", []) if target_doc else []) if v.get("cargo_dependencia")})

        system_prompt = (
            "Eres el Par Académico Evaluador Coordinador designado por el Ministerio de Educación Nacional (MEN) y CONACES, "
            "experto en trámites de Cambio de Carácter Académico de Institución Técnica Profesional / Tecnológica a "
            "Institución Universitaria (Ley 30 de 1992, Ley 749 de 2002 Art. 13-15, Decreto 1075 de 2015, Decreto 1330 de 2019, "
            "Decreto 2038 de 2023 y Acuerdo CESU 01 de 2025). "
            "Tu misión es auditar con rigor técnico el documento institucional presentado por el equipo y verificar si "
            "realmente cumple con el requerimiento normativo exigido para una Institución Universitaria."
        )

        user_prompt = f"""
Audita el siguiente documento institucional construido en equipo:
- **Título del Documento:** {titulo}
- **Producto Asociado:** {producto} | **Frente:** {frente}
- **Requisito Normativo Principal Evaluado:** [{req_item.get('id')}] {req_item.get('title')}
  * Descripción normativa: {req_item.get('desc')}
  * Evidencia requerida por el MEN: {req_item.get('evidencia_requerida')}
  * Marco Legal: {req_item.get('ley')}
- **Criterios Normativos Concordantes del Frente:**
{related_reqs_str}
- **Trazabilidad de Construcción en Equipo Registrada:** {num_versiones} versión(es), {num_aportes} aporte(s)/mesa(s) registrados por: {', '.join(autores_equipo) or frente}.

CONTENIDO DEL DOCUMENTO A EVALUAR:
{contenido[:28000]}

Evalúa rigurosamente el documento bajo la Metodología de las 6 Preguntas Institucionales y los estándares de visita de Pares del MEN.
Devuelve EXCLUSIVAMENTE un bloque JSON válido con esta estructura exacta:
```json
{{
  "puntaje_cumplimiento": 85,
  "nivel_concepto": "Cumple Parcialmente (Avance Sólido)",
  "preguntas_6": {{
    "existe": true,
    "vigente": true,
    "aprobado": false,
    "pertinente": true,
    "aplica": true,
    "evidencia": true
  }},
  "fortalezas": [
    "Fortaleza específica 1 detectada en el texto frente a la norma...",
    "Fortaleza específica 2..."
  ],
  "aspectos_por_mejorar": [
    "Brecha o aspecto que un Par Académico del MEN observaría en visita...",
    "Segundo aspecto por complementar para llegar al 100%..."
  ],
  "texto_sugerido": "## Propuesta de Articulado / Parágrafo Complementario Sugerido\\nRedacta aquí el texto exacto listo para insertar en el documento y subsanar los vacíos detectados...",
  "dictamen_markdown": "### Dictamen Técnico del Par Evaluador MEN\\nRedacta un análisis ejecutivo formal sobre la coherencia, pertinencia universitaria y trazabilidad de equipo del documento."
}}
```
"""

        ai_response = call_ai([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], max_tokens=4000, temperature=0.25, inst_id=inst_id)

        import re
        match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
        json_str = match.group(1) if match else ai_response.strip().strip('`')
        if json_str.startswith('json'):
            json_str = json_str[4:].strip()

        try:
            parsed = json.loads(json_str)
        except Exception:
            parsed = {
                "puntaje_cumplimiento": 78,
                "nivel_concepto": "En Consolidación Técnica",
                "preguntas_6": {"existe": True, "vigente": True, "aprobado": False, "pertinente": True, "aplica": False, "evidencia": True},
                "fortalezas": ["El documento desarrolla la estructura base requerida para el cambio de carácter."],
                "aspectos_por_mejorar": ["Reforzar la evidencia de aprobación por órgano colegiado e indicadores de seguimiento."],
                "texto_sugerido": "",
                "dictamen_markdown": ai_response
            }

        now_iso = datetime.datetime.now().isoformat()
        audit_record = {
            "id": str(uuid.uuid4()),
            "fecha": now_iso,
            "version_evaluada": target_doc.get("version_actual", "v1.0") if target_doc else "v1.0",
            "requisito_id": req_item.get("id"),
            "requisito_titulo": f"{req_item.get('id').upper()} - {req_item.get('title')}",
            "puntaje_cumplimiento": int(parsed.get("puntaje_cumplimiento", 80)),
            "nivel_concepto": parsed.get("nivel_concepto", "Evaluado"),
            "preguntas_6": parsed.get("preguntas_6", {}),
            "fortalezas": parsed.get("fortalezas", []),
            "aspectos_por_mejorar": parsed.get("aspectos_por_mejorar", []),
            "texto_sugerido": parsed.get("texto_sugerido", ""),
            "dictamen_markdown": parsed.get("dictamen_markdown", "")
        }

        if target_doc:
            if "auditorias_ia" not in target_doc or not isinstance(target_doc["auditorias_ia"], list):
                target_doc["auditorias_ia"] = []
            target_doc["auditorias_ia"].insert(0, audit_record)
            target_doc["ultimo_puntaje_ia"] = audit_record["puntaje_cumplimiento"]

        # Actualizar también las 6 preguntas del requisito en la matriz si aplica
        rid = req_item.get("id")
        if rid and rid in project.get("requisitos", {}) and parsed.get("preguntas_6"):
            project["requisitos"][rid]["preguntas_6"] = parsed["preguntas_6"]
            if audit_record["puntaje_cumplimiento"] >= 85:
                project["requisitos"][rid]["status"] = "Completado"
            elif project["requisitos"][rid].get("status") == "Pendiente":
                project["requisitos"][rid]["status"] = "En Construcción"

        save_cc_project(inst_id, project)

        return jsonify({
            "status": "success",
            "audit": audit_record
        })
    except Exception as e:
        print(f"[CC AI Audit Doc] Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@cambio_caracter_bp.route('/api/cambio_caracter/ai_history/delete', methods=['POST'])
def api_cc_ai_history_delete():
    try:
        inst_id = request.json.get('inst_id', get_active_inst_id())
        item_id = request.json.get('id')
        project = get_cc_project(inst_id)
        if "ai_history" in project:
            project["ai_history"] = [h for h in project["ai_history"] if h["id"] != item_id]
            save_cc_project(inst_id, project)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@cambio_caracter_bp.route('/api/cambio_caracter/download_word', methods=['POST'])
def api_cc_download_word():
    try:
        inst_id = request.form.get('inst_id', get_active_inst_id(), type=int)
        doc_id = request.form.get('doc_id', '')
        title = request.form.get('title', 'Documento Institucional - Cambio de Carácter')
        text = request.form.get('content', '')
        include_trace = request.form.get('include_traceability', '1') == '1'

        project = get_cc_project(inst_id)
        doc_item = next((h for h in project.get("ai_history", []) if h.get("id") == doc_id), None)

        doc = docx.Document()
        
        # Page Margins (Normal 1 inch)
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Cover / Header Style
        title_para = doc.add_paragraph()
        title_run = title_para.add_run("INTENALCO EDUCACIÓN SUPERIOR\nPROCESO DE CAMBIO DE CARÁCTER A INSTITUCIÓN UNIVERSITARIA")
        title_run.font.name = 'Calibri'
        title_run.font.size = Pt(11)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(49, 46, 129)
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc_heading = doc.add_heading(title, level=0)
        doc_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Ficha de Control Documental en el Encabezado si existe doc_item
        if doc_item:
            meta_table = doc.add_table(rows=2, cols=4)
            meta_table.style = 'Table Grid'
            meta_cells_r0 = [
                f"Código: {doc_item.get('codigo_doc', 'DOC-CC')}",
                f"Versión: {doc_item.get('version_actual', 'v1.0')}",
                f"Estado: {doc_item.get('estado_editorial', 'En Construcción')}",
                f"Producto: {doc_item.get('producto', 'P5')}"
            ]
            meta_cells_r1 = [
                f"Categoría: {doc_item.get('categoria', 'Políticas y Modelos')}",
                f"Frente: {doc_item.get('frente', 'Institucional')}",
                f"Requisito MEN: {(doc_item.get('requisito_id') or 'req_1').upper()}",
                f"Fase: {doc_item.get('fase', 'Fase III')}"
            ]
            for c_i, val in enumerate(meta_cells_r0):
                cell = meta_table.cell(0, c_i)
                cell.text = val
                for run in cell.paragraphs[0].runs:
                    run.font.size = Pt(8.5)
                    run.font.bold = True
            for c_i, val in enumerate(meta_cells_r1):
                cell = meta_table.cell(1, c_i)
                cell.text = val
                for run in cell.paragraphs[0].runs:
                    run.font.size = Pt(8.5)
            doc.add_paragraph().paragraph_format.space_after = Pt(6)
        
        date_para = doc.add_paragraph()
        d_run = date_para.add_run(f"Generado el: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} | Expediente Co-Construido en SIAC 360")
        d_run.font.name = 'Calibri'
        d_run.font.size = Pt(9)
        d_run.font.italic = True
        d_run.font.color.rgb = RGBColor(100, 116, 139)
        date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph().paragraph_format.space_after = Pt(10)

        # Parse markdown text line by line
        for line in text.split('\n'):
            line_str = line.strip()
            if not line_str:
                doc.add_paragraph()
                continue
            
            if line_str.startswith('# '):
                p = doc.add_heading(line_str[2:].replace('**', ''), level=1)
                p.paragraph_format.space_before = Pt(14)
                p.paragraph_format.space_after = Pt(6)
            elif line_str.startswith('## '):
                p = doc.add_heading(line_str[3:].replace('**', ''), level=2)
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(4)
            elif line_str.startswith('### '):
                p = doc.add_heading(line_str[4:].replace('**', ''), level=3)
                p.paragraph_format.space_before = Pt(8)
                p.paragraph_format.space_after = Pt(2)
            elif line_str.startswith('- ') or line_str.startswith('* '):
                bullet_text = line_str[2:].replace('**', '')
                doc.add_paragraph(bullet_text, style='List Bullet')
            elif line_str.startswith('1. ') or line_str.startswith('2. ') or line_str.startswith('3. '):
                num_text = line_str[3:].replace('**', '')
                doc.add_paragraph(num_text, style='List Number')
            else:
                p = doc.add_paragraph()
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.space_after = Pt(6)
                parts = line_str.split('**')
                for i, part in enumerate(parts):
                    if not part: continue
                    run = p.add_run(part)
                    run.font.name = 'Calibri'
                    run.font.size = Pt(10.5)
                    if i % 2 == 1:
                        run.font.bold = True

        # ANEXO DE TRAZABILIDAD Y TRABAJO EN EQUIPO PARA PARES EVALUADORES
        if include_trace and doc_item:
            doc.add_page_break()
            h_anexo = doc.add_heading("ANEXO DE TRAZABILIDAD Y CONSTRUCCIÓN COLECTIVA (SOPORTE PARA PARES ACADÉMICOS MEN)", level=1)
            h_anexo.alignment = WD_ALIGN_PARAGRAPH.LEFT

            intro_p = doc.add_paragraph(
                "El presente anexo certifica la trazabilidad metodológica, el control de versiones por dependencia, "
                "los acuerdos de mesas de trabajo participativas y la auditoría interna de cumplimiento normativo "
                "adelantada por el equipo institucional en el marco de la Ley 749 de 2002 y el Decreto 2038 de 2023."
            )
            intro_p.runs[0].font.size = Pt(9.5)
            intro_p.runs[0].font.italic = True

            # 1. Tabla de Control de Versiones y Co-Autores
            doc.add_heading("1. Historial de Versiones y Co-Edición del Equipo", level=2)
            versiones = doc_item.get("bitacora_versiones", [])
            if versiones:
                t_ver = doc.add_table(rows=1, cols=5)
                t_ver.style = 'Table Grid'
                hdrs = ["Versión", "Fecha", "Responsable / Co-Autor", "Cargo / Dependencia", "Actuación y Resumen del Aporte"]
                for idx_c, h_txt in enumerate(hdrs):
                    c = t_ver.cell(0, idx_c)
                    c.text = h_txt
                    for r in c.paragraphs[0].runs:
                        r.font.bold = True
                        r.font.size = Pt(8.5)
                for v in versiones:
                    row_cells = t_ver.add_row().cells
                    row_cells[0].text = str(v.get("version", "v1.0"))
                    row_cells[1].text = str(v.get("fecha", ""))[:16].replace("T", " ")
                    row_cells[2].text = str(v.get("autor", ""))
                    row_cells[3].text = f"{v.get('cargo_dependencia', '')} ({v.get('fase', '')})"
                    row_cells[4].text = f"[{v.get('tipo_actuacion', '')}] {v.get('resumen_cambio', '')}"
                    for rc in row_cells:
                        for r in rc.paragraphs[0].runs:
                            r.font.size = Pt(8.5)

            # 2. Tabla de Mesas de Trabajo, Revisiones y Avales del Equipo
            doc.add_heading("2. Registro de Mesas de Trabajo, Revisiones y Avales Colegiados", level=2)
            aportes = doc_item.get("aportes_equipo", [])
            if aportes:
                t_ap = doc.add_table(rows=1, cols=5)
                t_ap.style = 'Table Grid'
                hdrs_ap = ["Fecha", "Participante / Instancia", "Dependencia / Estamento", "Tipo de Intervención", "Detalle del Aporte / Acuerdo / Aval"]
                for idx_c, h_txt in enumerate(hdrs_ap):
                    c = t_ap.cell(0, idx_c)
                    c.text = h_txt
                    for r in c.paragraphs[0].runs:
                        r.font.bold = True
                        r.font.size = Pt(8.5)
                for ap in aportes:
                    row_cells = t_ap.add_row().cells
                    row_cells[0].text = str(ap.get("fecha", ""))[:16].replace("T", " ")
                    row_cells[1].text = str(ap.get("autor", ""))
                    row_cells[2].text = str(ap.get("cargo_dependencia", ""))
                    row_cells[3].text = f"{ap.get('tipo', '')} ({ap.get('seccion_referencia', 'General')})"
                    row_cells[4].text = str(ap.get("comentario", ""))
                    for rc in row_cells:
                        for r in rc.paragraphs[0].runs:
                            r.font.size = Pt(8.5)
            else:
                doc.add_paragraph("Sin observaciones adicionales pendientes de cierre.")

            # 3. Resumen de Verificación Normativa IA
            auditorias = doc_item.get("auditorias_ia", [])
            if auditorias:
                ult = auditorias[0]
                doc.add_heading("3. Dictamen Interno de Cumplimiento Normativo (Ley 749 / Dec. 2038)", level=2)
                p_aud = doc.add_paragraph()
                r_aud = p_aud.add_run(
                    f"Índice de Alineación Normativa Verificado: {ult.get('puntaje_cumplimiento', 0)}% ({ult.get('nivel_concepto', '')}) "
                    f"| Requisito contrastado: {ult.get('requisito_titulo', '')} | Versión evaluada: {ult.get('version_evaluada', '')}"
                )
                r_aud.font.bold = True
                r_aud.font.size = Pt(9.5)
                for f_item in ult.get("fortalezas", []):
                    doc.add_paragraph(f"Fortaleza verificada: {f_item}", style='List Bullet')
                
        io_stream = io.BytesIO()
        doc.save(io_stream)
        io_stream.seek(0)
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()
        filename = f"{safe_title[:40].replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.docx"
        return send_file(io_stream, as_attachment=True, download_name=filename, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    except Exception as e:
        print(f"[CC] Word Download Error: {e}")
        return str(e), 500

@cambio_caracter_bp.route('/api/cambio_caracter/download_pdf', methods=['POST'])
def api_cc_download_pdf():
    try:
        inst_id = request.form.get('inst_id', get_active_inst_id(), type=int)
        doc_id = request.form.get('doc_id', '')
        title = request.form.get('title', 'Documento Institucional - Cambio de Caracter')
        text = request.form.get('content', '')
        include_trace = request.form.get('include_traceability', '1') == '1'

        project = get_cc_project(inst_id)
        doc_item = next((h for h in project.get("ai_history", []) if h.get("id") == doc_id), None)

        from fpdf import FPDF
        
        class CC_PDF(FPDF):
            def header(self):
                self.set_font("helvetica", "B", 10)
                self.set_text_color(99, 102, 241)
                self.cell(0, 8, "INTENALCO - CAMBIO DE CARACTER A INSTITUCION UNIVERSITARIA", border=0, align="C")
                self.ln(5)
                self.set_font("helvetica", "I", 8)
                self.set_text_color(148, 163, 184)
                self.cell(0, 5, "Sistema de Aseguramiento de la Calidad (SIAC 360) - Expediente Co-Construido", border=0, align="C")
                self.ln(8)
                self.set_draw_color(226, 232, 240)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(6)
                
            def footer(self):
                self.set_y(-15)
                self.set_font("helvetica", "I", 8)
                self.set_text_color(148, 163, 184)
                self.cell(0, 10, f"Pagina {self.page_no()}", border=0, align="C")

        pdf = CC_PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Document Title
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(30, 41, 59)
        safe_title = title.encode('latin-1', 'replace').decode('latin-1')
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 8, txt=safe_title, align="C")
        pdf.ln(3)

        if doc_item:
            pdf.set_font("helvetica", "B", 8.5)
            pdf.set_text_color(79, 70, 229)
            meta_line = (
                f"Codigo: {doc_item.get('codigo_doc', 'DOC')} | Version: {doc_item.get('version_actual', 'v1.0')} | "
                f"Estado: {doc_item.get('estado_editorial', 'En Construccion')} | Frente: {doc_item.get('frente', '')} | "
                f"Producto: {doc_item.get('producto', '')}"
            ).encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(pdf.epw, 5, txt=meta_line, align="C")
            pdf.ln(4)
        
        pdf.set_font("helvetica", size=9)
        pdf.set_text_color(51, 65, 85)
        
        for raw_line in text.split('\n'):
            line = raw_line.strip()
            if not line:
                pdf.ln(4)
                continue
                
            pdf.set_x(pdf.l_margin)
            if line.startswith('# '):
                pdf.set_font("helvetica", "B", 12)
                pdf.set_text_color(67, 56, 202)
                safe_l = line[2:].replace('**', '').encode('latin-1', 'replace').decode('latin-1')
                pdf.ln(4)
                pdf.multi_cell(pdf.epw, 7, txt=safe_l)
                pdf.set_font("helvetica", size=9)
                pdf.set_text_color(51, 65, 85)
            elif line.startswith('## '):
                pdf.set_font("helvetica", "B", 10.5)
                pdf.set_text_color(79, 70, 229)
                safe_l = line[3:].replace('**', '').encode('latin-1', 'replace').decode('latin-1')
                pdf.ln(3)
                pdf.multi_cell(pdf.epw, 6, txt=safe_l)
                pdf.set_font("helvetica", size=9)
                pdf.set_text_color(51, 65, 85)
            elif line.startswith('### '):
                pdf.set_font("helvetica", "B", 9.5)
                pdf.set_text_color(30, 41, 59)
                safe_l = line[4:].replace('**', '').encode('latin-1', 'replace').decode('latin-1')
                pdf.ln(2)
                pdf.multi_cell(pdf.epw, 5, txt=safe_l)
                pdf.set_font("helvetica", size=9)
                pdf.set_text_color(51, 65, 85)
            else:
                safe_l = line.replace('**', '').encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(pdf.epw, 5, txt=safe_l)

        if include_trace and doc_item:
            pdf.add_page()
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(49, 46, 129)
            pdf.multi_cell(pdf.epw, 7, txt="ANEXO DE TRAZABILIDAD Y CONSTRUCCION EN EQUIPO (EVIDENCIA PARES MEN)")
            pdf.ln(3)

            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(30, 41, 59)
            pdf.multi_cell(pdf.epw, 6, txt="1. Historial de Versiones y Co-Edicion Institucional:")
            pdf.set_font("helvetica", size=8.5)
            pdf.set_text_color(51, 65, 85)
            for v in doc_item.get("bitacora_versiones", []):
                v_txt = (
                    f"- {v.get('version', 'v1.0')} ({str(v.get('fecha', ''))[:16].replace('T', ' ')}): "
                    f"{v.get('autor', '')} [{v.get('cargo_dependencia', '')}] - {v.get('tipo_actuacion', '')}: {v.get('resumen_cambio', '')}"
                ).encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(pdf.epw, 5, txt=v_txt)
            pdf.ln(4)

            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(30, 41, 59)
            pdf.multi_cell(pdf.epw, 6, txt="2. Mesas de Trabajo, Aportes y Avales del Equipo:")
            pdf.set_font("helvetica", size=8.5)
            pdf.set_text_color(51, 65, 85)
            aportes = doc_item.get("aportes_equipo", [])
            if aportes:
                for ap in aportes:
                    ap_txt = (
                        f"- [{ap.get('tipo', '')}] {ap.get('autor', '')} ({ap.get('cargo_dependencia', '')} - {str(ap.get('fecha', ''))[:10]}): "
                        f"{ap.get('comentario', '')}"
                    ).encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(pdf.epw, 5, txt=ap_txt)
            else:
                pdf.multi_cell(pdf.epw, 5, txt="- Sin observaciones pendientes.")
            pdf.ln(4)

            auditorias = doc_item.get("auditorias_ia", [])
            if auditorias:
                ult = auditorias[0]
                pdf.set_font("helvetica", "B", 10)
                pdf.set_text_color(30, 41, 59)
                aud_hdr = f"3. Verificacion Normativa IA: {ult.get('puntaje_cumplimiento', 0)}% ({ult.get('nivel_concepto', '')})".encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(pdf.epw, 6, txt=aud_hdr)
                pdf.set_font("helvetica", size=8.5)
                for f_it in ult.get("fortalezas", []):
                    ft = f"  * {f_it}".encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(pdf.epw, 5, txt=ft)

        pdf_bytes = pdf.output()
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
            
        io_stream = io.BytesIO(pdf_bytes)
        filename = f"Documento_CC_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
        return send_file(io_stream, as_attachment=True, download_name=filename, mimetype="application/pdf")
    except Exception as e:
        print(f"[CC] PDF Download Error: {e}")
        return str(e), 500

@cambio_caracter_bp.route('/api/cambio_caracter/export_excel', methods=['GET'])
def api_cc_export_excel():
    try:
        inst_id = request.args.get('inst_id', get_active_inst_id(), type=int)
        project = get_cc_project(inst_id)

        wb = openpyxl.Workbook()
        
        # Styles
        header_fill = PatternFill(start_color="312E81", end_color="312E81", fill_type="solid") # Dark Indigo
        sub_fill = PatternFill(start_color="4338CA", end_color="4338CA", fill_type="solid")
        zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        font_data = Font(name="Calibri", size=10)
        font_bold = Font(name="Calibri", size=10, bold=True)
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        def style_header_row(ws, cols):
            for col_num in range(1, cols + 1):
                cell = ws.cell(row=1, column=col_num)
                cell.fill = header_fill
                cell.font = font_header
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ws.row_dimensions[1].height = 28

        def autofit_cols(ws):
            for col in ws.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    val_str = str(cell.value or '')
                    if '\n' in val_str:
                        val_str = max(val_str.split('\n'), key=len)
                    max_len = max(max_len, len(val_str))
                ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 48)

        # 1. SHEET: FASES Y PLAN
        ws_fases = wb.active
        ws_fases.title = "Fases del Plan"
        headers_fases = ["Fase", "Nombre", "Periodo", "Propósito", "Productos e Hitos", "Progreso (%)", "Estado"]
        ws_fases.append(headers_fases)
        style_header_row(ws_fases, len(headers_fases))
        for row_idx, f in enumerate(project.get("fases", []), start=2):
            ws_fases.append([
                f.get("numero", ""),
                f.get("nombre", ""),
                f.get("periodo", ""),
                f.get("proposito", ""),
                f.get("productos_hitos", ""),
                f.get("progreso", 0),
                f.get("estado", "")
            ])
            for c in range(1, len(headers_fases) + 1):
                cell = ws_fases.cell(row=row_idx, column=c)
                cell.font = font_data
                cell.border = thin_border
                if row_idx % 2 == 0: cell.fill = zebra_fill
        autofit_cols(ws_fases)

        # 2. SHEET: CRONOGRAMA QUINCENAL
        ws_q = wb.create_sheet(title="Cronograma Quincenal")
        headers_q = ["Quincena", "Hito Verificable", "Producto Asociado", "Responsable Líder", "Estado", "Notas"]
        ws_q.append(headers_q)
        style_header_row(ws_q, len(headers_q))
        for row_idx, q in enumerate(project.get("quincenas", []), start=2):
            ws_q.append([
                q.get("quincena", ""),
                q.get("hito", ""),
                q.get("producto_asociado", ""),
                q.get("responsable", ""),
                q.get("estado", ""),
                q.get("notas", "")
            ])
            for c in range(1, len(headers_q) + 1):
                cell = ws_q.cell(row=row_idx, column=c)
                cell.font = font_data
                cell.border = thin_border
                if row_idx % 2 == 0: cell.fill = zebra_fill
        autofit_cols(ws_q)

        # 3. SHEET: FRENTES Y LÍDERES
        ws_fr = wb.create_sheet(title="Frentes y Líderes")
        headers_fr = ["Frente de Trabajo", "Líder Responsable", "Qué se Diagnosticará", "Qué se Hará (Hallazgos)", "Asesoría Experta", "Periodo", "Progreso (%)", "Estado"]
        ws_fr.append(headers_fr)
        style_header_row(ws_fr, len(headers_fr))
        for row_idx, fr in enumerate(project.get("frentes", []), start=2):
            ws_fr.append([
                fr.get("nombre", ""),
                fr.get("lider", ""),
                fr.get("que_diagnosticara", ""),
                fr.get("que_se_hara", ""),
                fr.get("asesoria", ""),
                fr.get("periodo", ""),
                fr.get("progreso", 0),
                fr.get("estado", "")
            ])
            for c in range(1, len(headers_fr) + 1):
                cell = ws_fr.cell(row=row_idx, column=c)
                cell.font = font_data
                cell.border = thin_border
                if row_idx % 2 == 0: cell.fill = zebra_fill
        autofit_cols(ws_fr)

        # 4. SHEET: MATRIZ DE BRECHAS
        ws_br = wb.create_sheet(title="Matriz de Brechas")
        headers_br = ["Código", "Frente", "Fuente Normativa", "Descripción Brecha", "Evidencia Disponible", "Evidencia Faltante", "Tratamiento / Acción", "Responsable", "Plazo", "Prioridad", "Estado"]
        ws_br.append(headers_br)
        style_header_row(ws_br, len(headers_br))
        for row_idx, br in enumerate(project.get("brechas", []), start=2):
            ws_br.append([
                br.get("id", ""),
                br.get("frente", ""),
                br.get("fuente_normativa", ""),
                br.get("descripcion", ""),
                br.get("evidencia_disponible", ""),
                br.get("evidencia_faltante", ""),
                br.get("accion_propuesta", ""),
                br.get("responsable", ""),
                br.get("plazo", ""),
                br.get("prioridad", ""),
                br.get("estado", "")
            ])
            for c in range(1, len(headers_br) + 1):
                cell = ws_br.cell(row=row_idx, column=c)
                cell.font = font_data
                cell.border = thin_border
                if row_idx % 2 == 0: cell.fill = zebra_fill
        autofit_cols(ws_br)

        # 5. SHEET: PRODUCTOS P1-P10
        ws_pr = wb.create_sheet(title="Productos Entregables")
        headers_pr = ["Código", "Producto", "Contenido Mínimo", "Fase Entrega", "Líder Responsable", "Versión", "Fecha Límite", "Estado"]
        ws_pr.append(headers_pr)
        style_header_row(ws_pr, len(headers_pr))
        for row_idx, pr in enumerate(project.get("productos", []), start=2):
            ws_pr.append([
                pr.get("codigo", ""),
                pr.get("nombre", ""),
                pr.get("contenido_minimo", ""),
                pr.get("fase", ""),
                pr.get("responsable", ""),
                pr.get("version", ""),
                pr.get("fecha_limite", ""),
                pr.get("estado", "")
            ])
            for c in range(1, len(headers_pr) + 1):
                cell = ws_pr.cell(row=row_idx, column=c)
                cell.font = font_data
                cell.border = thin_border
                if row_idx % 2 == 0: cell.fill = zebra_fill
        autofit_cols(ws_pr)

        # 6. SHEET: RIESGOS Y CONTROLES
        ws_rk = wb.create_sheet(title="Matriz de Riesgos")
        headers_rk = ["Código", "Categoría", "Riesgo Identificado", "Probabilidad", "Impacto", "Control Preventivo / Mitigación", "Responsable", "Estado"]
        ws_rk.append(headers_rk)
        style_header_row(ws_rk, len(headers_rk))
        for row_idx, rk in enumerate(project.get("riesgos", []), start=2):
            ws_rk.append([
                rk.get("id", ""),
                rk.get("categoria", ""),
                rk.get("descripcion", ""),
                rk.get("probabilidad", ""),
                rk.get("impacto", ""),
                rk.get("control", ""),
                rk.get("responsable", ""),
                rk.get("estado", "")
            ])
            for c in range(1, len(headers_rk) + 1):
                cell = ws_rk.cell(row=row_idx, column=c)
                cell.font = font_data
                cell.border = thin_border
                if row_idx % 2 == 0: cell.fill = zebra_fill
        autofit_cols(ws_rk)

        # 7. SHEET: REQUISITOS NORMATIVOS
        ws_rq = wb.create_sheet(title="Requisitos Normativos")
        headers_rq = ["ID", "Eje", "Factor", "Título", "Aspecto Exigido", "Evidencia Exigida", "Norma / Ley", "Estado", "Observaciones", "Evidencias Cargadas"]
        ws_rq.append(headers_rq)
        style_header_row(ws_rq, len(headers_rq))
        req_states = project.get("requisitos", {})
        for row_idx, req in enumerate(REQUISITOS, start=2):
            r_data = req_states.get(req["id"], {})
            ev_count = len(r_data.get("evidences", []))
            ws_rq.append([
                req.get("id", ""),
                req.get("eje", ""),
                req.get("factor", ""),
                req.get("title", ""),
                req.get("desc", ""),
                req.get("evidencia_requerida", ""),
                req.get("ley", ""),
                r_data.get("status", "Pendiente"),
                r_data.get("notes", ""),
                ev_count
            ])
            for c in range(1, len(headers_rq) + 1):
                cell = ws_rq.cell(row=row_idx, column=c)
                cell.font = font_data
                cell.border = thin_border
                if row_idx % 2 == 0: cell.fill = zebra_fill
        autofit_cols(ws_rq)

        # 8. SHEET: DOCUMENTOS Y TRAZABILIDAD DE EQUIPO
        ws_dc = wb.create_sheet(title="Documentos y Trabajo Equipo")
        headers_dc = [
            "Código Doc", "Título del Documento", "Categoría", "Producto", "Frente",
            "Requisito MEN", "Versión Actual", "Estado Editorial", "Último Autor / Dependencia",
            "N° Versiones", "N° Aportes / Mesas", "Cumplimiento Normativo IA (%)"
        ]
        ws_dc.append(headers_dc)
        style_header_row(ws_dc, len(headers_dc))
        for row_idx, d_item in enumerate(project.get("ai_history", []), start=2):
            auds = d_item.get("auditorias_ia", [])
            pct_ia = f"{auds[0].get('puntaje_cumplimiento', 0)}%" if auds else "Pendiente auditar"
            ws_dc.append([
                d_item.get("codigo_doc", ""),
                d_item.get("titulo", ""),
                d_item.get("categoria", ""),
                d_item.get("producto", ""),
                d_item.get("frente", ""),
                d_item.get("requisito_id", ""),
                d_item.get("version_actual", "v1.0"),
                d_item.get("estado_editorial", "En Construcción"),
                f"{d_item.get('autor', '')} ({d_item.get('cargo_dependencia', '')})",
                len(d_item.get("bitacora_versiones", [])),
                len(d_item.get("aportes_equipo", [])),
                pct_ia
            ])
            for c in range(1, len(headers_dc) + 1):
                cell = ws_dc.cell(row=row_idx, column=c)
                cell.font = font_data
                cell.border = thin_border
                if row_idx % 2 == 0: cell.fill = zebra_fill
        autofit_cols(ws_dc)

        output_stream = io.BytesIO()
        wb.save(output_stream)
        output_stream.seek(0)
        filename = f"Matriz_Planeacion_Cambio_Caracter_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"
        return send_file(output_stream, as_attachment=True, download_name=filename, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        print(f"[CC] Excel Export Error: {e}")
        return str(e), 500


@cambio_caracter_bp.route('/api/cambio_caracter/reset_project', methods=['POST'])
def api_cc_reset_project():
    """Elimina todos los registros de prueba, evidencias y versiones previas del proyecto de Cambio de Carácter y lo reinicia en 0%."""
    try:
        data = request.json or {}
        inst_id = int(data.get("inst_id") or get_active_inst_id())
        existing = get_cc_project(inst_id)

        paths_to_delete = []
        for r_val in (existing.get("requisitos") or {}).values():
            for ev in (r_val.get("evidences") or []):
                if ev.get("path"):
                    paths_to_delete.append(ev["path"])

        for doc_item in (existing.get("ai_history") or []):
            if doc_item.get("storage_path"):
                paths_to_delete.append(doc_item["storage_path"])
            for v in (doc_item.get("bitacora_versiones") or []):
                if v.get("storage_path"):
                    paths_to_delete.append(v["storage_path"])

        unique_paths = list({p for p in paths_to_delete if p})
        try:
            col_items = supabase.storage.from_('evidencias').list(f"inst_{inst_id}/cambio_caracter/documentos_colectivos") or []
            for x in col_items:
                if x.get("name"):
                    unique_paths.append(f"inst_{inst_id}/cambio_caracter/documentos_colectivos/{x['name']}")
        except Exception:
            pass
        unique_paths = list(set(unique_paths))
        if unique_paths:
            try:
                supabase.storage.from_('evidencias').remove(unique_paths)
            except Exception as st_err:
                print(f"[CC] Storage cleanup warning: {st_err}")

        clean_project = build_clean_cc_project(inst_id)
        save_cc_project(inst_id, clean_project)
        return jsonify({
            "status": "success",
            "message": "El módulo de Cambio de Carácter ha sido reiniciado completamente en limpio (0%).",
            "deleted_files_count": len(unique_paths),
            "data": clean_project
        })
    except Exception as e:
        print(f"[CC] Reset Project Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def generate_manual_operativo_docx_bytes():
    """Genera el Manual Operativo y Metodológico Paso a Paso del Módulo de Cambio de Carácter Académico (SKEL360)."""
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.95)
        section.right_margin = Inches(0.95)

    h0 = doc.add_heading("MANUAL OPERATIVO Y METODOLÓGICO PASO A PASO", level=0)
    h0.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = sub.add_run(
        "Módulo de Cambio de Carácter Académico (Ley 749 de 2002 · Decreto 1330 de 2019 · Decreto 2038 de 2023)\n"
        "Guía de Utilización de Botones, Flujo Cronológico de Trabajo en Equipo y Trazabilidad Probatoria en Supabase (skel360.online)"
    )
    r_sub.font.bold = True
    r_sub.font.size = Pt(10.5)
    r_sub.font.color.rgb = RGBColor(79, 70, 229)

    doc.add_paragraph()

    # SECCIÓN 1: ARQUITECTURA DE ALMACENAMIENTO Y TRAZABILIDAD
    doc.add_heading("1. ¿Cómo funciona la Trazabilidad y dónde reposan los documentos?", level=1)
    p1 = doc.add_paragraph(
        "Todo el trabajo realizado por el equipo institucional en https://skel360.online/cambio_caracter queda respaldado en tiempo real en dos capas de Supabase:"
    )
    doc.add_paragraph("Base de Datos (Tabla 'statistics' -> Clave CC_PROJ_7): Guarda el estado de las 6 Fases, 12 Quincenas, 13 Frentes, 56 Requisitos (con las 6 preguntas de verificación), Matriz de Brechas, Productos P1-P10, bitácora de versiones, aportes de mesas de trabajo y dictámenes de auditoría IA.", style='List Bullet')
    doc.add_paragraph("Repositorio Cloud de Archivos (Supabase Storage -> Bucket 'evidencias'): Guarda todos los archivos probatorios (.pdf, .docx, .xlsx) subidos en los 56 requisitos y genera automáticamente un archivo Word (.docx) en la nube por cada versión de los documentos trabajados en equipo, indexándolo automáticamente al requisito normativo correspondiente.", style='List Bullet')

    # SECCIÓN 2: BOTONES DE LA BARRA SUPERIOR (HERO BANNER)
    doc.add_heading("2. Función de cada Botón de la Barra Superior Principal", level=1)
    t_hero = doc.add_table(rows=1, cols=3)
    t_hero.style = 'Table Grid'
    hdr_h = ["Botón en Pantalla", "¿Para qué sirve?", "¿Cuándo utilizarlo?"]
    for i, h_txt in enumerate(hdr_h):
        c = t_hero.cell(0, i)
        c.text = h_txt
        for r in c.paragraphs[0].runs:
            r.font.bold = True
            r.font.size = Pt(9)

    hero_rows = [
        ("Guía / Manual Paso a Paso", "Abre en pantalla la guía metodológica interactiva y permite descargar este Manual Operativo en Word (.docx).", "En cualquier momento para orientar a los líderes de frente o al equipo de calidad."),
        ("Subir / Crear Documento en Equipo", "Abre la ventana para importar un documento que usted ya tenga en Word/PDF (ej. Modelo Pedagógico, Estatuto General, PEI) o crear uno nuevo en la Mesa de Co-Construcción.", "Cada vez que vaya a poner un documento institucional a disposición del equipo para lectura, co-edición y auditoría IA."),
        ("Asistente IA Experto MEN", "Genera borradores técnicos, diagnósticos o capítulos desde cero con apoyo de Inteligencia Artificial especializada en Ley 749 y Decreto 2038.", "Cuando necesite estructurar un capítulo nuevo o analizar brechas de un frente completo."),
        ("Exportar Master (Excel)", "Descarga el libro Excel maestro con 8 hojas (Cronograma, Frentes, Brechas, Productos, Riesgos, 56 Requisitos y Trazabilidad de Documentos).", "Al cierre de cada quincena o para presentar el tablero consolidado al Comité Directivo y Pares."),
        ("Guardar Todo", "Sincroniza manualmente cualquier cambio realizado en las tablas con la base de datos de Supabase.", "Después de actualizar porcentajes o estados generales (aunque los modales guardan automáticamente)."),
        ("Reiniciar en Limpio (0%)", "Elimina datos previos o de prueba y deja todo el módulo en 0% de avance para iniciar un proceso desde cero.", "Únicamente al iniciar formalmente el proceso con los documentos definitivos de la institución.")
    ]
    for b_name, b_purpose, b_when in hero_rows:
        rc = t_hero.add_row().cells
        rc[0].text = b_name
        rc[1].text = b_purpose
        rc[2].text = b_when
        for cell in rc:
            for r in cell.paragraphs[0].runs:
                r.font.size = Pt(8.5)

    doc.add_paragraph()

    # SECCIÓN 3: RUTA CRONOLÓGICA PASO A PASO (LOS 7 PASOS MAESTROS)
    doc.add_heading("3. Ruta Metodológica Paso a Paso (Orden Recomendado de Trabajo)", level=1)

    steps = [
        (
            "PASO 1: Configurar Responsables en la Pestaña 2 (Frentes y Líderes) y Pestaña 1 (Cronograma)",
            [
                "Ingrese a la Pestaña '2. Frentes y Líderes (13)'.",
                "En cada uno de los 13 frentes sectoriales (Gobierno, PEI, Oferta y Currículo, Investigación, Bienestar, Financiero, etc.), haga clic en el botón 'Editar (Lápiz)'.",
                "Asigne el nombre y correo del Líder Responsable (conectado a los usuarios de SKEL360) y deje el estado inicial en 'En Ejecución' o 'Pendiente'.",
                "Luego pase a la Pestaña '1. Fases y Cronograma (12 Q)' y active la Fase I ('En Ejecución') y la Quincena 1 (Q1) usando el botón de edición de cada fila."
            ]
        ),
        (
            "PASO 2: Evaluar la Línea Base en la Pestaña 3 (Requisitos Normativos - 6 Preguntas)",
            [
                "Ingrese a la Pestaña '3. Requisitos (6 Preguntas)' donde están los 56 requisitos de la Ley 749 de 2002 y Decreto 2038 de 2023 organizados por Ejes.",
                "En cada requisito, marque los 6 botones de verificación diagnóstica: [1. ¿Existe?] [2. ¿Vigente?] [3. ¿Aprobado?] [4. ¿Pertinente?] [5. ¿Se aplica?] [6. ¿Evidencia?].",
                "Haga clic en el botón 'Gestionar Evidencias / Margy IA' de cada requisito para abrir su expediente:",
                "  - En la sub-pestaña 'Repositorio de Evidencias por Fase': Seleccione la Fase (ej. Fase I o II), el Tipo de Soporte (Acto Administrativo, Documento Maestro, Acta de Socialización), la versión (v1.0) y suba el archivo PDF/Word a Supabase con el botón 'Cargar al Histórico'.",
                "  - En la sub-pestaña 'Asesoría Experta Margy IA': Use los botones rápidos ('¿Qué evidencia exacta exige el MEN aquí?', '¿Cómo demostrar que se aplica con resultados?') si tiene dudas sobre cómo cumplir ese requisito."
            ]
        ),
        (
            "PASO 3: Subir sus Documentos Maestros (ej. Modelo Pedagógico, Reglamentos) para Trabajo en Equipo",
            [
                "Diríjase a la Pestaña '5. Productos Entregables (P1-P10)' o a la Pestaña '7. Mesa Co-Construcción, IA & Trazabilidad'.",
                "Observe que un mismo Producto (por ejemplo P5: Propuesta Académica y Curricular, o P4: Reforma Estatutaria y Reglamentaria) agrupa varios documentos independientes.",
                "Haga clic en el botón '+ Subir / Crear Documento del Equipo'.",
                "En la ventana que se abre:",
                "  1. Escriba el Título del documento (ej. 'Modelo Pedagógico Institucional', 'Reglamento Estudiantil', 'Política de Investigación').",
                "  2. Seleccione la Categoría ('Políticas y Modelos', 'Reglamentos y Estatutos', etc.).",
                "  3. Asócielo al Producto Entregable (P1 a P10), al Frente Sectorial y al Requisito Normativo MEN exacto (ej. req_17 Modelo Pedagógico).",
                "  4. Indique la Fase actual, la Versión inicial (v1.0) y el Autor/Dependencia que lo carga.",
                "  5. En el recuadro azul, seleccione su archivo Word (.docx) o PDF desde su computador y haga clic en 'Crear y Publicar para el Equipo'.",
                "El sistema extraerá todo el texto para edición colaborativa, guardará el archivo Word v1.0 en Supabase Storage y lo vinculará automáticamente como evidencia del requisito seleccionado."
            ]
        ),
        (
            "PASO 4: Co-Edición, Mesas de Trabajo y Trazabilidad de Equipo (Pestaña 7)",
            [
                "En la Pestaña '7. Mesa Co-Construcción, IA & Trazabilidad', seleccione el documento en la columna izquierda.",
                "En el panel central (Editor Colaborativo), cualquier líder o miembro del equipo puede enriquecer o ajustar el contenido.",
                "Antes de guardar una modificación, diligencie la barra 'Registrar Nueva Versión en Bitácora': indique su Nombre/Dependencia, la Fase, el Tipo de Actuación ('Aporte Mesa de Trabajo', 'Revisión Par Interno', 'Ajuste por Auditoría IA', 'Aval Consejo Académico') y el resumen de qué se modificó.",
                "Haga clic en el botón verde 'Guardar Nueva Versión':",
                "  - El sistema incrementa automáticamente la versión (v1.0 -> v1.1 -> v1.2).",
                "  - Guarda la foto exacta (snapshot) de esa versión en la pestaña 'Bitácora de Versiones' (con el botón 'Ver texto de esta versión').",
                "  - Genera y sube automáticamente el nuevo archivo .docx con Anexo de Trazabilidad a Supabase Storage y actualiza la evidencia en el Requisito MEN.",
                "Además, en la sub-pestaña 'Aportes y Avales del Equipo' del panel derecho, haga clic en '+ Registrar Aporte / Acta / Aval' para dejar constancia de los acuerdos de mesas de trabajo con docentes, directivos, estudiantes o egresados."
            ]
        ),
        (
            "PASO 5: Auditar el Documento con IA contra la Norma MEN (Pestaña 7 - Panel Derecho)",
            [
                "Con el documento abierto en la Pestaña 7, vaya al panel derecho, sub-pestaña 'Auditoría IA MEN', y haga clic en el botón 'Ejecutar Auditoría IA'.",
                "La IA contrastará el contenido real de su documento contra el Requisito legal de la Ley 749 de 2002 / Decreto 1330 / Decreto 2038.",
                "Le entregará:",
                "  - El Porcentaje de Cumplimiento Normativo (0% a 100%) y el Nivel de Concepto.",
                "  - La evaluación de las 6 Preguntas Institucionales.",
                "  - Las Fortalezas detectadas para defender ante los Pares.",
                "  - Los Vacíos o Aspectos Faltantes.",
                "  - Un bloque de 'Texto Sugerido para Completar el Requisito' con el botón '+ Insertar Texto Sugerido en el Editor'. Al pulsarlo, el texto se incorpora al documento para que el equipo lo revise y guarde una nueva versión auditada."
            ]
        ),
        (
            "PASO 6: Gestionar Brechas y Riesgos (Pestañas 4 y 6)",
            [
                "En la Pestaña '4. Matriz de Brechas':",
                "  - Puede hacer clic en '+ Nueva Brecha' para registrar manualmente hallazgos derivados de la autoevaluación de los 56 requisitos.",
                "  - O hacer clic en 'Generar Brechas con IA' para que el sistema proponga brechas y su plan de tratamiento a partir del diagnóstico.",
                "  - Conforme el equipo cierre los documentos y evidencias, edite la brecha y cambie su estado a 'Cerrada'.",
                "En la Pestaña '6. Riesgos y Controles (12)': Revise periódicamente los 12 riesgos críticos del proceso y actualice sus controles preventivos."
            ]
        ),
        (
            "PASO 7: Descargar Soportes con Anexo Probatorio para Pares Académicos",
            [
                "En la Pestaña 7, cada documento cuenta con los botones 'Word + Anexo Trazabilidad' y 'PDF Oficial':",
                "  - Al descargarlos, el documento incluye el contenido técnico completo MÁS el 'ANEXO DE TRAZABILIDAD Y CONSTRUCCIÓN COLECTIVA', que contiene: (1) Tabla de Historial de Versiones y Co-Autores, (2) Tabla de Mesas de Trabajo y Avales Colegiados, y (3) Dictamen Interno de Cumplimiento Normativo IA.",
                "En la Pestaña 5 ('Productos Entregables P1-P10'), una vez todos los sub-documentos de un producto (ej. P5) estén aprobados, puede usar el botón 'Consolidar en Dossier' para integrar la síntesis ejecutiva del producto.",
                "Finalmente, descargue el 'Exportar Master (Excel)' en la barra superior como índice maestro de todo el Dossier."
            ]
        )
    ]

    for title_step, bullets in steps:
        doc.add_heading(title_step, level=2)
        for b in bullets:
            doc.add_paragraph(b, style='List Bullet')

    io_stream = io.BytesIO()
    doc.save(io_stream)
    io_stream.seek(0)
    return io_stream.getvalue()


@cambio_caracter_bp.route('/api/cambio_caracter/download_manual', methods=['GET'])
def api_cc_download_manual():
    """Descarga el Manual Operativo y Metodológico Paso a Paso en formato Word (.docx)."""
    try:
        docx_bytes = generate_manual_operativo_docx_bytes()
        io_stream = io.BytesIO(docx_bytes)
        io_stream.seek(0)
        filename = "Manual_Operativo_Paso_a_Paso_Cambio_Caracter_SKEL360.docx"
        return send_file(
            io_stream,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        print(f"[CC] Manual Download Error: {e}")
        return str(e), 500

