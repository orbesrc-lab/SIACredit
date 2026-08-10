from flask import Blueprint, jsonify, request, render_template
from utils.auth import require_permission

def safe_int(val, default=1):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default
from utils.db import supabase, get_active_inst_id
import traceback

planning_bp = Blueprint('planning', __name__)
from routes.ai import call_ai

# --- MÓDULO PLANIFICACIÓN Y CONTROL ---

@planning_bp.route('/planificacion.html')
def planificacion_page():
    return render_template('planificacion.html')

@planning_bp.route('/api/dofa/suggest_axes', methods=['POST'])
@require_permission('planificacion')
def suggest_dofa_axes():
    try:
        data = request.json
        dofa_data = data.get('dofa_data')
        
        if not dofa_data:
            return jsonify({'status': 'error', 'message': 'No hay datos DOFA'})

        strategies = []
        for q in ['FO', 'DO', 'FA', 'DA']:
            if q in dofa_data:
                for s in dofa_data[q]:
                    if s.strip():
                        strategies.append(f"[{q}] {s.strip()}")

        if not strategies:
            return jsonify({'status': 'error', 'message': 'No hay estrategias para agrupar'})

        prompt = (
            "Eres un experto en planificación estratégica institucional. A continuación te presento una lista de "
            "estrategias resultantes de una matriz DOFA. Tu tarea es analizar estas estrategias y agruparlas en 3 a 5 "
            "'Ejes Estratégicos' coherentes.\n"
            "Responde ÚNICAMENTE con un JSON estrictamente válido que siga esta estructura exacta (sin markdown ni explicaciones adicionales):\n"
            "[\n"
            "  {\n"
            "    \"name\": \"Nombre del Eje (Ej: Calidad Académica)\",\n"
            "    \"description\": \"Descripción breve del eje\",\n"
            "    \"strategies\": [\"[FO] Estrategia exacta 1\", \"[DO] Estrategia exacta 2\"]\n"
            "  }\n"
            "]\n\n"
            "Lista de estrategias a agrupar:\n" + "\n".join(f"- {s}" for s in strategies)
        )

        response = call_ai(
            messages=[
                {"role": "system", "content": "Eres un sistema de procesamiento de datos en JSON puro. No uses formato markdown de bloque (```json). Devuelve el texto JSON directamente."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2500
        )
        
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
            
        import json
        axes_suggestion = json.loads(response.strip())
        
        return jsonify({'status': 'success', 'axes': axes_suggestion})
    except Exception as e:
        print(f"Error en suggest_dofa_axes: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


@planning_bp.route('/api/planning/migrate_dofa', methods=['POST'])
@require_permission('planificacion')
def migrate_dofa():
    import re
    try:
        data = request.json
        inst_id = data.get('inst_id')
        program_id = data.get('program_id', 0)
        structured_axes = data.get('structured_axes')
        dofa_data = data.get('dofa_data')
        
        if not inst_id:
            return jsonify({'status': 'error', 'message': 'Faltan datos requeridos'})

        migrated_count = 0
        if structured_axes:
            # Flujo Nuevo con Ejes Sugeridos por IA
            for axis in structured_axes:
                axis_name = axis.get('name', 'Nuevo Eje')
                axis_res = supabase.table('planning_axes').select('*').eq('inst_id', inst_id).eq('name', axis_name).execute()
                if not axis_res.data:
                    axis_insert = supabase.table('planning_axes').insert({
                        'inst_id': inst_id,
                        'name': axis_name,
                        'description': axis.get('description', '')
                    }).execute()
                    axis_id = axis_insert.data[0]['id']
                else:
                    axis_id = axis_res.data[0]['id']

                for strategy in axis.get('strategies', []):
                    quad_match = re.match(r'^\[(FO|DO|FA|DA)\]\s*(.*)', strategy)
                    if quad_match:
                        quadKey = quad_match.group(1)
                        desc = quad_match.group(2)
                    else:
                        quadKey = 'FO' # fallback
                        desc = strategy
                    
                    if desc.strip():
                        check_res = supabase.table('planning_strategies').select('id').eq('inst_id', inst_id).eq('quadrant', quadKey).eq('description', desc.strip()).execute()
                        if not check_res.data:
                            supabase.table('planning_strategies').insert({
                                'inst_id': inst_id,
                                'program_id': program_id,
                                'axis_id': axis_id,
                                'quadrant': quadKey,
                                'description': desc.strip()
                            }).execute()
                            migrated_count += 1
                        else:
                            strategy_id = check_res.data[0]['id']
                            supabase.table('planning_strategies').update({
                                'axis_id': axis_id
                            }).eq('id', strategy_id).execute()
                            migrated_count += 1
        elif dofa_data:
            # Flujo Antiguo/Fallback
            axis_res = supabase.table('planning_axes').select('*').eq('inst_id', inst_id).eq('name', 'General DOFA').execute()
            if not axis_res.data:
                axis_insert = supabase.table('planning_axes').insert({
                    'inst_id': inst_id,
                    'name': 'General DOFA',
                    'description': 'Eje creado automáticamente desde el Cruce DOFA'
                }).execute()
                axis_id = axis_insert.data[0]['id']
            else:
                axis_id = axis_res.data[0]['id']

            for quadKey in ['FO', 'DO', 'FA', 'DA']:
                if quadKey in dofa_data:
                    for strategy in dofa_data[quadKey]:
                        if strategy.strip():
                            check_res = supabase.table('planning_strategies').select('id').eq('inst_id', inst_id).eq('quadrant', quadKey).eq('description', strategy.strip()).execute()
                            if not check_res.data:
                                supabase.table('planning_strategies').insert({
                                    'inst_id': inst_id,
                                    'program_id': program_id,
                                    'axis_id': axis_id,
                                    'quadrant': quadKey,
                                    'description': strategy.strip()
                                }).execute()
                                migrated_count += 1
                            
        return jsonify({'status': 'success', 'migrated_count': migrated_count})
    except Exception as e:
        print(f"Error en migrate_dofa: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@planning_bp.route('/api/planning/tree', methods=['GET'])
@require_permission('planificacion')
def get_planning_tree():
    try:
        inst_id = request.args.get('inst_id')
        try:
            inst_id = int(inst_id)
        except (ValueError, TypeError):
            inst_id = 1
            
        program_id = request.args.get('program_id')
        try:
            program_id = int(program_id) if program_id else 0
        except (ValueError, TypeError):
            program_id = 0
            
        if not inst_id:
            return jsonify({'status': 'error', 'message': 'inst_id is required'})

        axes = supabase.table('planning_axes').select('*').eq('inst_id', inst_id).execute().data
        
        strategies_query = supabase.table('planning_strategies').select('*').eq('inst_id', inst_id)
        if program_id != 0:
            strategies_query = strategies_query.eq('program_id', program_id)
        strategies = strategies_query.execute().data
        
        strat_ids = [s['id'] for s in strategies] if strategies else []
        gen_objs = []
        if strat_ids:
            gen_objs = supabase.table('planning_general_objectives').select('*').in_('strategy_id', strat_ids).execute().data
            
        gen_obj_ids = [g['id'] for g in gen_objs] if gen_objs else []
        spec_objs = []
        if gen_obj_ids:
            spec_objs = supabase.table('planning_specific_objectives').select('*').in_('general_objective_id', gen_obj_ids).execute().data
            
        spec_obj_ids = [s['id'] for s in spec_objs] if spec_objs else []
        activities = []
        if spec_obj_ids:
            activities = supabase.table('planning_activities').select('*').in_('specific_objective_id', spec_obj_ids).execute().data

        act_by_spec = {}
        for a in activities:
            act_by_spec.setdefault(a['specific_objective_id'], []).append(a)
            
        spec_by_gen = {}
        for s in spec_objs:
            s['activities'] = act_by_spec.get(s['id'], [])
            spec_by_gen.setdefault(s['general_objective_id'], []).append(s)
            
        gen_by_strat = {}
        for g in gen_objs:
            g['specific_objectives'] = spec_by_gen.get(g['id'], [])
            gen_by_strat.setdefault(g['strategy_id'], []).append(g)
            
        strat_by_axis = {}
        for s in strategies:
            s['general_objectives'] = gen_by_strat.get(s['id'], [])
            strat_by_axis.setdefault(s['axis_id'], []).append(s)
            
        tree = []
        for ax in axes:
            ax['strategies'] = strat_by_axis.get(ax['id'], [])
            if program_id == 0 or len(ax['strategies']) > 0:
                tree.append(ax)

        return jsonify({'status': 'success', 'tree': tree})
    except Exception as e:
        print(f"Error in planning tree: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@planning_bp.route('/api/planning/node', methods=['POST'])
@require_permission('planificacion')
def add_planning_node():
    try:
        data = request.json
        node_type = data.get('type')
        inst_id = data.get('inst_id')
        try:
            inst_id = int(inst_id)
        except (ValueError, TypeError):
            inst_id = 1
        parent_id = data.get('parent_id')
        
        if not node_type or not inst_id or not parent_id:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros'})

        if node_type == 'strategy':
            program_id = data.get('program_id', 0)
            supabase.table('planning_strategies').insert({
                'inst_id': inst_id,
                'program_id': program_id,
                'axis_id': parent_id,
                'description': data.get('description', ''),
                'weight_percentage': data.get('weight_percentage', 0),
                'quadrant': data.get('quadrant', 'MANUAL')
            }).execute()
        elif node_type == 'gen_obj':
            supabase.table('planning_general_objectives').insert({
                'strategy_id': parent_id,
                'description': data.get('description', ''),
                'alignment_pdi': data.get('alignment_pdi', '')
            }).execute()
        elif node_type == 'spec_obj':
            supabase.table('planning_specific_objectives').insert({
                'general_objective_id': parent_id,
                'description': data.get('description', ''),
                'weight_percentage': data.get('weight_percentage', 0),
                'indicator_type': data.get('indicator_type', ''),
                'indicator_description': data.get('indicator_description', '')
            }).execute()
        elif node_type == 'activity':
            supabase.table('planning_activities').insert({
                'specific_objective_id': parent_id,
                'description': data.get('description', ''),
                'start_date': data.get('start_date'),
                'end_date': data.get('end_date'),
                'goal': data.get('goal', ''),
                'responsible': data.get('responsible', ''),
                'financial_budget': data.get('financial_budget', 0),
                'status': 'Pendiente'
            }).execute()
        else:
            return jsonify({'status': 'error', 'message': 'Tipo inválido'})

        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error in add planning node: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@planning_bp.route('/api/planning/node/edit', methods=['POST'])
@require_permission('planificacion')
def edit_planning_node():
    try:
        data = request.json
        node_type = data.get('type')
        node_id = data.get('id')
        
        if not node_type or not node_id:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros'})

        table_map = {
            'axis': 'planning_axes',
            'strategy': 'planning_strategies',
            'gen_obj': 'planning_general_objectives',
            'spec_obj': 'planning_specific_objectives',
            'activity': 'planning_activities'
        }
        
        table_name = table_map.get(node_type)
        if not table_name:
            return jsonify({'status': 'error', 'message': 'Tipo inválido'})
            
        update_data = {}
        if 'description' in data: update_data['description'] = data['description']
        if 'name' in data: update_data['name'] = data['name']
        if 'weight_percentage' in data: update_data['weight_percentage'] = data['weight_percentage']
        if 'alignment_pdi' in data: update_data['alignment_pdi'] = data['alignment_pdi']
        if 'indicator_type' in data: update_data['indicator_type'] = data['indicator_type']
        if 'indicator_description' in data: update_data['indicator_description'] = data['indicator_description']
        if 'start_date' in data: update_data['start_date'] = data['start_date']
        if 'end_date' in data: update_data['end_date'] = data['end_date']
        if 'goal' in data: update_data['goal'] = data['goal']
        if 'responsible' in data: update_data['responsible'] = data['responsible']
        if 'financial_budget' in data: update_data['financial_budget'] = data['financial_budget']

        if update_data:
            supabase.table(table_name).update(update_data).eq('id', node_id).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@planning_bp.route('/api/planning/node/delete', methods=['POST'])
@require_permission('planificacion')
def delete_planning_node():
    try:
        data = request.json
        node_type = data.get('type')
        node_id = data.get('id')
        
        if not node_type or not node_id:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros'})

        table_map = {
            'axis': 'planning_axes',
            'strategy': 'planning_strategies',
            'gen_obj': 'planning_general_objectives',
            'spec_obj': 'planning_specific_objectives',
            'activity': 'planning_activities'
        }
        
        table_name = table_map.get(node_type)
        if not table_name:
            return jsonify({'status': 'error', 'message': 'Tipo inválido'})
            
        supabase.table(table_name).delete().eq('id', node_id).execute()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error deleting planning node: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@planning_bp.route('/api/planning/suggest', methods=['POST'])
@require_permission('planificacion')
def suggest_planning_node():
    try:
        data = request.json
        req_type = data.get('type')
        target_id = data.get('target_id')
        inst_id = data.get('inst_id')
        try:
            inst_id = int(inst_id)
        except (ValueError, TypeError):
            inst_id = 1
        
        if not req_type or not target_id:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros'})

        prompt = ""
        
        if req_type == 'gen_obj':
            strat = supabase.table('planning_strategies').select('*').eq('id', target_id).execute().data
            if not strat:
                return jsonify({'status': 'error', 'message': 'Estrategia no encontrada'})
            context_text = strat[0]['description']
            prompt = f"Actúa como un experto en planificación estratégica institucional. Basado en la siguiente ESTRATEGIA: '{context_text}', redacta UN solo OBJETIVO GENERAL claro, medible y ambicioso que permita cumplir esta estrategia. No incluyas explicaciones, responde ÚNICAMENTE con el texto del objetivo."
            
        elif req_type == 'spec_obj':
            gen = supabase.table('planning_general_objectives').select('*').eq('id', target_id).execute().data
            if not gen:
                return jsonify({'status': 'error', 'message': 'Objetivo General no encontrado'})
            context_text = gen[0]['description']
            prompt = f"Actúa como un experto en planificación estratégica institucional. Basado en el siguiente OBJETIVO GENERAL: '{context_text}', redacta UN solo OBJETIVO ESPECÍFICO que divida o concrete el objetivo general. Debe ser preciso y orientarse a un resultado medible. No incluyas explicaciones, responde ÚNICAMENTE con el texto del objetivo."
            
        elif req_type == 'activity':
            spec = supabase.table('planning_specific_objectives').select('*').eq('id', target_id).execute().data
            if not spec:
                return jsonify({'status': 'error', 'message': 'Objetivo Específico no encontrado'})
            context_text = spec[0]['description']
            prompt = f"Actúa como un experto en planificación estratégica institucional. Basado en el siguiente OBJETIVO ESPECÍFICO: '{context_text}', redacta UNA ACTIVIDAD concreta, ejecutable y clara que contribuya a lograr ese objetivo. No incluyas explicaciones, responde ÚNICAMENTE con el texto de la actividad."
        
        if not prompt:
            return jsonify({'status': 'error', 'message': 'Tipo inválido'})

        suggestion = call_ai(
            messages=[
                {"role": "system", "content": "Eres un experto en Planeación Estratégica. Responde ÚNICAMENTE con el texto de la sugerencia, sin markdown ni explicaciones adicionales."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        suggestion = suggestion.strip()
        if suggestion.startswith('"') and suggestion.endswith('"'):
            suggestion = suggestion[1:-1]
        
        return jsonify({'status': 'success', 'suggestion': suggestion})
    except Exception as e:
        print(f"Error in suggest_planning_node: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@planning_bp.route('/api/planning/users', methods=['GET'])
@require_permission('planificacion')
def get_planning_users():
    """Returns list of users in the institution for assignment dropdowns.
    Only returns users with roles allowed as activity responsibles:
    admin, inst_admin, lider, operativo.
    Excludes: estudiante, profesor, auditor, consultor.
    """
    # Roles autorizados para ser responsables de actividades
    ALLOWED_ROLES = {'admin', 'inst_admin', 'lider', 'operativo'}
    try:
        inst_id = request.args.get('inst_id')
        try:
            inst_id = int(inst_id)
        except (ValueError, TypeError):
            inst_id = 1
        if not inst_id:
            return jsonify({'status': 'error', 'message': 'inst_id required'})
        res = supabase.table('users').select('id, name, email, role').eq('inst_id', inst_id).execute()
        users = res.data or []
        # Filtrar solo roles permitidos como responsables
        users = [u for u in users if u.get('role') in ALLOWED_ROLES]
        # Ordenar por prioridad de rol
        role_order = {'admin': 0, 'inst_admin': 1, 'lider': 2, 'operativo': 3}
        users.sort(key=lambda u: role_order.get(u.get('role', ''), 99))
        return jsonify({'status': 'success', 'users': users})
    except Exception as e:
        print(f"Error in get_planning_users: {e}")
        return jsonify({'status': 'error', 'message': str(e)})



# ══════════════════════════════════════════════════════════════════


import json
from datetime import datetime

@planning_bp.route('/api/planning/activity/alert/<int:act_id>', methods=['POST'])
@require_permission('planificacion')
def add_activity_alert(act_id):
    try:
        data = request.json
        inst_id = safe_int(data.get('inst_id'), 1)
        program_id = safe_int(data.get('program_id'), 0)
        if program_id == 0: program_id = None
        message = data.get('message', 'Alerta de Planificación')
        sender = data.get('sender', 'Sistema')
        responsible_email = data.get('responsible_email')

        if not responsible_email:
            return jsonify({'status': 'error', 'message': 'No hay responsable asignado'})

        # 1. Guardar en notificaciones
        supabase.table('notificaciones').insert({
            'inst_id': inst_id,
            'program_id': program_id,
            'usuario_email': responsible_email,
            'tipo': 'alerta_planificacion',
            'titulo': 'Alerta de Actividad',
            'mensaje': message,
            'leido': False
        }).execute()

        # 2. Guardar en statistics (logs de la actividad)
        table_id = f"PLANNING_ACT_LOGS_{act_id}"
        stats_res = supabase.table('statistics').select('*').eq('table_id', table_id).execute().data
        
        new_log = {
            'date': datetime.now().isoformat(),
            'message': message,
            'sender': sender
        }
        
        if stats_res:
            logs = json.loads(stats_res[0]['data_json']) if isinstance(stats_res[0]['data_json'], str) else stats_res[0]['data_json']
            if not isinstance(logs, list): logs = []
            logs.append(new_log)
            supabase.table('statistics').update({'data_json': logs}).eq('id', stats_res[0]['id']).execute()
        else:
            supabase.table('statistics').insert({
                'inst_id': inst_id,
                'program_id': program_id,
                'table_id': table_id,
                'data_json': [new_log]
            }).execute()

        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error in add_activity_alert: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


@planning_bp.route('/api/planning/activity/finance/<int:act_id>', methods=['POST'])
@require_permission('planificacion')
def update_activity_finance(act_id):
    try:
        data = request.json
        inst_id = safe_int(data.get('inst_id'), 1)
        program_id = safe_int(data.get('program_id'), 0)
        if program_id == 0: program_id = None
        executed_budget = float(data.get('executed_budget', 0))
        executed_hours = float(data.get('executed_hours', 0))

        table_id = f"PLANNING_ACT_FINANCE_{act_id}"
        stats_res = supabase.table('statistics').select('*').eq('table_id', table_id).execute().data
        
        finance_data = {
            'executed_budget': executed_budget,
            'executed_hours': executed_hours,
            'updated_at': datetime.now().isoformat()
        }
        
        if stats_res:
            supabase.table('statistics').update({'data_json': finance_data}).eq('id', stats_res[0]['id']).execute()
        else:
            supabase.table('statistics').insert({
                'inst_id': inst_id,
                'program_id': program_id,
                'table_id': table_id,
                'data_json': finance_data
            }).execute()

        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error in update_activity_finance: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


@planning_bp.route('/api/planning/activity/evidence/<int:act_id>', methods=['POST'])
@require_permission('planificacion')
def add_activity_evidence(act_id):
    try:
        inst_id = safe_int(request.form.get('inst_id'), 1)
        program_id = safe_int(request.form.get('program_id'), 0)
        if program_id == 0: program_id = None
        uploader = request.form.get('uploader', 'Usuario')
        
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file uploaded'})
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'})

        import uuid, os
        file_ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"
        storage_path = f"inst_{inst_id}/prog_{program_id}/planning/{act_id}/{unique_name}"
        
        file_bytes = file.read()
        res = supabase.storage.from_('evidencias').upload(storage_path, file_bytes)
        
        # Get public url
        url_res = supabase.storage.from_('evidencias').get_public_url(storage_path)
        file_url = url_res if isinstance(url_res, str) else url_res.get('publicURL', '')

        table_id = f"PLANNING_ACT_EVID_{act_id}"
        stats_res = supabase.table('statistics').select('*').eq('table_id', table_id).execute().data
        
        new_ev = {
            'name': file.filename,
            'url': storage_path,
            'public_url': file_url,
            'date': datetime.now().isoformat(),
            'uploader': uploader
        }
        
        if stats_res:
            evs = json.loads(stats_res[0]['data_json']) if isinstance(stats_res[0]['data_json'], str) else stats_res[0]['data_json']
            if not isinstance(evs, list): evs = []
            evs.append(new_ev)
            supabase.table('statistics').update({'data_json': evs}).eq('id', stats_res[0]['id']).execute()
        else:
            supabase.table('statistics').insert({
                'inst_id': inst_id,
                'program_id': program_id,
                'table_id': table_id,
                'data_json': [new_ev]
            }).execute()

        return jsonify({'status': 'success', 'evidence': new_ev})
    except Exception as e:
        print(f"Error in add_activity_evidence: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@planning_bp.route('/api/planning/activity/evidence/<int:act_id>', methods=['DELETE'])
@require_permission('planificacion')
def delete_activity_evidence(act_id):
    try:
        data = request.json
        url_to_delete = data.get('url')
        if not url_to_delete:
            return jsonify({'status': 'error', 'message': 'Missing url'})
            
        table_id = f"PLANNING_ACT_EVID_{act_id}"
        stats_res = supabase.table('statistics').select('*').eq('table_id', table_id).execute().data
        if not stats_res:
            return jsonify({'status': 'error', 'message': 'No evidences found'})
            
        evs = json.loads(stats_res[0]['data_json']) if isinstance(stats_res[0]['data_json'], str) else stats_res[0]['data_json']
        new_evs = [ev for ev in evs if ev.get('url') != url_to_delete]
        
        try:
            supabase.storage.from_('evidencias').remove([url_to_delete])
        except Exception as e_storage:
            print(f"Storage remove error: {e_storage}")
            
        supabase.table('statistics').update({'data_json': new_evs}).eq('id', stats_res[0]['id']).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error deleting evidence: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


@planning_bp.route('/api/cron/planning_alerts', methods=['GET', 'POST'])
def cron_planning_alerts():
    try:
        activities = supabase.table('planning_activities').select('*').neq('status', 'Cumplido').execute().data
        if not activities:
            return jsonify({'status': 'success', 'message': 'No pending activities'})
            
        alerts_sent = 0
        now = datetime.now()
        
        for act in activities:
            if not act.get('end_date'): continue
            if not act.get('responsible'): continue
            
            try:
                end_date = datetime.strptime(act['end_date'], "%Y-%m-%d")
            except:
                continue
                
            delta = end_date - now
            if delta.days <= 1:
                act_id = act['id']
                table_id = f"PLANNING_ACT_LOGS_{act_id}"
                stats_res = supabase.table('statistics').select('data_json, id').eq('table_id', table_id).execute().data
                
                already_sent_today = False
                if stats_res:
                    logs = json.loads(stats_res[0]['data_json']) if isinstance(stats_res[0]['data_json'], str) else stats_res[0]['data_json']
                    if isinstance(logs, list):
                        for log in logs:
                            if log.get('sender') == 'CronBot' and log.get('date', '').startswith(now.strftime("%Y-%m-%d")):
                                already_sent_today = True
                                break
                                
                if not already_sent_today:
                    message = f"ALERTA AUTOMÁTICA: La actividad '{act['description']}' vence el {act['end_date']}."
                    
                    supabase.table('notificaciones').insert({
                        'inst_id': 1,
                        'program_id': 0,
                        'usuario_email': act['responsible'],
                        'tipo': 'alerta_planificacion_cron',
                        'titulo': 'Vencimiento Próximo/Cumplido',
                        'mensaje': message,
                        'leido': False
                    }).execute()
                    
                    new_log = {
                        'date': now.isoformat(),
                        'message': message,
                        'sender': 'CronBot'
                    }
                    if stats_res:
                        logs = json.loads(stats_res[0]['data_json']) if isinstance(stats_res[0]['data_json'], str) else stats_res[0]['data_json']
                        if not isinstance(logs, list): logs = []
                        logs.append(new_log)
                        supabase.table('statistics').update({'data_json': logs}).eq('id', stats_res[0]['id']).execute()
                    else:
                        supabase.table('statistics').insert({
                            'inst_id': 1,
                            'program_id': 0,
                            'table_id': table_id,
                            'data_json': [new_log]
                        }).execute()
                    alerts_sent += 1

        return jsonify({'status': 'success', 'alerts_sent': alerts_sent})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)})

@planning_bp.route('/api/planning/reports/finance', methods=['GET'])
@require_permission('planificacion')
def report_finance():
    try:
        inst_id = request.args.get('inst_id', 1, type=int)
        program_id = request.args.get('program_id', 0, type=int)
        
        # We need strategies, general_objectives, specific_objectives, activities, and their finance data
        axes = supabase.table('planning_axes').select('*').eq('inst_id', inst_id).execute().data
        
        strategies_query = supabase.table('planning_strategies').select('*').eq('inst_id', inst_id)
        if program_id != 0:
            strategies_query = strategies_query.eq('program_id', program_id)
        strategies = strategies_query.execute().data
        gen_objs = supabase.table('planning_general_objectives').select('*').execute().data
        spec_objs = supabase.table('planning_specific_objectives').select('*').execute().data
        activities = supabase.table('planning_activities').select('*').execute().data
        
        stats_res = supabase.table('statistics').select('*').like('table_id', 'PLANNING_ACT_FINANCE_%').execute().data
        finance_map = {}
        for s in stats_res:
            try:
                act_id = int(s['table_id'].replace('PLANNING_ACT_FINANCE_', ''))
                finance_map[act_id] = json.loads(s['data_json']) if isinstance(s['data_json'], str) else s['data_json']
            except:
                pass
                
        # Aggregate logic
        act_by_spec = {}
        for a in activities:
            f = finance_map.get(a['id'], {})
            a['executed_budget'] = f.get('executed_budget', 0)
            a['financial_budget'] = float(a.get('financial_budget') or 0)
            act_by_spec.setdefault(a['specific_objective_id'], []).append(a)
            
        spec_by_gen = {}
        for s in spec_objs:
            acts = act_by_spec.get(s['id'], [])
            s['activities'] = acts
            s['projected_budget'] = sum(a['financial_budget'] for a in acts)
            s['executed_budget'] = sum(a['executed_budget'] for a in acts)
            spec_by_gen.setdefault(s['general_objective_id'], []).append(s)
            
        gen_by_strat = {}
        for g in gen_objs:
            specs = spec_by_gen.get(g['id'], [])
            g['specific_objectives'] = specs
            g['projected_budget'] = sum(s['projected_budget'] for s in specs)
            g['executed_budget'] = sum(s['executed_budget'] for s in specs)
            gen_by_strat.setdefault(g['strategy_id'], []).append(g)
            
        report = []
        total_projected = 0
        total_executed = 0
        
        for st in strategies:
            gens = gen_by_strat.get(st['id'], [])
            st['general_objectives'] = gens
            proj = sum(g['projected_budget'] for g in gens)
            exec_b = sum(g['executed_budget'] for g in gens)
            
            st['projected_budget'] = proj
            st['executed_budget'] = exec_b
            total_projected += proj
            total_executed += exec_b
            
            report.append({
                'id': st['id'],
                'description': st['description'],
                'projected': proj,
                'executed': exec_b,
                'difference': proj - exec_b,
                'children': [{
                    'id': g['id'],
                    'description': g['description'],
                    'projected': g['projected_budget'],
                    'executed': g['executed_budget'],
                    'difference': g['projected_budget'] - g['executed_budget'],
                    'children': [{
                        'id': s['id'],
                        'description': s['description'],
                        'projected': s['projected_budget'],
                        'executed': s['executed_budget'],
                        'difference': s['projected_budget'] - s['executed_budget'],
                        'children': [{
                            'id': a['id'],
                            'description': a['description'],
                            'projected': a['financial_budget'],
                            'executed': a['executed_budget'],
                            'difference': a['financial_budget'] - a['executed_budget'],
                            'status': a['status']
                        } for a in s['activities']]
                    } for s in g['specific_objectives']]
                } for g in gens]
            })
            
        return jsonify({
            'status': 'success',
            'report': report,
            'total_projected': total_projected,
            'total_executed': total_executed,
            'total_difference': total_projected - total_executed
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)})



@planning_bp.route('/api/planning/activity/evidences/<int:act_id>', methods=['GET'])
@require_permission('planificacion')
def get_activity_evidences(act_id):
    try:
        table_id = f"PLANNING_ACT_EVID_{act_id}"
        stats_res = supabase.table('statistics').select('*').eq('table_id', table_id).execute().data
        if not stats_res:
            return jsonify({'status': 'success', 'evidences': []})
        
        import json
        evs = stats_res[0]['data_json']
        if isinstance(evs, str):
            evs = json.loads(evs)
        return jsonify({'status': 'success', 'evidences': evs})
    except Exception as e:
        print(f"Error in get_activity_evidences: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

