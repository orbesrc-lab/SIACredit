import os

file_path = r'c:\SIAC\templates\empresa_matrices.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add #printSection and print CSS before </head>
print_css = """
    <style id="printStyle">
        @media print {
            body * { visibility: hidden !important; }
            #printSection, #printSection * { visibility: visible !important; }
            #printSection { position: absolute !important; left: 0 !important; top: 0 !important; width: 100% !important; display: block !important; background: white !important; padding: 20px !important; color: #0f172a !important; font-family: 'Segoe UI', Arial, sans-serif !important; }
            .no-print { display: none !important; }
        }
        #printSection { display: none; }
    </style>
</head>"""

if "id=\"printStyle\"" not in content:
    content = content.replace('</head>', print_css)

# 2. Add <div id="printSection"></div> before </body>
if '<div id="printSection"></div>' not in content:
    content = content.replace('</body>', '<div id="printSection"></div>\n</body>')

# 3. Replace exportPDF function with current window print logic
new_export_pdf = """
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

            const reportHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #2563eb; padding-bottom: 15px; margin-bottom: 20px;">
                    <div>
                        ${logoSrc ? `<img src="${logoSrc}" style="max-height: 55px; max-width: 220px; object-fit: contain;">` : '<div style="font-weight:bold; font-size:1.3rem; color:#2563eb;">SIAC STRATEGIC</div>'}
                    </div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #1e3a8a; text-transform: uppercase; text-align: right;">${instName}</div>
                </div>

                <div style="text-align: center; font-size: 1.5rem; color: #0f172a; margin-top: 10px; margin-bottom: 5px; font-weight: bold;">INFORME DE MATRICES ESTRATÉGICAS (MEFI / MEFE)</div>
                <div style="text-align: center; font-size: 0.95rem; color: #64748b; margin-bottom: 25px;">📅 Fecha de Levantamiento de Información: <strong>${evalDate || 'No especificada'}</strong></div>

                <h3 style="color: #1e3a8a; font-size: 1.15rem; border-bottom: 1px solid #cbd5e1; padding-bottom: 5px; margin-top: 25px;">1. Matriz de Evaluación de Factores Internos (MEFI)</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 0.88rem;">
                    <thead>
                        <tr style="background-color: #f1f5f9; color: #334155; font-weight: bold;">
                            <th style="padding:9px; border:1px solid #cbd5e1; text-align:left;">Factor Interno (Fortalezas / Debilidades)</th>
                            <th style="width:110px; padding:9px; border:1px solid #cbd5e1; text-align:center;">Peso (0.0-1.0)</th>
                            <th style="width:110px; padding:9px; border:1px solid #cbd5e1; text-align:center;">Calificación (1-4)</th>
                            <th style="width:120px; padding:9px; border:1px solid #cbd5e1; text-align:center;">Valor Ponderado</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${mefiRowsHTML || '<tr><td colspan="4" style="text-align:center;">Sin datos</td></tr>'}
                    </tbody>
                    <tfoot>
                        <tr style="background-color: #f8fafc; font-weight: bold;">
                            <td style="padding:9px; border:1px solid #cbd5e1;">Total MEFI</td>
                            <td style="padding:9px; border:1px solid #cbd5e1; text-align:center;">${mefiTotalWeight}</td>
                            <td style="padding:9px; border:1px solid #cbd5e1;"></td>
                            <td style="padding:9px; border:1px solid #cbd5e1; text-align:center;">${mefiTotalScore}</td>
                        </tr>
                    </tfoot>
                </table>

                <h3 style="color: #1e3a8a; font-size: 1.15rem; border-bottom: 1px solid #cbd5e1; padding-bottom: 5px; margin-top: 25px;">2. Matriz de Evaluación de Factores Externos (MEFE)</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 0.88rem;">
                    <thead>
                        <tr style="background-color: #f1f5f9; color: #334155; font-weight: bold;">
                            <th style="padding:9px; border:1px solid #cbd5e1; text-align:left;">Factor Externo (Oportunidades / Amenazas)</th>
                            <th style="width:110px; padding:9px; border:1px solid #cbd5e1; text-align:center;">Peso (0.0-1.0)</th>
                            <th style="width:110px; padding:9px; border:1px solid #cbd5e1; text-align:center;">Calificación (1-4)</th>
                            <th style="width:120px; padding:9px; border:1px solid #cbd5e1; text-align:center;">Valor Ponderado</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${mefeRowsHTML || '<tr><td colspan="4" style="text-align:center;">Sin datos</td></tr>'}
                    </tbody>
                    <tfoot>
                        <tr style="background-color: #f8fafc; font-weight: bold;">
                            <td style="padding:9px; border:1px solid #cbd5e1;">Total MEFE</td>
                            <td style="padding:9px; border:1px solid #cbd5e1; text-align:center;">${mefeTotalWeight}</td>
                            <td style="padding:9px; border:1px solid #cbd5e1;"></td>
                            <td style="padding:9px; border:1px solid #cbd5e1; text-align:center;">${mefeTotalScore}</td>
                        </tr>
                    </tfoot>
                </table>

                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-top: 20px; line-height: 1.5;">
                    <h4 style="margin-top:0; color:#1e293b; font-size:1.05rem;">Resumen del Balance Estratégico</h4>
                    <p style="margin: 5px 0;"><strong>Puntuación Ponderada Interna (MEFI):</strong> ${mefiTotalScore} / 4.00 
                    <em>(${parseFloat(mefiTotalScore) >= 2.5 ? 'Posición interna fuerte - superior al promedio de 2.5' : 'Posición interna débil - inferior al promedio de 2.5'})</em></p>
                    <p style="margin: 5px 0;"><strong>Puntuación Ponderada Externa (MEFE):</strong> ${mefeTotalScore} / 4.00 
                    <em>(${parseFloat(mefeTotalScore) >= 2.5 ? 'Responde de manera eficaz a las presiones del entorno' : 'Respuesta débil a las presiones del entorno externo'})</em></p>
                </div>
            `;

            const printSection = document.getElementById('printSection');
            printSection.innerHTML = reportHTML;
            window.print();
        }"""

if "function exportPDF()" in content:
    idx = content.find("function exportPDF()")
    end_idx = content.rfind("</script>")
    content = content[:idx] + new_export_pdf + "\n    " + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("empresa_matrices.html patched with native print section!")
