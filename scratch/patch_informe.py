import re

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add getCNAClass and update cargarAutoevaluacion
new_script = """        function getCNAClass(avg) {
            if (avg >= 4.5) return 'grade-4-5';
            if (avg >= 4.0) return 'grade-4-0';
            if (avg >= 3.0) return 'grade-3-0';
            if (avg > 0) return 'grade-low';
            return '';
        }

        async function cargarAutoevaluacion() {
            try {
                const res = await fetch(`/api/informe_dinamico?inst_id=${getInstId()}&program_id=${getProgramId()}`);
                const data = await res.json();
                
                if(data && !data.error && data.factores) {
                    // Populate Resumen Table and Radar
                    const tbody = document.querySelector('#tablaResumenCNA tbody');
                    if (tbody) tbody.innerHTML = '';
                    const radarLabels = [];
                    const radarData = [];
                    
                    if (tbody) {
                        data.factores.forEach(f => {
                            const tr = document.createElement('tr');
                            tr.style.borderBottom = '1px solid #e2e8f0';
                            
                            let qualColor = '#94a3b8';
                            if(f.nota_promedio >= 4.5) qualColor = '#10b981';
                            else if(f.nota_promedio >= 4.0) qualColor = '#3b82f6';
                            else if(f.nota_promedio >= 3.0) qualColor = '#f59e0b';
                            else if(f.nota_promedio > 0) qualColor = '#ef4444';

                            tr.innerHTML = `
                                <td style="padding: 12px 10px;">Factor ${f.number}: ${f.name}</td>
                                <td style="padding: 12px 10px;"><b>${f.nota_promedio.toFixed(1)}</b> / 5.0</td>
                                <td style="padding: 12px 10px;"><span style="background:${qualColor}20; color:${qualColor}; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:0.8rem;">${f.cualitativo}</span></td>
                            `;
                            tbody.appendChild(tr);

                            radarLabels.push(`F${f.number}`);
                            radarData.push(f.nota_promedio);
                        });

                        // Draw Radar Chart
                        if (window.myRadarCNA) window.myRadarCNA.destroy();
                        const canvas = document.getElementById('radarChartCNA');
                        if (canvas) {
                            const ctx = canvas.getContext('2d');
                            window.myRadarCNA = new Chart(ctx, {
                                type: 'radar',
                                data: {
                                    labels: radarLabels,
                                    datasets: [{
                                        label: 'Calificación Obtenida',
                                        data: radarData,
                                        backgroundColor: 'rgba(37, 99, 235, 0.2)',
                                        borderColor: 'rgba(37, 99, 235, 1)',
                                        pointBackgroundColor: 'rgba(37, 99, 235, 1)'
                                    }, {
                                        label: 'Meta Ideal',
                                        data: Array(radarLabels.length).fill(4.5),
                                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                        borderColor: 'rgba(16, 185, 129, 0.5)',
                                        borderDash: [5, 5]
                                    }]
                                },
                                options: { scales: { r: { min: 0, max: 5 } }, responsive: true, maintainAspectRatio: false }
                            });
                        }
                    }

                    let html = `<h3>Análisis Cualitativo de Fortalezas y Debilidades</h3>${marked.parse(data.fortalezas || '')}`;
                    html += `<h3>Recomendaciones</h3>${marked.parse(data.recomendaciones || '')}`;
                    document.getElementById('texto_informe_dinamico').innerHTML = html;
                } else {
                    document.getElementById('texto_informe_dinamico').innerHTML = "No hay reporte dinámico generado aún para esta institución.";
                }
            } catch(e) { document.getElementById('texto_informe_dinamico').innerHTML = "Error cargando reporte."; console.error(e); }
        }"""
content = re.sub(r'async function cargarAutoevaluacion\(\) \{.*?\}(?=\s*async function cargarEstadisticas)', new_script, content, flags=re.DOTALL)


# 2. Add HTML structure
html_to_insert = """                        <h3 class="section-title">Informe Dinámico Generado</h3>
                        
                        <!-- NEW CNA RESUMEN -->
                        <div style="display: flex; flex-wrap: wrap; gap: 30px; margin-bottom: 30px; background: #fff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                            <div style="flex: 1; min-width: 350px;">
                                <h4 style="color: #1e3a8a; margin-bottom: 15px; font-size: 1.1rem;"><i class="fas fa-list"></i> Resumen Ejecutivo (Escala CNA)</h4>
                                <table id="tablaResumenCNA" style="width:100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">
                                    <thead>
                                        <tr style="border-bottom: 2px solid #cbd5e1; color: #475569;">
                                            <th style="padding: 10px;">Factor</th>
                                            <th style="padding: 10px;">Calificación</th>
                                            <th style="padding: 10px;">Evaluación CNA</th>
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                            <div style="flex: 1; min-width: 300px; display: flex; flex-direction: column; align-items: center;">
                                <h4 style="color: #1e3a8a; margin-bottom: 15px; font-size: 1.1rem;"><i class="fas fa-spider"></i> Desempeño Global</h4>
                                <div style="width: 100%; max-width: 350px; height: 350px;">
                                    <canvas id="radarChartCNA"></canvas>
                                </div>
                            </div>
                        </div>"""
content = re.sub(r'<h3 class="section-title">Informe Dinámico Generado</h3>', html_to_insert, content, count=1)

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied successfully.")
