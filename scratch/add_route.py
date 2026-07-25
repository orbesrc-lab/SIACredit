import os

route = '''
@app.route('/api/crm/prospects/bulk_delete', methods=['POST'])
def bulk_delete_prospects():
    data = request.json
    if not data or 'ids' not in data:
        return jsonify({'status': 'error', 'message': 'No ids provided'}), 400
    
    ids = data['ids']
    if not isinstance(ids, list) or len(ids) == 0:
        return jsonify({'status': 'error', 'message': 'Invalid ids array'}), 400
        
    try:
        deleted_count = 0
        for pid in ids:
            supabase.table('prospects').delete().eq('id', pid).execute()
            deleted_count += 1
        return jsonify({'status': 'success', 'deleted_count': deleted_count})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
'''

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

split_str = "if __name__ == '__main__':"
parts = content.split(split_str)
new_content = parts[0] + route + '\n' + split_str + parts[1]

with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Added bulk_delete_prospects')
