from flask import Blueprint, jsonify, request, send_file
import io
import zipfile
import xml.etree.ElementTree as ET
import formacion_storage
import re

export_bp = Blueprint('export', __name__)

def sanitize_filename(name):
    # Remove invalid characters for filenames
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.replace(' ', '_').lower()

@export_bp.route('/api/courses/<course_id>/export/moodle', methods=['GET'])
def export_moodle(course_id):
    # Load course data
    courses = formacion_storage.load_courses(1, 0)
    course = next((c for c in courses if c.get('id') == course_id), None)
    
    if not course:
        return jsonify({"status": "error", "message": "Curso no encontrado"}), 404
        
    course_title = course.get('name') or course.get('title') or "Curso"
    
    # Create in-memory zip file
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        
        # Build XML ElementTree for imsmanifest.xml
        manifest = ET.Element('manifest', {
            'identifier': 'MANIFEST-1',
            'xmlns': 'http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd'
        })
        
        metadata = ET.SubElement(manifest, 'metadata')
        schema = ET.SubElement(metadata, 'schema')
        schema.text = 'IMS Common Cartridge'
        schemaversion = ET.SubElement(metadata, 'schemaversion')
        schemaversion.text = '1.1.0'
        
        organizations = ET.SubElement(manifest, 'organizations')
        organization = ET.SubElement(organizations, 'organization', {'identifier': 'ORG-1', 'structure': 'rooted-hierarchy'})
        
        root_item = ET.SubElement(organization, 'item', {'identifier': 'root'})
        
        resources = ET.SubElement(manifest, 'resources')
        
        # Loop through units and topics
        res_counter = 1
        
        for u_idx, unit in enumerate(course.get('units', [])):
            unit_id = f"UNIT-{u_idx+1}"
            unit_item = ET.SubElement(root_item, 'item', {'identifier': unit_id})
            unit_title = ET.SubElement(unit_item, 'title')
            unit_title.text = unit.get('name', f'Unidad {u_idx+1}')
            
            for t_idx, topic in enumerate(unit.get('topics', [])):
                if isinstance(topic, str):
                    t_title = topic
                    t_content = f"<h3>{t_title}</h3><p>Sin contenido</p>"
                else:
                    t_title = topic.get('title', 'Tema')
                    t_content = topic.get('content', '') or f"<h3>{t_title}</h3><p>Sin contenido</p>"
                
                # Write HTML file to ZIP
                safe_title = sanitize_filename(t_title)[:30]
                file_path = f"topics/u{u_idx+1}_t{t_idx+1}_{safe_title}.html"
                
                html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{t_title}</title>
</head>
<body>
    {t_content}
</body>
</html>"""
                zf.writestr(file_path, html_body.encode('utf-8'))
                
                # Add to manifest
                item_id = f"ITEM-{res_counter}"
                res_id = f"RES-{res_counter}"
                
                topic_item = ET.SubElement(unit_item, 'item', {
                    'identifier': item_id,
                    'identifierref': res_id
                })
                t_title_el = ET.SubElement(topic_item, 'title')
                t_title_el.text = t_title
                
                resource = ET.SubElement(resources, 'resource', {
                    'identifier': res_id,
                    'type': 'webcontent',
                    'href': file_path
                })
                file_el = ET.SubElement(resource, 'file', {'href': file_path})
                
                res_counter += 1
                
        # Write imsmanifest.xml
        # In Python 3.8+ ET.tostring doesn't add the XML declaration easily, so we prepend it
        xml_str = b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(manifest, encoding='utf-8')
        zf.writestr('imsmanifest.xml', xml_str)

    memory_file.seek(0)
    
    # Send the zip file
    filename = sanitize_filename(course_title) + "_moodle.imscc"
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )
