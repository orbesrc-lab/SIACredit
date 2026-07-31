import os
import re

file_path = r'c:\SIAC\templates\empresa_informe_gerencial.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Update the header
html = html.replace('<h1>Informe Gerencial de Evaluación Organizacional</h1>', 
                    '<h1>📑 Informe Gerencial Integral</h1>')

# Add sections for Porter, Riesgos, etc. before the AI conclusion
new_sections = """
                <!-- Integración Porter -->
                <div class="section-card">
                    <h2>📈 Análisis Competitivo (Porter)</h2>
                    <p style="font-size: 0.85rem; color:#64748b; margin-bottom:10px;">Presión competitiva e industria.</p>
                    <div id="porterSummary" class="ai-result-box">Cargando datos de Porter...</div>
                </div>

                <!-- Integración Riesgos -->
                <div class="section-card">
                    <h2>🛡️ Gestión de Riesgos</h2>
                    <p style="font-size: 0.85rem; color:#64748b; margin-bottom:10px;">Principales riesgos identificados y su criticidad.</p>
                    <div id="riesgosSummary" class="ai-result-box">Cargando datos de Riesgos...</div>
                </div>
                
                <!-- Integración Stakeholders -->
                <div class="section-card">
                    <h2>🤝 Mapeo de Stakeholders</h2>
                    <p style="font-size: 0.85rem; color:#64748b; margin-bottom:10px;">Grupos de interés clave.</p>
                    <div id="stakeholdersSummary" class="ai-result-box">Cargando datos de Stakeholders...</div>
                </div>
"""

# Insert new sections right before <!-- Conclusión IA -->
html = html.replace('<!-- Conclusión IA -->', new_sections + '\n                <!-- Conclusión IA -->')

# Update JS to load all these tools
js_addition = """
        async function cargarPorter() {
            try {
                const res = await fetch(`/api/business/matrix/PORTER?inst_id=${getInstId()}`);
                const data = await res.json();
                const container = document.getElementById('porterSummary');
                if(data && data.data && data.data.analysis && data.data.analysis.scores) {
                    let html = '<ul>';
                    data.data.analysis.scores.forEach(s => {
                        html += `<li><strong>${s.force}:</strong> Presión ${s.score}/10 - ${s.description}</li>`;
                    });
                    html += '</ul>';
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<i>No se encontró análisis de Porter configurado.</i>';
                }
            } catch(e) { document.getElementById('porterSummary').innerText = 'Error cargando Porter'; }
        }

        async function cargarRiesgos() {
            try {
                const res = await fetch(`/api/business/matrix/RIESGOS?inst_id=${getInstId()}`);
                const data = await res.json();
                const container = document.getElementById('riesgosSummary');
                if(data && data.data && data.data.risks) {
                    let html = '<ul>';
                    data.data.risks.forEach(r => {
                        html += `<li><strong>${r.categoria}:</strong> ${r.descripcion} (Impacto: ${r.impacto}, Probabilidad: ${r.probabilidad})</li>`;
                    });
                    html += '</ul>';
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<i>No se encontraron riesgos configurados.</i>';
                }
            } catch(e) { document.getElementById('riesgosSummary').innerText = 'Error cargando Riesgos'; }
        }

        async function cargarStakeholders() {
            try {
                const res = await fetch(`/api/business/matrix/STAKEHOLDERS?inst_id=${getInstId()}`);
                const data = await res.json();
                const container = document.getElementById('stakeholdersSummary');
                if(data && data.data && data.data.stakeholders) {
                    let html = '<ul>';
                    data.data.stakeholders.forEach(s => {
                        html += `<li><strong>${s.nombre}:</strong> Poder ${s.poder}, Interés ${s.interes} - ${s.estrategia}</li>`;
                    });
                    html += '</ul>';
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<i>No se encontraron stakeholders configurados.</i>';
                }
            } catch(e) { document.getElementById('stakeholdersSummary').innerText = 'Error cargando Stakeholders'; }
        }
"""

html = html.replace('async function cargarMEFI() {', js_addition + '\n        async function cargarMEFI() {')

# Update init() to call new loaders
html = html.replace('cargarMEFE(),', 'cargarMEFE(),\n                cargarPorter(),\n                cargarRiesgos(),\n                cargarStakeholders(),')

# Update AI route call from /api/business/ai_dofa to /api/business/ai_informe_gerencial
html = html.replace('/api/business/ai_dofa', '/api/business/ai_informe_gerencial')

# Save updated HTML
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated empresa_informe_gerencial.html")
