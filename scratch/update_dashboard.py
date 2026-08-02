import os
import re

file_path = r'c:\SIAC\templates\skel_empresa_dashboard.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace button onclicks
html = html.replace("onclick=\"alert('Asignación en desarrollo')\"", "onclick=\"abrirModalPerfiles()\"")
html = html.replace("onclick=\"alert('Logística en desarrollo')\"", "onclick=\"lanzarEncuestas()\"")

# Add Modals before </main>
modals = """
        <!-- Modal Perfiles -->
        <div id="modalPerfiles" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000; justify-content:center; align-items:center;">
            <div style="background:var(--glass-bg); padding:30px; border-radius:15px; width:600px; max-width:90%; border:1px solid var(--glass-border); box-shadow:var(--shadow-lg);">
                <h3 style="margin-bottom:20px;">Gestionar Perfiles de Cargos</h3>
                <div style="margin-bottom:15px;">
                    <label>Seleccionar Cargo:</label>
                    <select id="select-cargo" onchange="cargarCompetenciasCargo()" style="width:100%; padding:10px; border-radius:8px; border:1px solid var(--border-color); background:var(--bg-color); color:var(--text-color);">
                        <option value="">Cargando cargos...</option>
                    </select>
                </div>
                <div style="margin-bottom:15px; max-height:250px; overflow-y:auto; padding:10px; background:rgba(0,0,0,0.2); border-radius:8px;">
                    <h4>Competencias a evaluar:</h4>
                    <div id="lista-competencias">Cargando...</div>
                </div>
                <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:20px;">
                    <button class="btn-primary" style="background:#64748b;" onclick="document.getElementById('modalPerfiles').style.display='none'">Cancelar</button>
                    <button class="btn-primary" onclick="guardarPerfil()">Guardar Asignación</button>
                </div>
            </div>
        </div>
        
        <!-- Modal Links -->
        <div id="modalLinks" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000; justify-content:center; align-items:center;">
            <div style="background:var(--glass-bg); padding:30px; border-radius:15px; width:800px; max-width:90%; border:1px solid var(--glass-border); box-shadow:var(--shadow-lg);">
                <h3 style="margin-bottom:20px;">Encuestas Lanzadas (Magic Links)</h3>
                <p style="margin-bottom:15px;">Copia y comparte estos links seguros con los colaboradores para que ingresen a su formulario.</p>
                <div style="max-height:400px; overflow-y:auto;">
                    <table class="admin-table">
                        <thead><tr><th>Colaborador</th><th>Correo</th><th>Magic Link</th></tr></thead>
                        <tbody id="links-tbody"></tbody>
                    </table>
                </div>
                <div style="display:flex; justify-content:flex-end; margin-top:20px;">
                    <button class="btn-primary" onclick="document.getElementById('modalLinks').style.display='none'">Cerrar</button>
                </div>
            </div>
        </div>
"""
html = html.replace("</main>", modals + "\n    </main>")

# Inject JS logic inside <script>
js_logic = """
        let allCargos = [];
        let allCompetencias = [];
        
        async function abrirModalPerfiles() {
            document.getElementById('modalPerfiles').style.display = 'flex';
            
            // Cargar Diccionario
            const resDicc = await fetch('/api/skel360/diccionario');
            const dataDicc = await resDicc.json();
            allCompetencias = dataDicc.data || [];
            
            // Cargar Cargos de la empresa
            const resPerf = await fetch(`/api/skel360/empresa/${empresaId}/perfiles`);
            const dataPerf = await resPerf.json();
            allCargos = dataPerf.data || [];
            
            const sel = document.getElementById('select-cargo');
            sel.innerHTML = '<option value="">Seleccione un cargo...</option>';
            allCargos.forEach(c => {
                sel.innerHTML += `<option value="${c.id}">${c.nombre}</option>`;
            });
            
            document.getElementById('lista-competencias').innerHTML = 'Seleccione un cargo arriba.';
        }
        
        function cargarCompetenciasCargo() {
            const cargoId = document.getElementById('select-cargo').value;
            if(!cargoId) {
                document.getElementById('lista-competencias').innerHTML = 'Seleccione un cargo arriba.';
                return;
            }
            
            const cargo = allCargos.find(c => c.id === cargoId);
            const html = allCompetencias.map(comp => {
                const isChecked = cargo.competencias.includes(comp.id) ? 'checked' : '';
                return `<label style="display:block; margin-bottom:5px;"><input type="checkbox" class="comp-cb" value="${comp.id}" ${isChecked}> ${comp.nombre}</label>`;
            }).join('');
            
            document.getElementById('lista-competencias').innerHTML = html;
        }
        
        async function guardarPerfil() {
            const cargoId = document.getElementById('select-cargo').value;
            if(!cargoId) return alert('Seleccione un cargo');
            
            const checks = document.querySelectorAll('.comp-cb:checked');
            const compIds = Array.from(checks).map(c => c.value);
            
            try {
                const res = await fetch(`/api/skel360/empresa/${empresaId}/perfiles`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ cargo_id: cargoId, competencias: compIds })
                });
                const data = await res.json();
                if(data.status === 'success') {
                    alert('Asignación guardada con éxito.');
                    document.getElementById('modalPerfiles').style.display = 'none';
                }
            } catch(e) { console.error(e); }
        }
        
        async function lanzarEncuestas() {
            if(!confirm('¿Estás seguro de generar las evaluaciones para todos los colaboradores?')) return;
            
            try {
                const res = await fetch(`/api/skel360/empresa/${empresaId}/lanzar`, {method: 'POST'});
                const data = await res.json();
                if(data.status === 'success') {
                    alert(data.message);
                    const tbody = document.getElementById('links-tbody');
                    tbody.innerHTML = '';
                    data.links.forEach(l => {
                        tbody.innerHTML += `<tr><td>${l.nombre}</td><td>${l.correo}</td><td><a href="${l.link}" target="_blank" style="color:#3b82f6; font-size:0.85rem;">${l.link}</a></td></tr>`;
                    });
                    document.getElementById('modalLinks').style.display = 'flex';
                } else {
                    alert('Error: ' + data.message);
                }
            } catch(e) { console.error(e); }
        }
"""
html = html.replace("loadColaboradores();", "loadColaboradores();\n" + js_logic)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("skel_empresa_dashboard.html actualizado con modals y lógica JS.")
