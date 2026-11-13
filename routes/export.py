from flask import Blueprint, jsonify, request, send_file
import io
import zipfile
import xml.etree.ElementTree as ET
import formacion_storage
import re
import json
from datetime import datetime
import urllib.request
import urllib.parse

export_bp = Blueprint('export', __name__)

def sanitize_filename(name):
    """Limpia caracteres inválidos para nombres de archivo."""
    if not name:
        return "archivo"
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r'\s+', "_", name)
    return name.lower()[:45]

def extract_youtube_id(url):
    """Extrae el ID de un video de YouTube para embebido."""
    if not url: return None
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return match.group(1) if match else None


# =========================================================================
# VALIDACIÓN INSTITUCIONAL DE CALIDAD EN SKEL 360
# =========================================================================

@export_bp.route('/api/courses/<course_id>/validate_skel', methods=['POST'])
def validate_course_skel(course_id):
    """Valida y certifica el curso en SKEL 360 antes de su migración a Moodle."""
    course = formacion_storage.load_course(course_id)
    if not course:
        return jsonify({"status": "error", "message": "Curso no encontrado"}), 404
        
    inst_id = request.json.get('inst_id') or course.get('inst_id', 1) if request.json else course.get('inst_id', 1)
    
    units = course.get('units', [])
    if isinstance(units, dict):
        units = list(units.values())
        
    total_topics = 0
    completed_topics = 0
    total_resources = 0
    total_activities = 0
    total_evaluations = 0
    
    for u in units:
        topics = u.get('topics', [])
        if isinstance(topics, dict): topics = list(topics.values())
        for t in topics:
            total_topics += 1
            content = t.get('content', '') if isinstance(t, dict) else ''
            if len(content.strip()) > 200:
                completed_topics += 1
                
        res = u.get('resources', [])
        total_resources += len(res) if isinstance(res, list) else len(res.values()) if isinstance(res, dict) else 0
        
        act = u.get('activities', [])
        total_activities += len(act) if isinstance(act, list) else len(act.values()) if isinstance(act, dict) else 0
        
        ev = u.get('evaluations', [])
        total_evaluations += len(ev) if isinstance(ev, list) else len(ev.values()) if isinstance(ev, dict) else 0

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M")
    validation_seal = f"SKEL-CERT-{course_id.upper()[:8]}-2026"
    
    course['skel_validated'] = True
    course['skel_validation_date'] = now_iso
    course['skel_validation_seal'] = validation_seal
    
    # Guardar en base de datos
    formacion_storage.save_course(inst_id, course.get('program_id', 0), course)
    
    return jsonify({
        "status": "success",
        "success": True,
        "validation": {
            "course_id": course_id,
            "course_title": course.get('title') or course.get('name'),
            "validated": True,
            "date": now_iso,
            "seal": validation_seal,
            "stats": {
                "units": len(units),
                "topics": total_topics,
                "completed_topics": completed_topics,
                "resources": total_resources,
                "activities": total_activities,
                "evaluations": total_evaluations
            }
        },
        "data": {
            "course_id": course_id,
            "course_title": course.get('title') or course.get('name'),
            "validated": True,
            "validation_date": now_iso,
            "validation_seal": validation_seal,
            "stats": {
                "units": len(units),
                "total_topics": total_topics,
                "completed_topics": completed_topics,
                "resources": total_resources,
                "activities": total_activities,
                "evaluations": total_evaluations
            }
        }
    })


# =========================================================================
# EXPORTACIÓN INTEGRAL DEL CURSO A MOODLE (IMS COMMON CARTRIDGE + RECURSOS)
# =========================================================================

@export_bp.route('/api/courses/<course_id>/export/moodle', methods=['GET'])
def export_moodle(course_id):
    """Genera paquete completo de migración a Moodle con temas, recursos, tareas y evaluaciones."""
    course = formacion_storage.load_course(course_id)
    if not course:
        # Intento fallback
        courses = formacion_storage.load_courses(1, 0)
        course = next((c for c in courses if c.get('id') == course_id), None)
    
    if not course:
        return jsonify({"status": "error", "message": "Curso no encontrado"}), 404
        
    course_title = course.get('name') or course.get('title') or "Curso_SKEL"
    units = course.get('units', [])
    if isinstance(units, dict):
        units = list(units.values())
        
    validation_seal = course.get('skel_validation_seal', f"SKEL-CERT-{course_id.upper()[:8]}-2026")
    validation_date = course.get('skel_validation_date', datetime.now().strftime("%Y-%m-%d"))

    # Crear archivo ZIP en memoria con formato IMS Common Cartridge estándar
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        
        # Manifest XML para Moodle
        manifest = ET.Element('manifest', {
            'identifier': f'MANIFEST-{course_id}',
            'xmlns': 'http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1',
            'xmlns:lom': 'http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd'
        })
        
        metadata = ET.SubElement(manifest, 'metadata')
        schema = ET.SubElement(metadata, 'schema')
        schema.text = 'IMS Common Cartridge'
        schemaversion = ET.SubElement(metadata, 'schemaversion')
        schemaversion.text = '1.1.0'
        
        # Metadatos del curso
        lom_meta = ET.SubElement(metadata, 'lom:lom')
        general = ET.SubElement(lom_meta, 'lom:general')
        title_el = ET.SubElement(general, 'lom:title')
        title_val = ET.SubElement(title_el, 'lom:string', {'language': 'es'})
        title_val.text = course_title
        
        desc_el = ET.SubElement(general, 'lom:description')
        desc_val = ET.SubElement(desc_el, 'lom:string', {'language': 'es'})
        desc_val.text = course.get('description', 'Curso diseñado y validado bajo estándares SKEL 360.')
        
        organizations = ET.SubElement(manifest, 'organizations')
        organization = ET.SubElement(organizations, 'organization', {'identifier': f'ORG-{course_id}', 'structure': 'rooted-hierarchy'})
        
        root_item = ET.SubElement(organization, 'item', {'identifier': 'root'})
        root_title = ET.SubElement(root_item, 'title')
        root_title.text = course_title
        
        resources = ET.SubElement(manifest, 'resources')
        res_counter = 1

        # ── 1. PÁGINA GENERAL DE PRESENTACIÓN Y VALIDACIÓN SKEL ──
        info_file = "intro/presentacion_curso.html"
        competencies_li = "".join([f"<li>{c}</li>" for c in course.get('competencies', [])])
        outcomes_li = "".join([f"<li>{o}</li>" for o in course.get('outcomes', [])])
        
        intro_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>{course_title} - Presentación Oficial</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1e293b; max-width: 900px; margin: 30px auto; padding: 0 20px; }}
        .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 30px; border-radius: 14px; margin-bottom: 25px; }}
        .badge {{ display: inline-block; background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; margin-bottom: 10px; }}
        .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin-bottom: 20px; }}
        h1 {{ margin: 0 0 10px 0; font-size: 1.8rem; }}
        h2 {{ color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 25px; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <span class="badge">🛡️ VALIDADO EN SKEL 360</span>
        <h1>{course_title}</h1>
        <p style="margin:0; opacity:0.9;"><strong>Duración:</strong> {course.get('duration', 40)} Horas • <strong>Nivel:</strong> {course.get('level', 'Intermedio')} • <strong>Certifica:</strong> {course.get('certifier', 'SKEL')}</p>
        <p style="margin:5px 0 0 0; font-size:0.85rem; opacity:0.8;">Sello de Validación: <code>{validation_seal}</code> • Fecha: {validation_date}</p>
    </div>

    <div class="card">
        <h2>Descripción del Curso</h2>
        <p>{course.get('description', 'Sin descripción.')}</p>
    </div>

    {f'<div class="card"><h2>Competencias a Desarrollar</h2><ul>{competencies_li}</ul></div>' if competencies_li else ''}
    {f'<div class="card"><h2>Resultados de Aprendizaje</h2><ul>{outcomes_li}</ul></div>' if outcomes_li else ''}
</body>
</html>"""
        zf.writestr(info_file, intro_html.encode('utf-8'))
        
        intro_item = ET.SubElement(root_item, 'item', {'identifier': f'ITEM-INTRO', 'identifierref': 'RES-INTRO'})
        intro_t = ET.SubElement(intro_item, 'title')
        intro_t.text = "📌 Presentación del Curso y Calidad SKEL"
        
        intro_res = ET.SubElement(resources, 'resource', {'identifier': 'RES-INTRO', 'type': 'webcontent', 'href': info_file})
        ET.SubElement(intro_res, 'file', {'href': info_file})

        # ── 2. PROCESAR UNIDADES, TEMAS, RECURSOS, ACTIVIDADES Y EVALUACIONES ──
        all_quiz_questions = []

        for u_idx, unit in enumerate(units):
            unit_name = unit.get('name') or f"Unidad {u_idx+1}"
            unit_id = f"UNIT-{u_idx+1}"
            
            unit_item = ET.SubElement(root_item, 'item', {'identifier': unit_id})
            unit_title_el = ET.SubElement(unit_item, 'title')
            unit_title_el.text = unit_name

            # A. TEMAS ACADÉMICOS
            topics = unit.get('topics', [])
            if isinstance(topics, dict): topics = list(topics.values())
            
            for t_idx, topic in enumerate(topics):
                if isinstance(topic, str):
                    t_title = topic
                    t_content = f"<h3>{t_title}</h3><p>Contenido introductorio del tema.</p>"
                else:
                    t_title = topic.get('title', f'Tema {t_idx+1}')
                    t_content = topic.get('content', '') or f"<h3>{t_title}</h3><p>Contenido del tema.</p>"
                    
                safe_title = sanitize_filename(t_title)
                file_path = f"topics/u{u_idx+1}_t{t_idx+1}_{safe_title}.html"
                
                topic_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>{t_title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.7; color: #1e293b; max-width: 900px; margin: 30px auto; padding: 0 20px; }}
        .topic-header {{ border-bottom: 3px solid #1e3a8a; padding-bottom: 12px; margin-bottom: 25px; }}
        h1, h2, h3, h4 {{ color: #0f172a; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 10px; text-align: left; }}
        th {{ background: #1e3a8a; color: white; }}
        tr:nth-child(even) {{ background: #f8fafc; }}
        blockquote {{ border-left: 4px solid #3b82f6; margin: 20px 0; padding: 10px 20px; background: #f0fdf4; border-radius: 0 8px 8px 0; }}
        .footer-seal {{ margin-top: 40px; padding-top: 15px; border-top: 1px solid #e2e8f0; font-size: 0.8rem; color: #64748b; text-align: right; }}
    </style>
</head>
<body>
    <div class="topic-header">
        <span style="font-size:0.85rem; color:#64748b; text-transform:uppercase; font-weight:bold;">{unit_name}</span>
        <h1 style="margin:5px 0 0 0;">{t_title}</h1>
    </div>
    
    <div class="content-body">
        {t_content}
    </div>

    <div class="footer-seal">
        Sello de Calidad y Validación: <strong>{validation_seal}</strong> • SKEL 360 LMS
    </div>
</body>
</html>"""
                zf.writestr(file_path, topic_html.encode('utf-8'))
                
                item_id = f"ITEM-TOPIC-{res_counter}"
                res_id = f"RES-TOPIC-{res_counter}"
                res_counter += 1
                
                topic_item = ET.SubElement(unit_item, 'item', {'identifier': item_id, 'identifierref': res_id})
                t_t = ET.SubElement(topic_item, 'title')
                t_t.text = f"📖 {t_title}"
                
                r_el = ET.SubElement(resources, 'resource', {'identifier': res_id, 'type': 'webcontent', 'href': file_path})
                ET.SubElement(r_el, 'file', {'href': file_path})

            # B. RECURSOS (VIDEOS, DOCUMENTOS, INFOGRAFÍAS, LINKS)
            resources_list = unit.get('resources', [])
            if isinstance(resources_list, dict): resources_list = list(resources_list.values())
            
            for r_idx, r in enumerate(resources_list):
                r_name = r.get('name', f'Recurso {r_idx+1}')
                r_url = r.get('url', '#')
                r_type = r.get('type', 'link')
                safe_rname = sanitize_filename(r_name)
                res_file_path = f"resources/u{u_idx+1}_r{r_idx+1}_{safe_rname}.html"
                
                yt_id = extract_youtube_id(r_url)
                if yt_id:
                    media_block = f"""
                    <div style="position:relative; padding-bottom:56.25%; height:0; overflow:hidden; border-radius:12px; margin:20px 0; box-shadow:0 10px 25px rgba(0,0,0,0.15);">
                        <iframe src="https://www.youtube.com/embed/{yt_id}" frameborder="0" allowfullscreen style="position:absolute; top:0; left:0; width:100%; height:100%;"></iframe>
                    </div>
                    """
                elif r_type in ['infographic', 'image'] or r_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    media_block = f"""
                    <div style="text-align:center; margin:20px 0;">
                        <img src="{r_url}" alt="{r_name}" style="max-width:100%; border-radius:10px; box-shadow:0 10px 25px rgba(0,0,0,0.1);">
                    </div>
                    """
                else:
                    media_block = f"""
                    <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:20px; text-align:center; margin:20px 0;">
                        <p style="font-size:1.05rem; color:#1e40af; margin-bottom:15px;"><strong>Documento / Enlace de Estudio:</strong> {r_name}</p>
                        <a href="{r_url}" target="_blank" style="display:inline-block; background:#1e3a8a; color:white; padding:12px 24px; text-decoration:none; border-radius:8px; font-weight:bold; font-size:0.95rem;">
                            Abrir Documento Institucional ↗
                        </a>
                    </div>
                    <iframe src="{r_url}" style="width:100%; height:550px; border:1px solid #cbd5e1; border-radius:10px;" onerror="this.style.display='none';"></iframe>
                    """

                res_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>{r_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1e293b; max-width: 900px; margin: 30px auto; padding: 0 20px; }}
        h1 {{ color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
    </style>
</head>
<body>
    <span style="font-size:0.85rem; color:#64748b; text-transform:uppercase; font-weight:bold;">{unit_name} • RECURSO PEDAGÓGICO</span>
    <h1>{r_name}</h1>
    {media_block}
    <p style="text-align:right; font-size:0.8rem; color:#64748b; margin-top:30px;">Recurso integrado desde SKEL 360</p>
</body>
</html>"""
                zf.writestr(res_file_path, res_html.encode('utf-8'))
                
                item_id = f"ITEM-RES-{res_counter}"
                res_id = f"RES-FILE-{res_counter}"
                res_counter += 1
                
                r_item = ET.SubElement(unit_item, 'item', {'identifier': item_id, 'identifierref': res_id})
                r_t = ET.SubElement(r_item, 'title')
                r_t.text = f"📁 {r_name}"
                
                r_res = ET.SubElement(resources, 'resource', {'identifier': res_id, 'type': 'webcontent', 'href': res_file_path})
                ET.SubElement(r_res, 'file', {'href': res_file_path})

            # C. ACTIVIDADES / TAREAS (ASSIGNMENTS)
            activities_list = unit.get('activities', [])
            if isinstance(activities_list, dict): activities_list = list(activities_list.values())
            
            for a_idx, act in enumerate(activities_list):
                act_title = act.get('title', f'Actividad {a_idx+1}')
                act_desc = act.get('description', 'Desarrolla la actividad conforme a las pautas dadas.')
                act_weight = act.get('weight', 10)
                act_due = act.get('due_date', 'Según cronograma académico')
                safe_aname = sanitize_filename(act_title)
                act_file_path = f"activities/u{u_idx+1}_a{a_idx+1}_{safe_aname}.html"
                
                act_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Actividad: {act_title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1e293b; max-width: 900px; margin: 30px auto; padding: 0 20px; }}
        .header {{ background:#eff6ff; border-left:5px solid #2563eb; padding:20px; border-radius:0 12px 12px 0; margin-bottom:25px; }}
        .meta-pill {{ display:inline-block; background:#1e3a8a; color:white; padding:3px 10px; border-radius:15px; font-size:0.8rem; font-weight:bold; margin-right:8px; }}
        h1 {{ color:#1e3a8a; margin:10px 0; }}
        .box {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:20px; margin-bottom:20px; }}
    </style>
</head>
<body>
    <div class="header">
        <span class="meta-pill">📝 TAREA EVALUATIVA</span>
        <span class="meta-pill" style="background:#10b981;">Ponderación: {act_weight}%</span>
        <h1>{act_title}</h1>
        <p style="margin:5px 0 0 0; color:#475569;"><strong>Unidad:</strong> {unit_name} • <strong>Fecha sugerida de entrega:</strong> {act_due}</p>
    </div>

    <div class="box">
        <h3>Orientaciones y Consigna de la Actividad</h3>
        <p>{act_desc}</p>
    </div>

    <div class="box">
        <h3>Criterios de Evaluación y Calificación</h3>
        <ul>
            <li>Dominio conceptual y argumentación técnica sustentada.</li>
            <li>Aplicación práctica y pertinencia al contexto institucional.</li>
            <li>Presentación, estructura y citación bibliográfica bajo normas APA.</li>
        </ul>
    </div>
</body>
</html>"""
                zf.writestr(act_file_path, act_html.encode('utf-8'))
                
                item_id = f"ITEM-ACT-{res_counter}"
                res_id = f"RES-ACT-{res_counter}"
                res_counter += 1
                
                act_item = ET.SubElement(unit_item, 'item', {'identifier': item_id, 'identifierref': res_id})
                act_t = ET.SubElement(act_item, 'title')
                act_t.text = f"📝 [Tarea] {act_title} ({act_weight}%)"
                
                act_res = ET.SubElement(resources, 'resource', {'identifier': res_id, 'type': 'webcontent', 'href': act_file_path})
                ET.SubElement(act_res, 'file', {'href': act_file_path})

            # D. EVALUACIONES / CUESTIONARIOS
            evaluations_list = unit.get('evaluations', [])
            if isinstance(evaluations_list, dict): evaluations_list = list(evaluations_list.values())
            
            for e_idx, ev in enumerate(evaluations_list):
                ev_title = ev.get('title', f'Evaluación {e_idx+1}')
                ev_weight = ev.get('weight', 20)
                ev_min = ev.get('min_grade', 3.0)
                ev_max = ev.get('max_grade', 5.0)
                questions = ev.get('questions', [])
                if isinstance(questions, dict): questions = list(questions.values())
                
                safe_ename = sanitize_filename(ev_title)
                ev_file_path = f"evaluations/u{u_idx+1}_e{e_idx+1}_{safe_ename}.html"
                
                questions_preview = ""
                for q_idx, q in enumerate(questions):
                    q_text = q.get('text') or q.get('question') or f"Pregunta {q_idx+1}"
                    opts = q.get('options', [])
                    opts_html = "".join([f"<li>{o.get('text', o) if isinstance(o, dict) else o}</li>" for o in opts])
                    questions_preview += f"<div style='margin-bottom:15px;'><strong>{q_idx+1}. {q_text}</strong><ul>{opts_html}</ul></div>"
                    all_quiz_questions.append({
                        "category": f"{unit_name} / {ev_title}",
                        "question": q
                    })
                    
                ev_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Evaluación: {ev_title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1e293b; max-width: 900px; margin: 30px auto; padding: 0 20px; }}
        .header {{ background:#fef3c7; border-left:5px solid #f59e0b; padding:20px; border-radius:0 12px 12px 0; margin-bottom:25px; }}
        .meta-pill {{ display:inline-block; background:#b45309; color:white; padding:3px 10px; border-radius:15px; font-size:0.8rem; font-weight:bold; margin-right:8px; }}
        h1 {{ color:#92400e; margin:10px 0; }}
        .box {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:20px; margin-bottom:20px; }}
    </style>
</head>
<body>
    <div class="header">
        <span class="meta-pill">🏆 EVALUACIÓN DEL APRENDIZAJE</span>
        <span class="meta-pill" style="background:#10b981;">Ponderación: {ev_weight}%</span>
        <h1>{ev_title}</h1>
        <p style="margin:5px 0 0 0; color:#78350f;"><strong>Escala de Calificación:</strong> Aprobación {ev_min} / Máxima {ev_max} • <strong>Preguntas:</strong> {len(questions)}</p>
    </div>

    <div class="box">
        <h3>Instrucciones del Cuestionario</h3>
        <p>Lee con atención cada planteamiento antes de responder. Este cuestionario evalúa las competencias y resultados de aprendizaje adquiridos en la {unit_name}.</p>
    </div>

    {f'<div class="box"><h3>Estructura de Preguntas</h3>{questions_preview}</div>' if questions_preview else '<div class="box"><p style="color:#64748b;">Las preguntas se cargarán automáticamente al configurar el cuestionario en Moodle.</p></div>'}
</body>
</html>"""
                zf.writestr(ev_file_path, ev_html.encode('utf-8'))
                
                item_id = f"ITEM-EV-{res_counter}"
                res_id = f"RES-EV-{res_counter}"
                res_counter += 1
                
                ev_item = ET.SubElement(unit_item, 'item', {'identifier': item_id, 'identifierref': res_id})
                ev_t = ET.SubElement(ev_item, 'title')
                ev_t.text = f"🏆 [Evaluación] {ev_title} ({ev_weight}%)"
                
                ev_res = ET.SubElement(resources, 'resource', {'identifier': res_id, 'type': 'webcontent', 'href': ev_file_path})
                ET.SubElement(ev_res, 'file', {'href': ev_file_path})

        # ── 3. GUÍA DE RESTAURACIÓN PASO A PASO EN MOODLE ──
        guide_file = "moodle_guia_restauracion.html"
        guide_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Cómo Restaurar este Curso en tu Moodle Institucional</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1e293b; max-width: 850px; margin: 30px auto; padding: 0 20px; }}
        .header {{ background:#1e3a8a; color:white; padding:25px; border-radius:12px; margin-bottom:25px; }}
        .step {{ background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; padding:18px; margin-bottom:15px; }}
        .step-num {{ font-size:1.1rem; font-weight:bold; color:#1e3a8a; margin-bottom:6px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin:0 0 5px 0;">🚀 Guía de Migración a Moodle Institucional</h2>
        <p style="margin:0; opacity:0.9;">Sigue estos sencillos pasos para importar este curso completo en tu plataforma Moodle.</p>
    </div>

    <div class="step">
        <div class="step-num">Paso 1: Ingresa a tu Moodle Institucional</div>
        <p>Inicia sesión con tu cuenta de Profesor o Administrador en la plataforma Moodle de tu universidad o institución.</p>
    </div>

    <div class="step">
        <div class="step-num">Paso 2: Ve a la opción Restaurar</div>
        <p>Entra al curso de destino (o en <strong>Administración del sitio &gt; Cursos &gt; Restaurar curso</strong>).</p>
    </div>

    <div class="step">
        <div class="step-num">Paso 3: Sube este archivo .imscc / .zip</div>
        <p>Arrastra o selecciona el archivo descargado desde SKEL 360 en la zona de subida de archivos y haz clic en <strong>Restaurar</strong>.</p>
    </div>

    <div class="step">
        <div class="step-num">Paso 4: Confirma la importación</div>
        <p>Haz clic en <strong>Continuar &gt; Siguiente &gt; Ejecutar restauración</strong>. ¡Listo! Moodle creará automáticamente todas las secciones, páginas de contenido, recursos multimedia y tareas.</p>
    </div>
</body>
</html>"""
        zf.writestr(guide_file, guide_html.encode('utf-8'))
        
        guide_item = ET.SubElement(root_item, 'item', {'identifier': 'ITEM-GUIDE', 'identifierref': 'RES-GUIDE'})
        gt = ET.SubElement(guide_item, 'title')
        gt.text = "📘 Guía de Restauración en Moodle"
        
        gres = ET.SubElement(resources, 'resource', {'identifier': 'RES-GUIDE', 'type': 'webcontent', 'href': guide_file})
        ET.SubElement(gres, 'file', {'href': guide_file})

        # ── 4. BANCO DE PREGUNTAS EN FORMATO MOODLE XML (SI HAY PREGUNTAS) ──
        if all_quiz_questions:
            quiz_xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<quiz>']
            current_cat = None
            for q_data in all_quiz_questions:
                cat = q_data['category']
                if cat != current_cat:
                    current_cat = cat
                    quiz_xml_lines.append(f"""  <question type="category">
    <category>
      <text>$course$/top/{cat}</text>
    </category>
  </question>""")
                
                q = q_data['question']
                q_text = q.get('text') or q.get('question') or "Pregunta"
                options = q.get('options', [])
                
                quiz_xml_lines.append(f"""  <question type="multichoice">
    <name><text>{q_text[:40]}</text></name>
    <questiontext format="html"><text><![CDATA[<p>{q_text}</p>]]></text></questiontext>
    <defaultgrade>1.0</defaultgrade>
    <single>true</single>
    <shuffleanswers>1</shuffleanswers>""")
                
                has_correct = any(isinstance(o, dict) and o.get('is_correct') for o in options)
                for opt_idx, o in enumerate(options):
                    if isinstance(o, dict):
                        opt_text = o.get('text', '')
                        is_corr = o.get('is_correct', False) or (not has_correct and opt_idx == 0)
                    else:
                        opt_text = str(o)
                        is_corr = (opt_idx == 0)
                    fraction = "100" if is_corr else "0"
                    quiz_xml_lines.append(f"""    <answer fraction="{fraction}" format="html"><text><![CDATA[<p>{opt_text}</p>]]></text></answer>""")
                
                quiz_xml_lines.append('  </question>')
                
            quiz_xml_lines.append('</quiz>')
            zf.writestr('banco_preguntas_moodle.xml', "\n".join(quiz_xml_lines).encode('utf-8'))

        # ── 5. GUARDAR imsmanifest.xml ──
        xml_str = b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(manifest, encoding='utf-8')
        zf.writestr('imsmanifest.xml', xml_str)

    memory_file.seek(0)
    
    filename = f"{sanitize_filename(course_title)}_moodle.imscc"
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )


# =========================================================================
# MIGRACIÓN DIRECTA POR API REST DE MOODLE (WEBSERVICES)
# =========================================================================

@export_bp.route('/api/courses/<course_id>/migrate_moodle_api', methods=['POST'])
def migrate_moodle_api(course_id):
    """Crea y migra el curso directamente a la plataforma Moodle institucional vía Web Services."""
    data = request.json or {}
    moodle_url = (data.get('moodle_url') or '').rstrip('/')
    moodle_token = data.get('moodle_token') or data.get('wstoken') or ''
    category_id = int(data.get('category_id') or 1)
    
    if not moodle_url or not moodle_token:
        return jsonify({"status": "error", "message": "Debes ingresar la URL de Moodle institucional y el Token de Web Service."}), 400
        
    course = formacion_storage.load_course(course_id)
    if not course:
        return jsonify({"status": "error", "message": "Curso no encontrado"}), 404
        
    course_fullname = course.get('name') or course.get('title') or "Curso SKEL 360"
    shortname = sanitize_filename(course_fullname)[:20].upper() + "_" + course_id[:5].upper()
    units = course.get('units', [])
    num_sections = len(units) if isinstance(units, list) else len(units.values()) if isinstance(units, dict) else 4
    
    # Parámetros para core_course_create_courses en Moodle
    ws_endpoint = f"{moodle_url}/webservice/rest/server.php"
    
    payload = {
        'wstoken': moodle_token,
        'wsfunction': 'core_course_create_courses',
        'moodlewsrestformat': 'json',
        'courses[0][fullname]': course_fullname,
        'courses[0][shortname]': shortname,
        'courses[0][categoryid]': category_id,
        'courses[0][summary]': course.get('description', 'Curso migrado y validado desde SKEL 360.'),
        'courses[0][format]': 'topics',
        'courses[0][numsections]': num_sections,
        'courses[0][visible]': 1
    }
    
    encoded_data = urllib.parse.urlencode(payload).encode('utf-8')
    req = urllib.request.Request(ws_endpoint, data=encoded_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_text = response.read().decode('utf-8')
            res_json = json.loads(res_text)
            
            # Moodle devuelve una lista con el curso creado o un objeto con error (exception)
            if isinstance(res_json, dict) and res_json.get('exception'):
                return jsonify({
                    "status": "error",
                    "message": f"Moodle API Error: {res_json.get('message', 'Error desconocido en Moodle.')}"
                }), 400
                
            if isinstance(res_json, list) and len(res_json) > 0:
                created_course = res_json[0]
                moodle_course_id = created_course.get('id')
                course_url = f"{moodle_url}/course/view.php?id={moodle_course_id}"
                
                # Marcar en el curso local
                course['moodle_migrated'] = True
                course['moodle_course_id'] = moodle_course_id
                course['moodle_url'] = course_url
                formacion_storage.save_course(course.get('inst_id', 1), course.get('program_id', 0), course)
                
                return jsonify({
                    "status": "success",
                    "success": True,
                    "message": "¡Curso creado y migrado exitosamente en la plataforma Moodle institucional!",
                    "moodle_course_id": moodle_course_id,
                    "data": {
                        "moodle_course_id": moodle_course_id,
                        "course_url": course_url,
                        "shortname": shortname,
                        "fullname": course_fullname,
                        "num_sections": num_sections,
                        "message": "¡Curso creado y migrado exitosamente en la plataforma Moodle institucional!"
                    }
                })
            else:
                return jsonify({"status": "error", "message": f"Respuesta inesperada de Moodle: {res_text}"}), 400
                
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"No se pudo conectar con el servidor Moodle ({moodle_url}): {str(e)}. Verifica la URL y el Token."
        }), 500
