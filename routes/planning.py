from flask import Blueprint, jsonify, request
from utils.db import supabase, get_active_inst_id
import traceback

planning_bp = Blueprint('planning', __name__)

# --- MÓDULO PLANIFICACIÓN Y CONTROL ---

@planning_bp.route('/planificacion.html')
def planificacion_page():
    return render_template('planificacion.html')

@planning_bp.route('/api/dofa/suggest_axes', methods=['POST'])
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
def get_planning_tree():
    try:
        inst_id = request.args.get('inst_id')
        try:
            inst_id = int(inst_id)
        except (ValueError, TypeError):
            inst_id = 1
        if not inst_id:
            return jsonify({'status': 'error', 'message': 'inst_id is required'})

        axes = supabase.table('planning_axes').select('*').eq('inst_id', inst_id).execute().data
        strategies = supabase.table('planning_strategies').select('*').eq('inst_id', inst_id).execute().data
        
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
            tree.append(ax)

        return jsonify({'status': 'success', 'tree': tree})
    except Exception as e:
        print(f"Error in planning tree: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@planning_bp.route('/api/planning/node', methods=['POST'])
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
            supabase.table('planning_strategies').insert({
                'inst_id': inst_id,
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
def delete_planning_node():
    try:
        data = request.json
        node_type = data.get('type')
        node_id = data.get('id')
        
        if not node_type or not node_id:
            return jsonify({'status': 'error', 'message': 'Faltan parámetros'})

        table_map = {
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
def get_planning_users():
    """Returns list of users in the institution for assignment dropdowns."""
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
        # Sort by role priority
        role_order = {'admin': 0, 'lider': 1, 'operador': 2, 'docente': 3, 'estudiante': 4}
        users.sort(key=lambda u: role_order.get(u.get('role', 'estudiante'), 99))
        return jsonify({'status': 'success', 'users': users})
    except Exception as e:
        print(f"Error in get_planning_users: {e}")
        return jsonify({'status': 'error', 'message': str(e)})



# ══════════════════════════════════════════════════════════════════
