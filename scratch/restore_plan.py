import re

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'r', encoding='utf-8') as f:
    content = f.read()

plan_func = """
        async function cargarPlanificacion() {
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
        }
"""

content = re.sub(r'(async function cargarISO\(\) \{)', plan_func + r'\1', content)

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Restored")
