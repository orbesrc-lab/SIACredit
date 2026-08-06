from flask import Blueprint, jsonify, request
from utils.db import supabase
from utils.auth import require_permission

crm_bp = Blueprint('crm', __name__)

# --- RUTAS DE PARTNERS ---
@crm_bp.route('/api/partners', methods=['GET'])
@require_permission('herramientas')
def get_partners():
    try:
        res = supabase.table('partners').select("*").order("created_at", desc=False).execute()
        return jsonify({"status": "success", "data": res.data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@crm_bp.route('/api/partners', methods=['POST'])
@require_permission('herramientas')
def add_partner():
    try:
        data = request.json
        res = supabase.table('partners').insert({
            "name": data.get("name"),
            "url": data.get("url"),
            "logo_base64": data.get("logo_base64")
        }).execute()
        return jsonify({"status": "success", "data": res.data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@crm_bp.route('/api/partners/<int:partner_id>', methods=['DELETE'])
@require_permission('herramientas')
def delete_partner(partner_id):
    try:
        res = supabase.table('partners').delete().eq("id", partner_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


