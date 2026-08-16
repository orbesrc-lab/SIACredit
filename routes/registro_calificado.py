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
RC_DATA_DIR = os.path.join(BASE_DIR, 'instance', 'registro_calificado')
RC_UPLOADS_DIR = os.path.join(RC_DATA_DIR, 'uploads')
os.makedirs(RC_UPLOADS_DIR, exist_ok=True)

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
    # 1. Intentar de archivo local
    projects = load_local_projects()
    if project_id in projects:
        return projects[project_id]
    
    # 2. Fallback a Supabase statistics
    try:
        res = supabase.table('statistics').select('data_json').eq('table_id', f"RC_PROJ_{project_id}").order('id', desc=True).limit(1).execute()
        if res.data:
            proj = json.loads(res.data[0]['data_json'])
            projects[project_id] = proj
            save_local_projects(projects)
            return proj
    except Exception as e:
        print(f"[RC] Error fetching project from DB: {e}")
    return None

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
        # Si local está vacío, buscar en Supabase
        if not projects:
            try:
                res = supabase.table('statistics').select('data_json').like('table_id', 'RC_PROJ_%').execute()
                if res.data:
                    for row in res.data:
                        try:
                            p = json.loads(row['data_json'])
                            projects[p['id']] = p
                        except Exception:
                            pass
                    save_local_projects(projects)
            except Exception as e:
                print(f"[RC] Error fetching all projects from DB: {e}")

        # Retornar lista ordenada por updated_at descendente
        proj_list = list(projects.values())
        proj_list.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return jsonify({'status': 'success', 'projects': proj_list})
    except Exception as e:
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


# ==========================================
# MOTOR DE IA: GENERADOR DE CONDICIONES Y AUDITORÍA
# ==========================================

CONDITIONS_METADATA = {
    'cond_intro': {
        'num': '0',
        'title': 'Introducción y Contextualización Institucional',
        'focus': 'Presentación formal de la institución, misión, visión, modelo pedagógico, propósito del trámite (Otorgamiento/Renovación), pertinencia y articulación con el PDI.'
    },
    'cond_1': {
        'num': '1',
        'title': 'Denominación del Programa',
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.1 & Decreto 0529/2024. Coherencia de la denominación con el nivel de formación, campo amplio/específico CINE-F 2013 A.C., clasificación CIUO-08, objetivos de desarrollo sostenible (ODS) y perfil de egreso.'
    },
    'cond_2': {
        'num': '2',
        'title': 'Justificación del Programa',
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.2. Pertinencia en los contextos internacional, nacional y regional; estudio de demanda laboral y tendencias ocupacionales; estado de la oferta académica (SNIES, SPADIES, DANE); atributos diferenciadores del programa y articulación con el Plan de Desarrollo Institucional.'
    },
    'cond_3': {
        'num': '3',
        'title': 'Aspectos Curriculares',
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.3 & Res. 021795. Conceptualización teórica y epistemológica, diseño curricular basado en Resultados de Aprendizaje (RA) formulados rigurosamente bajo la TAXONOMÍA SOLO (Preestructural, Uniestructural, Multiestructural, Relacional, Abstracto Ampliado), plan de estudios detallado con créditos (horas de acompañamiento docente vs. trabajo independiente), áreas y componentes de formación, interdisciplinariedad, flexibilidad curricular, estrategias de evaluación del aprendizaje y COMPONENTE PROPEDÉUTICO articulado (si aplica ciclos propedéuticos).'
    },
    'cond_4': {
        'num': '4',
        'title': 'Organización de las Actividades Académicas y del Proceso Formativo',
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.4 & Registro Único Multimodal. Estrategias pedagógicas y didácticas discriminadas por cada modalidad solicitada (Presencial, Virtual, A Distancia Tradicional, Híbrida, Dual); mediaciones tecnológicas, equivalencia académica y de créditos entre modalidades, interacciones sincrónicas/asincrónicas y aseguramiento del aprendizaje.'
    },
    'cond_5': {
        'num': '5',
        'title': 'Investigación, Innovación y/o Creación Artística y Cultural',
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.5. Articulación de la formación investigativa en el plan de estudios, líneas y sublíneas de investigación, semilleros y grupos de investigación institucionales, proyectos, producción científica/tecnológica y proyección de sostenibilidad a los 7 años de vigencia.'
    },
    'cond_6': {
        'num': '6',
        'title': 'Relación con el Sector Externo',
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.6. Proyección social, extensión, vinculación con el sector productivo y comunitario, internacionalización del currículo, convenios de prácticas, seguimiento a egresados y programas de responsabilidad social.'
    },
    'cond_7': {
        'num': '7',
        'title': 'Profesores',
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.7. Planta docente proyectada, perfiles académicos y de experiencia requeridos acordes a las modalidades, plan de formación y cualificación pedagógica/disciplinar, estatuto docente, dedicación horaria (docencia, investigación, extensión) y sistema de evaluación docente.'
    },
    'cond_8': {
        'num': '8',
        'title': 'Medios Educativos',
        'focus': 'Decreto 1330/2019 Art. 2.5.3.2.3.2.8. Recursos bibliográficos físicos y digitales (bases de datos científicas), plataformas virtuales de aprendizaje (LMS), software especializado, simuladores, laboratorios virtuales, políticas de accesibilidad e inclusión y programas de capacitación a usuarios.'
    },
    'cond_9': {
        'num': '9',
        'title': 'Infraestructura Física y Tecnológica',
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
        
        # Compilar contexto de evidencias cargadas
        evidences_context = []
        for ev in proj.get('evidences', []):
            ev_text = ev.get('full_text', '')
            if ev_text:
                # Tomar un extracto representativo por evidencia
                sample = ev_text[:3500] if len(ev_text) > 3500 else ev_text
                evidences_context.append(f"--- [DOCUMENTO FUENTE: {ev.get('name')} | TIPO: {ev.get('doc_type')}] ---\n{sample}\n")
                
        evidences_str = "\n".join(evidences_context) if evidences_context else "No se adjuntaron documentos adicionales. Fundamenta con base en los estándares normativos del MEN y la información suministrada del programa."
        
        # Modalidades y ciclos propedéuticos
        modalities_str = ", ".join(proj.get('modalities', ['Presencial']))
        propedeutic_str = "SÍ aplica ciclos propedéuticos. Niveles articulados: " + ", ".join(proj.get('propedeutic_levels', [])) if proj.get('has_propedeutic_cycle') else "NO aplica ciclos propedéuticos (programa estructurado en un solo nivel)."
        
        # Trámite (Renovación vs Nuevo)
        procedure_type = proj.get('procedure_type', 'nuevo')
        procedure_instructions = ""
        if procedure_type == 'renovacion':
            procedure_instructions = """
ATENCIÓN ESPECIAL - TRÁMITE DE RENOVACIÓN DE REGISTRO CALIFICADO:
Este documento corresponde a una RENOVACIÓN de Registro Calificado. Debes enfatizar:
1. La trayectoria, evolución y madurez demostrada por el programa durante sus 7 años de vigencia.
2. Los resultados concretos de los procesos de autoevaluación institucional (incorporando los datos del Informe de Autoevaluación adjunto si está presente).
3. El cumplimiento y efectividad de los Planes de Mejoramiento implementados para superar brechas históricas.
4. Las actualizaciones curriculares e innovaciones pedagógicas adoptadas para responder a los nuevos desafíos del contexto."""
        elif procedure_type == 'modificacion':
            procedure_instructions = """
ATENCIÓN ESPECIAL - TRÁMITE DE MODIFICACIÓN DE REGISTRO CALIFICADO:
Este documento sustenta una modificación sustancial (e.g. ampliación de modalidades para Registro Único o ajuste curricular). Argumenta con solidez la pertinencia, coherencia académica y viabilidad institucional del cambio propuesto."""

        system_prompt = f"""Eres un Evaluador Senior de la Sala de CONACES (Comisión Nacional Intersectorial de Aseguramiento de la Calidad de la Educación Superior), Par Académico del CNA y Especialista de Alto Nivel en Diseño Curricular y Aseguramiento de la Calidad del Ministerio de Educación Nacional de Colombia.

Tu misión es redactar el texto técnico, riguroso, explicativo y sólidamente argumentado para el DOCUMENTO MAESTRO DE REGISTRO CALIFICADO de la condición solicitada.

MARCO NORMATIVO Y TÉCNICO OBLIGATORIO:
- Decreto 1330 de 2019 (Condiciones de calidad de programas).
- Decreto 0529 de 2024 (Lineamientos de registro calificado y flexibilización curricular).
- Parámetros técnicos de la Resolución 021795 de 2020 (Rigor conceptual, evidencias verificables e indicadores).
- TAXONOMÍA SOLO (Structure of Observed Learning Outcomes) y Bloom revisada para la formulación de Resultados de Aprendizaje (RA) en la Condición 3.
- Lineamientos de REGISTRO ÚNICO (Articulación y equivalencia entre modalidades: Presencial, Virtual, A Distancia Tradicional, Dual e Híbrida).
- Articulación de CICLOS PROPEDÉUTICOS en un único documento maestro integral si aplica.

DIRECTRICES DE REDACCIÓN:
1. Redacta en tercera persona con tono institucional, académico, persuasivo y de máxima calidad técnica.
2. Cita expresamente las políticas, reglamentos, acuerdos institucionales y evidencias extraídas de los documentos fuente suministrados.
3. Incluye tablas estructuradas en formato Markdown (con columnas claras y contenido exhaustivo) cuando la condición lo requiera (por ejemplo: correspondencia CINE-F/CIUO-08, alineación ODS, taxonomía SOLO en resultados de aprendizaje, créditos y horas presenciales/independientes, líneas de investigación, planta docente, medios educativos).
4. No generes textos genéricos ni respuestas superficiales; redacta párrafos amplios, fundamentados, con cifras, indicadores y justificaciones técnicas completas listas para ser presentadas ante el MEN/CONACES.
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
- Clasificación CINE-F: {proj.get('cine_f_code')} | CIUO-08: {proj.get('ciuo_08_code')}
- Alineación ODS: {proj.get('ods_alignment')}

{procedure_instructions}

SECCIÓN A REDACTAR:
CONDICIÓN: {meta.get('title')} (Condición {meta.get('num')})
ENFOQUE NORMATIVO Y EXIGENCIAS:
{meta.get('focus')}

INSTRUCCIONES ADICIONALES DEL USUARIO:
{user_instructions if user_instructions else 'Generar la sección de manera completa, con sus subtítulos, tablas comparativas y argumentación exhaustiva.'}

EVIDENCIAS Y DOCUMENTOS INSTITUCIONALES DISPONIBLES EN EL PROYECTO:
{evidences_str}

Por favor, genera el desarrollo completo y exhaustivo de esta condición en formato Markdown limpio y profesional. Asegúrate de incluir subtítulos numerados claros (e.g. 3.1, 3.2, 3.3...), tablas completas y todas las justificaciones pertinentes.
"""

        response_text = call_ai(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=4000,
            temperature=0.4,
            inst_id=proj.get('inst_id')
        )
        
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
        content = data.get('content', '')
        
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
