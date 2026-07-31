import os

file_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alineación ISO 9001 + IA - SKEL SIAC</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        .sgc-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .action-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }
        .btn-action { padding: 10px 18px; border-radius: 8px; border: none; font-weight: bold; font-size: 0.9rem; cursor: pointer; display: flex; align-items: center; gap: 8px; color: white; transition: transform 0.1s ease; }
        .btn-action:hover { transform: translateY(-1px); }
        .btn-save { background: #10b981; }
        .btn-ai { background: linear-gradient(135deg, #8b5cf6, #3b82f6); }
        .btn-pdf { background: #059669; }
        .btn-back { background: #64748b; text-decoration: none; }

        /* Process Map Grid */
        .process-map-container { display: flex; flex-direction: column; gap: 15px; margin-top: 15px; }
        .process-tier { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; }
        .tier-title { font-weight: bold; font-size: 1rem; color: #1e3a8a; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
        .process-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
        .process-box { background: white; border: 2px solid #cbd5e1; border-radius: 8px; padding: 15px; cursor: pointer; transition: all 0.2s ease; display: flex; flex-direction: column; justify-content: space-between; }
        .process-box:hover { border-color: #3b82f6; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(59,130,246,0.15); }
        .process-box.tier-strat { border-left: 5px solid #8b5cf6; }
        .process-box.tier-misional { border-left: 5px solid #3b82f6; }
        .process-box.tier-apoyo { border-left: 5px solid #10b981; }
        .process-name { font-weight: bold; color: #0f172a; font-size: 0.95rem; margin-bottom: 5px; }
        .process-meta { font-size: 0.8rem; color: #64748b; }

        /* Modal SIPOC */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(15,23,42,0.6); backdrop-filter: blur(4px); justify-content: center; align-items: center; }
        .modal-content { background: white; width: 92%; max-width: 1000px; max-height: 90vh; border-radius: 14px; overflow-y: auto; padding: 25px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.3); }
        .phva-tab-bar { display: flex; gap: 5px; border-bottom: 2px solid #e2e8f0; margin-bottom: 20px; }
        .phva-tab { padding: 10px 18px; border: none; background: #f1f5f9; font-weight: bold; font-size: 0.9rem; color: #475569; cursor: pointer; border-radius: 8px 8px 0 0; }
        .phva-tab.active { background: #3b82f6; color: white; }
        .phva-panel { display: none; }
        .phva-panel.active { display: block; }

        /* SIPOC Table */
        .sipoc-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.88rem; }
        .sipoc-table th { background: #1e3a8a; color: white; padding: 8px; border: 1px solid #cbd5e1; }
        .sipoc-table td { padding: 8px; border: 1px solid #cbd5e1; vertical-align: top; }
        .sipoc-table textarea { width: 100%; height: 70px; border: none; resize: vertical; font-family: inherit; font-size: 0.85rem; }

        @media print {
            body * { visibility: hidden !important; }
            #printSection, #printSection * { visibility: visible !important; }
            #printSection { position: absolute !important; left: 0 !important; top: 0 !important; width: 100% !important; display: block !important; background: white !important; padding: 20px !important; color: #0f172a !important; font-family: 'Segoe UI', Arial, sans-serif !important; }
        }
        #printSection { display: none; }
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
                        <h1 style="margin:0; font-size:1.6rem; color:#0f172a;">🏆 Alineación ISO 9001:2015 Auditor-Ready</h1>
                        <p style="margin:5px 0 0; color:#64748b; font-size:0.9rem;">Sistema Integrado de Gestión de Calidad (Mapa de Procesos, SIPOC, Ciclo PHVA y Evidencias).</p>
                    </div>
                    <a href="empresa_dashboard.html" class="btn-action btn-back"><i class="fas fa-arrow-left"></i> Volver al Hub Estratégico</a>
                </div>

                <!-- Date & Main Action Bar -->
                <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <label style="font-weight: bold; color: #334155; font-size: 0.9rem;">📅 Fecha de Levantamiento de Información:</label>
                        <input type="date" id="eval_date" style="padding: 8px 12px; border-radius: 6px; border: 1px solid #cbd5e1; font-size: 0.9rem;">
                    </div>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <button class="btn-action btn-save" onclick="saveSGC()"><i class="fas fa-save"></i> Guardar SGC</button>
                        <button class="btn-action btn-ai" onclick="generateSGCAI()"><i class="fas fa-robot"></i> Auto-Generar SGC con IA</button>
                        <button class="btn-action btn-pdf" onclick="exportPDF()"><i class="fas fa-file-pdf"></i> Descargar Informe Auditoría PDF</button>
                    </div>
                </div>

                <!-- Policy & Objectives Section -->
                <div class="sgc-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #e2e8f0; padding-bottom:10px; margin-bottom:15px;">
                        <h3 style="margin:0; color:#1e3a8a; font-size:1.15rem;"><i class="fas fa-award"></i> Política y Objetivos de Calidad (Cláusula 5.2 / 6.2)</h3>
                        <button class="btn-action btn-ai" style="padding:6px 12px; font-size:0.8rem;" onclick="generatePolicyAI()"><i class="fas fa-magic"></i> Generar Política con IA</button>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="font-weight:bold; color:#334155; font-size:0.9rem; display:block; margin-bottom:5px;">Política de Calidad Institucional:</label>
                        <textarea id="sgc_policy" style="width:100%; height:75px; padding:10px; border:1px solid #cbd5e1; border-radius:8px; font-family:inherit; font-size:0.9rem;" placeholder="La institución se compromete a brindar servicios de alta calidad, satisfaciendo las necesidades de los usuarios y promoviendo la mejora continua..."></textarea>
                    </div>

                    <div>
                        <label style="font-weight:bold; color:#334155; font-size:0.9rem; display:block; margin-bottom:5px;">Objetivos de Calidad Medibles:</label>
                        <textarea id="sgc_objectives" style="width:100%; height:75px; padding:10px; border:1px solid #cbd5e1; border-radius:8px; font-family:inherit; font-size:0.9rem;" placeholder="1. Aumentar la satisfacción de los usuarios al 90%.&#10;2. Cumplir el 95% del plan de formación..."></textarea>
                    </div>
                </div>

                <!-- Process Map Section -->
                <div class="sgc-card">
                    <h3 style="margin-top:0; color:#1e3a8a; font-size:1.15rem; border-bottom:2px solid #e2e8f0; padding-bottom:10px; margin-bottom:15px;"><i class="fas fa-sitemap"></i> Mapa de Procesos Institucional (Haga clic en un proceso para ver su Caracterización y PHVA)</h3>
                    
                    <div class="process-map-container">
                        <!-- Procesos Estratégicos -->
                        <div class="process-tier">
                            <div class="tier-title"><i class="fas fa-compass" style="color:#8b5cf6;"></i> PROCESOS ESTRATÉGICOS (Dirección y Planificación)</div>
                            <div class="process-grid" id="gridEstrategicos"></div>
                        </div>

                        <!-- Procesos Misionales -->
                        <div class="process-tier">
                            <div class="tier-title"><i class="fas fa-cogs" style="color:#3b82f6;"></i> PROCESOS MISIONALES / OPERATIVOS (Cadena de Valor)</div>
                            <div class="process-grid" id="gridMisionales"></div>
                        </div>

                        <!-- Procesos de Apoyo -->
                        <div class="process-tier">
                            <div class="tier-title"><i class="fas fa-hand-holding-heart" style="color:#10b981;"></i> PROCESOS DE APOYO (Soporte Institucional)</div>
                            <div class="process-grid" id="gridApoyo"></div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- Modal Characterization & PHVA (SIPOC) -->
    <div class="modal" id="processModal">
        <div class="modal-content">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #e2e8f0; padding-bottom:12px; margin-bottom:15px;">
                <div>
                    <h2 id="modalProcessTitle" style="margin:0; color:#1e3a8a; font-size:1.3rem;">Ficha de Caracterización de Proceso</h2>
                    <span id="modalProcessTier" class="process-meta">Proceso Misional</span>
                </div>
                <button onclick="closeModal()" style="background:none; border:none; font-size:1.5rem; cursor:pointer; color:#64748b;">&times;</button>
            </div>

            <!-- PHVA Tab Navigation -->
            <div class="phva-tab-bar">
                <button class="phva-tab active" onclick="switchPHVATab('tabSipoc')">📋 Caracterización (SIPOC)</button>
                <button class="phva-tab" onclick="switchPHVATab('tabPlanear')">🎯 P - PLANEAR (Análisis)</button>
                <button class="phva-tab" onclick="switchPHVATab('tabHacer')">⚙️ H - HACER (Ejecución)</button>
                <button class="phva-tab" onclick="switchPHVATab('tabVerificar')">🔍 V - VERIFICAR (Evidencias)</button>
                <button class="phva-tab" onclick="switchPHVATab('tabActuar')">🤖 A - ACTUAR (IA Auditor)</button>
            </div>

            <!-- Panel SIPOC -->
            <div class="phva-panel active" id="tabSipoc">
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-bottom:15px;">
                    <div><label style="font-weight:bold; font-size:0.85rem;">Líder del Proceso:</label> <input type="text" id="proc_leader" style="width:100%; padding:6px; border:1px solid #cbd5e1; border-radius:4px;" placeholder="Ej. Vicerrectoría Académica / Dirección"></div>
                    <div><label style="font-weight:bold; font-size:0.85rem;">Objetivo del Proceso:</label> <input type="text" id="proc_objective" style="width:100%; padding:6px; border:1px solid #cbd5e1; border-radius:4px;" placeholder="Ej. Garantizar la excelencia en el diseño e impartición..."></div>
                </div>

                <h4 style="margin-bottom:5px; color:#1e3a8a;">Matriz SIPOC</h4>
                <table class="sipoc-table">
                    <thead>
                        <tr>
                            <th>S - Proveedores</th>
                            <th>I - Entradas</th>
                            <th>P - Actividades Principales</th>
                            <th>O - Salidas</th>
                            <th>C - Clientes / Usuarios</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><textarea id="sipoc_s" placeholder="Ej. Dirección, Entidades externas, Usuarios..."></textarea></td>
                            <td><textarea id="sipoc_i" placeholder="Ej. Solicitudes, Requisitos legales, Recursos..."></textarea></td>
                            <td><textarea id="sipoc_p" placeholder="Ej. 1. Planificar el servicio.&#10;2. Ejecutar actividades.&#10;3. Evaluar satisfacción."></textarea></td>
                            <td><textarea id="sipoc_o" placeholder="Ej. Servicio prestado, Informes de gestión..."></textarea></td>
                            <td><textarea id="sipoc_c" placeholder="Ej. Estudiantes, Comunidad, Auditores..."></textarea></td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Panel Planear -->
            <div class="phva-panel" id="tabPlanear">
                <h4 style="color:#1e3a8a;">Planificación e Insumos Estratégicos (DOFA / MEFI / MEFE / Porter)</h4>
                <p style="font-size:0.88rem; color:#64748b;">Insumos estratégicos vinculados desde el análisis de la organización:</p>
                <textarea id="phva_planear" style="width:100%; height:120px; padding:10px; border:1px solid #cbd5e1; border-radius:8px;" placeholder="Ej. Fortalezas F1, F2 de la MEFI incorporadas al plan. Mitigación del Riesgo R1 de la matriz de riesgos..."></textarea>
            </div>

            <!-- Panel Hacer -->
            <div class="phva-panel" id="tabHacer">
                <h4 style="color:#1e3a8a;">Ejecución de Actividades (Módulo de Planificación)</h4>
                <p style="font-size:0.88rem; color:#64748b;">Actividades de operación ejecutadas dentro del período evaluado:</p>
                <textarea id="phva_hacer" style="width:100%; height:120px; padding:10px; border:1px solid #cbd5e1; border-radius:8px;" placeholder="Ej. Ejecución de talleres de capacitación docentes. Implementación de nueva plataforma digital..."></textarea>
            </div>

            <!-- Panel Verificar -->
            <div class="phva-panel" id="tabVerificar">
                <h4 style="color:#1e3a8a;">Verificación y Evidencias de Cumplimiento</h4>
                <p style="font-size:0.88rem; color:#64748b;">Adjunte notas de verificación, URLs de evidencias y soporte documental para auditoría:</p>
                <textarea id="phva_verificar" style="width:100%; height:100px; padding:10px; border:1px solid #cbd5e1; border-radius:8px; margin-bottom:10px;" placeholder="Ej. Evidencia 1: Acta de reunión No. 4 (https://drive.google.com/...). Evidencia 2: Reporte de indicadores Q2..."></textarea>
            </div>

            <!-- Panel Actuar -->
            <div class="phva-panel" id="tabActuar">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <h4 style="color:#1e3a8a; margin:0;">Evaluación del Auditor e IA (ISO 9001 Cláusula 10)</h4>
                    <button class="btn-action btn-ai" style="padding:6px 12px; font-size:0.8rem;" onclick="evalProcessAI()"><i class="fas fa-robot"></i> Evaluar Cumplimiento con IA</button>
                </div>
                <div id="aiActResults" style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:15px; font-size:0.9rem; min-height:100px;">
                    <em>Haga clic en "Evaluar Cumplimiento con IA" para que el Auditor Virtual analice la brecha PHVA y proponga Acciones de Mejora.</em>
                </div>
            </div>

            <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:20px; border-top:1px solid #e2e8f0; padding-top:15px;">
                <button class="btn-action btn-back" onclick="closeModal()">Cerrar</button>
                <button class="btn-action btn-save" onclick="saveProcessData()"><i class="fas fa-check"></i> Guardar Ficha de Proceso</button>
            </div>
        </div>
    </div>

    <!-- Print Container -->
    <div id="printSection"></div>

    <script src="{{ url_for('static', filename='app.js') }}"></script>
    <script>
        let sgcData = {
            policy: '',
            objectives: '',
            eval_date: '',
            processes: {
                "Gestión de la Dirección": { type: "Estratégico", leader: "Rectoría / Dirección", objective: "Liderar la estrategia organizacional", s: "", i: "", p: "", o: "", c: "", planear: "", hacer: "", verificar: "", actuar: "" },
                "Aseguramiento de Calidad y Riesgos": { type: "Estratégico", leader: "Comité de Calidad", objective: "Garantizar el cumplimiento normativo ISO 9001", s: "", i: "", p: "", o: "", c: "", planear: "", hacer: "", verificar: "", actuar: "" },
                "Gestión Académica y Docencia": { type: "Misional", leader: "Vicerrectoría Académica", objective: "Garantizar la calidad en la enseñanza y aprendizaje", s: "", i: "", p: "", o: "", c: "", planear: "", hacer: "", verificar: "", actuar: "" },
                "Investigación e Innovación": { type: "Misional", leader: "Dirección de Investigación", objective: "Fomentar la producción científica e innovación", s: "", i: "", p: "", o: "", c: "", planear: "", hacer: "", verificar: "", actuar: "" },
                "Proyección Social y Extensión": { type: "Misional", leader: "Dirección de Extensión", objective: "Gestionar el impacto y articulación con el entorno", s: "", i: "", p: "", o: "", c: "", planear: "", hacer: "", verificar: "", actuar: "" },
                "Gestión del Talento Humano": { type: "Apoyo", leader: "Dirección de Gestión Humana", objective: "Asegurar la competencia y bienestar del personal", s: "", i: "", p: "", o: "", c: "", planear: "", hacer: "", verificar: "", actuar: "" },
                "Tecnología y Sistemas (TI)": { type: "Apoyo", leader: "Dirección de Tecnología", objective: "Mantener la infraestructura tecnológica y datos", s: "", i: "", p: "", o: "", c: "", planear: "", hacer: "", verificar: "", actuar: "" },
                "Gestión Financiera": { type: "Apoyo", leader: "Dirección Administrativa y Financiera", objective: "Asegurar la sostenibilidad financiera", s: "", i: "", p: "", o: "", c: "", planear: "", hacer: "", verificar: "", actuar: "" }
            }
        };

        let currentActiveProcess = null;

        function logout() { localStorage.removeItem('siac_user'); window.top.location.href = 'login.html'; }

        document.addEventListener('DOMContentLoaded', async () => {
            await initHeader();
            await loadSGC();
            renderProcessMap();
        });

        async function initHeader() {
            try {
                const resp = await fetch(`/api/institution?inst_id=${getInstId()}`);
                if (resp.ok) {
                    const data = await resp.json();
                    document.getElementById('inst_name_display').textContent = data.name || 'INSTITUCIÓN EDUCATIVA';
                    if (data.logo_url) {
                        const img = document.getElementById('inst_logo_img');
                        img.src = data.logo_url; img.style.display = 'block';
                    }
                }
            } catch(e) { console.error(e); }
        }

        function renderProcessMap() {
            const gStrat = document.getElementById('gridEstrategicos');
            const gMis = document.getElementById('gridMisionales');
            const gApoyo = document.getElementById('gridApoyo');

            gStrat.innerHTML = ''; gMis.innerHTML = ''; gApoyo.innerHTML = '';

            for (const [pName, pData] of Object.entries(sgcData.processes)) {
                let cssClass = 'tier-misional';
                if (pData.type === 'Estratégico') cssClass = 'tier-strat';
                if (pData.type === 'Apoyo') cssClass = 'tier-apoyo';

                const boxHTML = `
                <div class="process-box ${cssClass}" onclick="openProcessModal('${pName}')">
                    <div class="process-name"><i class="fas fa-folder-open" style="color:#3b82f6; margin-right:5px;"></i> ${pName}</div>
                    <div class="process-meta"><i class="fas fa-user-tier"></i> ${pData.leader || 'Líder no asignado'}</div>
                </div>`;

                if (pData.type === 'Estratégico') gStrat.innerHTML += boxHTML;
                else if (pData.type === 'Apoyo') gApoyo.innerHTML += boxHTML;
                else gMis.innerHTML += boxHTML;
            }
        }

        function openProcessModal(pName) {
            currentActiveProcess = pName;
            const p = sgcData.processes[pName];

            document.getElementById('modalProcessTitle').textContent = pName;
            document.getElementById('modalProcessTier').textContent = `Proceso ${p.type}`;
            document.getElementById('proc_leader').value = p.leader || '';
            document.getElementById('proc_objective').value = p.objective || '';

            document.getElementById('sipoc_s').value = p.s || '';
            document.getElementById('sipoc_i').value = p.i || '';
            document.getElementById('sipoc_p').value = p.p || '';
            document.getElementById('sipoc_o').value = p.o || '';
            document.getElementById('sipoc_c').value = p.c || '';

            document.getElementById('phva_planear').value = p.planear || '';
            document.getElementById('phva_hacer').value = p.hacer || '';
            document.getElementById('phva_verificar').value = p.verificar || '';
            document.getElementById('aiActResults').innerHTML = p.actuar || '<em>Haga clic en "Evaluar Cumplimiento con IA" para que el Auditor Virtual analice la brecha PHVA y proponga Acciones de Mejora.</em>';

            switchPHVATab('tabSipoc');
            document.getElementById('processModal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('processModal').style.display = 'none';
        }

        function switchPHVATab(tabId) {
            document.querySelectorAll('.phva-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.phva-panel').forEach(p => p.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }

        function saveProcessData() {
            if (!currentActiveProcess) return;
            const p = sgcData.processes[currentActiveProcess];

            p.leader = document.getElementById('proc_leader').value.trim();
            p.objective = document.getElementById('proc_objective').value.trim();
            p.s = document.getElementById('sipoc_s').value.trim();
            p.i = document.getElementById('sipoc_i').value.trim();
            p.p = document.getElementById('sipoc_p').value.trim();
            p.o = document.getElementById('sipoc_o').value.trim();
            p.c = document.getElementById('sipoc_c').value.trim();
            p.planear = document.getElementById('phva_planear').value.trim();
            p.hacer = document.getElementById('phva_hacer').value.trim();
            p.verificar = document.getElementById('phva_verificar').value.trim();
            p.actuar = document.getElementById('aiActResults').innerHTML;

            renderProcessMap();
            closeModal();
            Swal.fire('¡Ficha Guardada!', `La caracterización del proceso "${currentActiveProcess}" fue actualizada.`, 'success');
        }

        async function loadSGC() {
            try {
                const res = await fetch(`/api/business/matrix/ISO9001?inst_id=${getInstId()}`);
                if (res.ok) {
                    const data = await res.json();
                    let dbData = data.data;
                    if (typeof dbData === 'string') { try { dbData = JSON.parse(dbData); } catch(e){} }

                    if (dbData) {
                        if (dbData.policy) document.getElementById('sgc_policy').value = dbData.policy;
                        if (dbData.objectives) document.getElementById('sgc_objectives').value = dbData.objectives;
                        if (dbData.eval_date) document.getElementById('eval_date').value = dbData.eval_date;
                        if (dbData.processes) sgcData.processes = { ...sgcData.processes, ...dbData.processes };
                    }
                }
            } catch(e) { console.error('Error loading SGC:', e); }
        }

        async function saveSGC() {
            sgcData.policy = document.getElementById('sgc_policy').value.trim();
            sgcData.objectives = document.getElementById('sgc_objectives').value.trim();
            sgcData.eval_date = document.getElementById('eval_date').value;

            try {
                const res = await fetch('/api/business/matrix/ISO9001', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        inst_id: getInstId(),
                        data: sgcData
                    })
                });
                if (res.ok) {
                    Swal.fire('¡Éxito!', 'Sistema de Gestión de Calidad ISO 9001 guardado correctamente.', 'success');
                } else {
                    Swal.fire('Error', 'No se pudo guardar la información.', 'error');
                }
            } catch(e) { Swal.fire('Error', 'Error de red al guardar.', 'error'); }
        }

        async function generatePolicyAI() {
            Swal.fire({ title: 'Generando Política de Calidad...', text: 'Analizando contexto estratégico...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
            try {
                const resp = await fetch('/api/business/iso9001_generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ inst_id: getInstId(), action_type: 'policy' })
                });
                const resData = await resp.json();
                Swal.close();

                if (resData.status === 'success' && resData.data) {
                    document.getElementById('sgc_policy').value = resData.data.politica || '';
                    document.getElementById('sgc_objectives').value = (resData.data.objetivos || []).join('\\n');
                    Swal.fire('¡Política Generada!', 'La Política y Objetivos de Calidad se redactaron con IA.', 'success');
                }
            } catch(e) { Swal.close(); Swal.fire('Error', 'No se pudo generar la política con IA.', 'error'); }
        }

        async function generateSGCAI() {
            await generatePolicyAI();
        }

        async function evalProcessAI() {
            if (!currentActiveProcess) return;
            Swal.fire({ title: 'Auditor Virtual Analizando PHVA...', text: 'Evaluando cumplimiento ISO 9001...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
            
            try {
                const resp = await fetch('/api/business/iso9001_generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        inst_id: getInstId(),
                        action_type: 'act',
                        process_name: currentActiveProcess,
                        process_data: sgcData.processes[currentActiveProcess]
                    })
                });
                const resData = await resp.json();
                Swal.close();

                if (resData.status === 'success' && resData.data) {
                    let html = `<p><strong>Evaluación de Auditoría:</strong> ${resData.data.evaluacion_auditor}</p>`;
                    html += `<h5 style="color:#1e3a8a; margin-top:10px;">Acciones de Mejora Recomendadas (Cláusula 10):</h5><ul>`;
                    (resData.data.acciones_mejora || []).forEach(a => {
                        html += `<li><strong>Acción:</strong> ${a.accion} <br><small><strong>Causa Raíz:</strong> ${a.causa_raiz} | <strong>Responsable:</strong> ${a.responsable}</small></li>`;
                    });
                    html += `</ul>`;
                    document.getElementById('aiActResults').innerHTML = html;
                    sgcData.processes[currentActiveProcess].actuar = html;
                }
            } catch(e) { Swal.close(); Swal.fire('Error', 'No se pudo evaluar con la IA.', 'error'); }
        }

        function exportPDF() {
            const logoImg = document.getElementById('inst_logo_img');
            const logoSrc = (logoImg && logoImg.style.display !== 'none' && logoImg.src) ? logoImg.src : '';
            const instName = document.getElementById('inst_name_display').textContent || 'INSTITUCIÓN EDUCATIVA';
            const evalDate = document.getElementById('eval_date').value || 'No especificada';
            const policy = document.getElementById('sgc_policy').value || 'Sin definir';
            const objectives = document.getElementById('sgc_objectives').value || 'Sin definir';

            let procRows = '';
            for (const [pName, pData] of Object.entries(sgcData.processes)) {
                procRows += `
                <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:12px; margin-bottom:15px;">
                    <h3 style="margin-top:0; color:#1e3a8a;">Proceso: ${pName} (${pData.type})</h3>
                    <p style="margin:4px 0;"><strong>Líder:</strong> ${pData.leader || '-'} | <strong>Objetivo:</strong> ${pData.objective || '-'}</p>
                    
                    <h4 style="margin:10px 0 4px; color:#334155;">Caracterización SIPOC</h4>
                    <p style="margin:2px 0; font-size:0.85rem;"><strong>Proveedores:</strong> ${pData.s || '-'} | <strong>Entradas:</strong> ${pData.i || '-'}</p>
                    <p style="margin:2px 0; font-size:0.85rem;"><strong>Actividades:</strong> ${pData.p || '-'}</p>
                    <p style="margin:2px 0; font-size:0.85rem;"><strong>Salidas:</strong> ${pData.o || '-'} | <strong>Clientes:</strong> ${pData.c || '-'}</p>

                    <h4 style="margin:10px 0 4px; color:#334155;">Ciclo PHVA</h4>
                    <p style="margin:2px 0; font-size:0.85rem;"><strong>Planear:</strong> ${pData.planear || '-'}</p>
                    <p style="margin:2px 0; font-size:0.85rem;"><strong>Hacer:</strong> ${pData.hacer || '-'}</p>
                    <p style="margin:2px 0; font-size:0.85rem;"><strong>Verificar (Evidencias):</strong> ${pData.verificar || '-'}</p>
                    <div style="margin-top:5px; padding:8px; background:white; border:1px solid #e2e8f0; border-radius:6px; font-size:0.85rem;">
                        <strong>Ajustar (Evaluación IA Auditora):</strong><br>
                        ${pData.actuar || 'Sin evaluación registrada.'}
                    </div>
                </div>`;
            }

            const printHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #2563eb; padding-bottom: 15px; margin-bottom: 20px;">
                <div>${logoSrc ? `<img src="${logoSrc}" style="max-height:55px; max-width:200px;">` : '<div style="font-weight:bold; font-size:1.3rem; color:#2563eb;">SIAC STRATEGIC</div>'}</div>
                <div style="font-size: 1.3rem; font-weight: bold; color: #1e3a8a; text-transform: uppercase;">${instName}</div>
            </div>

            <div style="text-align: center; font-size: 1.5rem; color: #0f172a; font-weight: bold;">INFORME AUDITORÍA ALINEACIÓN ISO 9001:2015</div>
            <div style="text-align: center; font-size: 0.95rem; color: #64748b; margin-bottom: 25px;">📅 Fecha de Evaluación de Auditoría: <strong>${evalDate}</strong></div>

            <div style="background:#eff6ff; padding:15px; border-radius:8px; border-left:4px solid #2563eb; margin-bottom:20px;">
                <h3 style="margin-top:0; color:#1e3a8a;">Política de Calidad Institucional</h3>
                <p style="margin:0; font-size:0.95rem;">${policy}</p>
                <h4 style="margin-top:10px; margin-bottom:5px; color:#1e3a8a;">Objetivos de Calidad</h4>
                <pre style="margin:0; font-family:inherit; font-size:0.9rem; white-space:pre-wrap;">${objectives}</pre>
            </div>

            <h2 style="color:#1e3a8a; border-bottom:1px solid #cbd5e1; padding-bottom:5px;">Fichas de Caracterización y PHVA por Proceso</h2>
            ${procRows}
            `;

            document.getElementById('printSection').innerHTML = printHTML;
            window.print();
        }
    </script>
</body>
</html>
"""

with open(r'c:\SIAC\templates\empresa_iso.html', 'w', encoding='utf-8') as f:
    f.write(file_content)

print("empresa_iso.html built with complete Auditor-Ready SGC ISO 9001 System!")
