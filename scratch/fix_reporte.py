import re

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix cargarAutoevaluacion
new_autoevaluacion = """        async function cargarAutoevaluacion() {
            try {
                const res = await fetch(`/api/informe_dinamico?inst_id=${getInstId()}&program_id=${getProgramId()}`);
                const data = await res.json();
                if(data && !data.error && data.factores) {
                    let html = `<h3>Análisis Fortalezas y Debilidades</h3>${marked.parse(data.fortalezas || '')}`;
                    html += `<h3>Recomendaciones</h3>${marked.parse(data.recomendaciones || '')}`;
                    document.getElementById('texto_informe_dinamico').innerHTML = html;
                } else {
                    document.getElementById('texto_informe_dinamico').innerHTML = "No hay reporte dinámico generado aún para esta institución.";
                }
            } catch(e) { document.getElementById('texto_informe_dinamico').innerHTML = "Error cargando reporte."; }
        }"""
content = re.sub(r'async function cargarAutoevaluacion\(\) \{.*?\}(?=\s*async function cargarEstadisticas)', new_autoevaluacion, content, flags=re.DOTALL)

# Fix cargarEstadisticas
new_estadisticas = """        async function cargarEstadisticas() {
            try {
                const res = await fetch(`/api/estadisticas?inst_id=${getInstId()}&program_id=${getProgramId()}`);
                const data = await res.json();
                if(data && !data.error) {
                    if(data.table_estudiantes && data.table_estudiantes.length > 0) { renderChartEstudiantes(data.table_estudiantes); } else { document.getElementById('chartEstudiantes').parentElement.innerHTML = "No hay datos de estudiantes"; }
                    if(data.table_docentes && data.table_docentes.length > 0) { renderChartDocentes(data.table_docentes); } else { document.getElementById('chartDocentes').parentElement.innerHTML = "No hay datos de docentes"; }
                    if(data.table_desercion && data.table_desercion.length > 0) { renderChartDesercion(data.table_desercion); } else { document.getElementById('chartDesercion').parentElement.innerHTML = "No hay datos de deserción"; }
                    if(data.table_productividad && data.table_productividad.length > 0) { renderChartProductividad(data.table_productividad); } else { document.getElementById('chartProductividad').parentElement.innerHTML = "No hay datos de productividad"; }
                    if(data.table_investigacion && data.table_investigacion.length > 0) { renderChartInvestigacion(data.table_investigacion); } else { document.getElementById('chartInvestigacion').parentElement.innerHTML = "No hay datos de investigación"; }
                }
            } catch(e) { console.error(e); }
        }"""
content = re.sub(r'async function cargarEstadisticas\(\) \{.*?\}(?=\s*async function cargarEvidencias)', new_estadisticas, content, flags=re.DOTALL)

# Fix cargarB2B
new_b2b = """        async function cargarB2B() {
            try {
                const mefiRes = await fetch(`/api/business/matrix/MEFI?inst_id=${getInstId()}`);
                const mefeRes = await fetch(`/api/business/matrix/MEFE?inst_id=${getInstId()}`);
                let mefiData = await mefiRes.json();
                let mefeData = await mefeRes.json();
                
                let mmHtml = "<h4>Análisis Interno (MEFI)</h4><ul>";
                let hasMefi = false;
                if(mefiData.data && mefiData.data.factors && mefiData.data.factors.length > 0) {
                    hasMefi = true;
                    mefiData.data.factors.forEach(f => { mmHtml += `<li><b>${(f.type||'').toUpperCase()}:</b> ${f.factor} (Peso: ${f.weight})</li>`; });
                } else { mmHtml += "<li>No hay factores internos definidos.</li>"; }
                mmHtml += "</ul><h4>Análisis Externo (MEFE)</h4><ul>";
                let hasMefe = false;
                if(mefeData.data && mefeData.data.factors && mefeData.data.factors.length > 0) {
                    hasMefe = true;
                    mefeData.data.factors.forEach(f => { mmHtml += `<li><b>${(f.type||'').toUpperCase()}:</b> ${f.factor} (Peso: ${f.weight})</li>`; });
                } else { mmHtml += "<li>No hay factores externos definidos.</li>"; }
                mmHtml += "</ul>";
                document.getElementById('texto_mefi_mefe').innerHTML = (hasMefi || hasMefe) ? mmHtml : "No hay matrices MEFI/MEFE guardadas.";

                const porterRes = await fetch(`/api/business/matrix/PORTER?inst_id=${getInstId()}`);
                let porterData = await porterRes.json();
                let pHtml = "<ul>";
                if(porterData.data && porterData.data.factors && porterData.data.factors.length > 0) {
                    porterData.data.factors.forEach(f => { pHtml += `<li><b>${f.force}:</b> ${f.factor} (Impacto: ${f.impact})</li>`; });
                    pHtml += "</ul>";
                    document.getElementById('texto_porter').innerHTML = pHtml;
                } else { document.getElementById('texto_porter').innerHTML = "No hay datos de Porter."; }

                const riesgosRes = await fetch(`/api/business/matrix/RIESGOS?inst_id=${getInstId()}`);
                let riesgosData = await riesgosRes.json();
                if(riesgosData.data && riesgosData.data.risks && riesgosData.data.risks.length > 0) {
                    let rHtml = "<ul>";
                    riesgosData.data.risks.forEach(r => { rHtml += `<li><b>${r.risk}:</b> Prob ${r.probability} x Imp ${r.impact} = Nivel ${r.level}</li>`; });
                    rHtml += "</ul>";
                    document.getElementById('texto_riesgos').innerHTML = rHtml;
                } else { document.getElementById('texto_riesgos').innerHTML = "No hay datos de Riesgos."; }

                const shRes = await fetch(`/api/business/matrix/STAKEHOLDERS?inst_id=${getInstId()}`);
                let shData = await shRes.json();
                if(shData.data && shData.data.stakeholders && shData.data.stakeholders.length > 0) {
                    let sHtml = "<ul>";
                    shData.data.stakeholders.forEach(s => { sHtml += `<li><b>${s.name}:</b> Int ${s.interest} x Pod ${s.power} - ${s.strategy}</li>`; });
                    sHtml += "</ul>";
                    document.getElementById('texto_stakeholders').innerHTML = sHtml;
                } else { document.getElementById('texto_stakeholders').innerHTML = "No hay datos de Stakeholders."; }
                
                const comRes = await fetch(`/api/business/matrix/COMUNICACION?inst_id=${getInstId()}`);
                let comData = await comRes.json();
                if(comData.data && comData.data.plans && comData.data.plans.length > 0) {
                    let cHtml = "<ul>";
                    comData.data.plans.forEach(c => { cHtml += `<li><b>${c.audience}:</b> ${c.message} (${c.channel})</li>`; });
                    cHtml += "</ul>";
                    document.getElementById('texto_comunicacion').innerHTML = cHtml;
                } else { document.getElementById('texto_comunicacion').innerHTML = "No hay datos de Comunicación."; }
                
            } catch(e) { console.error(e); }
        }"""
content = re.sub(r'async function cargarB2B\(\) \{.*?\}(?=\s*async function cargarPlanificacion)', new_b2b, content, flags=re.DOTALL)

# Fix cargarPlanificacion
new_plan = """        async function cargarPlanificacion() {
            try {
                const res = await fetch(`/api/planning/tree?inst_id=${getInstId()}&program_id=${getProgramId()}`);
                const data = await res.json();
                if(data && data.status === 'success' && data.tree && data.tree.length > 0) {
                    let html = "";
                    data.tree.forEach(eje => {
                        html += `<h4>Eje Estratégico: ${eje.name}</h4><ul>`;
                        if(eje.children) {
                            eje.children.forEach(strat => {
                                html += `<li><b>Estrategia:</b> ${strat.name}`;
                                if(strat.children) {
                                    html += "<ul>";
                                    strat.children.forEach(gen => { html += `<li><b>Obj. General:</b> ${gen.name}</li>`; });
                                    html += "</ul>";
                                }
                                html += `</li>`;
                            });
                        }
                        html += "</ul>";
                    });
                    document.getElementById('texto_planificacion').innerHTML = html;
                } else {
                    document.getElementById('texto_planificacion').innerHTML = "No hay estructura de planificación definida.";
                }

                const finRes = await fetch(`/api/planning/reports/finance?inst_id=${getInstId()}&program_id=${getProgramId()}`);
                const finData = await finRes.json();
                if(finData && finData.status === 'success' && finData.report && finData.report.length > 0) {
                    document.getElementById('texto_financiero').innerHTML = `<p><b>Presupuesto Total Estimado:</b> $${finData.total_projected || 0}</p>
                    <p>Se cuenta con ${finData.report.length} ejes presupuestados.</p>`;
                } else {
                    document.getElementById('texto_financiero').innerHTML = "No hay reporte financiero generado.";
                }
            } catch(e) { console.error(e); }
        }"""
content = re.sub(r'async function cargarPlanificacion\(\) \{.*?\}(?=\s*async function cargarISO)', new_plan, content, flags=re.DOTALL)

# Fix cargarISO
new_iso = """        async function cargarISO() {
            try {
                const res = await fetch(`/api/business/matrix/ISO9001?inst_id=${getInstId()}`);
                const resData = await res.json();
                let data = resData.data || {};
                if (typeof data === 'string') { try { data = JSON.parse(data); } catch(e){} }

                if(data && data.processes) {
                    let html = `<p><b>Política de Calidad:</b> ${data.policy || 'No definida'}</p>`;
                    html += `<ul>`;
                    for(let pName in data.processes) {
                        html += `<li><b>${pName}</b></li>`;
                    }
                    html += "</ul>";
                    document.getElementById('texto_iso').innerHTML = html;
                } else {
                    document.getElementById('texto_iso').innerHTML = "No hay alineación ISO 9001 configurada.";
                }
            } catch(e) { document.getElementById('texto_iso').innerHTML = "Error cargando ISO."; }
        }"""
content = re.sub(r'async function cargarISO\(\) \{.*?\}(?=\s*async function init)', new_iso, content, flags=re.DOTALL)

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
