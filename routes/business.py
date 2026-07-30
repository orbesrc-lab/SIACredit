from flask import Blueprint, jsonify, request
from utils.db import supabase
import uuid

business_bp = Blueprint('business', __name__)

@business_bp.route('/api/business/matrix/<matrix_type>', methods=['GET'])
def get_matrix(matrix_type):
    try:
        inst_id = request.args.get('inst_id')
        if not inst_id:
            return jsonify({'error': 'inst_id is required'}), 400
            
        res = supabase.table('business_matrices').select('*').eq('inst_id', inst_id).eq('matrix_type', matrix_type.upper()).execute()
        if res.data:
            return jsonify(res.data[0])
        else:
            return jsonify({'data': {}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@business_bp.route('/api/business/matrix/<matrix_type>', methods=['POST'])
def save_matrix(matrix_type):
    try:
        payload = request.json
        inst_id = payload.get('inst_id')
        data = payload.get('data')
        results = payload.get('results')
        user_id = payload.get('user_id')
        
        if not inst_id:
            return jsonify({'error': 'inst_id is required'}), 400
            
        # Check if exists
        res = supabase.table('business_matrices').select('id').eq('inst_id', inst_id).eq('matrix_type', matrix_type.upper()).execute()
        
        if res.data:
            # Update
            db_id = res.data[0]['id']
            update_res = supabase.table('business_matrices').update({
                'data': data,
                'results': results,
                'updated_at': 'now()'
            }).eq('id', db_id).execute()
            return jsonify({'status': 'success', 'message': 'Matrix updated'})
        else:
            # Insert
            insert_res = supabase.table('business_matrices').insert({
                'inst_id': inst_id,
                'matrix_type': matrix_type.upper(),
                'data': data,
                'results': results,
                'created_by': user_id
            }).execute()
            return jsonify({'status': 'success', 'message': 'Matrix created'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
