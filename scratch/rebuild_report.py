import re

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'r', encoding='utf-8') as f:
    gerencial_content = f.read()

# --- 1. Head / CSS ---
gantt_includes = """    <!-- Frappe Gantt -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/frappe-gantt/0.6.1/frappe-gantt.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/frappe-gantt/0.6.1/frappe-gantt.min.js"></script>
    <!-- End Frappe Gantt -->"""

if "frappe-gantt" not in gerencial_content:
    gerencial_content = gerencial_content.replace('</head>', f'{gantt_includes}\n</head>')

css_to_add = """
    <style>
        .grade-4-5 { background: #dcfce7; color: #166534; }
        .grade-4-0 { background: #dbeafe; color: #1e40af; }
        .grade-3-0 { background: #fef9c3; color: #854d0e; }
        .grade-low { background: #fee2e2; color: #991b1b; }
        .grade-badge { padding: 4px 8px; border-radius: 12px; font-weight: bold; }
        
        .factor-section { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        .factor-title { font-size: 1.2rem; color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
        .evidence-list { list-style: none; padding-left: 0; }
        .evidence-list li { margin-bottom: 8px; background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0; font-size: 0.9rem; }
        
        /* Node Tree */
        .node-card { background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; margin-bottom: 15px; position: relative; display: flex; gap: 15px; align-items: flex-start; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
        .node-card.level-1 { border-left: 5px solid #2563eb; margin-left: 0; }
        .node-card.level-2 { border-left: 5px solid #10b981; margin-left: 40px; background: #f8fafc; }
        .node-card.level-3 { border-left: 5px solid #f59e0b; margin-left: 80px; background: #fefce8; padding: 12px 15px; }
        .node-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: white; flex-shrink: 0; }
        .level-1 .node-icon { background: linear-gradient(135deg, #3b82f6, #2563eb); }
        .level-2 .node-icon { background: linear-gradient(135deg, #34d399, #10b981); }
        .level-3 .node-icon { background: linear-gradient(135deg, #fbbf24, #f59e0b); }
        
        /* Gantt override */
        .gantt .bar-label { fill: #fff; font-weight: bold; font-size: 12px; }
    </style>
"""
if "grade-4-5" not in gerencial_content:
    gerencial_content = gerencial_content.replace('</style>', f'</style>\n{css_to_add}')


# --- 2. HTML Containers (Chapter I, II, III, IV) ---
html_cap1 = """
                        <div id="detalleFactoresCompleto" style="margin-top: 30px;">
                            <!-- Aquí se inyectarán todos los factores, encuestas, características, cuadros e IA -->
                        </div>
                        
                        <div id="texto_informe_dinamico" style="display:none;"></div>
"""
if "detalleFactoresCompleto" not in gerencial_content:
    gerencial_content = gerencial_content.replace('<!-- NEW CNA RESUMEN -->', f'<!-- NEW CNA RESUMEN -->\n{html_cap1}')

html_cap2_old = """                        <div id="texto_mefi_mefe" class="editable-content" contenteditable="true">
                            Cargando análisis MEFI/MEFE...
                        </div>
                        <h3 class="section-title">Fuerzas de Porter</h3>
                        <div id="texto_porter" class="editable-content" contenteditable="true">
                            Cargando fuerzas de Porter...
                        </div>
                        <h3 class="section-title">Gestión de Riesgos</h3>
                        <div id="texto_riesgos" class="editable-content" contenteditable="true">
                            Cargando matriz de riesgos...
                        </div>
                        <h3 class="section-title">Mapeo de Stakeholders</h3>
                        <div id="texto_stakeholders" class="editable-content" contenteditable="true">
                            Cargando stakeholders...
                        </div>
                        <h3 class="section-title">Matriz de Comunicación</h3>
                        <div id="texto_comunicacion" class="editable-content" contenteditable="true">
                            Cargando planes de comunicación...
                        </div>"""
html_cap2_new = """                        
                        <div id="b2b_matrices_container" style="display: flex; flex-direction: column; gap: 20px;">
                            <div id="texto_mefi_mefe">Cargando análisis MEFI/MEFE...</div>
                            <div id="texto_porter">Cargando fuerzas de Porter...</div>
                            <div id="texto_riesgos">Cargando matriz de riesgos...</div>
                            <div id="texto_stakeholders">Cargando stakeholders...</div>
                            <div id="texto_comunicacion">Cargando planes de comunicación...</div>
                        </div>
"""
gerencial_content = gerencial_content.replace(html_cap2_old, html_cap2_new)

html_cap3_old = """                        <div id="texto_planificacion" class="editable-content" contenteditable="true">
                            Cargando planificación...
                        </div>
                        <h3 class="section-title">Informe Financiero Básico</h3>
                        <div id="texto_financiero" class="editable-content" contenteditable="true">
                            Cargando financiero...
                        </div>"""
html_cap3_new = """                        
                        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
                            <h4 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px;">Árbol Estratégico</h4>
                            <div id="planningTree">Cargando árbol de planificación...</div>
                        </div>

                        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
                            <h4 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px;">Cronograma Global (Gantt)</h4>
                            <div style="overflow-x: auto; padding-bottom: 20px;">
                                <svg id="ganttGlobal"></svg>
                            </div>
                        </div>

                        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px;">
                            <h4 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px;">Informe Financiero Básico</h4>
                            <div id="texto_financiero">Cargando financiero...</div>
                        </div>
"""
gerencial_content = gerencial_content.replace(html_cap3_old, html_cap3_new)


html_iso_old = """                        <div id="mapa_procesos">
                            <div class="iso-tier">
                                <h4>Procesos Estratégicos</h4>
                                <div class="iso-grid" id="iso_estrategicos">Cargando...</div>
                            </div>
                            <div class="iso-tier">
                                <h4>Procesos Misionales</h4>
                                <div class="iso-grid" id="iso_misionales">Cargando...</div>
                            </div>
                            <div class="iso-tier">
                                <h4>Procesos de Apoyo / Soporte</h4>
                                <div class="iso-grid" id="iso_apoyo">Cargando...</div>
                            </div>
                        </div>
                        <h3 class="section-title">Caracterización y SIPOC</h3>
                        <div id="texto_sipoc" class="editable-content" contenteditable="true">
                            Cargando caracterizaciones...
                        </div>"""

html_iso_new = """                        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
                            <h4 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px;">Mapa de Procesos</h4>
                            <div id="mapa_procesos" style="display: flex; flex-direction: column; gap: 20px;">
                                <div class="iso-tier" style="background:#f8fafc; padding:15px; border-radius:8px; border:1px solid #e2e8f0;">
                                    <h4 style="color:#7c3aed; text-align:center; font-weight:700;">PROCESOS ESTRATÉGICOS</h4>
                                    <div class="iso-grid" id="iso_estrategicos" style="justify-content:center;">Cargando...</div>
                                </div>
                                <div class="iso-tier" style="background:#eff6ff; padding:15px; border-radius:8px; border:1px solid #bfdbfe;">
                                    <h4 style="color:#2563eb; text-align:center; font-weight:700;">PROCESOS MISIONALES (Cadena de Valor)</h4>
                                    <div class="iso-grid" id="iso_misionales" style="justify-content:center;">Cargando...</div>
                                </div>
                                <div class="iso-tier" style="background:#f0fdf4; padding:15px; border-radius:8px; border:1px solid #bbf7d0;">
                                    <h4 style="color:#10b981; text-align:center; font-weight:700;">PROCESOS DE APOYO / SOPORTE</h4>
                                    <div class="iso-grid" id="iso_apoyo" style="justify-content:center;">Cargando...</div>
                                </div>
                            </div>
                        </div>

                        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
                            <h4 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px;">Caracterizaciones (Fichas de Procesos / SIPOC)</h4>
                            <div id="texto_sipoc">
                                Cargando caracterizaciones...
                            </div>
                        </div>"""
gerencial_content = gerencial_content.replace(html_iso_old, html_iso_new)


# --- 3. JS Replacements ---
# a) Helper functions
helpers_to_inject = """
        let _informeCharts = {};
        let _chartCounter = 0;

        function renderCuadrosProfesores(cuadros) {
            let dt = cuadros['factor4_profesores'] || cuadros['factor3_profesores'];
            if (!dt) return '';
            _chartCounter++;
            const canvasId = 'chart_prof_' + _chartCounter;
            const tableHtml = dt;
            const labels = [], dataVals = [], bgColors = [];
            
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = tableHtml;
            const rows = tempDiv.querySelectorAll('tbody tr');
            rows.forEach(tr => {
                const tds = tr.querySelectorAll('td');
                if (tds.length >= 2) {
                    labels.push(tds[0].innerText.trim());
                    dataVals.push(parseInt(tds[1].innerText.replace(/,/g, '')) || 0);
                    bgColors.push('#3b82f6');
                }
            });
            const config = {
                type: 'bar',
                data: { labels: labels, datasets: [{ label: 'Cantidad', data: dataVals, backgroundColor: bgColors }] },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
            };
            return `<div style="display:flex; flex-wrap:wrap; gap:20px; margin-top:15px; border-top:1px dashed #cbd5e1; padding-top:15px;">
                        <div style="flex:1; min-width:300px; font-size:0.85rem;">${tableHtml}</div>
                        <div style="flex:1; min-width:300px; height:250px;">
                            <canvas id="${canvasId}" data-config='${JSON.stringify(config).replace(/'/g, "&#39;")}'></canvas>
                        </div>
                    </div>`;
        }
        function renderCuadrosCurriculares(cuadros) { return renderCuadrosGeneric(cuadros['factor5_academicos']||cuadros['factor4_academicos'], 'aspectos académicos'); }
        function renderCuadrosExtension(cuadros) { return renderCuadrosGeneric(cuadros['factor7_extension']||cuadros['factor6_extension'], 'extensión e impacto'); }
        function renderCuadrosInvestigacion(cuadros) { return renderCuadrosGeneric(cuadros['factor8_investigacion']||cuadros['factor7_investigacion'], 'investigación'); }
        function renderCuadrosRecursos(cuadros) { return renderCuadrosGeneric(cuadros['factor10_recursos']||cuadros['factor9_recursos'], 'recursos e infraestructura'); }
        function renderCuadrosGeneric(dt, context) {
            if (!dt) return '';
            _chartCounter++;
            const canvasId = 'chart_gen_' + _chartCounter;
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = dt;
            const labels = [], dataVals = [], bgColors = [];
            const rows = tempDiv.querySelectorAll('tbody tr');
            rows.forEach((tr, i) => {
                const tds = tr.querySelectorAll('td');
                if (tds.length >= 2) {
                    labels.push(tds[0].innerText.trim());
                    dataVals.push(parseInt(tds[1].innerText.replace(/,/g, '')) || 0);
                    bgColors.push(i % 2 === 0 ? '#10b981' : '#f59e0b');
                }
            });
            const config = {
                type: 'bar',
                data: { labels: labels, datasets: [{ label: 'Total', data: dataVals, backgroundColor: bgColors }] },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
            };
            return `<div style="display:flex; flex-wrap:wrap; gap:20px; margin-top:15px; border-top:1px dashed #cbd5e1; padding-top:15px;">
                        <div style="flex:1; min-width:300px; font-size:0.85rem;">${dt}</div>
                        <div style="flex:1; min-width:300px; height:250px;">
                            <canvas id="${canvasId}" data-config='${JSON.stringify(config).replace(/'/g, "&#39;")}'></canvas>
                        </div>
                    </div>`;
        }
        function renderAIAnalysisPorFactor(cuadros, ...keys) {
            if(!cuadros) return '';
            for (const key of keys) {
                const txt = cuadros[`ai_analysis_${key}`];
                if (txt && txt.trim()) {
                    return `<div class="informe-ai-block" style="margin-top:15px; padding:15px; background:#f0f9ff; border:1px solid #bae6fd; border-radius:8px;">
                        <h5 style="color:#0369a1; margin-top:0;">🤖 Análisis de IA</h5>
                        <div style="font-size:0.9rem; color:#334155;">${marked.parse(txt)}</div>
                    </div>`;
                }
            }
            return '';
        }
        function renderAIAnalisisEstadisticas(cuadros) {
            const statsKeys = ['table_estudiantes','table_docentes','table_desercion','table_vinculacion_docente','table_investigacion','table_productividad','table_extension','table_infraestructura'];
            const labels = {'table_estudiantes': 'Población Estudiantil', 'table_docentes': 'Planta Docente', 'table_desercion': 'Deserción / Permanencia'};
            let html = '';
            statsKeys.forEach(k => {
                if (cuadros[`ai_analysis_${k}`]) {
                    html += `<div class="informe-ai-block" style="margin-bottom:14px; border-bottom:1px dashed #cbd5e1; padding-bottom:14px;">
                        <h5 style="color:#1e40af;">📌 Análsis IA: ${labels[k]||k}</h5>
                        <div class="ai-md-content" style="font-size:0.9rem;">${marked.parse(cuadros[`ai_analysis_${k}`])}</div>
                    </div>`;
                }
            });
            return html;
        }
        function escHtml(str) {
            if(!str) return '';
            return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
        }
        function renderTree(tree) {
            const container = document.getElementById('planningTree');
            if(!tree || tree.length === 0) {
                container.innerHTML = `<div style="text-align:center; padding:30px; color:#64748b;">No hay Planificación Estratégica definida.</div>`;
                return;
            }
            let html = '<div style="display:flex; flex-direction:column; gap:15px;">';
            tree.forEach(axis => {
                html += `
                <div style="border-left:5px solid #2563eb; background:white; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,0.1); overflow:hidden;">
                    <div style="padding:15px; background:#f8fafc; border-bottom:1px solid #e2e8f0;">
                        <span style="font-size:0.8rem; font-weight:bold; color:#2563eb; text-transform:uppercase;">Eje Estratégico</span>
                        <h4 style="margin:5px 0 0; color:#1e293b;">${escHtml(axis.name)}</h4>
                        ${axis.description ? `<p style="margin:10px 0 0; font-size:0.9rem; color:#64748b;">${escHtml(axis.description)}</p>` : ''}
                    </div>
                    <div style="padding:15px; display:flex; flex-direction:column; gap:15px;">
                `;
                
                if (axis.children && axis.children.length > 0) {
                    axis.children.forEach(obj => {
                        html += `
                        <div style="border-left:4px solid #10b981; padding-left:15px; margin-left:10px;">
                            <span style="font-size:0.75rem; font-weight:bold; color:#10b981; text-transform:uppercase;">Objetivo</span>
                            <h5 style="margin:3px 0; color:#0f172a;">${escHtml(obj.title)}</h5>
                            <div style="display:flex; flex-direction:column; gap:10px; margin-top:10px;">
                        `;
                        
                        if (obj.children && obj.children.length > 0) {
                            obj.children.forEach(strat => {
                                const statusColor = strat.status === 'Completed' ? '#10b981' : (strat.status === 'In Progress' ? '#3b82f6' : '#94a3b8');
                                html += `
                                <div style="border-left:3px solid #f59e0b; background:#fefce8; padding:10px 15px; border-radius:6px; margin-left:10px; display:flex; justify-content:space-between; align-items:center;">
                                    <div>
                                        <span style="font-size:0.7rem; font-weight:bold; color:#f59e0b; text-transform:uppercase;">Estrategia / Proyecto</span>
                                        <h6 style="margin:2px 0 5px; font-size:0.95rem; color:#334155;">${escHtml(strat.title)}</h6>
                                        <div style="font-size:0.8rem; color:#64748b;">Responsable: <b>${escHtml(strat.assigned_to_name||'Sin Asignar')}</b> | Fechas: ${escHtml(strat.start_date||'N/A')} al ${escHtml(strat.end_date||'N/A')}</div>
                                    </div>
                                    <span style="background:${statusColor}; color:white; padding:4px 8px; border-radius:12px; font-size:0.7rem; font-weight:bold;">${escHtml(strat.status)}</span>
                                </div>
                                `;
                            });
                        } else {
                            html += `<div style="font-size:0.85rem; color:#94a3b8; font-style:italic; margin-left:10px;">Sin estrategias definidas.</div>`;
                        }
                        html += `</div></div>`;
                    });
                } else {
                    html += `<div style="font-size:0.85rem; color:#94a3b8; font-style:italic;">Sin objetivos definidos.</div>`;
                }
                html += `</div></div>`;
            });
            html += `</div>`;
            container.innerHTML = html;
        }
"""
# Only replace the last </script>\n</body>.
gerencial_content = gerencial_content.replace('</script>\n</body>', f'{helpers_to_inject}\n</script>\n</body>')

# b) Autoevaluacion patch
carg_auto_patch = """
                    // --- INICIO RENDERING DETALLADO DE FACTORES ---
                    let todoElHtml = '';
                    if (data.factores && data.factores.length > 0) {
                        data.factores.forEach(f => {
                            let factorHtml = `
                                <div class="factor-section">
                                    <div class="factor-title">
                                        <span>Factor ${f.number}: ${f.name}</span>
                                        <span class="grade-badge ${getCNAClass(f.nota_promedio)}" style="font-size:1rem;">${f.nota_promedio.toFixed(1)} - ${f.cualitativo}</span>
                                    </div>
                                    <div style="background:#f8fafc; padding:15px; border-radius:8px; margin-bottom:20px; font-style:italic;">
                                        <b>Justificación Consolidada:</b> ${f.justificacion_general || 'No hay justificaciones cualitativas registradas.'}
                                    </div>
                            `;

                            let charsHtml = `<h4>Evaluación por Características y Percepción de la Comunidad:</h4>
                                             <div style="display:flex; flex-direction:column; gap:12px; margin-bottom:25px;">`;
                            f.caracteristicas.forEach(c => {
                                const cnaClass = getCNAClass(c.nota_promedio);
                                let percHtml = '';
                                if (c.percepcion_cantidad > 0) {
                                    const percClass = getCNAClass(c.percepcion_promedio);
                                    percHtml = `
                                        <div style="margin-top:8px; display:flex; align-items:center; gap:10px; font-size:0.8rem; color:#0369a1; background:#f0f9ff; padding:6px 12px; border-radius:6px; border:1px solid #bae6fd; flex-wrap:wrap;">
                                            <span> <b>Percepción Comunidad:</b> ${c.percepcion_promedio.toFixed(2)} / 5.0 (${c.percepcion_cantidad} respuestas)</span>
                                            <span class="grade-badge ${percClass}" style="padding:2px 8px; font-size:0.72rem;">${c.percepcion_promedio >= 4.5 ? 'Plenamente' : c.percepcion_promedio >= 4.0 ? 'Alto Grado' : c.percepcion_promedio >= 3.0 ? 'Aceptable' : 'No se cumple'}</span>
                                        </div>
                                    `;
                                    if (c.percepcion_comentarios && c.percepcion_comentarios.length > 0) {
                                        const topComments = c.percepcion_comentarios.slice(0, 2);
                                        percHtml += `<div style="font-size:0.78rem; color:#64748b; margin-top:5px; padding-left:12px; font-style:italic;">`;
                                        topComments.forEach(comm => { percHtml += `— "${comm.text}" (${comm.target})<br>`; });
                                        percHtml += `</div>`;
                                    }
                                } else {
                                    percHtml = `<div style="margin-top:8px; font-size:0.8rem; color:#64748b; background:#f8fafc; padding:6px 12px; border-radius:6px; border:1px solid #e2e8f0;">ℹ️ Sin datos de encuestas vinculadas a esta característica.</div>`;
                                }
                                charsHtml += `
                                    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:8px; padding:15px; box-shadow:0 1px 2px rgba(0,0,0,0.02);">
                                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                                            <span style="font-weight:600; font-size:0.92rem; color:#334155;">${c.number}. ${c.name}</span>
                                            <span class="grade-badge ${cnaClass}" style="font-size:0.75rem;">Autoevaluación: ${c.nota_promedio > 0 ? c.nota_promedio.toFixed(1) : 'Sin evaluar'}</span>
                                        </div>
                                        ${percHtml}
                                    </div>`;
                            });
                            charsHtml += `</div>`;
                            factorHtml += charsHtml;

                            if(typeof renderCuadrosProfesores === 'function' && data.cuadros) {
                                const c_name = String(f.name).toLowerCase();
                                if (f.number == 3 || f.number == 4 || c_name.includes('profesores') || c_name.includes('docentes')) {
                                    factorHtml += renderCuadrosProfesores(data.cuadros);
                                } else if (f.number == 5 || c_name.includes('académicos') || c_name.includes('academicos') || c_name.includes('curricular')) {
                                    factorHtml += renderCuadrosCurriculares(data.cuadros);
                                } else if (f.number == 7 || c_name.includes('entorno') || c_name.includes('extensi') || c_name.includes('sector externo')) {
                                    factorHtml += renderCuadrosExtension(data.cuadros);
                                } else if (f.number == 8 || c_name.includes('investigaci') || c_name.includes('innovaci')) {
                                    factorHtml += renderCuadrosInvestigacion(data.cuadros);
                                } else if (f.number == 10 || f.number == 9 || c_name.includes('recursos') || c_name.includes('ambientes') || c_name.includes('infraestructura') || c_name.includes('medios')) {
                                    factorHtml += renderCuadrosRecursos(data.cuadros);
                                } else {
                                    const anyAI = renderAIAnalysisPorFactor(data.cuadros, `table_estudiantes`, `table_desercion`);
                                    if (anyAI) factorHtml += anyAI;
                                }
                            }

                            let hasEvidences = false;
                            let evidencesHtml = `<h4>Evidencias Documentales Anexas:</h4><ul class="evidence-list">`;
                            f.caracteristicas.forEach(c => {
                                if(c.aspectos) {
                                    c.aspectos.forEach(a => {
                                        if (a.evidencias && a.evidencias.length > 0) {
                                            hasEvidences = true;
                                            a.evidencias.forEach(ev => {
                                                const periodBadge = ev.period ? `<span style="background:#e2e8f0; color:#475569; padding:2px 6px; border-radius:4px; font-size:0.75rem; margin-right:5px; font-weight:600;">[${ev.period}]</span>` : '';
                                                evidencesHtml += `<li><b>[A${a.number}]</b> ${periodBadge} 👁️ ${ev.name}</li>`;
                                            });
                                        }
                                    });
                                }
                            });
                            evidencesHtml += `</ul>`;
                            if (hasEvidences) factorHtml += evidencesHtml;
                            else factorHtml += `<p style="color:#64748b; font-size:0.9rem;">No hay evidencias documentales anexas para este factor.</p>`;

                            factorHtml += `</div>`;
                            todoElHtml += factorHtml;
                        });
                        
                        if (typeof renderAIAnalisisEstadisticas === 'function' && data.cuadros) {
                            const statsAIHtml = renderAIAnalisisEstadisticas(data.cuadros);
                            if (statsAIHtml || data.cuadros['ai_analysis_global']) {
                                let aiSectionHtml = `
                                    <div class="factor-section" style="margin-top:40px; border-radius:8px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);">
                                        <div class="factor-title" style="background:linear-gradient(135deg,#4338ca,#312e81); color:white; border-bottom:none; border-radius:8px 8px 0 0; padding:15px;">
                                            <span style="color:white;">* Análisis de IA — Cuadros de Datos Estadísticos</span>
                                        </div>
                                        <div style="padding:25px; background:white; border:1px solid #e2e8f0; border-radius:0 0 8px 8px;">
                                `;
                                if (data.cuadros['ai_analysis_global']) {
                                    aiSectionHtml += `<div class="informe-ai-block" style="margin-bottom:14px;"><h5>🌐 Análisis Integral Global</h5><div class="ai-md-content">${marked.parse(data.cuadros['ai_analysis_global'])}</div></div>`;
                                }
                                if (statsAIHtml) aiSectionHtml += statsAIHtml;
                                aiSectionHtml += `</div></div>`;
                                todoElHtml += aiSectionHtml;
                            }
                        }
                    }

                    document.getElementById('detalleFactoresCompleto').innerHTML = todoElHtml;
                    
                    setTimeout(() => {
                        Object.keys(_informeCharts).forEach(k => {
                            if (document.getElementById(k)) {
                                try {
                                    const configStr = document.getElementById(k).getAttribute('data-config');
                                    if(configStr) {
                                        const config = JSON.parse(configStr);
                                        _informeCharts[k] = new Chart(document.getElementById(k).getContext('2d'), config);
                                    }
                                } catch(e) {}
                            }
                        });
                    }, 500);

                    let html = `<h3>Análisis Cualitativo de Fortalezas y Debilidades</h3>${marked.parse(data.fortalezas || '')}`;
                    html += `<h3>Recomendaciones</h3>${marked.parse(data.recomendaciones || '')}`;
                    document.getElementById('texto_informe_dinamico').innerHTML = html;
                    document.getElementById('texto_informe_dinamico').style.display = 'block';
"""
gerencial_content = re.sub(
    r'let html = `<h3>Análisis Cualitativo de Fortalezas y Debilidades</h3>\$\{marked\.parse\(data\.fortalezas \|\| \'\'\)\}`;.*?document\.getElementById\(\'texto_informe_dinamico\'\)\.innerHTML = html;',
    carg_auto_patch,
    gerencial_content,
    flags=re.DOTALL
)

# c) B2B patch
carg_b2b_patch = """        async function cargarB2B() {
            try {
                const mefiRes = await fetch(`/api/business/matrix/MEFI?inst_id=${getInstId()}`);
                const mefeRes = await fetch(`/api/business/matrix/MEFE?inst_id=${getInstId()}`);
                let mefiData = await mefiRes.json();
                let mefeData = await mefeRes.json();
                
                let mmHtml = `
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:25px; margin-bottom:25px;">
                        <h4 style="color:#1e3a8a; border-bottom:2px solid #e2e8f0; padding-bottom:10px; margin-bottom:20px;">Análisis MEFI / MEFE</h4>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
                            <div>
                                <h5 style="color:#0f172a; margin-bottom:15px;">Matriz MEFI</h5>
                                <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                                    <tr style="background:#f1f5f9;"><th style="padding:8px;text-align:left;">Factor</th><th style="padding:8px;">Tipo</th><th style="padding:8px;">Peso</th></tr>
                `;
                if(mefiData.data && mefiData.data.factors && mefiData.data.factors.length > 0) {
                    mefiData.data.factors.forEach(f => { 
                        mmHtml += `<tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:8px;">${f.factor}</td><td style="padding:8px;font-weight:bold;">${(f.type||'').toUpperCase()}</td><td style="padding:8px;">${f.weight}</td></tr>`; 
                    });
                } else { mmHtml += `<tr><td colspan="3" style="padding:8px;">No hay factores internos.</td></tr>`; }
                
                mmHtml += `</table></div><div>
                                <h5 style="color:#0f172a; margin-bottom:15px;">Matriz MEFE</h5>
                                <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                                    <tr style="background:#f1f5f9;"><th style="padding:8px;text-align:left;">Factor</th><th style="padding:8px;">Tipo</th><th style="padding:8px;">Peso</th></tr>
                `;
                if(mefeData.data && mefeData.data.factors && mefeData.data.factors.length > 0) {
                    mefeData.data.factors.forEach(f => { 
                        mmHtml += `<tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:8px;">${f.factor}</td><td style="padding:8px;font-weight:bold;">${(f.type||'').toUpperCase()}</td><td style="padding:8px;">${f.weight}</td></tr>`; 
                    });
                } else { mmHtml += `<tr><td colspan="3" style="padding:8px;">No hay factores externos.</td></tr>`; }
                
                mmHtml += `</table></div></div></div>`;
                document.getElementById('texto_mefi_mefe').innerHTML = mmHtml;

                const porterRes = await fetch(`/api/business/matrix/PORTER?inst_id=${getInstId()}`);
                let porterData = await porterRes.json();
                let pHtml = `
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:25px; margin-bottom:25px;">
                        <h4 style="color:#1e3a8a; border-bottom:2px solid #e2e8f0; padding-bottom:10px; margin-bottom:20px;">5 Fuerzas de Porter</h4>
                        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                            <tr style="background:#f1f5f9;"><th style="padding:8px;text-align:left;">Fuerza</th><th style="padding:8px;text-align:left;">Descripción</th><th style="padding:8px;">Impacto</th></tr>
                `;
                if(porterData.data && porterData.data.factors && porterData.data.factors.length > 0) {
                    porterData.data.factors.forEach(f => { 
                        pHtml += `<tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:8px; font-weight:600;">${(f.type||'').toUpperCase()}</td><td style="padding:8px;">${f.factor}</td><td style="padding:8px;">${f.level||'N/A'}</td></tr>`; 
                    });
                } else { pHtml += `<tr><td colspan="3" style="padding:8px;">No hay fuerzas registradas.</td></tr>`; }
                pHtml += `</table></div>`;
                document.getElementById('texto_porter').innerHTML = pHtml;

                const riesgosRes = await fetch(`/api/business/matrix/RIESGOS?inst_id=${getInstId()}`);
                let riesgosData = await riesgosRes.json();
                let rHtml = `
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:25px; margin-bottom:25px;">
                        <h4 style="color:#1e3a8a; border-bottom:2px solid #e2e8f0; padding-bottom:10px; margin-bottom:20px;">Gestión de Riesgos</h4>
                        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                            <tr style="background:#f1f5f9;"><th style="padding:8px;text-align:left;">Riesgo</th><th style="padding:8px;">Probabilidad</th><th style="padding:8px;">Impacto</th><th style="padding:8px;text-align:left;">Mitigación</th></tr>
                `;
                if(riesgosData.data && riesgosData.data.factors && riesgosData.data.factors.length > 0) {
                    riesgosData.data.factors.forEach(f => { 
                        rHtml += `<tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:8px;">${f.factor}</td><td style="padding:8px;">${f.prob||'N/A'}</td><td style="padding:8px;">${f.impact||'N/A'}</td><td style="padding:8px;">${f.mitigation||'No definida'}</td></tr>`; 
                    });
                } else { rHtml += `<tr><td colspan="4" style="padding:8px;">No hay riesgos.</td></tr>`; }
                rHtml += `</table></div>`;
                document.getElementById('texto_riesgos').innerHTML = rHtml;

                const stRes = await fetch(`/api/business/matrix/STAKEHOLDERS?inst_id=${getInstId()}`);
                let stData = await stRes.json();
                let sHtml = `
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:25px; margin-bottom:25px;">
                        <h4 style="color:#1e3a8a; border-bottom:2px solid #e2e8f0; padding-bottom:10px; margin-bottom:20px;">Mapeo de Stakeholders</h4>
                        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                            <tr style="background:#f1f5f9;"><th style="padding:8px;text-align:left;">Stakeholder</th><th style="padding:8px;">Interés</th><th style="padding:8px;">Poder</th><th style="padding:8px;text-align:left;">Estrategia</th></tr>
                `;
                if(stData.data && stData.data.factors && stData.data.factors.length > 0) {
                    stData.data.factors.forEach(f => { 
                        sHtml += `<tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:8px;">${f.factor}</td><td style="padding:8px;">${f.interest||'N/A'}</td><td style="padding:8px;">${f.power||'N/A'}</td><td style="padding:8px;">${f.strategy||''}</td></tr>`; 
                    });
                } else { sHtml += `<tr><td colspan="4" style="padding:8px;">No hay stakeholders.</td></tr>`; }
                sHtml += `</table></div>`;
                document.getElementById('texto_stakeholders').innerHTML = sHtml;

                const comRes = await fetch(`/api/business/matrix/COMUNICACION?inst_id=${getInstId()}`);
                let comData = await comRes.json();
                let cHtml = `
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:25px; margin-bottom:25px;">
                        <h4 style="color:#1e3a8a; border-bottom:2px solid #e2e8f0; padding-bottom:10px; margin-bottom:20px;">Matriz de Comunicación</h4>
                        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                            <tr style="background:#f1f5f9;"><th style="padding:8px;text-align:left;">Asunto</th><th style="padding:8px;text-align:left;">Audiencia</th><th style="padding:8px;text-align:left;">Canal</th><th style="padding:8px;text-align:left;">Frecuencia</th></tr>
                `;
                if(comData.data && comData.data.factors && comData.data.factors.length > 0) {
                    comData.data.factors.forEach(f => { 
                        cHtml += `<tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:8px;">${f.factor}</td><td style="padding:8px;">${f.audience||''}</td><td style="padding:8px;">${f.channel||''}</td><td style="padding:8px;">${f.frequency||''}</td></tr>`; 
                    });
                } else { cHtml += `<tr><td colspan="4" style="padding:8px;">No hay comunicación.</td></tr>`; }
                cHtml += `</table></div>`;
                document.getElementById('texto_comunicacion').innerHTML = cHtml;

            } catch(e) { console.error("Error B2B", e); }
        }"""
gerencial_content = re.sub(
    r'async function cargarB2B\(\) \{.*?\}(?=\s*async function cargarISO)',
    carg_b2b_patch,
    gerencial_content,
    flags=re.DOTALL
)

# d) ISO patch
carg_iso_patch = """        async function cargarISO() {
            try {
                const res = await fetch(`/api/business/matrix/ISO9001?inst_id=${getInstId()}`);
                const data = await res.json();
                let estHtml = "", misHtml = "", apoHtml = "", sipocHtml = "";
                let hasIso = false;
                const buildSipoc = (p, tipo) => {
                    if (!p.sipoc || Object.keys(p.sipoc).length === 0) return `<div style="margin-bottom:15px; padding:15px; border:1px solid #e2e8f0; border-radius:8px;"><h5>${p.nombre} (${tipo})</h5><p style="color:#64748b;">No hay caracterización definida para este proceso.</p></div>`;
                    const s = p.sipoc;
                    return `
                    <div style="margin-bottom:25px; border:1px solid #cbd5e1; border-radius:8px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                        <div style="background:#1e293b; color:white; padding:12px 15px; display:flex; justify-content:space-between; align-items:center;">
                            <h5 style="margin:0; font-size:1.1rem; color:white;">${p.nombre}</h5>
                            <span style="background:#3b82f6; color:white; padding:2px 8px; border-radius:12px; font-size:0.75rem;">${tipo}</span>
                        </div>
                        <div style="padding:15px; background:white;">
                            <div style="margin-bottom:15px;"><b>Objetivo:</b> ${s.objetivo || 'N/A'}</div>
                            <table style="width:100%; border-collapse:collapse; margin-top:15px; font-size:0.85rem;">
                                <thead><tr style="background:#f1f5f9;"><th style="border:1px solid #e2e8f0; padding:8px;">Proveedores</th><th style="border:1px solid #e2e8f0; padding:8px;">Entradas</th><th style="border:1px solid #e2e8f0; padding:8px;">Actividades</th><th style="border:1px solid #e2e8f0; padding:8px;">Salidas</th><th style="border:1px solid #e2e8f0; padding:8px;">Clientes</th></tr></thead>
                                <tbody><tr>
                                        <td style="border:1px solid #e2e8f0; padding:8px; vertical-align:top;">${s.proveedores ? s.proveedores.replace(/\\n/g, '<br>') : ''}</td>
                                        <td style="border:1px solid #e2e8f0; padding:8px; vertical-align:top;">${s.entradas ? s.entradas.replace(/\\n/g, '<br>') : ''}</td>
                                        <td style="border:1px solid #e2e8f0; padding:8px; vertical-align:top;">${s.actividades ? s.actividades.replace(/\\n/g, '<br>') : ''}</td>
                                        <td style="border:1px solid #e2e8f0; padding:8px; vertical-align:top;">${s.salidas ? s.salidas.replace(/\\n/g, '<br>') : ''}</td>
                                        <td style="border:1px solid #e2e8f0; padding:8px; vertical-align:top;">${s.clientes ? s.clientes.replace(/\\n/g, '<br>') : ''}</td>
                                </tr></tbody>
                            </table>
                        </div>
                    </div>
                    `;
                };

                if(data.data && data.data.procesos) {
                    const proc = data.data.procesos;
                    if (proc.estrategicos && proc.estrategicos.length > 0) {
                        hasIso = true;
                        proc.estrategicos.forEach(p => { 
                            estHtml += `<div class="iso-card card-strat">${p.nombre}</div>`; 
                            sipocHtml += buildSipoc(p, 'Estratégico');
                        });
                    }
                    if (proc.misionales && proc.misionales.length > 0) {
                        hasIso = true;
                        proc.misionales.forEach(p => { 
                            misHtml += `<div class="iso-card card-misional">${p.nombre}</div>`; 
                            sipocHtml += buildSipoc(p, 'Misional');
                        });
                    }
                    if (proc.apoyo && proc.apoyo.length > 0) {
                        hasIso = true;
                        proc.apoyo.forEach(p => { 
                            apoHtml += `<div class="iso-card card-apoyo">${p.nombre}</div>`; 
                            sipocHtml += buildSipoc(p, 'Apoyo');
                        });
                    }
                }
                if (hasIso) {
                    document.getElementById('iso_estrategicos').innerHTML = estHtml || '<span style="color:#94a3b8;">Ninguno</span>';
                    document.getElementById('iso_misionales').innerHTML = misHtml || '<span style="color:#94a3b8;">Ninguno</span>';
                    document.getElementById('iso_apoyo').innerHTML = apoHtml || '<span style="color:#94a3b8;">Ninguno</span>';
                    document.getElementById('texto_sipoc').innerHTML = sipocHtml;
                }
            } catch(e) { console.error("Error ISO", e); }
        }"""
gerencial_content = re.sub(
    r'async function cargarISO\(\) \{.*?\}(?=\s*window\.onload)',
    carg_iso_patch,
    gerencial_content,
    flags=re.DOTALL
)

# e) Planificacion patch
carg_plan_patch = """        async function cargarPlanificacion() {
            try {
                const treeRes = await fetch(`/api/planning/tree?inst_id=${getInstId()}`);
                const treeData = await treeRes.json();
                if (treeData && !treeData.error && typeof renderTree === 'function') {
                    renderTree(treeData.tree);
                    let ganttTasks = [];
                    (treeData.tree || []).forEach(eje => {
                        (eje.children || []).forEach(obj => {
                            (obj.children || []).forEach(strat => {
                                if(strat.start_date && strat.end_date) {
                                    let progress = 0;
                                    if(strat.status === 'Completed') progress = 100;
                                    else if(strat.status === 'In Progress') progress = 50;
                                    ganttTasks.push({
                                        id: strat.id,
                                        name: strat.title,
                                        start: strat.start_date,
                                        end: strat.end_date,
                                        progress: progress,
                                        custom_class: strat.status === 'Completed' ? 'bar-success' : 'bar-primary'
                                    });
                                }
                            });
                        });
                    });
                    if (ganttTasks.length > 0) {
                        new Gantt("#ganttGlobal", ganttTasks, {
                            header_height: 50, column_width: 30, step: 24, view_modes: ['Quarter Day', 'Half Day', 'Day', 'Week', 'Month'], bar_height: 20, bar_corner_radius: 3, arrow_curve: 5, padding: 18, view_mode: 'Month', language: 'es'
                        });
                    } else {
                        document.getElementById('ganttGlobal').parentElement.innerHTML = "<p style='color:#64748b;'>No hay estrategias con fechas.</p>";
                    }
                }
                const finRes = await fetch(`/api/b2b/financiero?inst_id=${getInstId()}`);
                const finData = await finRes.json();
                if(finData && finData.informe) {
                    document.getElementById('texto_financiero').innerHTML = marked.parse(finData.informe);
                }
            } catch(e) { console.error("Error Planificacion", e); }
        }"""
gerencial_content = re.sub(
    r'async function cargarPlanificacion\(\) \{.*?\}(?=\s*async function cargarB2B)',
    carg_plan_patch,
    gerencial_content,
    flags=re.DOTALL
)

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'w', encoding='utf-8') as f:
    f.write(gerencial_content)

print("Rebuild complete!")
