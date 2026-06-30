import os

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """@app.route('/api/crm/prospects', methods=['GET'])
def get_prospects():
    try:
        res = supabase.table('prospects').select("*").order("created_at", desc=False).execute()
        return jsonify({"status": "success", "data": res.data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500"""

new_block = """@app.route('/api/crm/prospects', methods=['GET', 'POST'])
def handle_prospects():
    if request.method == 'GET':
        try:
            res = supabase.table('prospects').select("*").order("created_at", desc=False).execute()
            return jsonify({"status": "success", "data": res.data})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
            
    elif request.method == 'POST':
        try:
            data = request.json
            if not data or 'institution' not in data:
                return jsonify({"status": "error", "message": "Institution is required"}), 400
                
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
            return jsonify({"status": "error", "message": str(e)}), 500"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success")
else:
    print("Old block not found!")
