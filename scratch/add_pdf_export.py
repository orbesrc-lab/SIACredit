import os

file_path = r'c:\SIAC\templates\empresa_matrices.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add PDF Export Button
target_btns = r'''                        <button class="btn-primary" onclick="saveAllMatrices()">
                            💾 Guardar Matrices
                        </button>'''

replacement_btns = r'''                        <button class="btn-primary" onclick="saveAllMatrices()">
                            💾 Guardar Matrices
                        </button>
                        <button class="btn-primary" onclick="exportPDF()" style="background: linear-gradient(135deg, #059669, #10b981); border:none; margin-left: 8px;">
                            📄 Descargar Informe PDF
                        </button>'''

if "exportPDF()" not in content:
    content = content.replace(target_btns, replacement_btns)

# Add exportPDF function
export_pdf_code = """
        function exportPDF() {
            const logoImg = document.getElementById('inst_logo_img');
            const logoSrc = (logoImg && logoImg.style.display !== 'none' && logoImg.src) ? logoImg.src : '';
            const instNameDisplay = document.getElementById('inst_name_display');
            const instName = (instNameDisplay && instNameDisplay.innerText !== 'Cargando...') ? instNameDisplay.innerText : 'INSTITUCIÓN EDUCATIVA';
            const evalDate = document.getElementById('eval_date') ? document.getElementById('eval_date').value : 'No especificada';

            let mefiRowsHTML = (mefiData || []).map(f => `
                <tr>
                    <td style="padding:8px; border:1px solid #cbd5e1;">(${f.type === 'fortaleza' ? 'F' : 'D'}) ${f.factor}</td>
                    <td style="padding:8px; border:1px solid #cbd5e1; text-align:center;">${(parseFloat(f.weight) || 0).toFixed(2)}</td>
                    <td style="padding:8px; border:1px solid #cbd5e1; text-align:center;">${f.rating || 0}</td>
                    <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; font-weight:bold;">${((parseFloat(f.weight) || 0) * (parseFloat(f.rating) || 0)).toFixed(2)}</td>
                </tr>
            `).join('');

            let mefiTotalWeight = (mefiData || []).reduce((acc, curr) => acc + (parseFloat(curr.weight) || 0), 0).toFixed(2);
            let mefiTotalScore = (mefiData || []).reduce((acc, curr) => acc + ((parseFloat(curr.weight) || 0) * (parseFloat(curr.rating) || 0)), 0).toFixed(2);

            let mefeRowsHTML = (mefeData || []).map(f => `
                <tr>
                    <td style="padding:8px; border:1px solid #cbd5e1;">(${f.type === 'oportunidad' ? 'O' : 'A'}) ${f.factor}</td>
                    <td style="padding:8px; border:1px solid #cbd5e1; text-align:center;">${(parseFloat(f.weight) || 0).toFixed(2)}</td>
                    <td style="padding:8px; border:1px solid #cbd5e1; text-align:center;">${f.rating || 0}</td>
                    <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; font-weight:bold;">${((parseFloat(f.weight) || 0) * (parseFloat(f.rating) || 0)).toFixed(2)}</td>
                </tr>
            `).join('');

            let mefeTotalWeight = (mefeData || []).reduce((acc, curr) => acc + (parseFloat(curr.weight) || 0), 0).toFixed(2);
            let mefeTotalScore = (mefeData || []).reduce((acc, curr) => acc + ((parseFloat(curr.weight) || 0) * (parseFloat(curr.rating) || 0)), 0).toFixed(2);

            const printHTML = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Informe de Matrices Estratégicas - ${instName}</title>
                <style>
                    body { font-family: 'Segoe UI', Arial, sans-serif; color: #1e293b; padding: 30px; margin: 0; }
                    .header { display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #2563eb; padding-bottom: 15px; margin-bottom: 20px; }
                    .logo { max-height: 55px; max-width: 220px; object-fit: contain; }
                    .inst-name { font-size: 1.3rem; font-weight: bold; color: #1e3a8a; text-transform: uppercase; text-align: right; }
                    .report-title { text-align: center; font-size: 1.5rem; color: #0f172a; margin-top: 10px; margin-bottom: 5px; font-weight: bold; }
                    .meta-info { text-align: center; font-size: 0.95rem; color: #64748b; margin-bottom: 25px; }
                    h2 { color: #1e3a8a; font-size: 1.15rem; border-bottom: 1px solid #cbd5e1; padding-bottom: 5px; margin-top: 25px; }
                    table { width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 0.88rem; }
                    th { background-color: #f1f5f9; color: #334155; font-weight: bold; padding: 9px; border: 1px solid #cbd5e1; text-align: left; }
                    tfoot tr { background-color: #f8fafc; font-weight: bold; }
                    .summary-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-top: 20px; line-height: 1.5; }
                    @media print {
                        body { padding: 15px; }
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <div>
                        ${logoSrc ? `<img src="${logoSrc}" class="logo">` : '<div style="font-weight:bold; font-size:1.2rem; color:#2563eb;">SIAC STRATEGIC</div>'}
                    </div>
                    <div class="inst-name">${instName}</div>
                </div>

                <div class="report-title">INFORME DE MATRICES ESTRATÉGICAS (MEFI / MEFE)</div>
                <div class="meta-info">📅 Fecha de Levantamiento de Información: <strong>${evalDate || 'No especificada'}</strong></div>

                <h2>1. Matriz de Evaluación de Factores Internos (MEFI)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Factor Interno (Fortalezas / Debilidades)</th>
                            <th style="width:110px; text-align:center;">Peso (0.0-1.0)</th>
                            <th style="width:110px; text-align:center;">Calificación (1-4)</th>
                            <th style="width:120px; text-align:center;">Valor Ponderado</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${mefiRowsHTML || '<tr><td colspan="4" style="text-align:center;">Sin datos</td></tr>'}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td>Total MEFI</td>
                            <td style="text-align:center;">${mefiTotalWeight}</td>
                            <td></td>
                            <td style="text-align:center;">${mefiTotalScore}</td>
                        </tr>
                    </tfoot>
                </table>

                <h2>2. Matriz de Evaluación de Factores Externos (MEFE)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Factor Externo (Oportunidades / Amenazas)</th>
                            <th style="width:110px; text-align:center;">Peso (0.0-1.0)</th>
                            <th style="width:110px; text-align:center;">Calificación (1-4)</th>
                            <th style="width:120px; text-align:center;">Valor Ponderado</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${mefeRowsHTML || '<tr><td colspan="4" style="text-align:center;">Sin datos</td></tr>'}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td>Total MEFE</td>
                            <td style="text-align:center;">${mefeTotalWeight}</td>
                            <td></td>
                            <td style="text-align:center;">${mefeTotalScore}</td>
                        </tr>
                    </tfoot>
                </table>

                <div class="summary-box">
                    <h3 style="margin-top:0; color:#1e293b; font-size:1.05rem;">Resumen del Balance Estratégico</h3>
                    <p style="margin: 5px 0;"><strong>Puntuación Ponderada Interna (MEFI):</strong> ${mefiTotalScore} / 4.00 
                    <em>(${parseFloat(mefiTotalScore) >= 2.5 ? 'Posición interna fuerte - superior al promedio de 2.5' : 'Posición interna débil - inferior al promedio de 2.5'})</em></p>
                    <p style="margin: 5px 0;"><strong>Puntuación Ponderada Externa (MEFE):</strong> ${mefeTotalScore} / 4.00 
                    <em>(${parseFloat(mefeTotalScore) >= 2.5 ? 'Responde de manera eficaz a las presiones del entorno' : 'Respuesta débil a las presiones del entorno externo'})</em></p>
                </div>

                <script>
                    window.onload = function() {
                        setTimeout(() => {
                            window.print();
                        }, 500);
                    };
                <\/script>
            </body>
            </html>
            `;

            const win = window.open('', '_blank');
            if (win) {
                win.document.open();
                win.document.write(printHTML);
                win.document.close();
            } else {
                Swal.fire('Atención', 'Por favor permite las ventanas emergentes para generar el informe PDF.', 'warning');
            }
        }
"""

if "function exportPDF()" not in content:
    content += "\n" + export_pdf_code

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Added exportPDF button and function to empresa_matrices.html")
