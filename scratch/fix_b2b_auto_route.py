import os

filepath = "c:/SIAC/routes/business.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# We need to replace the `auto_populate_matrices` function completely
import re
# Find the start of the function
start_idx = content.find("@business_bp.route('/api/business/auto-populate-matrices', methods=['POST'])")

if start_idx != -1:
    new_func = """@business_bp.route('/api/business/auto-populate-matrices', methods=['POST'])
def auto_populate_matrices():
    try:
        payload = request.json
        inst_id = payload.get('inst_id')
        program_id = payload.get('program_id', 0)
        
        if not inst_id:
            return jsonify({'error': 'inst_id is required'}), 400
            
        # 1. Fetch current Autoevaluacion data
        factors = supabase.table('factors').select("*, characteristics(id, name, weight)").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        evals = supabase.table('evaluations').select("char_id, rating").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        eval_map = {e['char_id']: e['rating'] for e in evals}
        
        if not factors:
            return jsonify({'error': 'No hay factores de autoevaluación registrados para analizar.'}), 404
            
        # 2. Build the MEFI matrix deterministically (Autoevaluacion is mostly Internal)
        # We will map them directly without using AI to save tokens.
        
        fortalezas = []
        debilidades = []
        
        # To calculate relative weights properly
        total_items = 0
        
        for f in factors:
            for c in f.get('characteristics', []):
                rating = eval_map.get(c['id'], 0)
                if rating > 0:
                    total_items += 1
                    
        if total_items == 0:
            return jsonify({'error': 'No hay características evaluadas aún.'}), 404
            
        base_weight = round(1.0 / total_items, 2)
        
        for f in factors:
            for c in f.get('characteristics', []):
                rating = eval_map.get(c['id'], 0)
                if rating > 0:
                    char_name = c.get('name', 'Desconocido')
                    # Scale 1-5 to 1-4 for matrix
                    # 5 -> 4, 4 -> 3, 3 -> 2, 1-2 -> 1
                    matrix_rating = 1
                    if rating >= 4.5:
                        matrix_rating = 4
                    elif rating >= 3.5:
                        matrix_rating = 3
                    elif rating >= 2.5:
                        matrix_rating = 2
                    else:
                        matrix_rating = 1
                        
                    item = {
                        "name": char_name,
                        "weight": base_weight,
                        "rating": matrix_rating
                    }
                    
                    if rating >= 3.5:
                        fortalezas.append(item)
                    else:
                        debilidades.append(item)
                        
        # 3. Return the JSON structure directly
        parsed_data = {
            "mefi": {
                "fortalezas": fortalezas,
                "debilidades": debilidades
            },
            "mefe": {
                "oportunidades": [],
                "amenazas": []
            }
        }
        
        return jsonify(parsed_data)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
"""
    # Replace from start_idx to the end of the file (assuming it's the last function, which it is)
    content = content[:start_idx] + new_func
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Replaced auto_populate_matrices to avoid AI tokens.")
else:
    print("Function not found!")
