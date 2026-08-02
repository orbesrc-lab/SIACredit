from flask import Blueprint, jsonify, request, Response
from utils.db import supabase, get_active_inst_id
import json
import os
from openai import OpenAI
from urllib.parse import unquote
import re

import base64

ai_bp = Blueprint('ai', __name__)

DEFAULT_STATIC_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")


def call_ai(messages, max_tokens=1500, temperature=0.7, inst_id=None):
    import json
    provider = "gemini"
    api_key = DEFAULT_STATIC_GEMINI_KEY
    model = "gemini-2.5-flash"
    
    db_error = None
    check = None
    try:
        # 1) Try institution-specific config first (if inst_id provided)
        inst_config = None
        if inst_id:
            inst_check = supabase.table('statistics').select("data_json").eq("table_id", f"INST_AI_CONFIG_{inst_id}").eq("inst_id", inst_id).order("id", desc=True).limit(1).execute()
            if inst_check.data:
                inst_config = json.loads(inst_check.data[0]['data_json'])

        # 2) Fall back to global config
        check = supabase.table('statistics').select("data_json").eq("table_id", "GLOBAL_CONFIG").order("id", desc=True).limit(1).execute()
        global_config = {}
        if check.data:
            global_config = json.loads(check.data[0]['data_json'])

        # Institution config overrides global config.
        # If the institution has blocked_global=True, they CANNOT use the global key.
        if inst_config and inst_config.get('blocked_global'):
            data = inst_config  # Only institution's own config, no global fallback
        else:
            data = {**global_config, **(inst_config or {})}

        if data.get('ai_provider'): provider = data.get('ai_provider')
        if data.get('ai_api_key'): api_key = data.get('ai_api_key')
        
        _db_model = (data.get('ai_model') or "").strip()
        if _db_model:
            model = _db_model
        else:
            # Fallback per provider if model is empty in DB
            if provider == 'openai': model = 'gpt-4o-mini'
            elif provider == 'gemini': model = 'gemini-2.5-flash'
            elif provider == 'anthropic': model = 'claude-3-5-sonnet-20240620'
            else: model = 'glm-4'
            
        # Prevent using deprecated Gemini models saved previously in DB
        if provider == 'gemini' and model in ['gemini-1.5-flash', 'gemini-3.5-flash', 'gemini-flash-latest']:
            model = 'gemini-2.5-flash'

        # If institution is blocked from global and has no own key → raise clear error
        if inst_config and inst_config.get('blocked_global') and not inst_config.get('ai_api_key'):
            raise Exception("Esta institucion no tiene acceso a la IA del sistema. Configura tu propia llave de IA en el panel de Configuracion.")
            
        if data.get('ai_global_enabled') is False:
            raise Exception("La Inteligencia Artificial está desactivada temporalmente por el Super Administrador.")
    except Exception as e:
        db_error = str(e)
        print(f"Error fetching AI config: {e}")

    if api_key:
        # Sanitize api_key to prevent httpx ascii encode errors in headers
        api_key = str(api_key).encode('ascii', 'ignore').decode('ascii').strip()

    # Fallback to static system Gemini key if key is empty or masked placeholder
    if not api_key or set(api_key) <= {'•', '*', '\u2022'}:
        api_key = DEFAULT_STATIC_GEMINI_KEY

        if provider:
            provider = str(provider).strip().lower()
        if model:
            model = str(model).encode('ascii', 'ignore').decode('ascii').strip()

        # Prevent using deprecated Gemini models saved previously in DB
        if provider == 'gemini' and model in ['gemini-1.5-flash', 'gemini-3.5-flash', 'gemini-flash-latest']:
            model = 'gemini-2.5-flash'

        if not api_key:
            api_key = DEFAULT_STATIC_GEMINI_KEY



    if provider == 'anthropic':
        import urllib.request
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        system_text = ""
        anthropic_messages = []
        for m in messages:
            if m["role"] == "system":
                system_text += m["content"] + "\n"
            else:
                anthropic_messages.append(m)

        data = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": anthropic_messages
        }
        if system_text:
            data["system"] = system_text

        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            res_body = json.loads(response.read().decode('utf-8'))
            return res_body['content'][0]['text']
    else:
        if provider == 'openai':
            base_url = "https://api.openai.com/v1/"
        elif provider == 'gemini':
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        else:
            base_url = "https://open.bigmodel.cn/api/paas/v4/"
        
        if not api_key:
            raise Exception("No se ha configurado una llave API válida. Por favor ingresa tu llave de IA en el panel de Configuración.")
            
        client = OpenAI(api_key=api_key, base_url=base_url)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"{str(e)} [DEBUG: provider={provider}, base_url={base_url}, rows={len(check.data) if check else 'unknown'}, db_error={db_error}]")



@ai_bp.route('/api/analyze', methods=['POST'])
def analyze_stats():
    req_data = request.json
    table_id = req_data.get('table_id')
    all_data = req_data.get('all_data', {})
    
    try:
        if table_id:
            data_context = json.dumps(all_data.get(table_id, []), ensure_ascii=False)
            prompt = f"Actúa como un evaluador experto y consultor analítico de alto nivel. Analiza de manera formal y rigurosa los siguientes datos estadísticos del cuadro '{table_id}' e identifica tendencias, fortalezas o aspectos críticos. Emplea un lenguaje técnico y académico. Responde directamente con el análisis en formato Markdown. Datos: {data_context}"
        else:
            data_context = json.dumps(all_data, ensure_ascii=False)
            if len(data_context) > 30000:
                data_context = data_context[:30000] + "... [truncado]"
            prompt = f"Actúa como un evaluador experto y consultor analítico de alto nivel. Analiza de manera formal, integral y rigurosa los siguientes cuadros de datos estadísticos institucionales. Resalta los aspectos más importantes, tendencias globales y posibles oportunidades de mejora. Emplea un lenguaje técnico y académico. Responde directamente con el análisis en formato Markdown. Datos: {data_context}"

        answer = call_ai(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1500
        )
        
        safe_answer = answer.replace('<', '&lt;').replace('>', '&gt;')
        return jsonify({"analysis": safe_answer})
    except Exception as e:
        print(f"Error AI Analysis: {e}")
        return jsonify({"analysis": f"Error procesando análisis: {str(e)}"})

@ai_bp.route('/api/direct_upload/url', methods=['POST'])
def library_upload_url():
    try:
        data = request.json
        filename = data.get('filename')
        aspect_id = data.get('aspect_id')
        period = data.get('period', 'Biblioteca')
        
        inst_id = data.get('inst_id', 1)
        program_id = data.get('program_id', 0)
        
        if not inst_id or inst_id == 0:
            first_inst = supabase.table('institution').select("id").limit(1).execute()
            inst_id = first_inst.data[0]['id'] if first_inst.data else 1
            
        import re
        import time
        clean_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Append timestamp to avoid 'Duplicate resource' 400 error on PUT
        timestamp = int(time.time())
        parts = clean_filename.rsplit('.', 1)
        if len(parts) == 2:
            clean_filename = f"{parts[0]}_{timestamp}.{parts[1]}"
        else:
            clean_filename = f"{clean_filename}_{timestamp}"
        
        # Consistent path logic with original API
        file_path = f"inst_{inst_id}/prog_{program_id}/{aspect_id}/{period}/{clean_filename}"
        
        res = supabase.storage.from_('evidencias').create_signed_upload_url(file_path)
        signed_url = res.get('signedUrl')
        
        # Public URL to access the file later
        file_url = supabase.storage.from_('evidencias').get_public_url(file_path)
        
        return jsonify({
            "status": "success",
            "signed_url": signed_url,
            "file_url": file_url,
            "file_path": file_path
        })
    except Exception as e:
        print(f"Error generating upload url: {e}")
        return jsonify({"error": str(e)})

@ai_bp.route('/api/library/confirm_upload', methods=['POST'])
def library_confirm_upload():
    try:
        data = request.json
        aspect_id = data.get('aspect_id')
        filename = data.get('filename')
        file_url = data.get('file_url')
        inst_id = data.get('inst_id', 1)
        program_id = data.get('program_id', 0)

        if not inst_id or inst_id == 0:
            first_inst = supabase.table('institution').select("id").limit(1).execute()
            inst_id = first_inst.data[0]['id'] if first_inst.data else 1
            
        if not program_id or program_id == 0:
            first_prog = supabase.table('programs').select("id").limit(1).execute()
            program_id = first_prog.data[0]['id'] if first_prog.data else 1

        import time
        doc_record = {
            "id": int(time.time() * 1000),
            "name": filename,
            "file_url": file_url,
            "aspect_id": aspect_id
        }
        
        query = supabase.table('statistics').select("id, data_json").eq("table_id", aspect_id)
        if aspect_id != 'BIBLIOTECA_GLOBAL':
            query = query.eq("inst_id", inst_id)
        
        check = query.execute()
        if check.data:
            current_data = json.loads(check.data[0]['data_json'])
            if not isinstance(current_data, list): current_data = []
            current_data.append(doc_record)
            supabase.table('statistics').update({"data_json": json.dumps(current_data)}).eq("id", check.data[0]["id"]).execute()
        else:
            supabase.table('statistics').insert({
                "table_id": aspect_id,
                "data_json": json.dumps([doc_record]),
                "inst_id": inst_id,
                "program_id": program_id
            }).execute()

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error confirm upload: {e}")
        return jsonify({"error": str(e)})

@ai_bp.route('/api/evidences/confirm_upload', methods=['POST'])
def evidences_confirm_upload():
    try:
        data = request.json
        aspect_id = data.get('aspect_id')
        filename = data.get('filename')
        file_url = data.get('file_url')
        period = data.get('period', 'N/A')
        email = data.get('email', 'unknown')
        is_annex = data.get('is_annex', False)
        
        inst_id = data.get('inst_id', 1)
        program_id = data.get('program_id', 0)

        if not inst_id or inst_id == 0:
            first_inst = supabase.table('institution').select("id").limit(1).execute()
            inst_id = first_inst.data[0]['id'] if first_inst.data else 1

        # Generar "dependency" extraído del aspect_id (e.g. FACTOR_1 -> 1)
        import re
        match = re.search(r'\d+', str(aspect_id))
        dependency = match.group() if match else "1"

        # Siempre insertamos como una nueva evidencia para permitir múltiples adjuntos (y diferentes años)
        insert_data = {
            "name": filename,
            "file_url": file_url,
            "period": period,
            "dependency": dependency,
            "aspect_id": aspect_id,
            "user_email": email,
            "status": "pendiente",
            "inst_id": inst_id,
            "program_id": program_id
        }
        if is_annex:
            insert_data['is_annex'] = True
        supabase.table('evidences').insert(insert_data).execute()

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error confirm evidences upload: {e}")
        return jsonify({"error": str(e)})

@ai_bp.route('/api/surveys/upload', methods=['POST'])
def survey_upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    survey_id = request.form.get('survey_id', 'unknown')
    
    import re
    import time
    clean_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
    timestamp = int(time.time())
    parts = clean_filename.rsplit('.', 1)
    if len(parts) == 2:
        clean_filename = f"{parts[0]}_{timestamp}.{parts[1]}"
    else:
        clean_filename = f"{clean_filename}_{timestamp}"
        
    file_path = f"surveys/{survey_id}/{clean_filename}"
    try:
        file_content = file.read()
        supabase.storage.from_('evidencias').upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": file.content_type, "upsert": "true"}
        )
        file_url = supabase.storage.from_('evidencias').get_public_url(file_path)
        return jsonify({"status": "success", "url": file_url, "name": file.filename})
    except Exception as e:
        print(f"Error uploading survey file: {e}")
        return jsonify({"error": str(e)})

@ai_bp.route('/api/upload', methods=['POST'])
def upload_file():
    inst_id = request.form.get('inst_id', 1, type=int)
    program_id = request.form.get('program_id', 0, type=int)
    
    # Validar y corregir inst_id si es 0 o None para evitar errores de llave foránea
    if not inst_id or inst_id == 0:
        try:
            first_inst = supabase.table('institution').select("id").limit(1).execute()
            inst_id = first_inst.data[0]['id'] if first_inst.data else 1
        except Exception as e:
            print(f"Error fetching fallback institution: {e}")
            inst_id = 1

    # Validar y corregir program_id si es 0 o None para evitar errores de llave foránea
    if not program_id or program_id == 0:
        try:
            first_prog = supabase.table('programs').select("id").limit(1).execute()
            program_id = first_prog.data[0]['id'] if first_prog.data else 1
        except Exception as e:
            print(f"Error fetching fallback program: {e}")
            program_id = 1

    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    aspect_id = request.form.get('aspect_id')
    period = request.form.get('period', 'General')
    email = request.form.get('email')
    dependency = request.form.get('dependency', 'General')

    def sanitize_filename(filename):
        import re
        name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        return name

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    clean_filename = sanitize_filename(file.filename)
    # Nueva ruta incluyendo el periodo para evitar colisiones
    file_path = f"inst_{inst_id}/prog_{program_id}/{aspect_id}/{period}/{clean_filename}"
    try:
        file_content = file.read()
        supabase.storage.from_('evidencias').upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": file.content_type, "upsert": "true"}
        )
        file_url = supabase.storage.from_('evidencias').get_public_url(file_path)
        
        # Solo guardar en la tabla evidences si es un aspecto real (no una estadística)
        if aspect_id:
            if str(aspect_id).startswith('STAT_'):
                pass
            elif str(aspect_id).startswith('BIBLIOTECA_'):
                import time
                doc_record = {
                    "id": int(time.time() * 1000),
                    "name": file.filename,
                    "file_url": file_url,
                    "aspect_id": aspect_id
                }
                query = supabase.table('statistics').select("id, data_json").eq("table_id", aspect_id)
                if aspect_id != 'BIBLIOTECA_GLOBAL':
                    query = query.eq("inst_id", inst_id)
                
                check = query.execute()
                if check.data:
                    current_data = json.loads(check.data[0]['data_json'])
                    if not isinstance(current_data, list): current_data = []
                    current_data.append(doc_record)
                    supabase.table('statistics').update({"data_json": json.dumps(current_data)}).eq("id", check.data[0]["id"]).execute()
                else:
                    # Usar inst_id válido actual para evitar errores de llave foránea (inst_id=0 no existe)
                    save_inst_id = inst_id
                    
                    # Obtener un program_id válido
                    first_prog = supabase.table('programs').select("id").limit(1).execute()
                    save_prog_id = first_prog.data[0]['id'] if first_prog.data else 1
                    
                    supabase.table('statistics').insert({
                        "table_id": aspect_id,
                        "data_json": json.dumps([doc_record]),
                        "inst_id": save_inst_id,
                        "program_id": save_prog_id
                    }).execute()
            else:
                supabase.table('evidences').insert({
                    "aspect_id": aspect_id,
                    "name": file.filename,
                    "file_url": file_url,
                    "user_email": email,
                    "dependency": dependency,
                    "status": "pendiente",
                    "period": period,
                    "inst_id": inst_id,
                    "program_id": program_id
                }).execute()
            
        return jsonify({"status": "success", "url": file_url})
    except Exception as e:
        print(f"Error uploading: {e}")
        return jsonify({"error": str(e)})

@ai_bp.route('/api/evidences', methods=['GET'])
def get_evidences():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    aspect_id = request.args.get('aspect_id')
    query = supabase.table('evidences').select("*").eq("inst_id", inst_id).eq("program_id", program_id)
    if aspect_id:
        query = query.eq("aspect_id", aspect_id)
    res = query.execute()
    return jsonify(res.data)

@ai_bp.route('/api/library', methods=['GET'])
def get_library():
    inst_id = request.args.get('inst_id', 1, type=int)
    try:
        global_res = supabase.table('statistics').select("data_json").eq("table_id", "BIBLIOTECA_GLOBAL").execute()
        
        def parse_data(data_row):
            if not data_row: return []
            dj = data_row[0].get('data_json', [])
            if isinstance(dj, str):
                import json
                try: return json.loads(dj)
                except: return []
            return dj
            
        global_docs = parse_data(global_res.data)
        
        inst_res = supabase.table('statistics').select("data_json").eq("table_id", "BIBLIOTECA_INST").eq("inst_id", inst_id).execute()
        inst_docs = parse_data(inst_res.data)
        
        return jsonify({
            "global": global_docs,
            "institucional": inst_docs
        })
    except Exception as e:
        print(f"Error loading library: {e}")
        return jsonify({"global": [], "institucional": []})

@ai_bp.route('/api/library/<aspect_id>/<int:doc_id>', methods=['DELETE'])
def delete_library_doc(aspect_id, doc_id):
    inst_id = request.args.get('inst_id', 1, type=int)
    # Global puede no tener inst_id, pero para buscar en statistics usamos inst_id si no es global
    query = supabase.table('statistics').select("id, data_json").eq("table_id", aspect_id)
    if aspect_id != 'BIBLIOTECA_GLOBAL':
        query = query.eq("inst_id", inst_id)
    
    try:
        check = query.execute()
        if check.data:
            current_data = json.loads(check.data[0]['data_json'])
            # Filtrar el doc a borrar
            new_data = [d for d in current_data if d.get('id') != doc_id]
            supabase.table('statistics').update({"data_json": json.dumps(new_data)}).eq("id", check.data[0]["id"]).execute()
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "No encontrado"})
    except Exception as e:
        print(f"Error deleting library doc: {e}")
        return jsonify({"status": "error", "message": str(e)})


import urllib.request
import urllib.parse
import urllib.error
import json

@ai_bp.route('/api/library/search', methods=['GET'])
def library_search():
    q = request.args.get('q', '')
    limit = request.args.get('limit', 20)
    
    if 'filetype:pdf' in q.lower():
        try:
            print(f"Searching Europe PMC for: {q}")
            clean_q = q.lower().replace('filetype:pdf', '').strip()
            epmc_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={urllib.parse.quote(clean_q)}+HAS_PDF:y&format=json&resultType=core&pageSize={limit}"
            epmc_req = urllib.request.Request(epmc_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(epmc_req) as response:
                epmc_data = json.loads(response.read().decode('utf-8'))
                results = []
                for item in epmc_data.get('resultList', {}).get('result', []):
                    title = item.get('title', 'Sin título')
                    year = item.get('pubYear', 'S.F.')
                    
                    author_string = item.get('authorString', '')
                    authorships = [{'author': {'display_name': a.strip()}} for a in author_string.split(',')] if author_string else [{'author': {'display_name': 'Autor Desconocido'}}]
                    
                    pdf_url = ''
                    for u in item.get('fullTextUrlList', {}).get('fullTextUrl', []):
                        if u.get('documentStyle') == 'pdf':
                            pdf_url = u.get('url')
                            break
                            
                    doi = item.get('doi', '')
                    
                    results.append({
                        'id': item.get('id', f"epmc_{len(results)}"),
                        'title': title,
                        'publication_year': year,
                        'authorships': authorships,
                        'primary_location': {'source': {'display_name': item.get('journalTitle', 'Europe PMC')}},
                        'doi': f"https://doi.org/{doi}" if doi else '',
                        'open_access': {'oa_url': pdf_url},
                        'type': 'pdf'
                    })
                return jsonify({'results': results, 'meta': {'source': 'europepmc'}})
        except Exception as e:
            print(f"Europe PMC scrape error: {e}")
            return jsonify({'error': 'Error al buscar PDFs en Europe PMC.'})

    try:
        q = request.args.get('q', '')
        limit = request.args.get('limit', '20')
        if not limit.isdigit():
            limit = '20'
        if int(limit) > 100:
            limit = '100'
            
        if not q:
            return jsonify({'results': []})
        
        # Prepare the OpenAlex API URL with has_pdf_url:true and user limit
        url = f"https://api.openalex.org/works?search={urllib.parse.quote(q)}&filter=is_oa:true,has_pdf_url:true&per-page={limit}"
        
        mailto = os.environ.get('OPENALEX_MAILTO', 'orbesrc@gmail.com')
        api_key = os.environ.get('OPENALEX_API_KEY')
        url += f"&mailto={urllib.parse.quote(mailto)}"
        if api_key:
            url += f"&api_key={api_key}"
            
        req = urllib.request.Request(url, headers={'User-Agent': f'SIACredit/1.0 (mailto:{mailto})'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return jsonify(data)
    except urllib.error.HTTPError as e:
        print(f"OpenAlex HTTP Error: {e.code} - {e.reason}")
        if e.code in [429, 503]:
            try:
                print("Falling back to Crossref API...")
                cr_url = f"https://api.crossref.org/works?query={urllib.parse.quote(q)}&select=title,author,URL,published-print,published-online,DOI,container-title,type,link&rows={limit}"
                cr_req = urllib.request.Request(cr_url, headers={'User-Agent': f'SIACredit/1.0 (mailto:{mailto})'})
                with urllib.request.urlopen(cr_req) as cr_res:
                    cr_data = json.loads(cr_res.read().decode('utf-8'))
                    
                results = []
                for item in cr_data.get('message', {}).get('items', []):
                    title = item.get('title', ['Sin título'])[0]
                    year = None
                    for date_field in ['published-print', 'published-online']:
                        if date_field in item and 'date-parts' in item[date_field] and item[date_field]['date-parts']:
                            year = item[date_field]['date-parts'][0][0]
                            break
                    
                    authorships = []
                    for a in item.get('author', []):
                        display_name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                        if display_name:
                            authorships.append({'author': {'display_name': display_name}})
                            
                    source_name = item.get('container-title', [''])[0]
                    if not source_name:
                        source_name = item.get('publisher', 'Publicación Independiente')
                        
                    doi = item.get('URL', '')
                    pdf_url = ""
                    for link in item.get('link', []):
                        if link.get('content-type') == 'application/pdf':
                            pdf_url = link.get('URL')
                            break
                            
                    results.append({
                        'title': title,
                        'publication_year': year,
                        'authorships': authorships,
                        'primary_location': {'source': {'display_name': source_name}},
                        'doi': doi,
                        'open_access': {'oa_url': pdf_url} if pdf_url else {},
                        'type': item.get('type', 'article')
                    })
                return jsonify({'results': results, 'fallback': 'crossref'})
            except Exception as cr_err:
                print(f"Crossref fallback failed: {cr_err}")
                return jsonify({'error': 'La red académica global está experimentando alta demanda en este momento. Por favor, intenta de nuevo en unos minutos.'}), 503
        return jsonify({'error': str(e)}), e.code
    except Exception as e:
        print(f"Error fetching OpenAlex: {e}")
        return jsonify({'error': str(e)})

@ai_bp.route('/api/library/translate', methods=['POST'])
def library_translate():
    try:
        data = request.json
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'es') # 'es' o 'en'
        
        if not text:
            return jsonify({"status": "error", "message": "Texto vacío"})
            
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            translated_text = ''.join([sentence[0] for sentence in data[0] if sentence[0]])
            
        return jsonify({"status": "success", "translated": translated_text.strip()})
    except Exception as e:
        print(f"Error Translate: {e}")
        return jsonify({"status": "error", "message": str(e)})


@ai_bp.route('/api/library/ovas', methods=['GET'])
def get_ovas():
    try:
        url = "https://phet.colorado.edu/services/metadata/1.2/simulations?format=json&type=html&locale=es"
        req = urllib.request.Request(url, headers={'User-Agent': 'SIACredit/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            sims = []
            for proj in data.get('projects', []):
                for sim in proj.get('simulations', []):
                    title = sim.get('title', 'Sin título')
                    if 'es' in sim.get('localizedTitles', {}):
                        title = sim['localizedTitles']['es']
                    elif 'en' in sim.get('localizedTitles', {}):
                        title = sim['localizedTitles']['en']
                        
                    sims.append({
                        'id': sim.get('name', ''),
                        'title': title,
                        'description': sim.get('description', {}).get('es', sim.get('description', {}).get('en', 'Simulador interactivo PhET')),
                        'runUrl': f"https://phet.colorado.edu/sims/html/{sim.get('name')}/latest/{sim.get('name')}_es.html",
                        'thumbUrl': f"https://phet.colorado.edu/sims/html/{sim.get('name')}/latest/{sim.get('name')}-600.png"
                    })
            
            # Sort by title
            sims.sort(key=lambda x: x['title'])
            return jsonify({'status': 'success', 'ovas': sims})
    except Exception as e:
        print(f"Error fetching OVAs: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@ai_bp.route('/api/library/saved', methods=['GET', 'POST'])


def handle_saved_resources():
    if request.method == 'POST':
        data = request.json
        user_email = data.get('email')
        if not user_email:
            return jsonify({"status": "error", "message": "Email requerido"})
            
        try:
            supabase.table('saved_resources').insert({
                "user_email": user_email,
                "resource_id": data.get('resource_id'),
                "title": data.get('title'),
                "authors": data.get('authors', ''),
                "year": data.get('year'),
                "url": data.get('url', ''),
                "apa_citation": data.get('apa_citation', '')
            }).execute()
            return jsonify({"status": "success"})
        except Exception as e:
            print(f"Error saving resource: {e}")
            return jsonify({"status": "error", "message": str(e)})
            
    # GET
    user_email = request.args.get('email')
    if not user_email:
        return jsonify([])
    try:
        res = supabase.table('saved_resources').select('*').eq('user_email', user_email).order('saved_at', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        print(f"Error fetching saved resources: {e}")
        return jsonify([])

@ai_bp.route('/api/library/saved/<int:id>', methods=['DELETE'])
def delete_saved_resource(id):
    try:
        supabase.table('saved_resources').delete().eq('id', id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error deleting saved resource: {e}")
        return jsonify({"status": "error", "message": str(e)})

@ai_bp.route('/api/global-settings', methods=['GET', 'POST'])
def global_settings():
    try:
        check = supabase.table('statistics').select("id, data_json").eq("table_id", "GLOBAL_CONFIG").order("id", desc=True).limit(1).execute()
        current_data = {}
        row_id = None
        if check.data:
            row_id = check.data[0]['id']
            try:
                current_data = json.loads(check.data[0]['data_json'])
            except:
                pass

        if request.method == 'GET':
            # Remove api_key for security when sending to frontend, but send a flag that it exists
            resp_data = dict(current_data)
            resp_data['has_api_key'] = 'ai_api_key' in resp_data and bool(resp_data['ai_api_key'].strip())
            if 'ai_api_key' in resp_data:
                del resp_data['ai_api_key'] # Hide actual key from frontend
            return jsonify(resp_data)

        # POST
        data = request.json
        if 'theme' in data: current_data['theme'] = data.get('theme')
        if 'ai_provider' in data: current_data['ai_provider'] = data.get('ai_provider')
        if 'ai_model' in data: 
            model_val = data.get('ai_model')
            if current_data.get('ai_provider') == 'gemini' and model_val in ['gemini-1.5-flash', 'gemini-3.5-flash', 'gemini-flash-latest']:
                model_val = 'gemini-2.5-flash'
            current_data['ai_model'] = model_val
        if 'ai_api_key' in data: current_data['ai_api_key'] = data.get('ai_api_key')
        if 'ai_voice_colombia' in data: current_data['ai_voice_colombia'] = data.get('ai_voice_colombia')
        if 'ai_global_enabled' in data: current_data['ai_global_enabled'] = data.get('ai_global_enabled')
        if 'carousel_images' in data:
            c_imgs = data.get('carousel_images')
            if c_imgs and len(c_imgs) > 0:
                current_data['carousel_images'] = c_imgs
            elif data.get('clear_carousel'):
                current_data['carousel_images'] = []
        if 'carousel_speed' in data: current_data['carousel_speed'] = data.get('carousel_speed')
        if 'carousel_size' in data: current_data['carousel_size'] = data.get('carousel_size')
        
        config_data = json.dumps(current_data)
        
        if row_id:
            supabase.table('statistics').update({"data_json": config_data}).eq("id", row_id).execute()
        else:
            first_inst = supabase.table('institution').select("id").limit(1).execute()
            valid_inst_id = first_inst.data[0]['id'] if first_inst.data else 1
            
            first_prog = supabase.table('programs').select("id").limit(1).execute()
            valid_prog_id = first_prog.data[0]['id'] if first_prog.data else 1
            
            supabase.table('statistics').insert({
                "table_id": "GLOBAL_CONFIG",
                "data_json": config_data,
                "inst_id": valid_inst_id,
                "program_id": valid_prog_id
            }).execute()
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@ai_bp.route('/api/global-settings/carousel-upload', methods=['POST'])
def global_settings_carousel_upload():
    import uuid
    import os
    try:
        if 'image' not in request.files:
            return jsonify({"status": "error", "message": "No image provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400

        # Read file bytes
        file_bytes = file.read()
        
        # Generate unique filename
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = '.jpg'
        filename = f"{uuid.uuid4()}{ext}"
        storage_path = f"carousel/{filename}"
        
        # Upload to Supabase
        supabase.storage.from_('evidencias').upload(
            storage_path,
            file_bytes,
            {"content-type": file.content_type or "image/jpeg"}
        )
        
        file_url = supabase.storage.from_('evidencias').get_public_url(storage_path)
        
        return jsonify({"status": "success", "url": file_url})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@ai_bp.route('/api/inst-ai-settings', methods=['GET', 'POST'])
def inst_ai_settings():
    """Per-institution AI config. Admins set their own provider/key here.
    Falls back to global config if not set."""
    inst_id = request.args.get('inst_id', 1, type=int) if request.method == 'GET' else (request.json or {}).get('inst_id', 1)
    try:
        check = supabase.table('statistics').select("id, data_json").eq("table_id", f"INST_AI_CONFIG_{inst_id}").eq("inst_id", inst_id).order("id", desc=True).limit(1).execute()
        current_data = {}
        row_id = None
        if check.data:
            row_id = check.data[0]['id']
            try:
                current_data = json.loads(check.data[0]['data_json'])
            except:
                pass

        if request.method == 'GET':
            resp = dict(current_data)
            resp['has_api_key'] = bool(resp.get('ai_api_key', '').strip())
            if 'ai_api_key' in resp:
                del resp['ai_api_key']
            return jsonify(resp)

        # POST: save institution config
        data = request.json or {}
        if 'ai_provider' in data: current_data['ai_provider'] = data['ai_provider']
        if 'ai_model'    in data: current_data['ai_model']    = data['ai_model']
        if 'clear_key' in data and data['clear_key']:
            # Admin wants to remove their custom key and fall back to global
            current_data.pop('ai_api_key', None)
            current_data.pop('ai_provider', None)
            current_data.pop('ai_model', None)
        elif 'ai_api_key' in data:
            new_key = data['ai_api_key'].strip()
            # Verify new_key does not consist of just placeholder dots/stars
            import re
            if new_key and not re.match(r'^[\u2022\u25cf*]+$', new_key) and not '' in new_key and not '•' in new_key:
                current_data['ai_api_key'] = new_key

        config_str = json.dumps(current_data)
        if row_id:
            supabase.table('statistics').update({"data_json": config_str}).eq("id", row_id).execute()
        else:
            # Get a valid program_id for this institution (FK constraint requires valid program_id)
            prog_res = supabase.table('programs').select("id").eq("inst_id", inst_id).limit(1).execute()
            valid_prog_id = prog_res.data[0]['id'] if prog_res.data else None
            if valid_prog_id is None:
                # Fallback: any program
                any_prog = supabase.table('programs').select("id").limit(1).execute()
                valid_prog_id = any_prog.data[0]['id'] if any_prog.data else 1
            supabase.table('statistics').insert({"inst_id": inst_id, "program_id": valid_prog_id, "table_id": f"INST_AI_CONFIG_{inst_id}", "data_json": config_str}).execute()

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@ai_bp.route('/api/inst-ai-block', methods=['POST'])
def inst_ai_block():
    """Superadmin: block or unblock an institution from using the global AI key."""
    data = request.json or {}
    inst_id = data.get('inst_id')
    blocked = bool(data.get('blocked', False))
    if not inst_id:
        return jsonify({"status": "error", "message": "inst_id required"})
    try:
        check = supabase.table('statistics').select("id, data_json").eq("table_id", f"INST_AI_CONFIG_{inst_id}").eq("inst_id", inst_id).order("id", desc=True).limit(1).execute()
        current_data = {}
        row_id = None
        if check.data:
            row_id = check.data[0]['id']
            try: current_data = json.loads(check.data[0]['data_json'])
            except: pass
        current_data['blocked_global'] = blocked
        config_str = json.dumps(current_data)
        if row_id:
            supabase.table('statistics').update({"data_json": config_str}).eq("id", row_id).execute()
        else:
            prog_res = supabase.table('programs').select("id").eq("inst_id", inst_id).limit(1).execute()
            valid_prog_id = prog_res.data[0]['id'] if prog_res.data else None
            if not valid_prog_id:
                any_prog = supabase.table('programs').select("id").limit(1).execute()
                valid_prog_id = any_prog.data[0]['id'] if any_prog.data else 1
            supabase.table('statistics').insert({"inst_id": inst_id, "program_id": valid_prog_id, "table_id": f"INST_AI_CONFIG_{inst_id}", "data_json": config_str}).execute()
        return jsonify({"status": "success", "inst_id": inst_id, "blocked": blocked})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@ai_bp.route('/api/inst-ai-status', methods=['GET'])
def inst_ai_status_all():
    """Superadmin: get AI config status for all institutions."""
    try:
        insts = supabase.table('institution').select("id, name").execute()
        configs = supabase.table('statistics').select("inst_id, data_json").like("table_id", "INST_AI_CONFIG_%").execute()
        config_map = {}
        for c in configs.data:
            try: config_map[c['inst_id']] = json.loads(c['data_json'])
            except: pass
        result = []
        for inst in (insts.data or []):
            cfg = config_map.get(inst['id'], {})
            result.append({
                "inst_id": inst['id'],
                "name": inst.get('name', f"Institucion {inst['id']}"),
                "blocked_global": cfg.get('blocked_global', False),
                "has_own_key": bool(cfg.get('ai_api_key', '').strip()),
                "own_provider": cfg.get('ai_provider', ''),
            })
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@ai_bp.route('/api/evidences/<int:evidence_id>', methods=['DELETE'])
def delete_evidence(evidence_id):
    try:
        supabase.table('evidences').delete().eq("id", evidence_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error deleting evidence: {e}")
        return jsonify({"status": "error", "message": str(e)})

@ai_bp.route('/api/evidences/status', methods=['POST'])
def update_evidence_status():
    data = request.json
    try:
        supabase.table('evidences').update({
            "status": data['status']
        }).eq("id", data['id']).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error updating status: {e}")
        return jsonify({"status": "error", "message": str(e)})

@ai_bp.route('/api/proxy/external_pdf', methods=['GET'])
def proxy_external_pdf():
    file_url = request.args.get('url', '')
    if not file_url:
        return jsonify({'error': 'URL requerida'})
    try:
        import urllib.request
        import urllib.parse
        
        # Ensure the URL is properly encoded if it contains spaces
        parsed = urllib.parse.urlparse(file_url)
        safe_path = urllib.parse.quote(parsed.path, safe='/:@%')
        safe_url = parsed._replace(path=safe_path).geturl()
        
        req = urllib.request.Request(safe_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            return Response(data, mimetype='application/pdf', headers={
                'Content-Disposition': 'inline; filename="documento.pdf"',
                'Access-Control-Allow-Origin': '*'
            })
    except Exception as e:
        print(f"Error proxying external PDF: {e}")
        # If it fails, fallback by redirecting to the URL so at least it opens
        return redirect(file_url)

@ai_bp.route('/api/download')
def proxy_download():
    """Proxy file download from Supabase Storage with correct filename and Content-Disposition."""
    file_url = request.args.get('url', '')
    file_name = request.args.get('name', 'archivo')
    if not file_url:
        return jsonify({'error': 'URL requerida'})
    try:
        import urllib.parse
        import mimetypes
        # Safe encoding for URL in case it has spaces or special characters
        parsed = urllib.parse.urlparse(file_url)
        # Use safe='/:@%' to avoid double-encoding already-encoded chars
        safe_path = urllib.parse.quote(parsed.path, safe='/:@%')
        safe_url = parsed._replace(path=safe_path).geturl()
        
        req = urllib.request.Request(safe_url, headers={'User-Agent': 'SIACredit/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            content_type = resp.headers.get('Content-Type', 'application/octet-stream')
            # Strip charset and params from content type for clean mimetype
            content_type_clean = content_type.split(';')[0].strip()
        import io
        from flask import send_file

        # Siempre extraer el nombre real del archivo desde la URL de Supabase
        # El path de la URL contiene el nombre original con extensión
        parsed_url = urllib.parse.urlparse(file_url)
        # Obtener solo la última parte del path (sin query string, usando path no query)
        url_path_basename = urllib.parse.unquote(parsed_url.path.split('/')[-1])
        
        # Si el nombre recibido no tiene extensión o es genérico, usar el de la URL
        if not file_name or '.' not in file_name or file_name in ('evidencia', 'archivo'):
            if url_path_basename and '.' in url_path_basename:
                file_name = url_path_basename
            else:
                # Como último recurso, derivar extensión del content-type
                ext = mimetypes.guess_extension(content_type_clean) or ''
                # mimetypes puede dar .jpe en vez de .jpg, normalizar
                ext_map = {'.jpe': '.jpg', '.jpeg': '.jpg', '.htm': '.html'}
                ext = ext_map.get(ext, ext)
                file_name = (file_name or 'archivo') + ext
        else:
            # El nombre tiene extensión; si el de la URL tiene extensión diferente, priorizar la URL
            if url_path_basename and '.' in url_path_basename:
                url_ext = url_path_basename.rsplit('.', 1)[-1].lower()
                name_ext = file_name.rsplit('.', 1)[-1].lower()
                if url_ext != name_ext and url_ext:
                    # Reemplazar la extensión con la correcta según la URL del storage
                    file_name = file_name.rsplit('.', 1)[0] + '.' + url_ext

        return send_file(
            io.BytesIO(data),
            mimetype=content_type_clean,
            as_attachment=True,
            download_name=file_name
        )
    except Exception as e:
        print(f'Error proxying download: {e}')
        return jsonify({'error': str(e)})

# --- Rutas de Inteligencia Artificial ---

@ai_bp.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.json
    question = data.get('question', '')
    file_url = data.get('file_url', '')

    try:
        # Extraer texto del archivo si se proporciona
        file_context = ""
        if file_url:
            try:
                import urllib.request
                import tempfile
                import os
                
                req = urllib.request.Request(file_url, headers={'User-Agent': 'SIACredit/1.0'})
                with urllib.request.urlopen(req, timeout=30) as response:
                    file_bytes = response.read()
                    
                    if file_url.lower().split('?')[0].endswith('.pdf'):
                        import PyPDF2
                        import io
                        pdf = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                        text = ""
                        for page in pdf.pages:
                            text += page.extract_text() + "\n"
                        file_context = text
                    elif file_url.lower().split('?')[0].endswith('.docx'):
                        import docx2txt
                        import io
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                            tmp.write(file_bytes)
                            tmp_path = tmp.name
                        file_context = docx2txt.process(tmp_path)
                        os.unlink(tmp_path)
                    else:
                        file_context = file_bytes.decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"Error parsing attached file: {e}")
                file_context = f"[Error al leer el archivo adjunto: {e}]"

        system_prompt = (
            "Te llamas Margy. Eres una asistente experta en evaluación y aseguramiento de alta calidad "
            "para organizaciones, instituciones educativas y empresas, desarrollada por SKEL. "
            "Responde de manera formal, académica, profesional y analítica basándote en altos estándares "
            "de calidad. Si te preguntan cómo te llamas o quién eres, responde que te llamas "
            "Margy, la asistente de evaluación de SKEL."
        )
        
        final_prompt = question
        if file_context:
            if len(file_context) > 20000:
                file_context = file_context[:20000] + "... [texto truncado]"
            final_prompt = f"El usuario ha adjuntado un documento con el siguiente contenido:\n\n{file_context}\n\nPregunta del usuario: {question if question else 'Resume el documento o extrae los aspectos clave para la acreditación.'}"

        answer = call_ai(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            inst_id=data.get('inst_id')
        )
        
        # Save Q&A to ai_chat_logs for Chatbot Fine-Tuning
        try:
            from utils.db import supabase
            supabase.table('ai_chat_logs').insert({
                "inst_id": data.get('inst_id'),
                "user_uid": data.get('user_uid') or "N/A",
                "prompt": final_prompt,
                "response": answer,
                "provider": "unknown", # Could be extracted from call_ai if refactored, but this works
                "model": "auto"
            }).execute()
        except Exception as log_e:
            print(f"Error logging chat to DB: {log_e}")
        
        return jsonify({"status": "success", "answer": answer})
    except Exception as e:
        print(f"Error AI Chat: {e}")
        
        # Fallback: Intentar buscar en la base de datos de entrenamiento (ai_chat_logs)
        if question and not file_url:
            try:
                from utils.db import supabase
                res = supabase.table('ai_chat_logs').select('prompt, response').execute()
                if res.data:
                    query_words = set([w for w in question.lower().replace('?','').replace('¿','').split() if len(w) > 3])
                    best_match = None
                    best_score = 0
                    for row in res.data:
                        if not row.get('prompt') or not row.get('response'): continue
                        prompt_words = set([w for w in row['prompt'].lower().replace('?','').replace('¿','').split() if len(w) > 3])
                        
                        score = len(query_words.intersection(prompt_words))
                        # Basic threshold: at least 1 significant word match, but prioritize higher scores
                        if score > best_score and score >= 1:
                            best_score = score
                            best_match = row['response']
                    
                    if best_match:
                        fallback_msg = f"{best_match}\n\n*(Modo Offline: IA sin conexión. Respuesta obtenida de la base de conocimiento interno.)*"
                        return jsonify({"status": "success", "answer": fallback_msg})
            except Exception as fallback_e:
                print(f"Fallback search error: {fallback_e}")
                
        return jsonify({"error": str(e)})

@ai_bp.route('/api/export-chat-logs', methods=['GET'])
def export_chat_logs():
    try:
        from utils.db import supabase
        import json
        import io
        from flask import send_file
        
        # Superadmin check can be done via frontend or JWT, assuming it's protected by the UI
        res = supabase.table('ai_chat_logs').select("*").order("created_at", desc=False).execute()
        
        jsonl_lines = []
        for row in res.data:
            # Format as JSONL with OpenAI fine-tuning structure
            line = {
                "messages": [
                    {"role": "system", "content": "Te llamas Margy. Eres una asistente experta en evaluación y aseguramiento de alta calidad para organizaciones, instituciones educativas y empresas, desarrollada por SKEL. Responde de manera formal, académica, profesional y analítica basándote en altos estándares de calidad."},
                    {"role": "user", "content": row.get('prompt', '')},
                    {"role": "assistant", "content": row.get('response', '')}
                ]
            }
            jsonl_lines.append(json.dumps(line, ensure_ascii=False))
            
        jsonl_content = "\n".join(jsonl_lines)
        
        mem = io.BytesIO()
        mem.write(jsonl_content.encode('utf-8'))
        mem.seek(0)
        
        return send_file(
            mem,
            mimetype='application/jsonl',
            as_attachment=True,
            download_name='margy_training_data.jsonl'
        )
    except Exception as e:
        print(f"Error exporting chat logs: {e}")
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/api/chat-logs', methods=['GET'])
def get_chat_logs():
    try:
        from utils.db import supabase
        res = supabase.table('ai_chat_logs').select("*").order("created_at", desc=True).execute()
        return jsonify({"status": "success", "data": res.data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@ai_bp.route('/api/chat-logs/<int:log_id>', methods=['DELETE'])
def delete_chat_log(log_id):
    try:
        from utils.db import supabase
        supabase.table('ai_chat_logs').delete().eq("id", log_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@ai_bp.route('/api/export-chat-logs-csv', methods=['GET'])
def export_chat_logs_csv():
    try:
        from utils.db import supabase
        import csv
        import io
        from flask import send_file
        
        res = supabase.table('ai_chat_logs').select("*").order("created_at", desc=False).execute()
        
        # Use StringIO to build CSV
        si = io.StringIO()
        writer = csv.writer(si)
        # Add UTF-8 BOM so Excel opens it automatically with correct encoding
        si.write('\ufeff')
        writer.writerow(['ID', 'Fecha', 'Pregunta', 'Respuesta'])
        
        for row in res.data:
            writer.writerow([
                row.get('id', ''),
                row.get('created_at', ''),
                row.get('prompt', ''),
                row.get('response', '')
            ])
            
        mem = io.BytesIO()
        mem.write(si.getvalue().encode('utf-8'))
        mem.seek(0)
        
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name='margy_training_data.csv'
        )
    except Exception as e:
        print(f"Error exporting chat logs CSV: {e}")
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/api/ai/generate_report', methods=['POST'])
def ai_generate_report():
    data = request.json
    report_data = data.get('report_data', {})
    
    try:
        # Convert report_data to string but limit its size to avoid context length limits
        data_str = json.dumps(report_data, ensure_ascii=False)
        if len(data_str) > 30000:
            data_str = data_str[:30000] + "... [Datos truncados]"

        prompt = f"""
        Actúa como un evaluador experto y consultor analítico de alto nivel.
        A continuación se te provee un JSON con la información de la evaluación de una organización, institución o programa académico.
        Incluye calificaciones de autoevaluación, justificaciones, evidencias documentales adjuntas y referencias a cuadros estadísticos,
        así como resultados cualitativos y cuantitativos de encuestas aplicadas, en caso de existir.
        
        JSON de Evaluación:
        {data_str}

        Por favor, redacta un informe ejecutivo y analítico exhaustivo en formato Markdown estructurado.
        Estructura obligatoria del informe:
        # Informe de Evaluación Analítica Integral
        ## 1. Introducción y Apreciación General
        ## 2. Análisis Detallado por Factores
        (Para cada factor o dimensión, DEBES triangular y analizar conjuntamente los siguientes 4 elementos, si están disponibles:
        1. **Autoevaluación**: Resultados y justificaciones declaradas.
        2. **Evidencias**: Nivel de soporte documental referenciado.
        3. **Estadísticas**: Datos, cifras y cuadros estadísticos asociados.
        4. **Encuestas**: En caso de existir, contrasta la percepción (promedios y comentarios) con la autoevaluación.
        Identifica de manera rigurosa las fortalezas y oportunidades de mejora basándote en la articulación de estos 4 elementos).
        ## 3. Conclusiones
        ## 4. Recomendaciones Estratégicas y Plan de Mejoramiento
        
        Escribe de forma formal, propositiva, con un lenguaje técnico, académico u organizacional avanzado, basado estrictamente en los datos provistos.
        """
        
        report_text = call_ai(
            messages=[
                {"role": "system", "content": "Eres un redactor experto de informes analíticos institucionales y organizacionales de alto nivel."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        return jsonify({"status": "success", "report": report_text})
    except Exception as e:
        print(f"Error AI Generate Report: {e}")
        return jsonify({"error": str(e)})

@ai_bp.route('/api/ai/generate_dofa', methods=['POST'])
def ai_generate_dofa():
    data = request.json
    report_text = data.get('report_text', '')
    
    try:
        # Limitar tamaño si es excesivamente largo
        if len(report_text) > 40000:
            report_text = report_text[:40000] + "... [Texto truncado]"

        prompt = f"""
        Actúa como un analista experto en planeación estratégica institucional.
        Se te proporciona el Informe Parcial/Total de Autoevaluación de un programa académico.
        Tu tarea es determinar cuáles son las Fortalezas y Debilidades (Factores Internos) del programa basándote EXCLUSIVAMENTE en el texto provisto.
        
        Debes clasificar y priorizar estos factores de mayor a menor nivel de importancia.
        Utiliza estrictamente el formato D1, D2, D3... para las Debilidades y F1, F2, F3... para las Fortalezas, donde el número 1 es el más importante y crítico.
        Pueden diferenciarse en cantidad (p.ej. 5 Fortalezas y 3 Debilidades, o viceversa, extrae las más relevantes).
        
        Texto del Informe:
        {report_text}
        
        Debes devolver tu respuesta ESTRICTAMENTE en formato JSON válido, con la siguiente estructura:
        {{
            "fortalezas": [
                {{"id": "F1", "descripcion": "Descripción concisa...", "importancia": 1}}
            ],
            "debilidades": [
                {{"id": "D1", "descripcion": "Descripción concisa...", "importancia": 1}}
            ]
        }}
        Devuelve únicamente el texto JSON y NADA MÁS.
        """
        
        dofa_res = call_ai(
            messages=[
                {"role": "system", "content": "Eres un asistente experto que solo devuelve estructuras JSON puras y válidas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2500
        )
        
        # Limpieza básica por si el LLM incluye formato de bloque de código
        dofa_res = dofa_res.replace('```json', '').replace('```', '').strip()
        
        try:
            dofa_json = json.loads(dofa_res)
        except:
            dofa_json = {"fortalezas": [], "debilidades": [], "error_parseo": "El formato generado no fue un JSON válido."}
            
        return jsonify({"status": "success", "dofa": dofa_json})
    except Exception as e:
        print(f"Error AI Generate DOFA: {e}")
        return jsonify({"error": str(e)})


@ai_bp.route('/api/ai/generate_pesta', methods=['POST'])
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
        return jsonify({"error": str(e)})


@ai_bp.route('/api/ai/cruce_dofa', methods=['POST'])
def ai_cruce_dofa():
    data = request.json
    fortalezas = data.get('fortalezas', [])
    debilidades = data.get('debilidades', [])
    oportunidades = data.get('oportunidades', [])
    amenazas = data.get('amenazas', [])
    
    try:
        prompt = f"""
        Actúa como un Doctor en Planeación Estratégica Gerencial y Académica.
        Se te proporcionan los factores internos (F, D) y externos (O, A) de un proceso de diagnóstico de una institución o programa académico:
        
        FORTALEZAS: {json.dumps(fortalezas, ensure_ascii=False)}
        DEBILIDADES: {json.dumps(debilidades, ensure_ascii=False)}
        OPORTUNIDADES: {json.dumps(oportunidades, ensure_ascii=False)}
        AMENAZAS: {json.dumps(amenazas, ensure_ascii=False)}
        
        Realiza el Cruce Estratégico (Matriz TOWS / DOFA) para generar estrategias maestras de alto impacto.
        NO te limites a un número algorítmico o fijo de estrategias (como 2 por cada cuadrante). 
        Analiza profundamente la interacción real de los datos empíricos que recibes, y determina con un grado de importancia e inteligencia cuántas estrategias son verdaderamente necesarias, viables y críticas para cada dimensión. Un cuadrante puede tener múltiples estrategias maestras si los datos lo justifican, y otro cuadrante puede tener muy pocas.
        
        Tipos de estrategias esperadas:
        - Estrategias FO (Maxi-Maxi): Usar fortalezas para aprovechar oportunidades.
        - Estrategias DO (Mini-Maxi): Superar debilidades aprovechando oportunidades.
        - Estrategias FA (Maxi-Mini): Usar fortalezas para evitar o mitigar amenazas.
        - Estrategias DA (Mini-Mini): Tácticas defensivas para reducir debilidades y evitar amenazas.
        
        Cada estrategia DEBE iniciar indicando explícitamente qué variables cruza (ej. "(F1, F2, O2) Diseñar un sistema de...").
        
        Devuelve tu respuesta ESTRICTAMENTE en formato JSON válido, con la siguiente estructura (los arreglos pueden tener la cantidad de estrategias que consideres estratégicamente pertinentes):
        {{
            "FO": ["Estrategia 1...", "Estrategia 2...", "..."],
            "DO": ["Estrategia 1...", "..."],
            "FA": ["Estrategia 1...", "Estrategia 2...", "Estrategia 3...", "..."],
            "DA": ["Estrategia 1...", "..."]
        }}
        Devuelve ÚNICAMENTE el texto JSON puro sin etiquetas Markdown.
        """
        
        cruce_res = call_ai(
            messages=[
                {"role": "system", "content": "Eres un Doctor experto en Planeación Estratégica Gerencial. Responde solo con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=3000
        )
        
        cruce_res = cruce_res.replace('```json', '').replace('```', '').strip()
        
        try:
            cruce_json = json.loads(cruce_res)
        except:
            cruce_json = {"FO":[], "DO":[], "FA":[], "DA":[], "error_parseo": "JSON inválido devuelto por la IA."}
            
        return jsonify({"status": "success", "matriz": cruce_json})
    except Exception as e:
        print(f"Error AI Cruce DOFA: {e}")
        return jsonify({"error": str(e)})

@ai_bp.route('/api/ai/generar_rrc', methods=['POST'])
def ai_generar_rrc():
    """
    Genera el soporte documental para la Renovación de Registro Calificado
    basado en el informe de autoevaluación del programa activo.
    Aplica el Decreto 1330 de 2019 y la Resolución 0529 del MEN.
    """
    data = request.json
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
            meta_str = "\nMetadatos de Denominación: " + str(meta_res.data[0]['data_json'])

        justification_str = ""
        if justification_url:
            justification_str = f"\nEvidencia documental adjunta (Soporte global): {justification_url}. EXIGENCIA: Analizar y referenciar explícitamente esta evidencia donde aplique."

        # Serializar datos de condiciones, limitando el tamaño
        data_str = json.dumps(condiciones_data, ensure_ascii=False)
        if len(data_str) > 28000:
            data_str = data_str[:28000] + "... [datos truncados]"

        system_prompt = (
            "Eres un evaluador experto y consultor analítico de alto nivel en aseguramiento de la calidad. "
            "Dominas estándares normativos y de evaluación de alto rigor académico y organizacional. "
            "Tu función es generar un SOPORTE DOCUMENTAL formal, técnico y estrictamente analítico "
            "articulando de forma rigurosa los criterios de calidad con los indicadores evaluados."
        )

        prompt = f"""
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
"""

        rrc_text = call_ai(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.65,
            max_tokens=3500
        )

        return jsonify({"status": "success", "report": rrc_text})

    except Exception as e:
        print(f"Error AI Generar RRC: {e}")
        return jsonify({"error": str(e)})




@ai_bp.route('/api/ai/generar_rrc_condicion', methods=['POST'])
def ai_generar_rrc_condicion():
    """
    Genera el soporte documental para una sola condición de RRC.
    """
    data = request.json
    inst_id    = data.get('inst_id', 1)
    program_id = data.get('program_id', 0)
    condicion_num = data.get('condicion_num', '1')
    condicion_data = data.get('condicion_data', {})
    program_name   = data.get('program_name', 'Programa Académico')
    inst_name      = data.get('inst_name', 'Institución de Educación Superior')
    justification_url = data.get('justification_url', '')

    try:
        # Cargar metadatos
        meta_table = f"PROGRAM_METADATA_{program_id}"
        meta_res = supabase.table('statistics').select("data_json").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", meta_table).execute()
        meta_str = ""
        if meta_res.data:
            meta_str = "\nMetadatos de Denominación: " + str(meta_res.data[0]['data_json'])

        justification_str = ""
        if justification_url:
            justification_str = f"\n\nEVIDENCIA PRINCIPAL OBLIGATORIA ADJUNTA PARA LA CONDICIÓN {condicion_num}: {justification_url}\nEXIGENCIA CRÍTICA: Debes analizar exhaustivamente este documento y basar la argumentación de la Condición {condicion_num} en los hallazgos de este soporte documental."

        data_str = json.dumps(condicion_data, ensure_ascii=False)

        system_prompt = (
            "Eres un evaluador experto y consultor analítico de alto nivel en aseguramiento de la calidad. "
            "Tu función es generar un SOPORTE DOCUMENTAL formal, técnico y estrictamente analítico "
            f"articulando de forma rigurosa los criterios de calidad con los indicadores evaluados, exclusivamente para la Condición {condicion_num}."
        )

        prompt = f"""
Basado en el documento 'Indicadores Comunes del Modelo de Autoevaluación CESU', 
analiza la información de autoevaluación del programa académico **{program_name}** de la institución **{inst_name}**.{meta_str}{justification_str}

Datos específicos de la Condición {condicion_num}:
{data_str}

INSTRUCCIÓN CRÍTICA: Debes obligatoriamente referenciar de forma explícita los nombres de las *evidencias documentales* que soporten la condición, y argumentar basándote en los *cuadros estadísticos* (tasas, promedios). NO produzcas un texto puramente descriptivo sin datos.

Redacta el SOPORTE DOCUMENTAL exclusivamente para la Condición {condicion_num}.

Debes generar:
1. **Análisis de cumplimiento**: descripción de cómo el programa evidencia el cumplimiento de la condición.
2. **Indicadores normativos cubiertos**.
3. **Aspectos por fortalecer**.
4. **Estimación de Cumplimiento**: Cumple plenamente / Cumple en alto grado / Cumple aceptablemente / En proceso de cumplimiento.

IMPORTANTE: No uses el título principal `## Condición {condicion_num}: ...`, porque el contenedor visual ya lo tiene.
Simplemente devuelve el contenido interno con esta estructura de subtítulos en Markdown:
### Análisis de Cumplimiento
[texto]
### Indicadores con Soporte
[texto]
### Aspectos por Fortalecer  
[texto]
### Estimación de Cumplimiento
[texto]
"""

        rrc_text = call_ai(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return jsonify({'status': 'success', 'report': rrc_text})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@ai_bp.route('/api/rrc/report', methods=['GET', 'POST'])

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
            return jsonify({"status": "error", "message": str(e)})
    
    try:
        res = supabase.table('statistics').select("data_json").eq("inst_id", inst_id).eq("program_id", program_id).eq("table_id", table_id).execute()
        if res.data:
            return jsonify(json.loads(res.data[0]['data_json']))
        return jsonify({})
    except Exception as e:
        print("Error fetching RRC report:", e)
        return jsonify({})

