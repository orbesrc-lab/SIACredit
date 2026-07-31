import os

file_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registro de Riesgos - SKEL SIAC</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        .form-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 15px; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label { font-weight: bold; margin-bottom: 5px; font-size: 0.88rem; color: #334155; }
        .form-group input, .form-group select { padding: 9px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9rem; }
        .action-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }
        .btn-action { padding: 10px 18px; border-radius: 8px; border: none; font-weight: bold; font-size: 0.9rem; cursor: pointer; display: flex; align-items: center; gap: 8px; color: white; transition: transform 0.1s ease; }
        .btn-action:hover { transform: translateY(-1px); }
        .btn-add { background: #3b82f6; }
        .btn-save { background: #10b981; }
        .btn-pdf { background: #059669; }
        .btn-back { background: #64748b; text-decoration: none; }
        .table-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
        th { background: #f8fafc; text-align: left; padding: 12px; border-bottom: 2px solid #e2e8f0; color: #475569; }
        td { padding: 12px; border-bottom: 1px solid #f1f5f9; color: #1e293b; }
        .badge { padding: 4px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: bold; text-transform: uppercase; }
        .badge-critico { background: #fee2e2; color: #991b1b; }
        .badge-alto { background: #ffedd5; color: #9a3412; }
        .badge-medio { background: #fef9c3; color: #854d0e; }
        .badge-bajo { background: #dcfce7; color: #166534; }
        .btn-icon { background: none; border: none; cursor: pointer; font-size: 1.1rem; padding: 5px; }
        .btn-edit { color: #3b82f6; }
        .btn-delete { color: #ef4444; }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Global Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <img src="{{ url_for('static', filename='logo_skel.png') }}" alt="SKEL Logo" style="max-height: 50px; object-fit: contain;">
            </div>
            <div class="sidebar-menu">
                <div class="sidebar-group">
                    <div class="sidebar-group-title">Consultoría B2B</div>
                    <div class="sidebar-submenu">
                        <div class="sidebar-submenu-inner">
                            <a href="empresa_dashboard.html" class="sidebar-item">📊 Hub Estratégico</a>
                            <a href="empresa_informe_gerencial.html" class="sidebar-item">📑 Informe Gerencial Integral</a>
                        </div>
                    </div>
                </div>
            </div>
            <div style="padding: 15px;">
                <a href="javascript:void(0)" onclick="logout()" class="sidebar-item" style="color: #ef4444;"><i class="fas fa-sign-out-alt"></i> Cerrar Sesión</a>
            </div>
        </aside>

        <main class="main-content">
            <header class="topbar">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <img id="inst_logo_img" src="" alt="" style="height: 40px; display: none;">
                    <h2 id="inst_name_display" style="font-size: 1.25rem; margin: 0; color: #1e3a8a;">Cargando...</h2>
                </div>
            </header>

            <div class="content-area">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom: 15px;">
                    <div>
                        <h1 style="margin:0; font-size:1.6rem; color:#0f172a;">🛡️ Matriz de Gestión de Riesgos</h1>
                        <p style="margin:5px 0 0; color:#64748b; font-size:0.9rem;">Identificación, evaluación y control de riesgos organizacionales.</p>
                    </div>
                    <a href="empresa_dashboard.html" class="btn-action btn-back"><i class="fas fa-arrow-left"></i> Volver al Hub Estratégico</a>
                </div>

                <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 15px;">
                    <label style="font-weight: bold; color: #334155; font-size: 0.9rem;">📅 Fecha de Levantamiento de Información:</label>
                    <input type="date" id="eval_date" style="padding: 8px 12px; border-radius: 6px; border: 1px solid #cbd5e1; font-size: 0.9rem;">
                </div>

                <!-- Form Card -->
                <div class="form-card">
                    <h3 id="formTitle" style="margin-top:0; color:#1e3a8a; font-size:1.1rem; border-bottom:2px solid #e2e8f0; padding-bottom:8px;">Agregar Nuevo Riesgo</h3>
                    <input type="hidden" id="editIndex" value="-1">
                    <div class="form-grid">
                        <div class="form-group" style="grid-column: span 2;">
                            <label>Riesgo / Evento Adverso *</label>
                            <input type="text" id="r_riesgo" placeholder="Ej. Fuga de información confidencial de clientes...">
                        </div>
                        <div class="form-group">
                            <label>Impacto</label>
                            <select id="r_impacto" onchange="autoCalcLevel()">
                                <option value="Alto">Alto</option>
                                <option value="Medio" selected>Medio</option>
                                <option value="Bajo">Bajo</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Probabilidad</label>
                            <select id="r_probabilidad" onchange="autoCalcLevel()">
                                <option value="Alta">Alta</option>
                                <option value="Media" selected>Media</option>
                                <option value="Baja">Baja</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Nivel de Riesgo (Calculado)</label>
                            <select id="r_nivel">
                                <option value="Crítico">Crítico</option>
                                <option value="Alto">Alto</option>
                                <option value="Medio" selected>Medio</option>
                                <option value="Bajo">Bajo</option>
                            </select>
                        </div>
                        <div class="form-group" style="grid-column: span 2;">
                            <label>Estrategia de Mitigación / Control *</label>
                            <input type="text" id="r_estrategia" placeholder="Ej. Implementación de políticas de acceso estricto y encriptación...">
                        </div>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button class="btn-action btn-add" id="btnAdd" onclick="saveRiskForm()"><i class="fas fa-plus"></i> Agregar a la Tabla</button>
                        <button class="btn-action btn-back" id="btnCancelEdit" onclick="resetForm()" style="display:none;">Cancelar Edición</button>
                    </div>
                </div>

                <div class="action-bar">
                    <button class="btn-action btn-save" onclick="saveAllRisks()"><i class="fas fa-save"></i> Guardar Todo en Base de Datos</button>
                    <button class="btn-action btn-pdf" onclick="exportPDF()"><i class="fas fa-file-pdf"></i> Descargar Informe PDF</button>
                </div>

                <!-- Table Card -->
                <div class="table-card">
                    <table>
                        <thead>
                            <tr>
                                <th>Riesgo Identificado</th>
                                <th style="width: 100px; text-align:center;">Impacto</th>
                                <th style="width: 110px; text-align:center;">Probabilidad</th>
                                <th style="width: 110px; text-align:center;">Nivel</th>
                                <th>Estrategia Mitigante</th>
                                <th style="width: 90px; text-align:center;">Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="riskTableBody">
                            <tr><td colspan="6" style="text-align:center; color:#64748b;">No hay riesgos registrados. Ingrese uno arriba.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <script src="{{ url_for('static', filename='app.js') }}"></script>
    <script>
        let risksList = [];

        function logout() { localStorage.removeItem('siac_user'); window.top.location.href = 'login.html'; }

        document.addEventListener('DOMContentLoaded', async () => {
            await initHeader();
            await loadRisks();
        });

        async function initHeader() {
            try {
                const resp = await fetch(`/api/institution?inst_id=${getInstId()}`);
                if (resp.ok) {
                    const data = await resp.json();
                    document.getElementById('inst_name_display').textContent = data.name || 'INSTITUCIÓN';
                    if (data.logo_url) {
                        const img = document.getElementById('inst_logo_img');
                        img.src = data.logo_url; img.style.display = 'block';
                    }
                }
            } catch(e) { console.error(e); }
        }

        function autoCalcLevel() {
            const imp = document.getElementById('r_impacto').value;
            const prob = document.getElementById('r_probabilidad').value;
            const lvl = document.getElementById('r_nivel');

            if (imp === 'Alto' && prob === 'Alta') lvl.value = 'Crítico';
            else if (imp === 'Alto' || prob === 'Alta') lvl.value = 'Alto';
            else if (imp === 'Bajo' && prob === 'Baja') lvl.value = 'Bajo';
            else lvl.value = 'Medio';
        }

        function renderTable() {
            const tbody = document.getElementById('riskTableBody');
            if (risksList.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#64748b;">No hay riesgos registrados.</td></tr>';
                return;
            }
            tbody.innerHTML = risksList.map((r, idx) => {
                let badgeClass = 'badge-medio';
                if (r.nivel === 'Crítico') badgeClass = 'badge-critico';
                else if (r.nivel === 'Alto') badgeClass = 'badge-alto';
                else if (r.nivel === 'Bajo') badgeClass = 'badge-bajo';

                return `
                <tr>
                    <td><strong>${r.riesgo}</strong></td>
                    <td style="text-align:center;">${r.impacto}</td>
                    <td style="text-align:center;">${r.probabilidad}</td>
                    <td style="text-align:center;"><span class="badge ${badgeClass}">${r.nivel}</span></td>
                    <td>${r.estrategia}</td>
                    <td style="text-align:center;">
                        <button class="btn-icon btn-edit" onclick="editRisk(${idx})" title="Editar"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon btn-delete" onclick="deleteRisk(${idx})" title="Eliminar"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>`;
            }).join('');
        }

        function saveRiskForm() {
            const riesgo = document.getElementById('r_riesgo').value.trim();
            const impacto = document.getElementById('r_impacto').value;
            const probabilidad = document.getElementById('r_probabilidad').value;
            const nivel = document.getElementById('r_nivel').value;
            const estrategia = document.getElementById('r_estrategia').value.trim();
            const editIdx = parseInt(document.getElementById('editIndex').value);

            if (!riesgo || !estrategia) {
                Swal.fire('Atención', 'Por favor ingrese la descripción del riesgo y la estrategia.', 'warning');
                return;
            }

            const item = { riesgo, impacto, probabilidad, nivel, estrategia };

            if (editIdx >= 0) {
                risksList[editIdx] = item;
            } else {
                risksList.push(item);
            }

            resetForm();
            renderTable();
        }

        function editRisk(idx) {
            const r = risksList[idx];
            document.getElementById('editIndex').value = idx;
            document.getElementById('r_riesgo').value = r.riesgo;
            document.getElementById('r_impacto').value = r.impacto;
            document.getElementById('r_probabilidad').value = r.probabilidad;
            document.getElementById('r_nivel').value = r.nivel;
            document.getElementById('r_estrategia').value = r.estrategia;

            document.getElementById('formTitle').textContent = 'Editar Riesgo #' + (idx + 1);
            document.getElementById('btnAdd').innerHTML = '<i class="fas fa-check"></i> Actualizar Riesgo';
            document.getElementById('btnCancelEdit').style.display = 'inline-flex';
        }

        function deleteRisk(idx) {
            Swal.fire({
                title: '¿Eliminar riesgo?',
                text: 'Esta acción eliminará el riesgo de la lista.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sí, eliminar'
            }).then((result) => {
                if (result.isConfirmed) {
                    risksList.splice(idx, 1);
                    renderTable();
                }
            });
        }

        function resetForm() {
            document.getElementById('editIndex').value = -1;
            document.getElementById('r_riesgo').value = '';
            document.getElementById('r_estrategia').value = '';
            document.getElementById('formTitle').textContent = 'Agregar Nuevo Riesgo';
            document.getElementById('btnAdd').innerHTML = '<i class="fas fa-plus"></i> Agregar a la Tabla';
            document.getElementById('btnCancelEdit').style.display = 'none';
        }

        async function loadRisks() {
            try {
                const res = await fetch(`/api/business/matrix/RIESGOS?inst_id=${getInstId()}`);
                if (res.ok) {
                    const data = await res.json();
                    let dbData = data.data;
                    if (typeof dbData === 'string') { try { dbData = JSON.parse(dbData); } catch(e){} }

                    if (dbData && dbData.risks) {
                        risksList = dbData.risks;
                        renderTable();
                    }
                    if (dbData && dbData.eval_date) {
                        document.getElementById('eval_date').value = dbData.eval_date;
                    }
                }
            } catch(e) { console.error(e); }
        }

        async function saveAllRisks() {
            const evalDate = document.getElementById('eval_date').value;
            try {
                const res = await fetch('/api/business/matrix/RIESGOS', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        inst_id: getInstId(),
                        data: { risks: risksList, eval_date: evalDate }
                    })
                });
                if (res.ok) {
                    Swal.fire('¡Éxito!', 'Registro de Riesgos guardado correctamente en la base de datos.', 'success');
                }
            } catch(e) {
                Swal.fire('Error', 'No se pudieron guardar los riesgos.', 'error');
            }
        }

        function exportPDF() {
            const logoImg = document.getElementById('inst_logo_img');
            const logoSrc = (logoImg && logoImg.style.display !== 'none' && logoImg.src) ? logoImg.src : '';
            const instName = document.getElementById('inst_name_display').textContent || 'INSTITUCIÓN EDUCATIVA';
            const evalDate = document.getElementById('eval_date').value || 'No especificada';

            let rows = risksList.map(r => `
                <tr>
                    <td style="padding:8px; border:1px solid #cbd5e1;"><strong>${r.riesgo}</strong></td>
                    <td style="padding:8px; border:1px solid #cbd5e1; text-align:center;">${r.impacto}</td>
                    <td style="padding:8px; border:1px solid #cbd5e1; text-align:center;">${r.probabilidad}</td>
                    <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; font-weight:bold;">${r.nivel}</td>
                    <td style="padding:8px; border:1px solid #cbd5e1;">${r.estrategia}</td>
                </tr>
            `).join('');

            const printHTML = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Informe de Registro de Riesgos - ${instName}</title>
                <style>
                    body { font-family: 'Segoe UI', Arial, sans-serif; color: #1e293b; padding: 30px; }
                    .header { display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #2563eb; padding-bottom: 15px; margin-bottom: 20px; }
                    .logo { max-height: 55px; max-width: 200px; object-fit: contain; }
                    .inst-name { font-size: 1.3rem; font-weight: bold; color: #1e3a8a; text-transform: uppercase; }
                    .report-title { text-align: center; font-size: 1.5rem; color: #0f172a; margin-top: 10px; font-weight: bold; }
                    .meta-info { text-align: center; font-size: 0.95rem; color: #64748b; margin-bottom: 25px; }
                    table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
                    th { background-color: #f1f5f9; color: #334155; font-weight: bold; padding: 9px; border: 1px solid #cbd5e1; text-align: left; }
                </style>
            </head>
            <body>
                <div class="header">
                    <div>${logoSrc ? `<img src="${logoSrc}" class="logo">` : 'SIAC STRATEGIC'}</div>
                    <div class="inst-name">${instName}</div>
                </div>

                <div class="report-title">INFORME DE REGISTRO DE RIESGOS</div>
                <div class="meta-info">📅 Fecha de Levantamiento de Información: <strong>${evalDate}</strong></div>

                <table>
                    <thead>
                        <tr>
                            <th>Riesgo Identificado</th>
                            <th style="width: 100px; text-align:center;">Impacto</th>
                            <th style="width: 110px; text-align:center;">Probabilidad</th>
                            <th style="width: 110px; text-align:center;">Nivel</th>
                            <th>Estrategia de Mitigación</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows || '<tr><td colspan="5" style="text-align:center;">Sin riesgos registrados</td></tr>'}
                    </tbody>
                </table>

                <script>
                    window.onload = function() { setTimeout(() => { window.print(); }, 500); };
                <\\/script>
            <\\/body>
            <\\/html>
            `;

            const win = window.open('', '_blank');
            if (win) { win.document.open(); win.document.write(printHTML); win.document.close(); }
        }
    </script>
</body>
</html>
"""

with open(r'c:\SIAC\templates\empresa_riesgos.html', 'w', encoding='utf-8') as f:
    f.write(file_content)

print("empresa_riesgos.html rewritten successfully!")
