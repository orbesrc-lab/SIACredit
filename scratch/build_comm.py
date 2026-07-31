import re

base_file = r'c:\SIAC\templates\dofa.html'
content = open(base_file, encoding='utf-8').read()

parts = content.split('<div class="content-area">')
top_html = parts[0] + '<div class="content-area">\n'
bottom_html = '\n</main>\n' + parts[1].split('</main>')[1]
clean_bottom = bottom_html.replace('initPage();', '')

# 3. Comunicacion
comunicacion_content = """
    <style>
        .tool-header { margin-bottom: 25px; }
        .tool-header h1 { font-size: 1.8rem; margin-bottom: 8px; color: var(--primary-color); }
        .tool-header p { color: var(--text-muted); font-size: 0.95rem; }
        
        .input-panel {
            background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 30px;
        }
        
        .form-grid {
            display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px;
        }
        @media (max-width: 900px) { .form-grid { grid-template-columns: 1fr 1fr; } }
        @media (max-width: 600px) { .form-grid { grid-template-columns: 1fr; } }
        
        .form-group label { display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 5px; }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9rem;
        }
        
        .stakeholder-table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .stakeholder-table th, .stakeholder-table td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; }
        .stakeholder-table th { background-color: #f8fafc; font-weight: 600; color: #475569; }
        
        .badge { padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
        .b-int { background: #eff6ff; color: #1e3a8a; } /* Internal */
        .b-ext { background: #fef2f2; color: #991b1b; } /* External */
    </style>
    
    <div class="tool-header">
        <h1>📣 Plan de Comunicación Organizacional</h1>
        <p>Estructure y gestione los canales, mensajes y frecuencias de comunicación para asegurar el alineamiento estratégico con sus partes interesadas.</p>
    </div>

    <div class="input-panel">
        <h3 style="margin-top:0; font-size:1.1rem; border-bottom:1px solid #e2e8f0; padding-bottom:10px; margin-bottom:20px;">Nuevo Protocolo de Comunicación</h3>
        
        <div class="form-group" style="margin-bottom:15px;">
            <label>Mensaje Clave / Objetivo de Comunicación</label>
            <input type="text" id="c_mensaje" placeholder="Ej. Resultados trimestrales, Cambios de políticas, Plan Estratégico">
        </div>
        
        <div class="form-grid">
            <div class="form-group">
                <label>Público Objetivo (Audiencia)</label>
                <input type="text" id="c_audiencia" placeholder="Ej. Empleados, Inversores, Clientes">
            </div>
            <div class="form-group">
                <label>Tipo de Audiencia</label>
                <select id="c_tipo">
                    <option value="Interna">Interna</option>
                    <option value="Externa">Externa</option>
                </select>
            </div>
            <div class="form-group">
                <label>Canal / Medio</label>
                <input type="text" id="c_canal" placeholder="Ej. Intranet, Email, Reunión General">
            </div>
            <div class="form-group">
                <label>Frecuencia</label>
                <select id="c_frecuencia">
                    <option value="Diaria">Diaria</option>
                    <option value="Semanal">Semanal</option>
                    <option value="Quincenal">Quincenal</option>
                    <option value="Mensual">Mensual</option>
                    <option value="Trimestral">Trimestral</option>
                    <option value="Anual">Anual</option>
                    <option value="Ad-hoc (Según necesidad)">Ad-hoc (Según necesidad)</option>
                </select>
            </div>
            <div class="form-group">
                <label>Responsable</label>
                <input type="text" id="c_responsable" placeholder="Ej. Dirección General, RRHH">
            </div>
        </div>
        
        <div style="display:flex; gap:15px; margin-top:10px;">
            <button class="btn-primary" onclick="addComm()" style="flex:1; padding:10px; border-radius:6px; border:none; background:#6366f1; color:white; font-weight:600; cursor:pointer;">
                + Añadir al Plan
            </button>
            <button onclick="saveMatrixData()" style="flex:1; padding:10px; border-radius:6px; border:1px solid #10b981; background:#f0fdf4; color:#10b981; font-weight:600; cursor:pointer;">
                💾 Guardar Plan de Comunicación
            </button>
        </div>
    </div>

    <div>
        <h3 style="margin-bottom:15px; font-size:1.2rem; color:var(--primary-color);">Matriz de Comunicación Consolidada</h3>
        <table class="stakeholder-table">
            <thead>
                <tr>
                    <th>Mensaje / Objetivo</th>
                    <th>Público Objetivo</th>
                    <th>Canal</th>
                    <th>Frecuencia</th>
                    <th>Responsable</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody id="commList">
                <!-- Data injected by JS -->
            </tbody>
        </table>
    </div>

    <script>
        let communications = [];
        
        function loadMatriz() {}
        function loadInternos() {}
        function loadExternos() {}

        async function initPageComm() {
            try {
                const resp = await fetch(`/api/business/matrix/COMUNICACION?inst_id=${getInstId()}`);
                if(resp.ok) {
                    const res = await resp.json();
                    if(res.data && res.data.communications) {
                        communications = res.data.communications;
                    }
                }
            } catch(e) { console.error("Error cargando comunicacion", e); }
            
            renderComm();
        }

        function addComm() {
            const mensaje = document.getElementById('c_mensaje').value.trim();
            const audiencia = document.getElementById('c_audiencia').value.trim();
            const tipo = document.getElementById('c_tipo').value;
            const canal = document.getElementById('c_canal').value.trim();
            const frecuencia = document.getElementById('c_frecuencia').value;
            const responsable = document.getElementById('c_responsable').value.trim();
            
            if(!mensaje || !audiencia) return alert("Por favor ingresa al menos el mensaje y la audiencia.");
            
            communications.push({ id: Date.now(), mensaje, audiencia, tipo, canal, frecuencia, responsable });
            
            document.getElementById('c_mensaje').value = '';
            document.getElementById('c_audiencia').value = '';
            document.getElementById('c_canal').value = '';
            document.getElementById('c_responsable').value = '';
            
            renderComm();
        }

        function removeComm(idx) {
            communications.splice(idx, 1);
            renderComm();
        }

        function renderComm() {
            const tbody = document.getElementById('commList');
            tbody.innerHTML = '';
            
            if(communications.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#94a3b8;">No hay protocolos de comunicación registrados.</td></tr>';
            } else {
                communications.forEach((c, idx) => {
                    const tipoBadge = c.tipo === 'Interna' ? '<span class="badge b-int">Interna</span>' : '<span class="badge b-ext">Externa</span>';
                    tbody.innerHTML += `
                        <tr>
                            <td><strong>${c.mensaje}</strong></td>
                            <td>${c.audiencia} <br>${tipoBadge}</td>
                            <td>${c.canal || '-'}</td>
                            <td>${c.frecuencia}</td>
                            <td>${c.responsable || '-'}</td>
                            <td>
                                <button onclick="removeComm(${idx})" style="background:none; border:none; color:#ef4444; cursor:pointer;"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
                    `;
                });
            }
        }

        async function saveMatrixData() {
            const payload = {
                inst_id: getInstId(),
                user_id: user.id,
                data: { communications: communications },
                results: {}
            };
            
            try {
                const resp = await fetch('/api/business/matrix/COMUNICACION', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(resp.ok) {
                    alert("✅ Plan de Comunicación guardado con éxito.");
                } else {
                    alert("Error al guardar.");
                }
            } catch(e) {
                alert("Error de red.");
            }
        }
        
        setTimeout(() => { initPageComm(); }, 500);
    </script>
"""

with open(r'c:\SIAC\templates\empresa_comunicacion.html', 'w', encoding='utf-8') as f:
    f.write(top_html + comunicacion_content + clean_bottom)

print("Generated empresa_comunicacion.html successfully.")
