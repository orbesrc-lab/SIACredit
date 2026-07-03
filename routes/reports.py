from flask import Blueprint, jsonify, request
from utils.db import supabase, get_active_inst_id
import traceback
import json
import survey_storage

reports_bp = Blueprint('reports', __name__)

# --- Dashboard Stats ---

@reports_bp.route('/api/dashboard/stats')
def dashboard_stats():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    try:
        evidences = supabase.table('evidences').select("id, status").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        factors = supabase.table('factors').select("id").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        evals = supabase.table('evaluations').select("char_id, rating").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        
        users_query = supabase.table('users').select("id").eq("inst_id", inst_id)
        if program_id != 0:
            users_query = users_query.eq("program_id", program_id)
        users_count = users_query.execute().data

        total_ev = len(evidences)
        pending_ev = len([e for e in evidences if e['status'] == 'pendiente'])
        approved_ev = len([e for e in evidences if e['status'] == 'aprobado'])
        total_factors = len(factors)
        evaluated_factors = len(set(e['char_id'] for e in evals))
        avg_rating = round(sum(e['rating'] for e in evals) / len(evals), 2) if evals else 0
        global_progress = round((avg_rating / 5) * 100, 1) if avg_rating > 0 else 0

        return jsonify({
            "total_evidences": total_ev,
            "pending_evidences": pending_ev,
            "approved_evidences": approved_ev,
            "total_factors": total_factors,
            "evaluated_chars": evaluated_factors,
            "global_progress": global_progress,
            "total_users": len(users_count)
        })
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({"global_progress": 0, "total_evidences": 0, "pending_evidences": 0, "approved_evidences": 0, "total_factors": 0, "evaluated_chars": 0, "total_users": 0})


@reports_bp.route('/api/reports/summary')
def report_summary():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    try:
        # Traer factores con sus pesos y características
        factors = supabase.table('factors').select("*, characteristics(id, weight)").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        evals = supabase.table('evaluations').select("char_id, rating").eq("inst_id", inst_id).eq("program_id", program_id).execute().data
        eval_map = {e['char_id']: e['rating'] for e in evals}
        
        summary = []
        global_weighted_score = 0
        total_factor_weight = 0

        for f in factors:
            factor_score = 0
            # Sumar ponderación de características
            for c in f.get('characteristics', []):
                rating = eval_map.get(c['id'], 0)
                weight = c.get('weight', 0)
                factor_score += rating * (weight / 100)
            
            f_weight = f.get('weight', 0)
            global_weighted_score += factor_score * (f_weight / 100)
            total_factor_weight += f_weight

            summary.append({
                "name": f"Factor {f['number']}: {f['name']}",
                "avg": round(factor_score, 2),
                "cumplimiento": round((factor_score / 5) * 100, 1) if factor_score > 0 else 0,
                "weight": f_weight
            })
            
        return jsonify({
            "factors": summary,
            "global_avg": round(global_weighted_score, 2),
            "global_progress": round((global_weighted_score / 5) * 100, 1) if global_weighted_score > 0 else 0
        })
    except Exception as e:
        print(f"Error in summary: {e}")
        return jsonify({"factors": [], "global_avg": 0})

@reports_bp.route('/api/informe_dinamico', methods=['GET'])
def get_informe_dinamico():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    
    try:
        def safe_float(val):
            try:
                if val is None or str(val).strip() == '': return 999.0
                return float(val)
            except (ValueError, TypeError):
                return 999.0

        # 1. Traer modelo
        try:
            model_res = supabase.table('factors').select("*, characteristics(*, aspects(*))").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        except Exception:
            model_res = supabase.table('factors').select("*, characteristics(*, aspects(*))").eq("inst_id", inst_id).eq("program_id", program_id).execute()
            
        factors = model_res.data
        factors.sort(key=lambda x: safe_float(x.get('number')))
        
        # 2. Traer evaluaciones
        evals_res = supabase.table('evaluations').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        evals_map = {e['char_id']: e for e in evals_res.data}
        
        # 3. Traer evidencias
        evid_res = supabase.table('evidences').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        evid_map = {}
        for ev in evid_res.data:
            aspect_id = ev['aspect_id']
            if aspect_id not in evid_map:
                evid_map[aspect_id] = []
            evid_map[aspect_id].append(ev)
            
        # 4. Traer cuadros estadísticos (statistics)
        stats_res = supabase.table('statistics').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        stats_map = {s['table_id']: json.loads(s['data_json']) for s in stats_res.data}
        
        # 5. Traer encuestas y respuestas (para cruzar con autoevaluación)
        try:
            survey_storage.pull_from_supabase(inst_id, program_id, supabase)
        except Exception as e:
            print(f"Error pulling surveys for dynamic report: {e}")
            
        local_surveys = survey_storage.load_local_surveys(inst_id, program_id)
        local_responses = survey_storage.load_local_responses(inst_id, program_id)
        
        q_map = {}
        for s in local_surveys:
            for q in s.get('questions', []):
                q_map[q['id']] = {
                    "char_id": q.get('char_id'),
                    "aspect_id": q.get('aspect_id'),
                    "type": q.get('type')
                }
                
        char_perceptions = {}
        for r in local_responses:
            answers = r.get('answers', {})
            target = r.get('target', 'Comunidad')
            submitted_at = r.get('submitted_at', '')
            for q_id, val in answers.items():
                if q_id in q_map:
                    q_info = q_map[q_id]
                    char_id = q_info['char_id']
                    if not char_id:
                        continue
                    if char_id not in char_perceptions:
                        char_perceptions[char_id] = {
                            "rating_sum": 0.0,
                            "rating_count": 0,
                            "comments": []
                        }
                    if q_info['type'] == 'rating':
                        try:
                            val_f = float(val)
                            if 1.0 <= val_f <= 5.0:
                                char_perceptions[char_id]['rating_sum'] += val_f
                                char_perceptions[char_id]['rating_count'] += 1
                        except (ValueError, TypeError):
                            pass
                    elif q_info['type'] == 'text' and val and str(val).strip():
                        char_perceptions[char_id]['comments'].append({
                            "text": str(val).strip(),
                            "target": target,
                            "date": submitted_at[:10] if submitted_at else ''
                        })
        
        # Ensamblar datos
        report_data = {
            "institucion_id": inst_id,
            "programa_id": program_id,
            "factores": [],
            "cuadros": stats_map
        }
        
        for f in factors:
            factor_info = {
                "id": f['id'],
                "number": f.get('number', ''),
                "name": f.get('name', ''),
                "description": f.get('description', ''),
                "caracteristicas": [],
                "nota_promedio": 0,
                "cualitativo": "",
                "justificacion_general": ""
            }
            
            f_score_sum = 0
            f_score_count = 0
            f_justifications = []
            
            chars = f.get('characteristics', [])
            chars.sort(key=lambda x: safe_float(x.get('number')))
            
            for c in chars:
                c_id = c['id']
                e_data = evals_map.get(c_id, {})
                score = e_data.get('rating', 0)
                justification = e_data.get('just', '')
                
                perc = char_perceptions.get(c_id, {"rating_sum": 0.0, "rating_count": 0, "comments": []})
                avg_perc = round(perc['rating_sum'] / perc['rating_count'], 2) if perc['rating_count'] > 0 else 0.0
                
                char_info = {
                    "id": c_id,
                    "number": c.get('number', ''),
                    "name": c.get('name', ''),
                    "aspectos": [],
                    "nota_promedio": score,
                    "percepcion_promedio": avg_perc,
                    "percepcion_cantidad": perc['rating_count'],
                    "percepcion_comentarios": perc['comments']
                }
                
                if score > 0:
                    f_score_sum += score
                    f_score_count += 1
                    
                if justification:
                    f_justifications.append(justification)
                
                aspects = c.get('aspects', [])
                aspects.sort(key=lambda x: safe_float(x.get('number')))
                
                for a in aspects:
                    a_id = a['id']
                    evidencias = evid_map.get(a_id, [])
                    
                    aspect_info = {
                        "id": a_id,
                        "number": a.get('number', ''),
                        "name": a.get('name', a.get('text', '')),
                        "evidencias": [{"name": ev['name'], "file_url": ev.get('file_url', ev.get('file_path')), "period": ev.get('period', '')} for ev in evidencias]
                    }
                    char_info['aspectos'].append(aspect_info)
                
                factor_info['caracteristicas'].append(char_info)
                
            if f_score_count > 0:
                avg = round(f_score_sum / f_score_count, 2)
                factor_info['nota_promedio'] = avg
                if avg >= 4.5:
                    factor_info['cualitativo'] = "Se cumple plenamente"
                elif avg >= 4.0:
                    factor_info['cualitativo'] = "Se cumple en alto grado"
                elif avg >= 3.0:
                    factor_info['cualitativo'] = "Se cumple aceptablemente"
                elif avg > 0:
                    factor_info['cualitativo'] = "No se cumple"
                else:
                    factor_info['cualitativo'] = "Sin evaluar"
            else:
                factor_info['cualitativo'] = "Sin evaluar"
                
            # Unir justificaciones de manera simple
            factor_info['justificacion_general'] = " ".join(f_justifications[:3]) + ("..." if len(f_justifications) > 3 else "")
            
            report_data['factores'].append(factor_info)
            
        return jsonify(report_data)
    except Exception as e:
        print(f"Error informe dinamico: {e}")
        return jsonify({"error": str(e)})


