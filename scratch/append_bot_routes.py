import re

routes_code = '''

@core_bp.route('/api/bot/unanswered', methods=['GET', 'POST'])
def manage_unanswered_bot():
    import json
    import uuid
    from datetime import datetime
    
    if request.method == 'POST':
        try:
            data = request.json
            question = data.get('question', '').strip()
            if not question:
                return jsonify({"status": "error", "message": "No question provided"})
            
            # Fetch existing array
            res = supabase.table('statistics').select("data_json").eq("table_id", "BOT_UNANSWERED").execute()
            if res.data:
                unanswered_data = json.loads(res.data[0]['data_json'])
            else:
                unanswered_data = {"messages": []}
                
            unanswered_data["messages"].append({
                "id": str(uuid.uuid4()),
                "question": question,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "pending"
            })
            
            if res.data:
                supabase.table('statistics').update({"data_json": json.dumps(unanswered_data)}).eq("table_id", "BOT_UNANSWERED").execute()
            else:
                supabase.table('statistics').insert({"table_id": "BOT_UNANSWERED", "data_json": json.dumps(unanswered_data), "inst_id": 1}).execute()
                
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    # GET method
    try:
        res = supabase.table('statistics').select("data_json").eq("table_id", "BOT_UNANSWERED").execute()
        if res.data:
            unanswered_data = json.loads(res.data[0]['data_json'])
            return jsonify({"status": "success", "data": unanswered_data.get("messages", [])})
        return jsonify({"status": "success", "data": []})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@core_bp.route('/api/bot/unanswered/<msg_id>/resolve', methods=['POST'])
def resolve_bot_unanswered(msg_id):
    import json
    try:
        res = supabase.table('statistics').select("data_json").eq("table_id", "BOT_UNANSWERED").execute()
        if not res.data:
            return jsonify({"status": "error", "message": "No data found"})
            
        unanswered_data = json.loads(res.data[0]['data_json'])
        for msg in unanswered_data.get("messages", []):
            if msg["id"] == msg_id:
                msg["status"] = "resolved"
                break
                
        supabase.table('statistics').update({"data_json": json.dumps(unanswered_data)}).eq("table_id", "BOT_UNANSWERED").execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
'''

with open('routes/core.py', 'a', encoding='utf-8') as f:
    f.write(routes_code)
print('Routes appended')
