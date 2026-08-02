import re

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'r', encoding='utf-8') as f:
    gerencial_content = f.read()

# 1. Clean up everything after `let _informeCharts = {};` (or where the injection started)
# Wait, let's find the `let _informeCharts = {};`
clean_regex = r'let _informeCharts = \{.*?;</script>'
if re.search(clean_regex, gerencial_content, re.DOTALL):
    gerencial_content = re.sub(clean_regex, '</script>', gerencial_content, flags=re.DOTALL)

# Let's see if we successfully removed the old broken injection.
# We also had `function renderCuadrosProfesores` injected before `let _informeCharts = {}`? No, the python script did:
# `f'{helpers_to_inject}\n</script>\n</body>'`
# So the injection is right before `</script>\n</body>`

# Let's just cleanly replace the broken block by finding `let _informeCharts = {};` to the end of the file.
gerencial_content = re.sub(r'let _informeCharts = \{\};.*?</script>', '</script>', gerencial_content, flags=re.DOTALL)

# 2. Re-inject proper Read-Only helpers
read_only_helpers = """
        let _informeCharts = {};
        let _chartCounter = 0;

        // --- Helpers from Informes ---
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

        // --- Read-Only Tree Renderer ---
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

gerencial_content = gerencial_content.replace('</script>', f'{read_only_helpers}\n</script>')

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'w', encoding='utf-8') as f:
    f.write(gerencial_content)

print("JS logic fixed and Read-Only tree renderer injected.")
