import os

src_file = r"c:\SIAC\templates\estadisticas.html"
dst_file = r"c:\SIAC\templates\crm.html"

with open(src_file, "r", encoding="utf-8") as f:
    content = f.read()

# We need to replace the content inside <div class="content-area"> with our CRM UI.
# And add the CRM link to the sidebar in all HTML templates later.

# Basic split
parts = content.split('<div class="content-area">')
if len(parts) == 2:
    header_part = parts[0]
    # Find the end of the content-area
    footer_part = parts[1].split('</main>')[1]
    
    crm_content = """<div class="content-area">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h1 style="font-size: 1.8rem; margin: 0;">CRM B2B - Prospecci&oacute;n</h1>
                <div>
                    <a href="/api/crm/prospects" download="prospects.json" class="btn-outline">Descargar JSON</a>
                    <button class="btn-primary" onclick="document.getElementById('uploadFile').click()">Subir CSV</button>
                    <input type="file" id="uploadFile" style="display:none" accept=".csv" onchange="uploadCSV(event)">
                </div>
            </div>

            <div class="card" style="margin-bottom: 20px; padding: 20px;">
                <h3>Base de Datos de Prospectos</h3>
                <div style="overflow-x: auto; margin-top: 15px;">
                    <table style="width: 100%; border-collapse: collapse; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid var(--border-color);">
                                <th style="padding: 10px;">Nombre</th>
                                <th style="padding: 10px;">Cargo</th>
                                <th style="padding: 10px;">Instituci&oacute;n</th>
                                <th style="padding: 10px;">Correo</th>
                                <th style="padding: 10px;">Estado</th>
                                <th style="padding: 10px;">Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="prospectsBody">
                            <!-- Se llena por JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            async function loadProspects() {
                try {
                    const res = await fetch('/api/crm/prospects');
                    const data = await res.json();
                    if(data.status === 'success') {
                        const tbody = document.getElementById('prospectsBody');
                        tbody.innerHTML = '';
                        data.data.forEach(p => {
                            const tr = document.createElement('tr');
                            tr.style.borderBottom = "1px solid var(--border-color)";
                            tr.innerHTML = `
                                <td style="padding: 10px;"><b>${p.name}</b></td>
                                <td style="padding: 10px;">${p.position || '-'}</td>
                                <td style="padding: 10px;">${p.institution}<br><small>SNIES: ${p.snies_code || '-'}</small></td>
                                <td style="padding: 10px;">${p.email || '-'}</td>
                                <td style="padding: 10px;">
                                    <select onchange="updateStatus(${p.id}, this.value)" style="padding: 5px; border-radius: 4px; border: 1px solid var(--border-color); background: var(--bg-input);">
                                        <option value="Pendiente" ${p.status==='Pendiente'?'selected':''}>Pendiente</option>
                                        <option value="Correo 1" ${p.status==='Correo 1'?'selected':''}>Correo 1</option>
                                        <option value="Correo 2" ${p.status==='Correo 2'?'selected':''}>Correo 2</option>
                                        <option value="Interesado" ${p.status==='Interesado'?'selected':''}>Interesado</option>
                                        <option value="Rechazado" ${p.status==='Rechazado'?'selected':''}>Rechazado</option>
                                    </select>
                                </td>
                                <td style="padding: 10px;">
                                    ${p.linkedin ? `<a href="${p.linkedin}" target="_blank" style="color:#0077b5;">🔗 In</a>` : ''}
                                </td>
                            `;
                            tbody.appendChild(tr);
                        });
                    }
                } catch(e) {
                    console.error(e);
                }
            }

            async function updateStatus(id, newStatus) {
                try {
                    await fetch('/api/crm/prospects/' + id, {
                        method: 'PUT',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({status: newStatus})
                    });
                } catch(e) { console.error(e); }
            }

            async function uploadCSV(e) {
                const file = e.target.files[0];
                if(!file) return;
                const formData = new FormData();
                formData.append('file', file);
                try {
                    const res = await fetch('/api/crm/upload_prospects', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    alert(data.message);
                    loadProspects();
                } catch(err) {
                    alert('Error subiendo CSV');
                }
            }

            // Authentication check script to block non-admins
            document.addEventListener('DOMContentLoaded', () => {
                const user = JSON.parse(localStorage.getItem('siac_user'));
                if(!user || user.role !== 'admin') {
                    window.location.href = '/dashboard.html';
                } else {
                    document.getElementById('userInfo').innerText = user.name || user.email;
                    loadProspects();
                }
            });
        </script>
        </main>
"""
    
    with open(dst_file, "w", encoding="utf-8") as f:
        # Reemplazar el active del sidebar
        h = header_part.replace('class="sidebar-item active"', 'class="sidebar-item"')
        h = h.replace('<!-- FIN SIDEBAR LINKS -->', '<a href="crm.html" class="sidebar-item active" id="menuCrm">🚀 CRM B2B</a>\n            <!-- FIN SIDEBAR LINKS -->')
        # Si no hay el tag ese, intentemos agregarlo despues del configuracion.html
        if 'crm.html' not in h:
            h = h.replace('<a href="configuracion.html" class="sidebar-item">', '<a href="crm.html" class="sidebar-item active" id="menuCrm">🚀 CRM B2B</a>\n            <a href="configuracion.html" class="sidebar-item">')
            h = h.replace('<a href="configuracion.html" class="sidebar-item active">', '<a href="crm.html" class="sidebar-item active" id="menuCrm">🚀 CRM B2B</a>\n            <a href="configuracion.html" class="sidebar-item">')
        
        f.write(h + crm_content + footer_part)
        print("crm.html created")
