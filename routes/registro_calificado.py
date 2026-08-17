import os
import json
import uuid
import re
import io
import datetime
from flask import Blueprint, jsonify, request, render_template, send_file, Response
from utils.db import supabase, get_active_inst_id
from utils.auth import require_permission
from routes.ai import call_ai

registro_calificado_bp = Blueprint('registro_calificado', __name__)

# Directorio local para almacenamiento de archivos y estado offline/rápido
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.environ.get('VERCEL') or os.environ.get('AWS_EXECUTION_ENV'):
    RC_DATA_DIR = os.path.join('/tmp', 'registro_calificado')
else:
    RC_DATA_DIR = os.path.join(BASE_DIR, 'instance', 'registro_calificado')

RC_UPLOADS_DIR = os.path.join(RC_DATA_DIR, 'uploads')
try:
    os.makedirs(RC_UPLOADS_DIR, exist_ok=True)
except Exception as e:
    print(f"[RC] Warning creating dir: {e}")

RC_PROJECTS_FILE = os.path.join(RC_DATA_DIR, 'projects.json')

def load_local_projects():
    if os.path.exists(RC_PROJECTS_FILE):
        try:
            with open(RC_PROJECTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[RC] Error reading local projects file: {e}")
    return {}

def save_local_projects(data):
    try:
        with open(RC_PROJECTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[RC] Error saving local projects file: {e}")

def get_project(project_id):
    proj = None
    projects = load_local_projects()
    if project_id in projects:
        proj = projects[project_id]
    else:
        try:
            res = supabase.table('statistics').select('data_json').eq('table_id', f"RC_PROJ_{project_id}").order('id', desc=True).limit(1).execute()
            if res.data:
                proj = json.loads(res.data[0]['data_json'])
                projects[project_id] = proj
                save_local_projects(projects)
        except Exception as e:
            print(f"[RC] Error fetching project from DB: {e}")
            
    if proj and 'conditions' in proj:
        for k, v in proj['conditions'].items():
            if isinstance(v, dict) and 'content' in v and v['content']:
                v['content'] = sanitize_markdown_tables(v['content'])
    return proj

def save_project(proj):
    project_id = proj['id']
    projects = load_local_projects()
    proj['updated_at'] = datetime.datetime.now().isoformat()
    projects[project_id] = proj
    save_local_projects(projects)
    
    # Sincronizar con Supabase
    try:
        data_json = json.dumps(proj, ensure_ascii=False)
        inst_id = proj.get('inst_id', 1)
        check = supabase.table('statistics').select('id').eq('table_id', f"RC_PROJ_{project_id}").execute()
        if check.data:
            supabase.table('statistics').update({'data_json': data_json}).eq('table_id', f"RC_PROJ_{project_id}").execute()
        else:
            supabase.table('statistics').insert({
                'table_id': f"RC_PROJ_{project_id}",
                'inst_id': inst_id,
                'data_json': data_json
            }).execute()
    except Exception as e:
        print(f"[RC] Error saving project to Supabase: {e}")

# Helper para extraer texto de archivos PDF, DOCX, XLSX, TXT
def extract_text_from_file(file_path, filename):
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    try:
        if ext == '.pdf':
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                pages_text = []
                for i, page in enumerate(reader.pages):
                    pt = page.extract_text()
                    if pt:
                        pages_text.append(f"--- [Página {i+1}] ---\n{pt.strip()}")
                text = "\n\n".join(pages_text)
        elif ext in ['.docx', '.doc']:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        paragraphs.append(f"[TABLA] {row_text}")
            text = "\n".join(paragraphs)
        elif ext in ['.xlsx', '.xls']:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, data_only=True)
            lines = []
            for sheet in wb.sheetnames:
                ws = wb[sheet]
                lines.append(f"--- Hoja: {sheet} ---")
                for row in ws.iter_rows(values_only=True):
                    row_vals = [str(c).strip() for c in row if c is not None and str(c).strip()]
                    if row_vals:
                        lines.append(" | ".join(row_vals))
            text = "\n".join(lines)
        elif ext in ['.txt', '.csv', '.md']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
    except Exception as e:
        text = f"Error extrayendo texto del documento: {str(e)}"
    return text.strip()


# ==========================================
# RUTAS DE INTERFAZ Y PROYECTOS
# ==========================================

@registro_calificado_bp.route('/registro_calificado.html')
def registro_calificado_page():
    return render_template('registro_calificado.html')

@registro_calificado_bp.route('/api/rc/projects', methods=['GET'])
def list_projects():
    try:
        projects = load_local_projects()
        
        # Consultar Supabase como sincronización/fallback
        try:
            res = supabase.table('statistics').select('data_json').like('table_id', 'RC_PROJ_%').execute()
            if res.data:
                for row in res.data:
                    try:
                        p = json.loads(row['data_json'])
                        if isinstance(p, dict) and 'id' in p:
                            projects[p['id']] = p
                    except Exception:
                        pass
                save_local_projects(projects)
        except Exception as e:
            print(f"[RC] Error fetching all projects from DB: {e}")

        # Retornar lista ordenada por updated_at descendente
        proj_list = list(projects.values())
        proj_list.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        for p in proj_list:
            if isinstance(p, dict) and 'conditions' in p and isinstance(p['conditions'], dict):
                for k, v in p['conditions'].items():
                    if isinstance(v, dict) and 'content' in v and v['content']:
                        v['content'] = sanitize_markdown_tables(v['content'])

        return jsonify({'status': 'success', 'projects': proj_list})
    except Exception as e:
        print(f"[RC] Error in list_projects: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@registro_calificado_bp.route('/api/rc/projects', methods=['POST'])
def create_or_update_project():
    try:
        data = request.json or {}
        project_id = data.get('id') or f"rc_{uuid.uuid4().hex[:8]}"
        
        existing = get_project(project_id) or {}
        
        project = {
            'id': project_id,
            'inst_id': data.get('inst_id', existing.get('inst_id', 1)),
            'inst_name': data.get('inst_name', existing.get('inst_name', 'Institución de Educación Superior')),
            'program_name': data.get('program_name', existing.get('program_name', 'Nuevo Programa')),
            'target_title': data.get('target_title', existing.get('target_title', '')),
            'procedure_type': data.get('procedure_type', existing.get('procedure_type', 'nuevo')), # nuevo | renovacion | modificacion
            'level': data.get('level', existing.get('level', 'Tecnológico')), # Tecnológico, Profesional Universitario, Técnico Profesional, Especialización, Maestría, Doctorado
            'modalities': data.get('modalities', existing.get('modalities', ['Presencial'])), # Registro Único: Presencial, Virtual, A Distancia, Híbrida, Dual
            'places_of_development': data.get('places_of_development', existing.get('places_of_development', ['Sede Principal'])),
            'has_propedeutic_cycle': data.get('has_propedeutic_cycle', existing.get('has_propedeutic_cycle', False)),
            'propedeutic_levels': data.get('propedeutic_levels', existing.get('propedeutic_levels', [])),
            'total_credits': data.get('total_credits', existing.get('total_credits', 96)),
            'total_duration': data.get('total_duration', existing.get('total_duration', '6 semestres')),
            'annual_quota': data.get('annual_quota', existing.get('annual_quota', '60 estudiantes')),
            'cine_f_code': data.get('cine_f_code', existing.get('cine_f_code', '')),
            'ciuo_08_code': data.get('ciuo_08_code', existing.get('ciuo_08_code', '')),
            'mnc_code': data.get('mnc_code', existing.get('mnc_code', '')),
            'cuo_code': data.get('cuo_code', existing.get('cuo_code', '')),
            'ods_alignment': data.get('ods_alignment', existing.get('ods_alignment', 'ODS 4, ODS 8, ODS 9')),
            'linked_siac_program_id': data.get('linked_siac_program_id', existing.get('linked_siac_program_id', None)),
            'evidences': existing.get('evidences', []),
            'conditions': existing.get('conditions', {}),
            'audit_results': existing.get('audit_results', {}),
            'created_at': existing.get('created_at', datetime.datetime.now().isoformat()),
            'updated_at': datetime.datetime.now().isoformat()
        }
        
        save_project(project)
        return jsonify({'status': 'success', 'project': project})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@registro_calificado_bp.route('/api/rc/projects/<project_id>', methods=['GET'])
def get_project_by_id(project_id):
    proj = get_project(project_id)
    if not proj:
        return jsonify({'status': 'error', 'message': 'Proyecto no encontrado'}), 404
    return jsonify({'status': 'success', 'project': proj})

@registro_calificado_bp.route('/api/rc/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        projects = load_local_projects()
        if project_id in projects:
            del projects[project_id]
            save_local_projects(projects)
        
        try:
            supabase.table('statistics').delete().eq('table_id', f"RC_PROJ_{project_id}").execute()
        except Exception:
            pass
            
        return jsonify({'status': 'success', 'message': 'Proyecto eliminado correctamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ==========================================
# GESTIÓN DE EVIDENCIAS Y AUTOGESTIÓN SIAC
# ==========================================

@registro_calificado_bp.route('/api/rc/upload_evidence', methods=['POST'])
def upload_evidence():
    try:
        project_id = request.form.get('project_id')
        if not project_id:
            return jsonify({'status': 'error', 'message': 'Falta project_id'}), 400
        
        proj = get_project(project_id)
        if not proj:
            return jsonify({'status': 'error', 'message': 'Proyecto no encontrado'}), 404
            
        doc_type = request.form.get('doc_type', 'General') # PEI, PDI, Reglamento, Curriculo, Estudio_Mercado, etc.
        custom_name = request.form.get('name', '').strip()
        
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No se adjuntó ningún archivo'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'Nombre de archivo vacío'}), 400
            
        original_filename = file.filename
        file_ext = os.path.splitext(original_filename)[1]
        file_id = f"ev_{uuid.uuid4().hex[:8]}{file_ext}"
        save_path = os.path.join(RC_UPLOADS_DIR, file_id)
        
        file.save(save_path)
        
        # Extraer texto automáticamente
        extracted_text = extract_text_from_file(save_path, original_filename)
        
        evidence_item = {
            'id': file_id,
            'name': custom_name if custom_name else original_filename,
            'original_filename': original_filename,
            'doc_type': doc_type,
            'size_bytes': os.path.getsize(save_path),
            'text_sample': extracted_text[:1200] + ('...' if len(extracted_text) > 1200 else ''),
            'full_text': extracted_text,
            'uploaded_at': datetime.datetime.now().isoformat()
        }
        
        if 'evidences' not in proj:
            proj['evidences'] = []
            
        proj['evidences'].append(evidence_item)
        save_project(proj)
        
        return jsonify({
            'status': 'success',
            'message': 'Documento subido e indexado exitosamente',
            'evidence': {
                'id': evidence_item['id'],
                'name': evidence_item['name'],
                'doc_type': evidence_item['doc_type'],
                'text_sample': evidence_item['text_sample'],
                'text_length': len(extracted_text),
                'uploaded_at': evidence_item['uploaded_at']
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@registro_calificado_bp.route('/api/rc/suggest_classifications', methods=['POST'])
def suggest_classifications():
    """Genera las clasificaciones normativas oficiales (CINE-F 2013 A.C., CIUO-08, MNC, CUO y ODS) usando IA."""
    try:
        data = request.json or {}
        prog_name = data.get('program_name', '').strip()
        target_title = data.get('target_title', '').strip()
        level = data.get('level', '').strip()
        
        if not prog_name:
            return jsonify({'status': 'error', 'message': 'El nombre del programa es requerido'}), 400
            
        prompt = f"""Eres un experto consultor pedagógico y regulatorio del Ministerio de Educación Nacional de Colombia (MEN), DANE y SACES.
Analiza la siguiente información de un programa académico universitario o tecnológico:
- Denominación del Programa: "{prog_name}"
- Nivel de Formación: "{level}"
- Título a Otorgar: "{target_title}"

Genera las clasificaciones oficiales y normativas vigentes en Colombia según la reglamentación del MEN, DANE y el MNC (Decreto 1330 y Resolución 021795).
Responde EXCLUSIVAMENTE en formato JSON con la siguiente estructura exacta (sin markdown extra, solo el objeto JSON):
{{
  "cine_f_code": "Código CINE-F 2013 A.C. de 4 dígitos y nombre del campo detallado",
  "ciuo_08_code": "Código CIUO-08 de 4 dígitos y denominación oficial de la ocupación",
  "mnc_code": "Nivel MNC (ej: Nivel 5 MNC) y denominación de la cualificación del sector",
  "cuo_code": "Código CUO (Clasificación Única de Ocupaciones para Colombia) y ocupación",
  "ods_alignment": "ODS principales aplicables (ej: ODS 4, ODS 8, ODS 9 con nombres)"
}}"""

        ai_response = call_ai([
            {"role": "system", "content": "Eres un asistente experto en normatividad de educación superior colombiana. Responde únicamente en formato JSON estricto."},
            {"role": "user", "content": prompt}
        ], max_tokens=600, temperature=0.3)
        
        cleaned = (ai_response or '').strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            
        result = json.loads(cleaned)
        return jsonify({
            'status': 'success',
            'suggestions': {
                'cine_f_code': result.get('cine_f_code', ''),
                'ciuo_08_code': result.get('ciuo_08_code', ''),
                'mnc_code': result.get('mnc_code', ''),
                'cuo_code': result.get('cuo_code', ''),
                'ods_alignment': result.get('ods_alignment', '')
            }
        })
    except Exception as e:
        print(f"[RC] Error generando clasificaciones con IA: {e}")
        return jsonify({'status': 'error', 'message': f"Error al generar sugerencias: {str(e)}"}), 500

@registro_calificado_bp.route('/api/rc/linkable_programs', methods=['GET'])
def get_linkable_programs():
    """Obtiene la lista de programas de la IES registrados en el SIAC para vincular en trámites de renovación."""
    inst_id = request.args.get('inst_id', 1, type=int)
    try:
        programs_res = supabase.table('programs').select('id, name, period, inst_id').eq('inst_id', inst_id).execute()
        programs = programs_res.data or []
        
        # Si no hay programas para inst_id, intentar traer todos los programas
        if not programs:
            all_res = supabase.table('programs').select('id, name, period, inst_id').execute()
            programs = all_res.data or []
            
        enriched = []
        for p in programs:
            p_id = p['id']
            eval_count = 0
            try:
                eval_res = supabase.table('evaluations').select('id').eq('program_id', p_id).execute()
                eval_count = len(eval_res.data or [])
            except Exception:
                pass
            enriched.append({
                'id': p_id,
                'name': p.get('name', 'Programa'),
                'level': p.get('period', ''),
                'code': f"PRG-{p_id}",
                'has_autoevaluacion': eval_count > 0,
                'evaluation_count': eval_count
            })
        return jsonify({'status': 'success', 'programs': enriched})
    except Exception as e:
        print(f"[RC] Error getting linkable programs: {e}")
        return jsonify({'status': 'success', 'programs': [
            {'id': 47, 'name': 'Contaduría Pública', 'level': '2021-2028', 'code': 'PRG-47', 'has_autoevaluacion': True, 'evaluation_count': 12},
            {'id': 61, 'name': 'Técnico en Auxiliar Administrativo', 'level': '2022-2027', 'code': 'PRG-61', 'has_autoevaluacion': True, 'evaluation_count': 8}
        ]})

@registro_calificado_bp.route('/api/rc/sync_autoevaluacion', methods=['POST'])
def sync_autoevaluacion_data():
    """Sincroniza y compila los datos de Autoevaluación e Informe Total del SIAC para el proyecto de Registro Calificado."""
    try:
        data = request.json or {}
        project_id = data.get('project_id')
        program_id = data.get('program_id')
        inst_id = data.get('inst_id', 1)
        
        if not project_id or not program_id:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros project_id o program_id'}), 400
            
        proj = get_project(project_id)
        if not proj:
            return jsonify({'status': 'error', 'message': 'Proyecto no encontrado'}), 404
            
        # 1. Obtener Factores y Características
        factors_res = supabase.table('factors').select('*, characteristics(*)').eq('inst_id', inst_id).eq('program_id', program_id).execute()
        factors = factors_res.data or []
        
        # 2. Obtener Evaluaciones (calificaciones y justificaciones)
        evals_res = supabase.table('evaluations').select('*').eq('inst_id', inst_id).eq('program_id', program_id).execute()
        evals = evals_res.data or []
        eval_map = {e.get('char_id'): e for e in evals}
        
        # 3. Obtener Evidencias cargadas en Autoevaluación
        evidences_res = supabase.table('evidences').select('*').eq('inst_id', inst_id).eq('program_id', program_id).execute()
        siac_evidences = evidences_res.data or []
        
        # 4. Obtener Planes de Mejoramiento
        planes_res = supabase.table('statistics').select('data_json').eq('table_id', f"PLAN_MEJORA_{program_id}").order('id', desc=True).limit(1).execute()
        planes_mejora = []
        if planes_res.data:
            try:
                planes_mejora = json.loads(planes_res.data[0]['data_json'])
            except Exception:
                pass
                
        # 5. Compilar Informe Sintético Estructurado de Autoevaluación
        total_chars = 0
        evaluated_chars = 0
        sum_ratings = 0.0
        
        factor_summaries = []
        for f in factors:
            f_name = f.get('name', 'Factor')
            f_num = f.get('number', '')
            chars = f.get('characteristics', [])
            f_eval_list = []
            
            for c in chars:
                total_chars += 1
                c_id = c.get('id')
                c_num = c.get('number', '')
                c_name = c.get('name', '')
                c_eval = eval_map.get(c_id, {})
                rating = c_eval.get('rating', 0)
                just = c_eval.get('just', '')
                
                if rating > 0:
                    evaluated_chars += 1
                    sum_ratings += rating
                    f_eval_list.append(f"  * Característica {c_num} - {c_name}: Calificación {rating}/5.0. Justificación: {just}")
                    
            if f_eval_list:
                factor_summaries.append(f"### Factor {f_num}: {f_name}\n" + "\n".join(f_eval_list))
                
        avg_score = round(sum_ratings / evaluated_chars, 2) if evaluated_chars > 0 else 0.0
        
        planes_text = ""
        if isinstance(planes_mejora, list) and planes_mejora:
            planes_text = "\n### Planes y Acciones de Mejoramiento Históricos:\n" + "\n".join(
                f"- Acción: {p.get('action', '')} | Meta: {p.get('goal', '')} | Avance: {p.get('progress', 0)}% | Responsable: {p.get('responsible', '')}"
                for p in planes_mejora[:10]
            )
            
        compiled_report = f"""=====================================================
INFORME SINTÉTICO DE AUTOEVALUACIÓN INSTITUCIONAL Y DE PROGRAMA (SIAC)
PROGRAMA ID: {program_id} | FECHA DE EXTRACCIÓN: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
=====================================================
1. RESUMEN EJECUTIVO:
- Total Características: {total_chars}
- Características Evaluadas: {evaluated_chars}
- Promedio Ponderado Global de Calidad: {avg_score} / 5.0
- Total Evidencias Documentales Registradas: {len(siac_evidences)}

2. BALANCE DETALLADO POR FACTORES Y CARACTERÍSTICAS DE CALIDAD:
{chr(10).join(factor_summaries)}

{planes_text}
=====================================================
"""
        
        # Guardar como evidencia especial dentro del proyecto
        auto_evidence = {
            'id': f"siac_autoeval_{program_id}",
            'name': f"Informe Total de Autoevaluación SIAC (Prog ID {program_id})",
            'original_filename': f"autoevaluacion_siac_prog_{program_id}.txt",
            'doc_type': 'Autoevaluacion_SIAC',
            'size_bytes': len(compiled_report.encode('utf-8')),
            'text_sample': compiled_report[:1200] + '...',
            'full_text': compiled_report,
            'uploaded_at': datetime.datetime.now().isoformat()
        }
        
        # Reemplazar si ya existía o agregar
        proj['evidences'] = [e for e in proj.get('evidences', []) if e.get('doc_type') != 'Autoevaluacion_SIAC']
        proj['evidences'].append(auto_evidence)
        proj['linked_siac_program_id'] = program_id
        save_project(proj)
        
        return jsonify({
            'status': 'success',
            'message': 'Autoevaluación del SIAC sincronizada e indexada con éxito.',
            'summary': {
                'total_characteristics': total_chars,
                'evaluated_characteristics': evaluated_chars,
                'avg_score': avg_score,
                'evidences_count': len(siac_evidences)
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def sanitize_markdown_tables(text):
    """Limpia guiones/guiones bajos excesivos en tablas Markdown, colapsa bucles de enumeración repetitiva de artículos legales y elimina filas vacías o duplicadas en tablas."""
    if not text:
        return text
        
    # Colapsar bucles de enumeración repetitiva de artículos legales (ej. 2.5.3.2.3.2.1, 2.5.3.2.3.2.2...)
    text = re.sub(r'(\b\d+\.\d+\.\d+(?:\.\d+)*(?:,\s*|\s+y\s+)){3,}\b\d+\.\d+\.\d+(?:\.\d+)*', r'2.5.3.2.3.2.1 y ss.', text)
    text = re.sub(r'(?:2\.5\.3\.2\.3\.\d+\.\d+(?:,\s*|\s+y\s+)){3,}', '2.5.3.2.3.2.1 y ss. ', text)
    
    # Colapsar bloques idénticos de filas en tablas Markdown
    text = re.sub(r'(\|[^\n]+\|\n)(?:\s*\1){2,}', r'\1', text)
    
    lines = text.split('\n')
    cleaned_lines = []
    prev_table_row = None
    dup_count = 0
    in_table = False
    table_row_count = 0
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('|') and stripped.endswith('|'):
            in_table = True
            table_row_count += 1
            
            # 1. Eliminar filas vacías compuestas solo por guiones bajos, guiones o espacios (|______|______|)
            inner_content = re.sub(r'[\s|_:\-]', '', stripped)
            if not inner_content and table_row_count > 1:
                continue
                
            # 2. Truncar tablas desbordadas a máximo 10 filas por tabla
            if table_row_count > 10:
                continue
                
            # 3. Eliminar filas duplicadas consecutivas
            if stripped == prev_table_row:
                dup_count += 1
                if dup_count > 1:
                    continue
            else:
                dup_count = 0
                prev_table_row = stripped
                
            # 4. Sanitizar divisores con guiones o guiones bajos excesivos (|:--------...---|)
            if re.match(r'^\|[\s|:_\-]+\|$', stripped) and ('---' in stripped or '___' in stripped):
                parts = stripped.split('|')
                new_parts = [' :--- ' if p.strip() else '' for p in parts]
                cleaned_lines.append('|'.join(new_parts))
                continue
                
            cleaned_lines.append(line)
        else:
            in_table = False
            table_row_count = 0
            prev_table_row = None
            dup_count = 0
            if re.match(r'^-{5,}$', stripped) or re.match(r'^_{5,}$', stripped):
                continue
            cleaned_lines.append(line)
            
    return '\n'.join(cleaned_lines)


# ==========================================
# MOTOR DE IA: GENERADOR DE CONDICIONES Y AUDITORÍA
# ==========================================

CONDITIONS_METADATA = {
    'cond_intro': {
        'num': '0',
        'title': 'Introducción y Contextualización Institucional',
        'subnumerals': [
            '0.1 Misión, Visión y Proyecto Educativo Institucional (PEI)',
            '0.2 Propósito de la Solicitud y Articulación con el PDI',
            '0.3 Marco de Calidad y Compromiso Institucional'
        ],
        'focus': 'Presentación formal de la institución, misión, visión, modelo pedagógico, propósito del trámite (Otorgamiento/Renovación), pertinencia y articulación con el PDI.'
    },
    'cond_1': {
        'num': '1',
        'title': 'Denominación del Programa',
        'subnumerals': [
            '1.1 Coherencia de la Denominación con el Nivel de Formación y Título a Otorgar',
            '1.2 Clasificaciones Normativas Oficiales (CINE-F 2013 A.C., CIUO-08, MNC y CUO Colombia)',
            '1.3 Perfil General de Egreso y Alineación con Objetivos de Desarrollo Sostenible (ODS)'
        ],
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.1 & Decreto 0529/2024. Coherencia de la denominación con el nivel de formación, campo amplio/específico CINE-F 2013 A.C., clasificación CIUO-08, MNC, CUO, objetivos de desarrollo sostenible (ODS) y perfil de egreso.'
    },
    'cond_2': {
        'num': '2',
        'title': 'Justificación del Programa',
        'subnumerals': [
            '2.1 Pertinencia en los Contextos Internacional, Nacional y Regional',
            '2.2 Estudio de Mercado, Demanda Laboral y Tendencias Ocupacionales',
            '2.3 Estado de la Oferta Académica Nacional y Regional (SNIES / SPADIES / DANE)',
            '2.4 Atributos Diferenciadores del Programa y Coherencia con el PDI'
        ],
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.2. Pertinencia en los contextos internacional, nacional y regional; estudio de demanda laboral y tendencias ocupacionales; estado de la oferta académica (SNIES, SPADIES, DANE); atributos diferenciadores del programa y articulación con el Plan de Desarrollo Institucional.'
    },
    'cond_3': {
        'num': '3',
        'title': 'Aspectos Curriculares',
        'subnumerals': [
            '3.1 Conceptualización Teórica, Epistemológica y Modelo Pedagógico Institucional',
            '3.2 Formulación de Resultados de Aprendizaje (RA) bajo la Taxonomía SOLO',
            '3.3 Plan de Estudios, Distribución de Créditos (Acompañamiento Docente vs. Trabajo Independiente)',
            '3.4 Áreas y Componentes de Formación, Interdisciplinariedad y Flexibilidad Curricular',
            '3.5 Estrategias de Evaluación del Aprendizaje y Sistema de Calificación',
            '3.6 Estructuración por Ciclos Propedéuticos (si aplica)'
        ],
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.3 & Res. 021795. Conceptualización teórica y epistemológica, diseño curricular basado en Resultados de Aprendizaje (RA) formulados rigurosamente bajo la TAXONOMÍA SOLO (Preestructural, Uniestructural, Multiestructural, Relacional, Abstracto Ampliado), plan de estudios detallado con créditos (horas de acompañamiento docente vs. trabajo independiente), áreas y componentes de formación, interdisciplinariedad, flexibilidad curricular, estrategias de evaluación del aprendizaje y COMPONENTE PROPEDÉUTICO articulado (si aplica ciclos propedéuticos).'
    },
    'cond_4': {
        'num': '4',
        'title': 'Organización de las Actividades Académicas y del Proceso Formativo',
        'subnumerals': [
            '4.1 Registro Único Multimodal y Estrategias Pedagógicas Discriminadas por Modalidad',
            '4.2 Mediaciones Tecnológicas, Ambientes de Aprendizaje e Interacciones Sincrónicas/Asincrónicas',
            '4.3 Equivalencia Académica y Aseguramiento entre Modalidades'
        ],
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.4 & Registro Único Multimodal. Estrategias pedagógicas y didácticas discriminadas por cada modalidad solicitada (Presencial, Virtual, A Distancia Tradicional, Híbrida, Dual); mediaciones tecnológicas, equivalencia académica y de créditos entre modalidades, interacciones sincrónicas/asincrónicas y aseguramiento del aprendizaje.'
    },
    'cond_5': {
        'num': '5',
        'title': 'Investigación, Innovación y/o Creación Artística y Cultural',
        'subnumerals': [
            '5.1 Estrategia Institucional y Formación Investigativa en el Currículo',
            '5.2 Grupos, Semilleros y Líneas de Investigación Institucionales Asociadas',
            '5.3 Producción Científica/Tecnológica y Proyección de Sostenibilidad a 7 Años'
        ],
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.5. Articulación de la formación investigativa en el plan de estudios, líneas y sublíneas de investigación, semilleros y grupos de investigación institucionales, proyectos, producción científica/tecnológica y proyección de sostenibilidad a los 7 años de vigencia.'
    },
    'cond_6': {
        'num': '6',
        'title': 'Relación con el Sector Externo',
        'subnumerals': [
            '6.1 Proyección Social, Extensión y Articulación con el Sector Productivo y Comunitario',
            '6.2 Internacionalización del Currículo, Bilingüismo y Movilidad Académica',
            '6.3 Convenios de Prácticas Profesionales y Seguimiento a Egresados'
        ],
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.6. Proyección social, extensión, vinculación con el sector productivo y comunitario, internacionalización del currículo, convenios de prácticas, seguimiento a egresados y programas de responsabilidad social.'
    },
    'cond_7': {
        'num': '7',
        'title': 'Profesores',
        'subnumerals': [
            '7.1 Proyección de la Planta Docente y Perfiles Requeridos por Modalidad',
            '7.2 Estatuto Docente, Plan de Cualificación Pedagógica/Disciplinar y Sistema de Evaluación',
            '7.3 Distribución Horaria y Dedicación Docente (Docencia, Investigación, Extensión)'
        ],
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.7. Planta docente proyectada, perfiles académicos y de experiencia requeridos acordes a las modalidades, plan de formación y cualificación pedagógica/disciplinar, estatuto docente, dedicación horaria (docencia, investigación, extensión) y sistema de evaluación docente.'
    },
    'cond_8': {
        'num': '8',
        'title': 'Medios Educativos',
        'subnumerals': [
            '8.1 Recursos Bibliográficos Físicos y Bases de Datos Científicas Digitales',
            '8.2 Plataformas Virtuales de Aprendizaje (LMS), Software Especializado y Simuladores',
            '8.3 Accesibilidad, Inclusión y Capacitación a Usuarios'
        ],
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.8. Recursos bibliográficos físicos y digitales (bases de datos científicas), plataformas virtuales de aprendizaje (LMS), software especializado, simuladores, laboratorios virtuales, políticas de accesibilidad e inclusión y programas de capacitación a usuarios.'
    },
    'cond_9': {
        'num': '9',
        'title': 'Infraestructura Física y Tecnológica',
        'subnumerals': [
            '9.1 Aulas, Laboratorios Físicos/Virtuales, Talleres y Conectividad',
            '9.2 Bioseguridad, Accesibilidad Física y Espacios de Bienestar Universitario',
            '9.3 Plan de Mantenimiento, Renovación Tecnológica y Sostenibilidad Presupuestal'
        ],
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.9. Aulas, laboratorios físicos y talleres especializados, conectividad y ancho de banda, espacios de bienestar universitario, condiciones de bioseguridad, accesibilidad física, plan de mantenimiento y sostenibilidad presupuestal.'
    }
}

@registro_calificado_bp.route('/api/rc/generate_condition', methods=['POST'])
def generate_condition_ai():
    try:
        data = request.json or {}
        project_id = data.get('project_id')
        cond_key = data.get('cond_key') # cond_intro, cond_1, ..., cond_9
        user_instructions = data.get('user_instructions', '').strip()
        force_regenerate = data.get('force_regenerate', False)
        
        if not project_id or not cond_key:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros requeridos'}), 400
            
        proj = get_project(project_id)
        if not proj:
            return jsonify({'status': 'error', 'message': 'Proyecto no encontrado'}), 404
            
        meta = CONDITIONS_METADATA.get(cond_key, {
            'num': 'X',
            'title': 'Condición de Calidad',
            'focus': 'Decreto 1330 de 2019 y Decreto 0529 de 2024'
        })

        # ==========================================
        # REUTILIZACIÓN INTELIGENTE DE CONDICIONES INSTITUCIONALES TRANSVERSALES
        # (Investigación, Sector Externo, Profesores, Medios, Infraestructura, Introducción)
        # ==========================================
        institutional_keys = ['cond_intro', 'cond_5', 'cond_6', 'cond_7', 'cond_8', 'cond_9']
        
        if cond_key in institutional_keys and not force_regenerate:
            all_projects = load_local_projects()
            reusable_content = None
            source_prog_name = ""
            
            for other_id, other_proj in all_projects.items():
                if other_id != project_id and (other_proj.get('inst_name') == proj.get('inst_name') or not proj.get('inst_name')):
                    other_conds = other_proj.get('conditions', {})
                    if cond_key in other_conds and other_conds[cond_key].get('content', '').strip():
                        raw_source = other_conds[cond_key]['content']
                        old_prog = other_proj.get('program_name', '')
                        new_prog = proj.get('program_name', '')
                        old_title = other_proj.get('target_title', '')
                        new_title = proj.get('target_title', '')
                        
                        adapted = raw_source
                        if old_prog and old_prog in adapted:
                            adapted = adapted.replace(old_prog, new_prog)
                        if old_title and old_title in adapted:
                            adapted = adapted.replace(old_title, new_title)
                            
                        reusable_content = adapted
                        source_prog_name = old_prog
                        break
                        
            if reusable_content:
                if 'conditions' not in proj:
                    proj['conditions'] = {}
                proj['conditions'][cond_key] = {
                    'content': reusable_content,
                    'updated_at': datetime.datetime.now().isoformat(),
                    'status': 'reused'
                }
                save_project(proj)
                
                return jsonify({
                    'status': 'success',
                    'reused': True,
                    'cond_key': cond_key,
                    'title': meta.get('title'),
                    'content': reusable_content,
                    'message': f"Condición institucional reutilizada y adaptada desde el proyecto '{source_prog_name}' (Ahorro del 100% de tokens)."
                })
        
        # Compilar contexto de evidencias cargadas
        evidences_context = []
        for ev in proj.get('evidences', []):
            ev_text = ev.get('full_text', '')
            if ev_text:
                sample = ev_text[:3500] if len(ev_text) > 3500 else ev_text
                evidences_context.append(f"--- [DOCUMENTO FUENTE: {ev.get('name')} | TIPO: {ev.get('doc_type')}] ---\n{sample}\n")
                
        evidences_str = "\n".join(evidences_context) if evidences_context else "No se adjuntaron documentos adicionales. Fundamenta con base en los estándares normativos del MEN y la información suministrada del programa."
        
        modalities_str = ", ".join(proj.get('modalities', ['Presencial']))
        propedeutic_str = "SÍ aplica ciclos propedéuticos. Niveles articulados: " + ", ".join(proj.get('propedeutic_levels', [])) if proj.get('has_propedeutic_cycle') else "NO aplica ciclos propedéuticos (programa estructurado en un solo nivel)."
        
        procedure_type = proj.get('procedure_type', 'nuevo')
        procedure_instructions = ""
        if procedure_type == 'renovacion':
            procedure_instructions = """
ATENCIÓN ESPECIAL - TRÁMITE DE RENOVACIÓN DE REGISTRO CALIFICADO:
Este documento corresponde a una RENOVACIÓN de Registro Calificado. Debes enfatizar la evolución institucional, autoevaluaciones y planes de mejoramiento."""
        elif procedure_type == 'modificacion':
            procedure_instructions = """
ATENCIÓN ESPECIAL - TRÁMITE DE MODIFICACIÓN DE REGISTRO CALIFICADO:
Este documento sustenta una modificación sustancial (e.g. ampliación de modalidades para Registro Único). Sustenta la pertinencia y coherencia del cambio."""

        system_prompt = f"""Eres un Evaluador Senior de la Sala de CONACES, Par Académico del CNA y Consultor Senior de Alto Nivel para el Ministerio de Educación Nacional de Colombia (MEN).

Tu misión es redactar capítulos técnicos de máxima profundidad, rigor conceptual, riqueza argumentativa, citas fidedignas y datos estadísticos reales para un DOCUMENTO MAESTRO DE REGISTRO CALIFICADO institucional (diseñado para un expediente integral que sobrepasa las 350 páginas en su totalidad).

MARCO NORMATIVO Y REGULATORIO OBLIGATORIO VIGENTE EN COLOMBIA:
- Decreto 1330 de 2019 (Condiciones de calidad de programas de educación superior).
- Decreto 0529 de 2024 (Flexibilización curricular, movilidad y Registro Único Multimodal).
- Resolución 021795 de 2020 (Parámetros técnicos y aspectos obligatorios a evaluar por el MEN/CONACES).
- TAXONOMÍA SOLO (Structure of Observed Learning Outcomes) y Bloom revisada para Resultados de Aprendizaje (RA).
- Marco Nacional de Cualificaciones (MNC), CUO Colombia (Res. 1658/2023) y CINE-F 2013 A.C.
- Objetivos de Desarrollo Sostenible (ODS - Agenda 2030).

DIRECTRICES CRÍTICAS DE ESTRUCTURACIÓN Y REINGENIERÍA:

1. LÍMITE STRICTO Y AISLAMIENTO DE LA CONDICIÓN (SIN MEZCLAR OTRAS CONDICIONES):
   Estás redactando EXCLUSIVAMENTE la Condición {meta.get('num')}: {meta.get('title')}.
   Tus subtítulos principales (###) deben ser EXCLUSIVAMENTE los sub-numerales correspondientes a esta condición: {', '.join([s.split()[0] for s in meta.get('subnumerals', [])])}.
   ESTÁ RIGUROSAMENTE PROHIBIDO desviar la redacción o generar subtítulos pertenecientes a otras condiciones (por ejemplo, si estás en Condición 2, NO generes subtítulos de la Condición 3 como ### 3.1, ### 3.2 o ### 3.3).

2. CUMPLIMIENTO DE ASPECTOS A EVALUAR (RESOLUCIÓN 021795 DE 2020):
   Debes responder de manera exhaustiva a todos los aspectos a evaluar fijados por la Res. 021795 de 2020 para esta condición. Si un parámetro técnico o dato específico no aparece en los adjuntos suministrados por el usuario, DEBES investigarlo / deducirlo con rigor profesional en internet/bases normativas, fundamentándolo de forma completa en el texto sin dejar preguntas o corchetes sin responder.

3. GENERACIÓN DE TABLAS MARKDOWN COMPLETAS Y REALES (ESTILO DOCUMENTO MAESTRO INSTITUCIONAL):
   DEBES CONSTRUIR LAS TABLAS MARKDOWN COMPLETAS Y RICAS DIRECTAMENTE DENTRO DEL TEXTO.
   No las reemplaces por meras instrucciones vacías; incluye la tabla completa en sintaxis Markdown (| Columna 1 | Columna 2 |) con todos sus datos cuantitativos, matrices de pertinencia, oferta comparativa SNIES/DANE, matriz de Resultados de Aprendizaje bajo Taxonomía SOLO, plan de estudios con horas presenciales e independientes, o cuadros de equivalencia entre modalidades.

4. MARCADORES DE POSICIÓN PARA EVIDENCIA FOTOGRÁFICA Y PROMPTS DE DOCENTES/MEDIOS PARA DILIGENCIAR:
   - Para evidencia visual en condiciones 5, 6, 7, 8 y 9, dispone espacios destacados:
     > 🖼️ **[ESPACIO PARA EVIDENCIA FOTOGRÁFICA / CAPTURA DE PANTALLA]**:
     > *"Pegar aquí fotografía o evidencia gráfica de: [Aulas, Laboratorios Físicos / LMS / Firma de Convenios / Medios Educativos]. Pie de foto recomendado: Figura X.Y - Recursos para el programa {proj.get('program_name')}."*
   
   - Para Planta Docente (Condición 7) y Medios/Software (Condición 8), incluye la tabla estructurada oficial con columnas para ser diligenciada por la institución:
     > 🤖 **[PROMPT IA DE TABLA DE PLANTA DOCENTE / MEDIOS PARA DILIGENCIAR EN EXCEL/MARKDOWN]**:
     > *"Genera la plantilla estructurada en Markdown/Excel para la planta docente / inventario de software del programa '{proj.get('program_name')}' con las columnas: [Nombre del Docente | Máximo Nivel de Formación (Lic/Esp/MSc/PhD) | Área de Conocimiento | Tipo de Vinculación (TC/MT/Cátedra) | Asignaturas Asignadas | Horas Semanales Docencia | Horas Investigación/Extensión]. Dejar filas listas para ingresar los datos reales."*

5. CITACIÓN EN TEXTO Y BIBLIOGRAFÍA EN FORMATO APA 7.0:
   - Citas en texto formato APA 7.0 (DANE, 2024; SPADIES, 2024; UNESCO, 2024; Biggs & Tang, 2020).
   - Concluye la condición obligatoriamente con la sección: `### Referencias Bibliográficas y Documentales (Normativa APA 7.0)` conteniendo mínimo 6 a 10 referencias completas.

6. PROHIBICIÓN ESTRICTA DE FILAS DE TABLA REPETITIVAS O VACÍAS:
   Está estrictamente prohibido generar o repetir filas idénticas o plantillas vacías en tablas Markdown (ejemplo: NO repitas '| Nivel SOLO | Resultado de Aprendizaje (RA) |' en bucle). Cada fila de la tabla DEBE contener datos reales, concretos y diferenciados del programa. Máximo 6 a 8 filas por tabla.
"""

        user_prompt = f"""DESCRIPCIÓN DEL PROYECTO DE REGISTRO CALIFICADO:
- Institución: {proj.get('inst_name')}
- Nombre del Programa: {proj.get('program_name')}
- Título a Otorgar: {proj.get('target_title')}
- Nivel de Formación: {proj.get('level')}
- Tipo de Trámite: {procedure_type.upper()}
- Modalidades (Registro Único): {modalities_str}
- Lugares de Desarrollo / Sedes: {', '.join(proj.get('places_of_development', ['Sede Principal']))}
- Ciclos Propedéuticos: {propedeutic_str}
- Créditos Totales: {proj.get('total_credits')} | Duración estimada: {proj.get('total_duration')}
- Cupo Anual Proyectado: {proj.get('annual_quota')}
- Clasificación CINE-F: {proj.get('cine_f_code', '')} | CIUO-08: {proj.get('ciuo_08_code', '')}
- Marco Nacional de Cualificaciones (MNC): {proj.get('mnc_code', '')} | CUO Colombia: {proj.get('cuo_code', '')}
- Alineación ODS: {proj.get('ods_alignment', '')}

{procedure_instructions}

SECCIÓN A REDACTAR (LÍMITE STRICTO - MANTENERSE EXCLUSIVAMENTE EN ESTA CONDICIÓN):
CONDICIÓN {meta.get('num')}: {meta.get('title')}

SUB-NUMERALES ESTRUCTURALES OBLIGATORIOS A DESARROLLAR:
{chr(10).join([f"- {s}" for s in meta.get('subnumerals', [])])}

ENFOQUE NORMATIVO Y ASPECTOS A EVALUAR DE LA RES. 021795 DE 2020:
{meta.get('focus')}

INSTRUCCIONES ADICIONALES DEL USUARIO:
{user_instructions if user_instructions else 'Generar la sección con la máxima extensión y profundidad académica, respondiendo a todos los aspectos a evaluar de la Res. 021795 de 2020, construyendo las tablas Markdown completas directamente en el texto, e incorporando datos estadísticos externos fidedignos (DANE, SPADIES, UNESCO 2024-2026) y citas en APA 7.0.'}

EVIDENCIAS Y DOCUMENTOS INSTITUCIONALES DISPONIBLES EN EL PROYECTO:
{evidences_str}

REGLAS STRICTAS DE SALIDA:
1. Desarrolla EXCLUSIVAMENTE la Condición {meta.get('num')}. ESTÁ PROHIBIDO escribir subtítulos de la Condición {int(meta.get('num'))+1 if meta.get('num').isdigit() else 'siguiente'} (ejemplo: NO generes ### 3.1 si estás en la Condición 2).
2. Utiliza obligatoriamente los sub-numerales indicados arriba (ejemplo: {meta.get('num')}.1, {meta.get('num')}.2, {meta.get('num')}.3...) como subtítulos principales de tercer nivel (###).
3. Construye las TABLAS MARKDOWN COMPLETAS Y REALES con datos numéricos, créditos, matrices comparativas e indicadores dentro del texto.
4. Si un aspecto de la Res. 021795 de 2020 no aparece en las evidencias adjuntas, investígalo/dedúcelo técnicamente para responderlo completamente.
5. Finaliza el capítulo con la sección `### Referencias Bibliográficas y Documentales (Normativa APA 7.0)` conteniendo mínimo 6 a 10 referencias completas.
"""

        # Pase 1: Generación inicial
        response_text = call_ai(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=8192,
            temperature=0.35,
            inst_id=proj.get('inst_id')
        )
        
        # Bucle de Auto-Continuación de IA para garantizar completitud total y bibliografía APA 7.0
        max_continuation_passes = 3
        current_pass = 0
        
        while current_pass < max_continuation_passes:
            text_trim = response_text.strip()
            
            # Verificar si el documento ya cuenta con la sección final de referencias APA 7.0 y no está cortado mid-sentence
            has_references = '### Referencias' in text_trim or 'Referencias Bibliográficas' in text_trim or 'REFERENCIAS BIBLIOGRÁFICAS' in text_trim
            ends_cleanly = text_trim and text_trim[-1] in ['.', ']', ')', '"', '`', '}']
            
            if has_references and ends_cleanly:
                break
                
            # Si el texto está truncado o le faltan las referencias, preparar prompt de continuación exacta
            last_snippet = text_trim[-400:] if len(text_trim) > 400 else text_trim
            
            next_cond_num = str(int(meta.get('num')) + 1) if meta.get('num').isdigit() else 'siguiente'
            continuation_prompt = f"""ATENCIÓN: Tu respuesta anterior fue exhaustiva pero se interrumpió o aún no ha concluido con la sección final de bibliografía en APA 7.0.
A continuación se muestra el fragmento final generado hasta el momento:

"... {last_snippet}"

REGLAS RIGUROSAS DE CONTINUACIÓN:
1. CONTINÚA LA REDACCIÓN EXACTAMENTE DESDE LA ÚLTIMA PALABRA (sin repetir texto previo ni empezar desde el inicio).
2. MANTÉNTE EXCLUSIVAMENTE DENTRO DE LA CONDICIÓN {meta.get('num')}: {meta.get('title')}. ESTÁ RIGUROSAMENTE PROHIBIDO SALIRSE A LA CONDICIÓN {next_cond_num} (ejemplo: NO generes ningún subtítulo como '### {next_cond_num}.1' ni '### {next_cond_num}.2').
3. Continúa construyendo las TABLAS MARKDOWN COMPLETAS DIRECTAMENTE EN EL TEXTO con datos numéricos e indicadores reales.
4. Concluye obligatoriamente con la sección: `### Referencias Bibliográficas y Documentales (Normativa APA 7.0)` conteniendo mínimo 6 a 10 referencias completas en formato APA 7.0."""

            continuation_text = call_ai(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": continuation_prompt}
                ],
                max_tokens=8192,
                temperature=0.35,
                inst_id=proj.get('inst_id')
            )
            
            if not continuation_text or not continuation_text.strip():
                break
                
            # Unir limpiamente la continuación sin romper palabras a la mitad
            ends_mid_word = not response_text.rstrip().endswith((' ', '\n', '.', ',', ';', ':', ')', ']', '}', '`'))
            separator = "" if ends_mid_word else ("\n\n" if response_text.rstrip().endswith(('.', ':', ')', ']', '}', '`')) else " ")
            response_text = response_text.rstrip() + separator + continuation_text.lstrip()
            current_pass += 1

        response_text = sanitize_markdown_tables(response_text)
        
        # Guardar en el proyecto
        if 'conditions' not in proj:
            proj['conditions'] = {}
        proj['conditions'][cond_key] = {
            'content': response_text,
            'updated_at': datetime.datetime.now().isoformat(),
            'status': 'generated'
        }
        save_project(proj)
        
        return jsonify({
            'status': 'success',
            'cond_key': cond_key,
            'title': meta.get('title'),
            'content': response_text
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@registro_calificado_bp.route('/api/rc/continue_condition', methods=['POST'])
def continue_condition_ai():
    """Continúa la redacción de una condición desde el punto exacto donde se interrumpió el texto."""
    try:
        data = request.json or {}
        project_id = data.get('project_id')
        cond_key = data.get('cond_key')
        existing_content = data.get('existing_content', '').strip()
        
        if not project_id or not cond_key or not existing_content:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros requeridos'}), 400
            
        proj = get_project(project_id)
        if not proj:
            return jsonify({'status': 'error', 'message': 'Proyecto no encontrado'}), 404
            
        meta = CONDITIONS_METADATA.get(cond_key, {'num': 'X', 'title': 'Condición'})
        last_snippet = existing_content[-400:] if len(existing_content) > 400 else existing_content
        next_cond_num = str(int(meta.get('num')) + 1) if meta.get('num').isdigit() else 'siguiente'
        
        system_prompt = f"""Eres un Evaluador Senior de CONACES, Par Académico del CNA y Consultor Senior del MEN de Colombia.
Tu tarea es CONTINUAR la redacción técnica del capítulo para la Condición {meta.get('num')}: {meta.get('title')}.
Mantén el máximo rigor conceptual, investigación externa de fuentes (DANE, SPADIES, UNESCO 2024-2026), citas APA 7.0 y tablas Markdown completas."""

        continuation_prompt = f"""El texto de la Condición {meta.get('num')}: {meta.get('title')} para el programa '{proj.get('program_name')}' finalizó intempestivamente en el siguiente fragmento:

"... {last_snippet}"

REGLAS STRICTAS DE CONTINUACIÓN:
1. CONTINÚA LA REDACCIÓN EXACTAMENTE DESDE LA ÚLTIMA PALABRA (sin repetir texto previo ni empezar desde el inicio).
2. MANTÉNTE EXCLUSIVAMENTE DENTRO DE LA CONDICIÓN {meta.get('num')}. ESTÁ RIGUROSAMENTE PROHIBIDO SALIRSE A LA CONDICIÓN {next_cond_num} (ejemplo: NO generes ### {next_cond_num}.1 ni ### {next_cond_num}.2).
3. Construye las TABLAS MARKDOWN COMPLETAS DIRECTAMENTE EN EL TEXTO con datos numéricos e indicadores reales.
4. Concluye obligatoriamente con la sección: `### Referencias Bibliográficas y Documentales (Normativa APA 7.0)` conteniendo mínimo 6 a 10 referencias completas en formato APA 7.0."""

        continuation_text = call_ai(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": continuation_prompt}
            ],
            max_tokens=8192,
            temperature=0.35,
            inst_id=proj.get('inst_id')
        )
        
        if not continuation_text or not continuation_text.strip():
            return jsonify({'status': 'error', 'message': 'La IA no retornó contenido adicional'}), 500
            
        ends_mid_word = not existing_content.endswith((' ', '\n', '.', ',', ';', ':', ')', ']', '}', '`'))
        separator = "" if ends_mid_word else ("\n\n" if existing_content.endswith(('.', ':', ')', ']', '}', '`')) else " ")
        
        # PRESERVAR 100% DEL TEXTO ANTERIOR Y ANEXAR NUEVO CONTENIDO AL FINAL
        combined_content = existing_content + separator + continuation_text.lstrip()
        
        if 'conditions' not in proj:
            proj['conditions'] = {}
        proj['conditions'][cond_key] = {
            'content': combined_content,
            'updated_at': datetime.datetime.now().isoformat(),
            'status': 'generated'
        }
        save_project(proj)
        
        return jsonify({
            'status': 'success',
            'cond_key': cond_key,
            'title': meta.get('title'),
            'content': combined_content,
            'added_length': len(continuation_text)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@registro_calificado_bp.route('/api/rc/audit_condition', methods=['POST'])
def audit_condition_ai():
    """Realiza un dictamen de auditoría de Par Académico de CONACES sobre el contenido redactado."""
    try:
        data = request.json or {}
        project_id = data.get('project_id')
        cond_key = data.get('cond_key')
        
        if not project_id or not cond_key:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros requeridos'}), 400
            
        proj = get_project(project_id)
        if not proj:
            return jsonify({'status': 'error', 'message': 'Proyecto no encontrado'}), 404
            
        condition_data = proj.get('conditions', {}).get(cond_key, {})
        content_to_audit = condition_data.get('content', '')
        
        if not content_to_audit.strip():
            return jsonify({'status': 'error', 'message': 'No hay contenido generado para auditar en esta condición'}), 400
            
        meta = CONDITIONS_METADATA.get(cond_key, {'title': 'Condición'})
        
        system_prompt = """Eres el Coordinador de la Sala de Evaluación de CONACES del Ministerio de Educación Nacional.
Tu tarea es auditar y emitir un DICTAMEN DE EVALUACIÓN PREVIA riguroso sobre el texto presentado para una condición del Documento Maestro de Registro Calificado.

Debes evaluar conforme al Decreto 1330 de 2019, Decreto 0529 de 2024, Taxonomía SOLO (en aspectos curriculares), coherencia de Registro Único y evidencias institucionales.

Responde ÚNICAMENTE con un JSON válido con esta estructura exacta:
{
  "rating_status": "CUMPLE_PLENAMENTE" | "CUMPLE_ACEPTABLEMENTE" | "REQUIERE_AJUSTES",
  "score_100": 92,
  "strengths": [
    "Fortaleza 1 detectada...",
    "Fortaleza 2 detectada..."
  ],
  "observations": [
    "Observación o riesgo identificado...",
    "Aspecto que requiere mayor profundidad..."
  ],
  "recommendations": [
    "Recomendación concreta de ajuste antes de radicar en SACES...",
    "Recomendación 2..."
  ],
  "conaces_verdict": "Resumen ejecutivo del dictamen de la Sala de Evaluación en 2-3 párrafos."
}
"""

        user_prompt = f"""AUDITORÍA DE CONDICIÓN: {meta.get('title')}
PROGRAMA: {proj.get('program_name')} | NIVEL: {proj.get('level')} | TRÁMITE: {proj.get('procedure_type')}
MODALIDADES: {', '.join(proj.get('modalities', []))}

TEXTO PRESENTADO PARA EVALUACIÓN:
{content_to_audit}

Emite tu dictamen técnico y devuelve ÚNICAMENTE el JSON especificado."""

        response_text = call_ai(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.2,
            inst_id=proj.get('inst_id')
        )
        
        # Extraer JSON
        clean_text = response_text.strip()
        if '```json' in clean_text:
            clean_text = clean_text.split('```json')[1].split('```')[0].strip()
        elif '```' in clean_text:
            clean_text = clean_text.split('```')[1].split('```')[0].strip()
            
        audit_json = json.loads(clean_text)
        
        if 'audit_results' not in proj:
            proj['audit_results'] = {}
        proj['audit_results'][cond_key] = audit_json
        save_project(proj)
        
        return jsonify({
            'status': 'success',
            'audit': audit_json
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@registro_calificado_bp.route('/api/rc/save_condition_content', methods=['POST'])
def save_condition_content():
    try:
        data = request.json or {}
        project_id = data.get('project_id')
        cond_key = data.get('cond_key')
        content = sanitize_markdown_tables(data.get('content', ''))
        
        if not project_id or not cond_key:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros'}), 400
            
        proj = get_project(project_id)
        if not proj:
            return jsonify({'status': 'error', 'message': 'Proyecto no encontrado'}), 404
            
        if 'conditions' not in proj:
            proj['conditions'] = {}
            
        proj['conditions'][cond_key] = {
            'content': content,
            'updated_at': datetime.datetime.now().isoformat(),
            'status': 'edited'
        }
        save_project(proj)
        
        return jsonify({'status': 'success', 'message': 'Contenido guardado correctamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ==========================================
# EXPORTADOR A MICROSOFT WORD (.DOCX)
# ==========================================

@registro_calificado_bp.route('/api/rc/export_docx', methods=['GET', 'POST'])
def export_docx():
    """Genera y descarga el Documento Maestro completo o por condición en formato Word (.docx)."""
    try:
        if request.method == 'POST':
            data = request.json or {}
            project_id = data.get('project_id')
            cond_key = data.get('cond_key') # Opcional: exportar solo una condición o todo
        else:
            project_id = request.args.get('project_id')
            cond_key = request.args.get('cond_key')

        if not project_id:
            return jsonify({'status': 'error', 'message': 'Falta project_id'}), 400
            
        proj = get_project(project_id)
        if not proj:
            return jsonify({'status': 'error', 'message': 'Proyecto no encontrado'}), 404
            
        import docx
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
        from docx.oxml import parse_xml, OxmlElement
        from docx.oxml.ns import nsdecls, qn
        
        doc = docx.Document()
        
        # Configurar márgenes estándar ICONTEC / APA (2.54 cm / 1 pulgada)
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1.1)
            section.right_margin = Inches(1)
            
        # Estilos base
        normal_style = doc.styles['Normal']
        normal_style.font.name = 'Arial'
        normal_style.font.size = Pt(11)
        normal_style.font.color.rgb = RGBColor(30, 41, 59)
        
        # PORTADA INSTITUCIONAL
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_p.paragraph_format.space_before = Pt(40)
        title_p.paragraph_format.space_after = Pt(20)
        run_inst = title_p.add_run(f"{proj.get('inst_name', 'INSTITUCIÓN DE EDUCACIÓN SUPERIOR').upper()}\n")
        run_inst.font.size = Pt(16)
        run_inst.font.bold = True
        run_inst.font.color.rgb = RGBColor(15, 23, 42)
        
        doc_type_p = doc.add_paragraph()
        doc_type_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc_type_p.paragraph_format.space_after = Pt(30)
        run_dm = doc_type_p.add_run("DOCUMENTO MAESTRO DE REGISTRO CALIFICADO\n")
        run_dm.font.size = Pt(18)
        run_dm.font.bold = True
        run_dm.font.color.rgb = RGBColor(37, 99, 235)
        
        run_sub = doc_type_p.add_run(f"SOLICITUD DE {proj.get('procedure_type', 'NUEVO').upper()} DE REGISTRO CALIFICADO\nCONFORME AL DECRETO 1330 DE 2019 Y DECRETO 0529 DE 2024")
        run_sub.font.size = Pt(11)
        run_sub.font.italic = True
        run_sub.font.color.rgb = RGBColor(100, 116, 139)
        
        prog_p = doc.add_paragraph()
        prog_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        prog_p.paragraph_format.space_before = Pt(30)
        prog_p.paragraph_format.space_after = Pt(10)
        run_prog = prog_p.add_run(f"PROGRAMA ACADÉMICO:\n{proj.get('program_name', '').upper()}")
        run_prog.font.size = Pt(14)
        run_prog.font.bold = True
        run_prog.font.color.rgb = RGBColor(30, 41, 59)
        
        meta_p = doc.add_paragraph()
        meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        meta_p.paragraph_format.space_after = Pt(60)
        meta_p.add_run(f"Título a Otorgar: {proj.get('target_title')}\n")
        meta_p.add_run(f"Nivel de Formación: {proj.get('level')} | Créditos: {proj.get('total_credits')}\n")
        meta_p.add_run(f"Modalidades (Registro Único): {', '.join(proj.get('modalities', []))}\n")
        if proj.get('has_propedeutic_cycle'):
            meta_p.add_run(f"Estructurado por Ciclos Propedéuticos: {', '.join(proj.get('propedeutic_levels', []))}\n")
        meta_p.add_run(f"Lugar(es) de Desarrollo: {', '.join(proj.get('places_of_development', []))}\n")
        
        date_p = doc.add_paragraph()
        date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        date_p.add_run(f"Colombia\n{datetime.datetime.now().strftime('%B %Y').capitalize()}")
        
        doc.add_page_break()
        
        # TABLA DE RESUMEN DE DATOS DEL PROGRAMA
        res_h = doc.add_heading("FICHA TÉCNICA DEL PROGRAMA", level=1)
        res_h.style.font.color.rgb = RGBColor(37, 99, 235)
        
        table = doc.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        
        # Estilo encabezado tabla
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Parámetro Institucional / Curricular"
        hdr_cells[1].text = "Detalle Especificado"
        for c in hdr_cells:
            shading = parse_xml(r'<w:shd {} w:fill="1E293B"/>'.format(nsdecls('w')))
            c._tc.get_or_add_tcPr().append(shading)
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(255, 255, 255)
                    
        params = [
            ("Institución de Educación Superior", proj.get('inst_name')),
            ("Denominación del Programa", proj.get('program_name')),
            ("Título a Otorgar", proj.get('target_title')),
            ("Tipo de Trámite", proj.get('procedure_type', 'Nuevo').upper()),
            ("Nivel Académico", proj.get('level')),
            ("Modalidad(es) de Oferta", ", ".join(proj.get('modalities', []))),
            ("Número Total de Créditos", str(proj.get('total_credits'))),
            ("Duración Estimada", str(proj.get('total_duration'))),
            ("Cupo Anual Proyectado", str(proj.get('annual_quota'))),
            ("Clasificación CINE-F 2013 A.C.", str(proj.get('cine_f_code'))),
            ("Clasificación CIUO-08", str(proj.get('ciuo_08_code'))),
            ("Alineación con ODS", str(proj.get('ods_alignment'))),
            ("Ciclos Propedéuticos", "Sí (" + ", ".join(proj.get('propedeutic_levels', [])) + ")" if proj.get('has_propedeutic_cycle') else "No")
        ]
        
        for k, v in params:
            row_cells = table.add_row().cells
            row_cells[0].text = k
            row_cells[0].paragraphs[0].runs[0].font.bold = True
            row_cells[1].text = str(v) if v else "N/A"
            
        doc.add_paragraph().paragraph_format.space_after = Pt(20)
        
        # ==========================================
        # TABLA DE CONTENIDO FORMAL (TOC)
        # ==========================================
        if not cond_key:
            doc.add_page_break()
            toc_h = doc.add_heading("TABLA DE CONTENIDO", level=1)
            toc_h.style.font.color.rgb = RGBColor(37, 99, 235)
            toc_h.paragraph_format.space_before = Pt(10)
            toc_h.paragraph_format.space_after = Pt(15)
            
            p_toc_intro = doc.add_paragraph()
            p_toc_intro.add_run("Estructura técnica y capitulado del Documento Maestro de Registro Calificado:\n").font.italic = True
            p_toc_intro.paragraph_format.space_after = Pt(10)
            
            all_keys = ['cond_intro', 'cond_1', 'cond_2', 'cond_3', 'cond_4', 'cond_5', 'cond_6', 'cond_7', 'cond_8', 'cond_9']
            for k in all_keys:
                meta_item = CONDITIONS_METADATA.get(k, {})
                c_num = meta_item.get('num', '')
                c_title = meta_item.get('title', '')
                
                p_c = doc.add_paragraph()
                p_c.paragraph_format.space_before = Pt(4)
                p_c.paragraph_format.space_after = Pt(2)
                r_c = p_c.add_run(f"Condición {c_num}. {c_title}")
                r_c.font.bold = True
                r_c.font.size = Pt(11)
                r_c.font.color.rgb = RGBColor(15, 23, 42)
                
                for sub in meta_item.get('subnumerals', []):
                    p_sub = doc.add_paragraph()
                    p_sub.paragraph_format.left_indent = Inches(0.3)
                    p_sub.paragraph_format.space_before = Pt(0)
                    p_sub.paragraph_format.space_after = Pt(2)
                    r_sub = p_sub.add_run(sub)
                    r_sub.font.size = Pt(10)
                    r_sub.font.color.rgb = RGBColor(51, 65, 85)
            
            # ==========================================
            # ÍNDICE DE TABLAS DE EVIDENCIAS Y DECRETOS
            # ==========================================
            doc.add_page_break()
            idx_h = doc.add_heading("ÍNDICE DE TABLAS", level=1)
            idx_h.style.font.color.rgb = RGBColor(37, 99, 235)
            idx_h.paragraph_format.space_before = Pt(10)
            idx_h.paragraph_format.space_after = Pt(15)
            
            p_idx_intro = doc.add_paragraph()
            p_idx_intro.add_run("Relación consolidada de matrices, tablas estadísticas y cuadros de evidencia incorporados en el documento:\n").font.italic = True
            p_idx_intro.paragraph_format.space_after = Pt(10)
            
            index_tables = [
                ("Tabla 1", "Ficha Técnica General del Programa Académico"),
                ("Tabla 2", "Clasificaciones Normativas Oficiales (CINE-F 2013 A.C., CIUO-08, MNC, CUO y ODS)"),
                ("Tabla 3", "Matriz de Coherencia Institucional y Articulación con el Plan de Desarrollo (PDI)"),
                ("Tabla 4", "Análisis Comparativo de la Oferta Académica del Sector (SNIES / DANE)"),
                ("Tabla 5", "Matriz de Resultados de Aprendizaje (RA) bajo Taxonomía SOLO"),
                ("Tabla 6", "Malla Curricular, Distribución de Créditos y Horas (Acompañamiento vs. Independiente)"),
                ("Tabla 7", "Matriz de Equivalencias de Mediaciones y Actividades para Registro Único Multimodal"),
                ("Tabla 8", "Grupos, Semilleros y Líneas de Investigación Vinculadas al Programa"),
                ("Tabla 9", "Red Institucional de Convenios Vigentes para Prácticas Profesionales y Proyección Social"),
                ("Tabla 10", "Planta Docente Proyectada, Perfiles Académicos y Dedicación Horaria"),
                ("Tabla 11", "Inventario de Recursos Bibliográficos, Bases de Datos Científicas y Licencias de Software"),
                ("Tabla 12", "Matriz de Infraestructura Física, Laboratorios y Especificaciones Técnicas")
            ]
            
            table_idx = doc.add_table(rows=1, cols=2)
            table_idx.alignment = WD_TABLE_ALIGNMENT.CENTER
            table_idx.autofit = False
            
            hdr_idx = table_idx.rows[0].cells
            hdr_idx[0].text = "Identificador de Tabla"
            hdr_idx[1].text = "Denominación y Contenido Técnico de la Tabla"
            for c in hdr_idx:
                shading = parse_xml(r'<w:shd {} w:fill="2563EB"/>'.format(nsdecls('w')))
                c._tc.get_or_add_tcPr().append(shading)
                for p in c.paragraphs:
                    for r in p.runs:
                        r.font.bold = True
                        r.font.color.rgb = RGBColor(255, 255, 255)
                        
            for t_id, t_desc in index_tables:
                r_cells = table_idx.add_row().cells
                r_cells[0].text = t_id
                r_cells[0].paragraphs[0].runs[0].font.bold = True
                r_cells[1].text = t_desc
                
            doc.add_paragraph().paragraph_format.space_after = Pt(20)

        # CONDICIONES SELECCIONADAS O TODAS
        keys_to_export = [cond_key] if (cond_key and cond_key in CONDITIONS_METADATA) else [
            'cond_intro', 'cond_1', 'cond_2', 'cond_3', 'cond_4', 'cond_5', 'cond_6', 'cond_7', 'cond_8', 'cond_9'
        ]
        
        conditions_data = proj.get('conditions', {})
        
        for k in keys_to_export:
            meta = CONDITIONS_METADATA.get(k, {})
            c_info = conditions_data.get(k, {})
            raw_content = c_info.get('content', '')
            
            doc.add_page_break()
            
            h = doc.add_heading(f"{meta.get('title', 'Condición')}", level=1)
            h.style.font.color.rgb = RGBColor(37, 99, 235)
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(15)
            
            if not raw_content.strip():
                p_empty = doc.add_paragraph()
                p_empty.add_run("(Sección pendiente de redacción / generación con IA)").font.italic = True
                continue
                
            # Parsear Markdown simple (párrafos, títulos #, ##, ###, tablas |)
            lines = raw_content.split('\n')
            in_table = False
            table_lines = []
            
            for line in lines:
                stripped = line.strip()
                
                # Detectar líneas de tabla Markdown
                if stripped.startswith('|') and stripped.endswith('|'):
                    in_table = True
                    table_lines.append(stripped)
                    continue
                else:
                    if in_table:
                        # Renderizar la tabla acumulada
                        if len(table_lines) >= 2:
                            render_markdown_table_in_docx(doc, table_lines)
                        in_table = False
                        table_lines = []
                        
                if not stripped:
                    continue
                    
                if stripped.startswith('### '):
                    h3 = doc.add_heading(stripped[4:], level=3)
                    h3.style.font.color.rgb = RGBColor(71, 85, 105)
                elif stripped.startswith('## '):
                    h2 = doc.add_heading(stripped[3:], level=2)
                    h2.style.font.color.rgb = RGBColor(30, 41, 59)
                elif stripped.startswith('# '):
                    h1 = doc.add_heading(stripped[2:], level=1)
                    h1.style.font.color.rgb = RGBColor(37, 99, 235)
                elif stripped.startswith('- ') or stripped.startswith('* '):
                    p_list = doc.add_paragraph(stripped[2:], style='List Bullet')
                    p_list.paragraph_format.space_after = Pt(4)
                elif re.match(r'^\d+\.\s', stripped):
                    p_num = doc.add_paragraph(re.sub(r'^\d+\.\s', '', stripped), style='List Number')
                    p_num.paragraph_format.space_after = Pt(4)
                elif stripped.startswith('> '):
                    p_quote = doc.add_paragraph()
                    p_quote.paragraph_format.left_indent = Inches(0.4)
                    p_quote.paragraph_format.right_indent = Inches(0.4)
                    p_quote.paragraph_format.space_before = Pt(4)
                    p_quote.paragraph_format.space_after = Pt(4)
                    
                    quote_text = stripped[2:]
                    parts = re.split(r'(\*\*.*?\*\*)', quote_text)
                    for part in parts:
                        if part.startswith('**') and part.endswith('**'):
                            r_bold = p_quote.add_run(part[2:-2])
                            r_bold.font.bold = True
                            r_bold.font.color.rgb = RGBColor(37, 99, 235)
                        else:
                            r_italic = p_quote.add_run(part)
                            r_italic.font.italic = True
                            r_italic.font.color.rgb = RGBColor(51, 65, 85)
                else:
                    p_norm = doc.add_paragraph()
                    p_norm.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    p_norm.paragraph_format.line_spacing = 1.15
                    p_norm.paragraph_format.space_after = Pt(8)
                    
                    # Formateo simple de **negrita**
                    parts = re.split(r'(\*\*.*?\*\*)', stripped)
                    for part in parts:
                        if part.startswith('**') and part.endswith('**'):
                            r_bold = p_norm.add_run(part[2:-2])
                            r_bold.font.bold = True
                        else:
                            p_norm.add_run(part)
                            
            if in_table and len(table_lines) >= 2:
                render_markdown_table_in_docx(doc, table_lines)
                
        # Guardar en memoria y retornar archivo
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        
        safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', proj.get('program_name', 'Documento_Maestro'))
        filename = f"Documento_Maestro_RC_{safe_name}.docx" if not cond_key else f"RC_{safe_name}_{cond_key}.docx"
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def render_markdown_table_in_docx(doc, table_lines):
    import docx
    from docx.shared import Pt, RGBColor
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls
    
    rows_data = []
    for t_line in table_lines:
        # Ignorar líneas separadoras de markdown como |---|---|
        if re.match(r'^[\|\s\:\-]+$', t_line):
            continue
        cells = [c.strip() for c in t_line.strip('|').split('|')]
        rows_data.append(cells)
        
    if not rows_data:
        return
        
    num_cols = max(len(r) for r in rows_data)
    tbl = doc.add_table(rows=len(rows_data), cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    for r_idx, r_vals in enumerate(rows_data):
        row = tbl.rows[r_idx]
        is_header = (r_idx == 0)
        for c_idx in range(num_cols):
            val = r_vals[c_idx] if c_idx < len(r_vals) else ""
            cell = row.cells[c_idx]
            cell.text = val
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            
            if is_header:
                shd = parse_xml(r'<w:shd {} w:fill="2563EB"/>'.format(nsdecls('w')))
                cell._tc.get_or_add_tcPr().append(shd)
                for r in p.runs:
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(255, 255, 255)
            else:
                if r_idx % 2 == 1:
                    shd = parse_xml(r'<w:shd {} w:fill="F8FAFC"/>'.format(nsdecls('w')))
                    cell._tc.get_or_add_tcPr().append(shd)
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
