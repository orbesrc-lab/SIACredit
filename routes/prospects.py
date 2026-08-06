from flask import Blueprint, jsonify, request, render_template
from utils.db import supabase, get_active_inst_id
from utils.auth import require_permission
import traceback
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

prospects_bp = Blueprint('prospects', __name__)

# --- CRM / PROSPECTOS RUTAS ---

@prospects_bp.route('/crm.html')
@require_permission('herramientas')
def crm_view():
    return render_template('crm.html')

@prospects_bp.route('/api/crm/prospects', methods=['GET', 'POST'])
@require_permission('herramientas')
def handle_prospects():
    if request.method == 'GET':
        try:
            res = supabase.table('prospects').select('*').order('created_at', desc=True).execute()
            return jsonify({"status": "success", "data": res.data})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
            
    elif request.method == 'POST':
        try:
            data = request.json
            if not data or 'institution' not in data:
                return jsonify({"status": "error", "message": "Institution is required"})
                
            prospect_data = {
                "name": data.get('name', 'Por Definir'),
                "position": data.get('position', ''),
                "institution": data.get('institution', ''),
                "snies_code": data.get('snies_code', ''),
                "email": data.get('email', ''),
                "linkedin": data.get('linkedin', ''),
                "notes": data.get('notes', ''),
                "status": "Pendiente"
            }
            res = supabase.table('prospects').insert(prospect_data).execute()
            return jsonify({"status": "success", "data": res.data})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

@prospects_bp.route('/api/crm/prospects/<int:pid>', methods=['PUT', 'DELETE'])
@require_permission('herramientas')
def update_delete_prospect(pid):
    if request.method == 'DELETE':
        try:
            supabase.table('prospects').delete().eq('id', pid).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    if request.method == 'PUT':
        data = request.json
        try:
            res = supabase.table('prospects').update(data).eq('id', pid).execute()
            return jsonify({"status": "success", "data": res.data})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

import csv
import io

@prospects_bp.route('/api/crm/upload_prospects', methods=['POST'])
@require_permission('herramientas')
def upload_prospects():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})
    
    try:
        # Detect encoding safely
        content = file.stream.read()
        try:
            decoded_content = content.decode("utf-8")
        except:
            decoded_content = content.decode("latin-1")
            
        stream = io.StringIO(decoded_content, newline=None)
        # Try to detect delimiter
        first_line = decoded_content.split('\n')[0]
        delimiter = ';' if ';' in first_line else ','
        
        reader = csv.DictReader(stream, delimiter=delimiter)
        
        inserted_count = 0
        prospects_to_insert = []
        for row in reader:
            name = row.get('Nombre', row.get('name', '')).strip()
            if not name:
                name = "Por Definir"
                
            institution = row.get('Institucion', row.get('Institución', row.get('institution', ''))).strip()
            if not institution:
                continue
                
            prospect_data = {
                "name": name,
                "position": row.get('Cargo', row.get('position', '')),
                "institution": institution,
                "snies_code": row.get('SNIES', row.get('snies_code', '')),
                "email": row.get('Correo', row.get('email', '')),
                "linkedin": row.get('LinkedIn', row.get('linkedin', '')),
                "notes": row.get('Notas', row.get('notes', '')),
                "status": "Pendiente"
            }
            prospects_to_insert.append(prospect_data)
            
        if prospects_to_insert:
            supabase.table('prospects').insert(prospects_to_insert).execute()
            inserted_count = len(prospects_to_insert)
            
        return jsonify({"status": "success", "message": f"{inserted_count} prospectos subidos correctamente"})
    except Exception as e:
        print(f"Error uploading prospects: {e}")
        return jsonify({"status": "error", "message": str(e)})


@prospects_bp.route('/api/crm/prospects/bulk_delete', methods=['POST'])
@require_permission('herramientas')
def bulk_delete_prospects():
    data = request.json
    if not data or 'ids' not in data:
        return jsonify({'status': 'error', 'message': 'No ids provided'})
    
    ids = data['ids']
    if not isinstance(ids, list) or len(ids) == 0:
        return jsonify({'status': 'error', 'message': 'Invalid ids array'})
        
    try:
        deleted_count = 0
        for pid in ids:
            supabase.table('prospects').delete().eq('id', pid).execute()
            deleted_count += 1
        return jsonify({'status': 'success', 'deleted_count': deleted_count})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@prospects_bp.route('/api/crm/send_email', methods=['POST'])
@require_permission('herramientas')
def send_email_route():
    data = request.json
    if not data or 'email' not in data or 'subject' not in data or 'body' not in data:
        return jsonify({'status': 'error', 'message': 'Missing email, subject, or body'})
    
    to_email = data['email']
    subject = data['subject']
    body = data['body']
    
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = os.getenv('SMTP_PORT', '465')
    smtp_username = os.getenv('SMTP_EMAIL') or os.getenv('SMTP_USERNAME') or 'orbesrc@gmail.com'
    smtp_password = os.getenv('SMTP_PASSWORD', 'xplguaejibtfyqdn')
    
    if not smtp_server or not smtp_username or not smtp_password:
        return jsonify({'status': 'error', 'message': 'SMTP configuration is missing on the server. Please check your .env file.'})
        
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(smtp_server, int(smtp_port))
        else:
            server = smtplib.SMTP(smtp_server, int(smtp_port))
            server.starttls()
            
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return jsonify({'status': 'success', 'message': 'Email sent successfully'})
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'status': 'error', 'message': f"Failed to send email: {str(e)}"})
