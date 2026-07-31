import os

file_path = r'c:\SIAC\routes\business.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix get_matrix in routes/business.py
old_get_matrix = """def get_matrix(matrix_type):
    try:
        inst_id = request.args.get('inst_id')
        if not inst_id:
            return jsonify({'error': 'inst_id is required'}), 400
            
        # Modificado para usar la tabla statistics
        res = supabase.table('statistics').select('data_json').eq('inst_id', inst_id).eq('table_id', matrix_type.upper()).order('id', desc=True).limit(1).execute()
        if res.data:
            # We return data so it mimics the old behavior: {'data': res.data[0]['data_json']}
            return jsonify({'data': res.data[0]['data_json']})
        else:
            return jsonify({'data': {}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500"""

new_get_matrix = """def get_matrix(matrix_type):
    try:
        inst_id = request.args.get('inst_id')
        if not inst_id:
            return jsonify({'error': 'inst_id is required'}), 400
            
        res = supabase.table('statistics').select('data_json').eq('inst_id', inst_id).eq('table_id', matrix_type.upper()).order('id', desc=True).limit(1).execute()
        if res.data:
            val = res.data[0]['data_json']
            if isinstance(val, str):
                try:
                    val = json.loads(val)
                except Exception:
                    pass
            return jsonify({'data': val})
        else:
            return jsonify({'data': {}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500"""

content = content.replace(old_get_matrix.replace('\r\n', '\n'), new_get_matrix.replace('\r\n', '\n'))
content = content.replace(old_get_matrix, new_get_matrix)

# 2. Fix extract_name in populate_from_dofa_pesta
helper_func = """def extract_item_name(item):
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return item.get('descripcion') or item.get('description') or item.get('factor') or item.get('name') or str(item)
    return str(item)
"""

if "def extract_item_name" not in content:
    content = helper_func + "\n" + content

content = content.replace("name = item if isinstance(item, str) else item.get('description', str(item))", "name = extract_item_name(item)")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("routes/business.py successfully patched")
