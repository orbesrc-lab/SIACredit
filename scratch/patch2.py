import re

def patch():
    with open('c:\\SIAC\\app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "def create_zip_context" in content:
        print("Already patched.")
        return

    # 1. Inject helpers right after '# BACKUP MODULE'
    helpers = """
try:
    import pyzipper
except ImportError:
    pyzipper = None
import contextlib

@contextlib.contextmanager
def create_zip_context(buf, password=None):
    if pyzipper and password:
        zf = pyzipper.AESZipFile(buf, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES)
        zf.setpassword(password.encode('utf-8'))
    else:
        zf = zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED)
    try:
        yield zf
    finally:
        zf.close()

def verify_backup_security(user_id, password, inst_id, action_type):
    from werkzeug.security import check_password_hash
    if not user_id or not password:
        return False, "Se requiere contrasea de administrador."
        
    res = supabase.table('users').select('email, password_hash').eq('id', user_id).execute()
    if not res.data:
        return False, "Usuario no encontrado."
        
    user = res.data[0]
    email = user.get('email')
    phash = user.get('password_hash')
    
    is_valid = check_password_hash(phash, password) if phash else False
    status = 'SUCCESS' if is_valid else 'DENIED'
    
    try:
        supabase.table('security_backup_logs').insert({
            'user_id': user_id,
            'user_email': email,
            'inst_id': int(inst_id) if inst_id else None,
            'action_type': action_type,
            'status': status
        }).execute()
    except Exception as e:
        print("Error logging security:", e)
        
    return is_valid, ("Acceso denegado. Contrasea incorrecta." if not is_valid else "")
"""
    content = content.replace("# BACKUP MODULE", "# BACKUP MODULE\n" + helpers)

    # 2. Modify _build_full_zip definition to accept password and pass it to create_zip_context
    content = content.replace("def _build_full_zip(inst_id, scope, modules, year, program_id):", "def _build_full_zip(inst_id, scope, modules, year, program_id, password=None):")
    
    # 3. Replace all zipfile.ZipFile creations with create_zip_context
    content = content.replace("zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED)", "create_zip_context(buf, password)")

    # 4. Inject validation logic at the beginning of the try block in backup POST endpoints
    # We will search for `inst_id = data.get('inst_id', 1)` inside each endpoint and add the logic.
    
    def inject_validation(route_content, action_type):
        find_str = "        inst_id = data.get('inst_id', 1)"
        if find_str not in route_content:
            # Maybe it uses `data.get('inst_id')` or something else?
            if "        inst_id = data.get('inst_id')" in route_content:
                find_str = "        inst_id = data.get('inst_id')"
            else:
                return route_content # Skip if not found
                
        injection = f"""
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        is_valid, msg = verify_backup_security(user_id, password, inst_id, '{action_type}')
        if not is_valid:
            return jsonify({{'status': 'error', 'message': msg}}), 403
"""
        return route_content.replace(find_str, injection.strip('\n'), 1)

    # Need to split by @app.route
    parts = content.split('@app.route(')
    new_parts = [parts[0]]
    
    for part in parts[1:]:
        route_path = part.split(',')[0].strip("'\"")
        
        if route_path == '/api/backup/generate':
            part = inject_validation(part, 'FULL_BACKUP')
            part = part.replace("zip_bytes = _build_full_zip(inst_id, scope, modules, year, program_id)", "zip_bytes = _build_full_zip(inst_id, scope, modules, year, program_id, password)")
        elif route_path == '/api/backup/factor':
            part = inject_validation(part, 'FACTOR_BACKUP')
        elif route_path == '/api/backup/evidencias':
            part = inject_validation(part, 'EVIDENCIAS_BACKUP')
        elif route_path == '/api/backup/csv/all':
            part = inject_validation(part, 'CSV_ALL_BACKUP')
        elif route_path == '/api/backup/csv/<tipo>':
            # This one is a GET, convert it to POST
            part = part.replace("methods=['GET']", "methods=['POST']")
            # It currently extracts `inst_id = request.args.get('inst_id', 1, type=int)`
            # Change it to read from JSON payload
            part = part.replace("        inst_id = request.args.get('inst_id', 1, type=int)", "        data = request.json or {}\n        inst_id = data.get('inst_id', 1)")
            part = inject_validation(part, 'CSV_MODULE_BACKUP')
            
        new_parts.append(part)
        
    content = '@app.route('.join(new_parts)

    # 5. Add /api/backup/logs endpoint at the end of the file
    logs_endpoint = """
@app.route('/api/backup/logs', methods=['POST'])
def get_backup_logs():
    data = request.json or {}
    user_id = data.get('user_id')
    
    # Optional: Check if user is admin
    res_user = supabase.table('users').select('role').eq('id', user_id).execute()
    if not res_user.data or res_user.data[0].get('role') not in ('admin', 'inst_admin', 'super_admin'):
         return jsonify({'status': 'error', 'message': 'No autorizado'}), 403
         
    inst_id = data.get('inst_id')
    q = supabase.table('security_backup_logs').select('*').order('timestamp', desc=True).limit(50)
    if inst_id:
        q = q.eq('inst_id', inst_id)
    res = q.execute()
    return jsonify({'status': 'success', 'logs': res.data or []})
"""
    content += logs_endpoint

    with open('c:\\SIAC\\app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patch applied.")

if __name__ == '__main__':
    patch()
