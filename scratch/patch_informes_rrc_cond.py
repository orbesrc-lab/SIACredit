import re

with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Inject the "Analizar Archivo" button
old_html = """<input type="file" id="justificationFileRRC" accept=".pdf,.docx,.xlsx" style="font-size:0.8rem;">"""
new_html = """<input type="file" id="justificationFileRRC" accept=".pdf,.docx,.xlsx" style="font-size:0.8rem;">
                            <button class="btn-primary" style="font-size:0.75rem; padding: 4px 10px;" onclick="analizarSoporteCondicion()" id="btnAnalizarSoporte" title="Sube el archivo y analiza mediante IA solo la pestaña activa"><i class="fas fa-brain"></i> Analizar Pestaña Activa</button>"""
content = content.replace(old_html, new_html)

# 2. Inject the `analizarSoporteCondicion` function
js_function = """

        async function analizarSoporteCondicion() {
            const justFile = document.getElementById('justificationFileRRC').files[0];
            if (!justFile) {
                alert('Por favor selecciona un archivo primero.');
                return;
            }
            
            // Buscar tab activo
            let activeCond = '1';
            document.querySelectorAll('.rrc-tab').forEach(t => {
                if(t.classList.contains('active')) {
                    activeCond = t.id.replace('rrc-tab-', '');
                }
            });

            const btn = document.getElementById('btnAnalizarSoporte');
            const ogText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analizando...';
            btn.disabled = true;

            try {
                // Subir archivo
                const formData = new FormData();
                formData.append('file', justFile);
                formData.append('plan_id', 'RRC_JUSTIFICATION_COND_' + activeCond);
                
                const upRes = await fetch('/api/planes_mejora/upload_soporte', { method: 'POST', body: formData });
                const upData = await upRes.json();
                
                if (!upData.url) throw new Error('Error al subir el archivo.');
                
                const instId = getInstId();
                const programId = getProgramId();
                
                const condicion_data = _rrcCondData[activeCond] || {};

                // Llamar IA para condici\u00f3n espec\u00edfica
                const aiRes = await fetch('/api/ai/generar_rrc_condicion', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        inst_id: instId,
                        program_id: programId,
                        condicion_num: activeCond,
                        condicion_data: condicion_data,
                        program_name: _rrcProgName,
                        inst_name: _rrcInstName,
                        justification_url: upData.url
                    })
                });
                
                const aiData = await aiRes.json();
                if (aiData.status !== 'success') throw new Error(aiData.message || 'Error en an\u00e1lisis IA');
                
                // Actualizar panel activo
                const contentDiv = document.getElementById(`rrc-edit-content-${activeCond}`);
                if (contentDiv) {
                    contentDiv.innerHTML = marked.parse(aiData.report);
                    alert('Condici\u00f3n ' + activeCond + ' actualizada con el an\u00e1lisis del archivo.');
                    guardarReporteRRC(); // Auto-guardar
                }
                
            } catch (err) {
                alert('Error: ' + err.message);
            }
            btn.innerHTML = ogText;
            btn.disabled = false;
        }

        async function generarSoporteRRC(forceRegenerate = false) {"""

content = content.replace("async function generarSoporteRRC(forceRegenerate = false) {", js_function)

with open(r'c:\SIAC\templates\informes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied to informes.html")
