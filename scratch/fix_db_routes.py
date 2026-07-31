import os
import re

file_path = r'c:\SIAC\routes\business.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix get_matrix
new_get = """@business_bp.route('/api/business/matrix/<matrix_type>', methods=['GET'])
def get_matrix(matrix_type):
    try:
        inst_id = request.args.get('inst_id')
        if not inst_id:
            return jsonify({'error': 'inst_id is required'}), 400
            
        # Modificado para usar la tabla statistics
        res = supabase.table('statistics').select('data').eq('inst_id', inst_id).eq('table_id', matrix_type.upper()).order('id', desc=True).limit(1).execute()
        if res.data:
            # We return data so it mimics the old behavior: {'data': res.data[0]['data']}
            return jsonify({'data': res.data[0]['data']})
        else:
            return jsonify({'data': {}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
"""
content = re.sub(r"@business_bp\.route\('/api/business/matrix/<matrix_type>', methods=\['GET'\]\).*?def get_matrix.*?return jsonify\(\{'error': str\(e\)\}\), 500", new_get, content, flags=re.DOTALL)

# Fix save_matrix
new_save = """@business_bp.route('/api/business/matrix/<matrix_type>', methods=['POST'])
def save_matrix(matrix_type):
    try:
        payload = request.json
        inst_id = payload.get('inst_id')
        data = payload.get('data')
        results = payload.get('results', {})
        
        # Combinar results dentro de data si existen para que statistics los guarde todo
        if results:
            data['analysis_results'] = results

        # Insert into statistics directly
        insert_res = supabase.table('statistics').insert({
            'inst_id': inst_id,
            'table_id': matrix_type.upper(),
            'program_id': 0,
            'data': data
        }).execute()

        return jsonify({'status': 'success', 'message': 'Matrix updated/inserted in statistics'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
"""
content = re.sub(r"@business_bp\.route\('/api/business/matrix/<matrix_type>', methods=\['POST'\]\).*?def save_matrix.*?return jsonify\(\{'error': str\(e\)\}\), 500", new_save, content, flags=re.DOTALL)

# Also fix the fetch response check in empresa_matrices.html to actually show errors if not ok
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Backend routes updated for statistics table!")
