import re

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_init = """        async function init() {
            Swal.fire({ 
                title: 'Consolidando Informe...', 
                html: '<div>Recopilando datos de todas las áreas</div><div style="margin-top:15px; height:20px; background:#e2e8f0; border-radius:10px; overflow:hidden;"><div id="load-progress" style="height:100%; width:0%; background:#3b82f6; transition:width 0.3s;"></div></div><div id="load-text" style="margin-top:10px; font-size:0.85rem; color:#64748b;">0 / 5 módulos</div>',
                allowOutsideClick: false, 
                showConfirmButton: false,
                didOpen: () => Swal.showLoading() 
            });
            
            try {
                let completed = 0;
                const total = 5;
                const updateProgress = (name) => {
                    completed++;
                    const p = Math.round((completed / total) * 100);
                    const bar = document.getElementById('load-progress');
                    const txt = document.getElementById('load-text');
                    if(bar) bar.style.width = p + '%';
                    if(txt) txt.innerHTML = `${completed} / ${total} módulos (${name})`;
                };

                const wrap = async (fn, name) => {
                    await fn();
                    updateProgress(name);
                };

                // Fetch data in parallel
                await Promise.all([
                    wrap(cargarAutoevaluacion, 'Autoevaluación'),
                    wrap(cargarEstadisticas, 'Estadísticas'),
                    wrap(cargarB2B, 'Consultoría B2B'),
                    wrap(cargarPlanificacion, 'Planificación'),
                    wrap(cargarISO, 'Procesos ISO')
                ]);

                // Intentar cargar la versión guardada y sobreescribir si existe
                await cargarInformeGuardado();

                Swal.close();
            } catch(e) {
                console.error(e);
                Swal.fire('Atención', 'Algunos módulos no tienen datos completos.', 'warning');
            }
        }"""

content = re.sub(r'async function init\(\) \{.*?\n        \}', new_init, content, flags=re.DOTALL)

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Progress bar added")
