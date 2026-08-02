import re
import os

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'r', encoding='utf-8') as f:
    gerencial_content = f.read()
    
with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    informes_content = f.read()

with open(r'c:\SIAC\templates\planificacion.html', 'r', encoding='utf-8') as f:
    planificacion_content = f.read()

# --- 1. Extract JS Helpers from informes.html ---
# We need renderCuadrosProfesores, renderCuadrosCurriculares, renderCuadrosExtension, renderCuadrosInvestigacion, renderCuadrosRecursos, renderAIAnalysisPorFactor, renderAIAnalisisEstadisticas
helpers_regex = r'(function renderCuadrosProfesores.*?// ============================================================)'
helpers_match = re.search(helpers_regex, informes_content, re.DOTALL)
informes_helpers = helpers_match.group(1) if helpers_match else ""

# --- 2. Extract Tree rendering from planificacion.html ---
tree_regex = r'(function escHtml.*?function renderTree.*?})'
tree_match = re.search(tree_regex, planificacion_content, re.DOTALL)
tree_helpers = tree_match.group(1) if tree_match else ""

# Append helpers to the end of the script block in empresa_informe_gerencial
helpers_to_inject = f"""
        let _informeCharts = {{}};
        let _chartCounter = 0;
        let nodeDataMap = {{}};

{informes_helpers}

{tree_helpers}
"""
gerencial_content = gerencial_content.replace('</script>\n</body>', f'{helpers_to_inject}\n</script>\n</body>')

# --- 3. Modify cargarAutoevaluacion() to populate detalleFactoresCompleto ---
# We'll replace the part that just does marked.parse(data.fortalezas) with the full iteration.
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

                            // Características y percepción
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

                            // Cuadros
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

                            // Evidencias
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
                        
                        // Estadisticas globales AI
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
                    
                    // Inicializar los mini-charts de los cuadros
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

                    // Fortalezas extra
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

# --- 4. Modify cargarPlanificacion() to draw the Gantt and Tree ---
carg_plan_patch = """
        async function cargarPlanificacion() {
            try {
                // 1. Fetch Planificación Tree
                const treeRes = await fetch(`/api/planning/tree?inst_id=${getInstId()}`);
                const treeData = await treeRes.json();
                
                if (treeData && !treeData.error && typeof renderTree === 'function') {
                    renderTree(treeData.tree);
                    
                    // 2. Extraer estrategias/proyectos para el Gantt
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
                        document.getElementById('ganttGlobal').parentElement.innerHTML = "<p style='color:#64748b; font-size:0.9rem;'>No hay estrategias con fechas de inicio y fin definidas para mostrar en el cronograma.</p>";
                    }
                } else {
                    document.getElementById('planningTree').innerHTML = "No se pudo cargar el árbol de planificación.";
                }

                // 3. Fetch Informe Financiero (ya existente)
                const finRes = await fetch(`/api/b2b/financiero?inst_id=${getInstId()}`);
                const finData = await finRes.json();
                if(finData && finData.informe) {
                    document.getElementById('texto_financiero').innerHTML = marked.parse(finData.informe);
                }
            } catch(e) {
                console.error("Error cargando planificación:", e);
                document.getElementById('planningTree').innerHTML = "Error cargando planificación.";
            }
        }
"""
gerencial_content = re.sub(
    r'async function cargarPlanificacion\(\) \{.*?\}(?=\s*async function cargarB2B)',
    carg_plan_patch,
    gerencial_content,
    flags=re.DOTALL
)

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'w', encoding='utf-8') as f:
    f.write(gerencial_content)

print("JS logic injected successfully.")
