import re
import os

def patch_app_py():
    with open('c:\\SIAC\\app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Inject pyzipper and verify function right after "# BACKUP MODULE"
    if "import pyzipper" not in content:
        injection = """
try:
    import pyzipper
except ImportError:
    pyzipper = None

def verify_backup_security(user_id, password, inst_id, action_type):
    from werkzeug.security import check_password_hash
    # Fetch user password hash
    res = supabase.table('users').select('email, password_hash').eq('id', user_id).execute()
    if not res.data:
        return False, "Usuario no encontrado"
    
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
        print("Error logging backup security:", e)
        
    return is_valid, ("Acceso denegado" if not is_valid else "")
"""
        content = content.replace("# BACKUP MODULE", "# BACKUP MODULE\n" + injection)

    # 2. Modify _build_full_zip to use pyzipper and encryption
    old_full_zip_def = "def _build_full_zip(inst_id, scope, modules, year, program_id):"
    new_full_zip_def = "def _build_full_zip(inst_id, scope, modules, year, program_id, password=None):"
    content = content.replace(old_full_zip_def, new_full_zip_def)
    
    old_zip_ctx = "    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:"
    new_zip_ctx = """    
    if pyzipper and password:
        zf = pyzipper.AESZipFile(buf, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES)
        zf.setpassword(password.encode('utf-8'))
    else:
        zf = zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED)
    
    with zf:"""
    content = content.replace(old_zip_ctx, new_zip_ctx)

    # 3. Apply password parameter to other _build functions
    content = content.replace("def _build_factor_zip(inst_id, factor_id, year, program_id):", "def _build_factor_zip(inst_id, factor_id, year, program_id, password=None):")
    content = content.replace("def _build_evidencias_zip(inst_id, year, program_id):", "def _build_evidencias_zip(inst_id, year, program_id, password=None):")
    content = content.replace("def _build_all_csv_zip(inst_id):", "def _build_all_csv_zip(inst_id, password=None):")

    # 4. Modify POST routes to verify password
    routes = [
        ('/api/backup/generate', "'FULL_BACKUP'", "zip_bytes = _build_full_zip(inst_id, scope, modules, year, program_id)", "zip_bytes = _build_full_zip(inst_id, scope, modules, year, program_id, password)"),
        ('/api/backup/factor', "'FACTOR_BACKUP'", "zip_bytes = _build_factor_zip(inst_id, factor_id, year, program_id)", "zip_bytes = _build_factor_zip(inst_id, factor_id, year, program_id, password)"),
        ('/api/backup/evidencias', "'EVIDENCIAS_BACKUP'", "zip_bytes = _build_evidencias_zip(inst_id, year, program_id)", "zip_bytes = _build_evidencias_zip(inst_id, year, program_id, password)"),
        ('/api/backup/csv/all', "'CSV_ALL_BACKUP'", "zip_bytes = _build_all_csv_zip(inst_id)", "zip_bytes = _build_all_csv_zip(inst_id, password)")
    ]

    for route, action, old_call, new_call in routes:
        # Find the function def after the route
        route_idx = content.find(route)
        if route_idx == -1: continue
        
        # Inject validation right after data extraction
        injection_point = "        inst_id = data.get('inst_id', 1)"
        if route == '/api/backup/csv/all':
            pass # Same line
            
        validation_code = f"""
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        if not user_id or not password:
            return jsonify({{'status': 'error', 'message': 'Se requiere contraseña de administrador.'}}), 403
            
        is_valid, msg = verify_backup_security(user_id, password, inst_id, {action})
        if not is_valid:
            return jsonify({{'status': 'error', 'message': msg}}), 403
"""
        if route == '/api/backup/generate':
            content = content.replace("        inst_id = data.get('inst_id', 1)\n        scope = data.get('scope', 'inst')", validation_code + "\n        scope = data.get('scope', 'inst')")
        else:
            content = content.replace("        inst_id = data.get('inst_id', 1)", validation_code, 1)
            
        content = content.replace(old_call, new_call)

    # 5. Change CSV single route from GET to POST and add validation
    old_csv_route = "@app.route('/api/backup/csv/<tipo>', methods=['GET'])\ndef backup_csv_single(tipo):\n    \"\"\"Export a single module as CSV.\"\"\"\n    try:\n        inst_id = request.args.get('inst_id', 1, type=int)"
    new_csv_route = """@app.route('/api/backup/csv/<tipo>', methods=['POST'])
def backup_csv_single(tipo):
    \"\"\"Export a single module as CSV.\"\"\"
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        if not user_id or not password:
            return jsonify({'status': 'error', 'message': 'Se requiere contraseña.'}), 403
        is_valid, msg = verify_backup_security(user_id, password, inst_id, 'CSV_MODULE_BACKUP')
        if not is_valid:
            return jsonify({'status': 'error', 'message': msg}), 403"""
    content = content.replace(old_csv_route, new_csv_route)

    # Add Logs Endpoint
    if "/api/backup/logs" not in content:
        logs_endpoint = """
@app.route('/api/backup/logs', methods=['GET'])
def get_backup_logs():
    inst_id = request.args.get('inst_id')
    q = supabase.table('security_backup_logs').select('*').order('timestamp', desc=True).limit(50)
    if inst_id:
        q = q.eq('inst_id', inst_id)
    res = q.execute()
    return jsonify({'status': 'success', 'logs': res.data or []})
"""
        content = content + logs_endpoint

    with open('c:\\SIAC\\app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("app.py successfully patched.")

if __name__ == '__main__':
    patch_app_py()
