@app.route('/api/informe_dinamico', methods=['GET'])
def get_informe_dinamico():
    inst_id = request.args.get('inst_id', 1, type=int)
    program_id = request.args.get('program_id', 0, type=int)
    
    try:
        # 1. Traer modelo
        try:
            model_res = supabase.table('factors').select("*, characteristics(*, aspects(*))").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        except Exception:
            model_res = supabase.table('factors').select("*, characteristics(*, aspects(*))").eq("inst_id", inst_id).eq("program_id", program_id).execute()
            
        factors = model_res.data
        factors.sort(key=lambda x: int(x.get('number', 999)))
        
        # 2. Traer evaluaciones
        evals_res = supabase.table('evaluations').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        evals_map = {e['aspect_id']: e for e in evals_res.data}
        
        # 3. Traer evidencias
        evid_res = supabase.table('evidence').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        evid_map = {}
        for ev in evid_res.data:
            aspect_id = ev['aspect_id']
            if aspect_id not in evid_map:
                evid_map[aspect_id] = []
            evid_map[aspect_id].append(ev)
            
        # 4. Traer cuadros estadísticos (statistics)
        stats_res = supabase.table('statistics').select("*").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        stats_map = {s['table_id']: json.loads(s['data_json']) for s in stats_res.data}
        
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
                "number": f['number'],
                "name": f['name'],
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
            chars.sort(key=lambda x: float(x.get('number', 999)))
            
            for c in chars:
                char_info = {
                    "id": c['id'],
                    "number": c['number'],
                    "name": c['name'],
                    "aspectos": [],
                    "nota_promedio": 0
                }
                
                c_score_sum = 0
                c_score_count = 0
                
                aspects = c.get('aspects', [])
                aspects.sort(key=lambda x: float(x.get('number', 999)))
                
                for a in aspects:
                    a_id = a['id']
                    e_data = evals_map.get(a_id, {})
                    evidencias = evid_map.get(a_id, [])
                    
                    score = e_data.get('score', 0)
                    if score > 0:
                        c_score_sum += score
                        c_score_count += 1
                        
                    justification = e_data.get('justification', '')
                    if justification:
                        f_justifications.append(justification)
                        
                    aspect_info = {
                        "id": a_id,
                        "number": a['number'],
                        "name": a['name'],
                        "score": score,
                        "justification": justification,
                        "evidencias": [{"name": ev['name'], "file_path": ev['file_path']} for ev in evidencias]
                    }
                    char_info['aspectos'].append(aspect_info)
                
                if c_score_count > 0:
                    char_info['nota_promedio'] = round(c_score_sum / c_score_count, 2)
                    f_score_sum += char_info['nota_promedio']
                    f_score_count += 1
                    
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
        return jsonify({"error": str(e)}), 500
