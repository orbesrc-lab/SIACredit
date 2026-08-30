import sys, os, json
sys.path.insert(0, os.path.abspath('.'))
from scratch.build_iso_checklist import CHECKLIST_DEFAULT

checklist_json = json.dumps(CHECKLIST_DEFAULT, ensure_ascii=False)

with open('templates/empresa_iso.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the unclosed comment at line 1190
text = text.replace('/* ============================================================\n   AI\nasync function generateSGCAI()', '/* ============================================================\n   AI\n   ============================================================ */\nasync function generateSGCAI()')
text = text.replace('/* ============================================================\r\n   AI\r\nasync function generateSGCAI()', '/* ============================================================\r\n   AI\r\n   ============================================================ */\r\nasync function generateSGCAI()')

# 1. Update CSS
css_needle = '.iso-map-wrapper{display:flex;gap:15px;align-items:stretch;margin-top:15px;}'
css_add = '''
        /* Top Navigation Tabs for ISO Modules */
        .iso-nav-tabs{display:flex;gap:8px;margin-bottom:20px;border-bottom:2px solid #e2e8f0;padding-bottom:2px;overflow-x:auto;flex-wrap:nowrap;}
        .iso-nav-tab{padding:12px 20px;border:none;background:#f8fafc;color:#64748b;font-weight:700;font-size:.9rem;cursor:pointer;border-radius:10px 10px 0 0;display:flex;align-items:center;gap:8px;transition:all .2s;white-space:nowrap;border:1px solid #e2e8f0;border-bottom:none;}
        .iso-nav-tab:hover{background:#f1f5f9;color:#1e293b;}
        .iso-nav-tab.active{background:#1e3a8a;color:white;border-color:#1e3a8a;}
        .iso-view-panel{display:none;animation:fadeIn .25s ease-in-out;}
        .iso-view-panel.active{display:block;}
        @keyframes fadeIn{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:translateY(0);}}

        /* Table and badges */
        .sgc-table{width:100%;border-collapse:collapse;margin-top:10px;font-size:.85rem;}
        .sgc-table th{background:#1e293b;color:white;padding:9px 12px;text-align:left;font-size:.83rem;}
        .sgc-table td{padding:9px 12px;border-bottom:1px solid #e2e8f0;vertical-align:middle;}
        .sgc-table tr:hover{background:#f8fafc;}
        .badge-nc-mayor{background:#fee2e2;color:#991b1b;padding:3px 9px;border-radius:12px;font-weight:bold;font-size:.76rem;border:1px solid #fca5a5;}
        .badge-nc-menor{background:#fef3c7;color:#92400e;padding:3px 9px;border-radius:12px;font-weight:bold;font-size:.76rem;border:1px solid #fde68a;}
        .badge-nc-cerrada{background:#dcfce7;color:#166534;padding:3px 9px;border-radius:12px;font-weight:bold;font-size:.76rem;border:1px solid #86efac;}
        .badge-nc-progreso{background:#e0f2fe;color:#075985;padding:3px 9px;border-radius:12px;font-weight:bold;font-size:.76rem;border:1px solid #7dd3fc;}
        .badge-nc-verificada{background:#f3e8ff;color:#6b21a8;padding:3px 9px;border-radius:12px;font-weight:bold;font-size:.76rem;border:1px solid #d8b4fe;}
        .badge-nc-abierta{background:#ffe4e6;color:#9f1239;padding:3px 9px;border-radius:12px;font-weight:bold;font-size:.76rem;border:1px solid #fda4af;}
        
        .risk-critico{background:#fee2e2;color:#991b1b;font-weight:bold;padding:3px 8px;border-radius:6px;border:1px solid #fca5a5;}
        .risk-alto{background:#ffedd5;color:#9a3412;font-weight:bold;padding:3px 8px;border-radius:6px;border:1px solid #fdba74;}
        .risk-medio{background:#fef9c3;color:#854d0e;font-weight:bold;padding:3px 8px;border-radius:6px;border:1px solid #fde047;}
        .risk-bajo{background:#dcfce7;color:#166534;font-weight:bold;padding:3px 8px;border-radius:6px;border:1px solid #86efac;}
        
        .chk-card{background:white;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:12px;transition:all .2s;}
        .chk-card:hover{border-color:#3b82f6;box-shadow:0 4px 10px rgba(0,0,0,.04);}
        .chk-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}
        .chk-clausula{font-size:.75rem;font-weight:bold;color:#2563eb;background:#eff6ff;padding:2px 8px;border-radius:6px;}
        .chk-select{padding:4px 8px;border-radius:6px;font-size:.82rem;font-weight:bold;}
        .chk-cumple{background:#dcfce7;color:#166534;border:1px solid #86efac;}
        .chk-progreso{background:#fef3c7;color:#92400e;border:1px solid #fde68a;}
        .chk-nocumple{background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;}
'''

if css_needle in text:
    text = text.replace(css_needle, css_add + '\n        ' + css_needle)

# 2. Insert Nav Bar & Wrap Panels
nav_bar_needle = '<div style="background:white;padding:15px;border-radius:10px;margin-bottom:20px;box-shadow:0 2px 4px rgba(0,0,0,.05);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:15px;">'

nav_tabs_html = '''<div class="iso-nav-tabs">
                <button class="iso-nav-tab active" id="tab-nav-mapa" onclick="switchMainTab('view-mapa', this)"><i class="fas fa-sitemap"></i> 1. Mapa de Procesos & SIPOC</button>
                <button class="iso-nav-tab" id="tab-nav-auditorias" onclick="switchMainTab('view-auditorias', this)"><i class="fas fa-clipboard-list"></i> 2. Auditorías & Visitas (Cláusula 9.3)</button>
                <button class="iso-nav-tab" id="tab-nav-nc" onclick="switchMainTab('view-nc', this)"><i class="fas fa-exclamation-triangle"></i> 3. No Conformidades & Incidencias (Cláusula 10.2)</button>
                <button class="iso-nav-tab" id="tab-nav-riesgos" onclick="switchMainTab('view-riesgos', this)"><i class="fas fa-shield-alt"></i> 4. Matriz de Riesgos (Cláusula 6.1)</button>
                <button class="iso-nav-tab" id="tab-nav-indicadores" onclick="switchMainTab('view-indicadores', this)"><i class="fas fa-chart-line"></i> 5. Banco de Indicadores (Cláusula 9.1)</button>
                <button class="iso-nav-tab" id="tab-nav-checklist" onclick="switchMainTab('view-checklist', this)"><i class="fas fa-tasks"></i> 6. Checklist de Auditoría Oficial</button>
            </div>'''

pos_top = text.find(nav_bar_needle)
if pos_top != -1:
    text = text[:pos_top] + nav_tabs_html + '\n\n            <div id="view-mapa" class="iso-view-panel active">\n' + text[pos_top:]

# Close view-mapa after banco-section and add extra views
banco_end_needle = '<div id="banco_grid" class="banco-grid">\n                    <div class="banco-empty"><i class="fas fa-chart-bar"></i><p>No hay indicadores registrados aun.</p><small>Abra un proceso del Mapa y agregue indicadores.</small></div>\n                </div>\n            </div>\n        </div>\n    </main>'
banco_end_alt = '<div id="banco_grid" class="banco-grid">'

extra_views_html = '''</div>
            </div>
            <!-- CIERRE PANEL 1 MAPA -->
            </div>

            <!-- PANEL 2: AUDITORÍAS -->
            <div id="view-auditorias" class="iso-view-panel">
                <div class="sgc-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #e2e8f0;padding-bottom:12px;margin-bottom:16px;">
                        <div>
                            <h3 style="margin:0;color:#1e3a8a;font-size:1.15rem;"><i class="fas fa-calendar-check" style="color:#2563eb;"></i> Programa & Registro de Visitas de Auditoría <small style="font-weight:normal;color:#64748b;">(ISO 9001:2015 Cláusula 9.3)</small></h3>
                            <p style="margin:4px 0 0;color:#64748b;font-size:.84rem;">Registro histórico de auditorías internas, de certificación y seguimiento con trazabilidad de hallazgos.</p>
                        </div>
                        <button class="btn-action" style="background:#2563eb;" onclick="openAddAuditoriaModal()"><i class="fas fa-plus-circle"></i> Nueva Auditoría / Visita</button>
                    </div>
                    <div class="banco-stats" style="grid-template-columns:repeat(3,1fr);margin-bottom:16px;">
                        <div class="banco-stat-card stat-total"><div class="banco-stat-num" id="stat_total_auditorias">0</div><div class="banco-stat-label">Total Auditorías Registradas</div></div>
                        <div class="banco-stat-card stat-amarillo"><div class="banco-stat-num" id="stat_auditorias_programadas">0</div><div class="banco-stat-label">📅 Programadas / En Ejecución</div></div>
                        <div class="banco-stat-card stat-verde"><div class="banco-stat-num" id="stat_auditorias_ejecutadas">0</div><div class="banco-stat-label">✅ Completadas / Cerradas</div></div>
                    </div>
                    <div style="overflow-x:auto;">
                        <table class="sgc-table">
                            <thead><tr><th>Código</th><th>Título de Auditoría</th><th>Tipo</th><th>Fechas</th><th>Auditor Líder</th><th>Alcance</th><th>Hallazgos</th><th>Estado</th><th>Acciones</th></tr></thead>
                            <tbody id="tbody_auditorias"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- PANEL 3: NO CONFORMIDADES -->
            <div id="view-nc" class="iso-view-panel">
                <div class="sgc-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #e2e8f0;padding-bottom:12px;margin-bottom:16px;">
                        <div>
                            <h3 style="margin:0;color:#1e3a8a;font-size:1.15rem;"><i class="fas fa-exclamation-triangle" style="color:#ef4444;"></i> Matriz de No Conformidades, Causa Raíz & ACC <small style="font-weight:normal;color:#64748b;">(ISO 9001:2015 Cláusula 10.2)</small></h3>
                            <p style="margin:4px 0 0;color:#64748b;font-size:.84rem;">Gestión integral de incidencias: análisis de causas (5 Porqués / Ishikawa), planes correctivos y verificación de eficacia.</p>
                        </div>
                        <button class="btn-action" style="background:#ef4444;" onclick="openAddNCModal()"><i class="fas fa-plus-circle"></i> Registrar No Conformidad</button>
                    </div>
                    <div class="banco-stats" style="grid-template-columns:repeat(4,1fr);margin-bottom:16px;">
                        <div class="banco-stat-card stat-rojo"><div class="banco-stat-num" id="stat_nc_abiertas">0</div><div class="banco-stat-label">🔴 NCs Abiertas</div></div>
                        <div class="banco-stat-card stat-amarillo"><div class="banco-stat-num" id="stat_nc_progreso">0</div><div class="banco-stat-label">🔵 En Progreso (Plan ACC)</div></div>
                        <div class="banco-stat-card" style="background:#faf5ff;border-color:#d8b4fe;"><div class="banco-stat-num" id="stat_nc_verificadas" style="color:#7e22ce;">0</div><div class="banco-stat-label" style="color:#6b21a8;">🟣 Eficacia Verificada</div></div>
                        <div class="banco-stat-card stat-verde"><div class="banco-stat-num" id="stat_nc_cerradas">0</div><div class="banco-stat-label">🟢 NCs Cerradas</div></div>
                    </div>
                    <div class="filter-bar" style="margin-bottom:14px;">
                        <span style="font-weight:600;font-size:.83rem;color:#334155;"><i class="fas fa-filter"></i> Filtrar NCs:</span>
                        <select id="filter_nc_proceso" class="filter-select" onchange="renderNCTable()"><option value="">Todos los Procesos</option></select>
                        <select id="filter_nc_clasificacion" class="filter-select" onchange="renderNCTable()"><option value="">Todas las Clasificaciones</option><option value="Menor">Menor</option><option value="Mayor">Mayor</option></select>
                        <select id="filter_nc_estado" class="filter-select" onchange="renderNCTable()"><option value="">Todos los Estados</option><option value="Abierta">🔴 Abierta</option><option value="En progreso">🔵 En progreso</option><option value="Verificada">🟣 Verificada</option><option value="Cerrada">🟢 Cerrada</option></select>
                    </div>
                    <div style="overflow-x:auto;">
                        <table class="sgc-table">
                            <thead><tr><th>ID</th><th>Fecha</th><th>Proceso</th><th>Clasif.</th><th>Cláusula</th><th>Descripción</th><th>Causa Raíz</th><th>Plan ACC</th><th>Responsable</th><th>Plazo</th><th>Estado</th><th>Acciones</th></tr></thead>
                            <tbody id="tbody_nc"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- PANEL 4: MATRIZ DE RIESGOS -->
            <div id="view-riesgos" class="iso-view-panel">
                <div class="sgc-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #e2e8f0;padding-bottom:12px;margin-bottom:16px;">
                        <div>
                            <h3 style="margin:0;color:#1e3a8a;font-size:1.15rem;"><i class="fas fa-shield-alt" style="color:#059669;"></i> Matriz de Riesgos y Oportunidades del SGC <small style="font-weight:normal;color:#64748b;">(ISO 9001:2015 Cláusula 6.1)</small></h3>
                            <p style="margin:4px 0 0;color:#64748b;font-size:.84rem;">Evaluación de Probabilidad x Impacto (1 a 25), mapas de calor y planes de mitigación y contingencia.</p>
                        </div>
                        <button class="btn-action" style="background:#059669;" onclick="openAddRiesgoModal()"><i class="fas fa-plus-circle"></i> Nuevo Riesgo / Oportunidad</button>
                    </div>
                    <div class="banco-stats" style="grid-template-columns:repeat(4,1fr);margin-bottom:16px;">
                        <div class="banco-stat-card stat-rojo"><div class="banco-stat-num" id="stat_risk_criticos">0</div><div class="banco-stat-label">🔴 Riesgos Críticos (>15)</div></div>
                        <div class="banco-stat-card stat-amarillo"><div class="banco-stat-num" id="stat_risk_altos">0</div><div class="banco-stat-label">🟠 Riesgos Altos (10-15)</div></div>
                        <div class="banco-stat-card stat-verde"><div class="banco-stat-num" id="stat_risk_bajos">0</div><div class="banco-stat-label">🟢 Riesgos Bajos/Medios (&lt;10)</div></div>
                        <div class="banco-stat-card" style="background:#eff6ff;border-color:#93c5fd;"><div class="banco-stat-num" id="stat_oportunidades" style="color:#1d4ed8;">0</div><div class="banco-stat-label" style="color:#1e40af;">🌟 Oportunidades</div></div>
                    </div>
                    <div class="filter-bar" style="margin-bottom:14px;">
                        <span style="font-weight:600;font-size:.83rem;color:#334155;"><i class="fas fa-filter"></i> Filtrar Riesgos:</span>
                        <select id="filter_risk_proceso" class="filter-select" onchange="renderRiesgosTable()"><option value="">Todos los Procesos</option></select>
                        <select id="filter_risk_cat" class="filter-select" onchange="renderRiesgosTable()"><option value="">Categoría</option><option value="Riesgo">⚠️ Riesgos</option><option value="Oportunidad">🌟 Oportunidades</option></select>
                        <select id="filter_risk_nivel" class="filter-select" onchange="renderRiesgosTable()"><option value="">Nivel de Severidad</option><option value="Crítico">🔴 Crítico</option><option value="Alto">🟠 Alto</option><option value="Medio">🟡 Medio</option><option value="Bajo">🟢 Bajo</option></select>
                    </div>
                    <div style="overflow-x:auto;">
                        <table class="sgc-table">
                            <thead><tr><th>#</th><th>Categoría</th><th>Proceso</th><th>Descripción</th><th>Prob (1-5)</th><th>Imp (1-5)</th><th>Nivel PxI</th><th>Mitigación / Acción</th><th>Responsable</th><th>Plazo</th><th>Estado</th><th>Acciones</th></tr></thead>
                            <tbody id="tbody_riesgos"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- PANEL 5: BANCO DE INDICADORES DIRECTO -->
            <div id="view-indicadores" class="iso-view-panel">
                <div class="sgc-card">
                    <div class="banco-section-header">
                        <div>
                            <h3 style="margin:0;color:#1e3a8a;font-size:1.15rem;"><i class="fas fa-chart-bar" style="color:#7c3aed;"></i> Banco Central de Indicadores del SGC <small style="font-weight:normal;color:#64748b;">(Cláusula 9.1)</small></h3>
                            <p style="margin:4px 0 0;color:#64748b;font-size:.83rem;">Seguimiento integral, histórico de mediciones y gráficos de tendencia.</p>
                        </div>
                        <div style="display:flex;gap:8px;">
                            <button class="btn-action" style="background:#0f172a;padding:7px 14px;font-size:.82rem;" onclick="renderBancoIndicadores()"><i class="fas fa-sync-alt"></i> Actualizar</button>
                            <button class="btn-action" style="background:#2563eb;padding:7px 14px;font-size:.82rem;" onclick="exportBancoIndicadoresPDF()"><i class="fas fa-print"></i> Imprimir Banco</button>
                        </div>
                    </div>
                    <div id="banco_panel_container">
                        <!-- Synced with Banco section -->
                    </div>
                </div>
            </div>

            <!-- PANEL 6: CHECKLIST DE AUDITORÍA OFICIAL -->
            <div id="view-checklist" class="iso-view-panel">
                <div class="sgc-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #e2e8f0;padding-bottom:12px;margin-bottom:16px;">
                        <div>
                            <h3 style="margin:0;color:#1e3a8a;font-size:1.15rem;"><i class="fas fa-tasks" style="color:#2563eb;"></i> Checklist Oficial de Auditoría SGC ISO 9001:2015 <small style="font-weight:normal;color:#64748b;">(Cláusulas 4 a 10)</small></h3>
                            <p style="margin:4px 0 0;color:#64748b;font-size:.84rem;">Lista de verificación normativa con registro de evidencias objetivas y criterios de auditoría.</p>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:1.4rem;font-weight:800;color:#16a34a;" id="checklist_score">100%</div>
                            <div style="font-size:.75rem;color:#64748b;font-weight:bold;">Conformidad Normativa Global</div>
                        </div>
                    </div>

                    <div id="checklist_container"></div>
                </div>
            </div>
        </div>
    </main>'''

pos_banco = text.find('<div class="sgc-card" id="banco-section">')
if pos_banco != -1:
    pos_main_end = text.find('</main>', pos_banco)
    text = text[:pos_main_end] + extra_views_html + text[pos_main_end+7:]

# 3. Add "⚠️ Incidencias & Auditoría" tab to Process Modal
modal_tab_needle = '<button class="phva-tab" id="tab-btn-actuar" onclick="switchPHVATab(\'tabActuar\',this)">🤖 A — Actuar (IA)</button>'
modal_tab_add = '<button class="phva-tab" id="tab-btn-actuar" onclick="switchPHVATab(\'tabActuar\',this)">🤖 A — Actuar (IA)</button>\n            <button class="phva-tab" id="tab-btn-proc-nc" onclick="switchPHVATab(\'tabProcNC\',this)" style="color:#ef4444;font-weight:bold;">⚠️ Incidencias & Auditoría</button>'
text = text.replace(modal_tab_needle, modal_tab_add)

modal_panel_needle = '<!-- ACTUAR -->'
modal_nc_panel = '''<!-- PESTAÑA INCIDENCIAS Y AUDITORÍA POR PROCESO -->
        <div class="phva-panel" id="tabProcNC">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <div>
                    <h4 style="color:#1e3a8a;margin:0;"><i class="fas fa-history" style="color:#ef4444;"></i> Histórico de No Conformidades e Incidencias del Proceso</h4>
                    <p style="margin:4px 0 0;font-size:.82rem;color:#64748b;">Hallazgos detectados en auditorías previas asociados directamente a este proceso.</p>
                </div>
                <button class="btn-action" style="background:#ef4444;padding:6px 12px;font-size:.78rem;" onclick="openAddNCModal(currentActiveProcess)"><i class="fas fa-plus"></i> Reportar Hallazgo en este Proceso</button>
            </div>
            <div id="proc_nc_container" style="margin-top:10px;"></div>
        </div>
        <!-- ACTUAR -->'''
text = text.replace(modal_panel_needle, modal_nc_panel)

# 4. Add JS Functions for Tabs, Audits, NCs, Risks, Checklist
js_add = f'''
const DEFAULT_CHECKLIST = {checklist_json};

function switchMainTab(panelId, btnEl){{
    document.querySelectorAll('.iso-nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.iso-view-panel').forEach(p => p.classList.remove('active'));
    if(btnEl) btnEl.classList.add('active');
    const target = document.getElementById(panelId);
    if(target) target.classList.add('active');

    if(panelId === 'view-mapa') renderProcessMap();
    else if(panelId === 'view-auditorias') renderAuditoriasTable();
    else if(panelId === 'view-nc') renderNCTable();
    else if(panelId === 'view-riesgos') renderRiesgosTable();
    else if(panelId === 'view-indicadores') renderBancoIndicadores();
    else if(panelId === 'view-checklist') renderChecklist();
}}

/* ============================================================
   MÓDULO 2: AUDITORÍAS & VISITAS PERIÓDICAS (CLÁUSULA 9.3)
   ============================================================ */
function renderAuditoriasTable(){{
    const tbody = document.getElementById('tbody_auditorias');
    if(!tbody) return;
    const auds = sgcData.auditorias || [];
    
    let total = auds.length, prog = 0, comp = 0;
    auds.forEach(a => {{
        if(a.estado === 'Cerrada' || a.estado === 'Completada') comp++;
        else prog++;
    }});
    const stTot = document.getElementById('stat_total_auditorias'); if(stTot) stTot.textContent = total;
    const stProg = document.getElementById('stat_auditorias_programadas'); if(stProg) stProg.textContent = prog;
    const stEj = document.getElementById('stat_auditorias_ejecutadas'); if(stEj) stEj.textContent = comp;

    if(!auds.length){{
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;padding:30px;color:#94a3b8;"><i class="fas fa-calendar-times" style="font-size:2rem;margin-bottom:8px;display:block;"></i>No hay auditorías registradas en el programa.<br><small>Haga clic en "+ Nueva Auditoría / Visita" para agendar una.</small></td></tr>';
        return;
    }}

    let h = '';
    auds.forEach((a, idx) => {{
        const ncCount = (sgcData.no_conformidades||[]).filter(n => n.auditoria_id === a.id || n.auditoria_id === a.codigo).length;
        const ncBadge = ncCount > 0 ? `<span class="badge-nc-mayor">${{ncCount}} Hallazgos</span>` : '<span class="badge-nc-cerrada">0 Hallazgos</span>';
        const stBadge = a.estado === 'Completada' || a.estado === 'Cerrada' ? '<span class="badge-nc-cerrada">✅ Completada</span>' : a.estado === 'En Ejecución' ? '<span class="badge-nc-progreso">⚙️ En Ejecución</span>' : '<span class="badge-nc-menor">📅 Programada</span>';
        
        h += `<tr>
            <td><strong>${{a.codigo||('AUD-00'+(idx+1))}}</strong></td>
            <td><strong>${{a.titulo}}</strong></td>
            <td><span style="font-size:.78rem;background:#f1f5f9;padding:3px 7px;border-radius:6px;color:#334155;">${{a.tipo||'Interna'}}</span></td>
            <td><small>${{a.fecha_inicio||'—'}} a ${{a.fecha_fin||'—'}}</small></td>
            <td><i class="fas fa-user-tie" style="color:#2563eb;"></i> ${{a.auditor_lider||'Por definir'}}</td>
            <td style="max-width:180px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${{a.alcance||''}}">${{a.alcance||'SGC Completo'}}</td>
            <td>${{ncBadge}}</td>
            <td>${{stBadge}}</td>
            <td>
                <div style="display:flex;gap:4px;">
                    <button class="btn-action" style="background:#64748b;padding:3px 7px;font-size:.74rem;" onclick="openEditAuditoriaModal(${{idx}})" title="Editar"><i class="fas fa-edit"></i></button>
                    <button class="btn-action" style="background:#ef4444;padding:3px 7px;font-size:.74rem;" onclick="deleteAuditoria(${{idx}})" title="Eliminar"><i class="fas fa-trash-alt"></i></button>
                </div>
            </td>
        </tr>`;
    }});
    tbody.innerHTML = h;
}}

function openAddAuditoriaModal(){{
    Swal.fire({{
        title: 'Programar Visita de Auditoría',
        width: '650px',
        html: `<div style="text-align:left;font-size:.86rem;">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Código de Auditoría *</label><input id="sw_aud_cod" class="swal2-input" value="AUD-${{new Date().getFullYear()}}-0${{(sgcData.auditorias||[]).length+1}}" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                <div><label style="font-weight:bold;">Tipo de Auditoría</label><select id="sw_aud_tipo" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="Interna (1ra Parte)">Interna (1ra Parte)</option><option value="Proveedor (2da Parte)">Proveedor (2da Parte)</option><option value="Certificación (3ra Parte)">Certificación (3ra Parte)</option><option value="Seguimiento / Ente de Control">Seguimiento / Ente de Control</option></select></div>
            </div>
            <div style="margin-bottom:10px;"><label style="font-weight:bold;">Título / Objetivo de la Auditoría *</label><input id="sw_aud_tit" class="swal2-input" placeholder="Ej. Auditoría Periódica Integral SGC 2026" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Fecha Inicio</label><input id="sw_aud_fini" type="date" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                <div><label style="font-weight:bold;">Fecha Fin</label><input id="sw_aud_ffin" type="date" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Auditor Líder</label>${{buildUserSelect('sw_aud_lider', '', 'Seleccionar auditor líder...')}}</div>
                <div><label style="font-weight:bold;">Estado</label><select id="sw_aud_est" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="Programada">Programada</option><option value="En Ejecución">En Ejecución</option><option value="Completada">Completada</option></select></div>
            </div>
            <div style="margin-bottom:10px;"><label style="font-weight:bold;">Alcance y Criterios (Procesos / Cláusulas)</label><textarea id="sw_aud_alcance" class="swal2-input" style="width:100%;height:55px;margin-top:4px;box-sizing:border-box;" placeholder="Ej. Procesos Misionales y Estratégicos, Cláusulas 4 a 10 ISO 9001:2015"></textarea></div>
        </div>`,
        showCancelButton: true, confirmButtonText: 'Guardar Auditoría', cancelButtonText: 'Cancelar',
        preConfirm: () => {{
            const cod = document.getElementById('sw_aud_cod').value.trim();
            const tit = document.getElementById('sw_aud_tit').value.trim();
            if(!cod || !tit){{ Swal.showValidationMessage('Código y Título son obligatorios.'); return false; }}
            return {{
                id: generateId(),
                codigo: cod,
                titulo: tit,
                tipo: document.getElementById('sw_aud_tipo').value,
                fecha_inicio: document.getElementById('sw_aud_fini').value,
                fecha_fin: document.getElementById('sw_aud_ffin').value,
                auditor_lider: document.getElementById('sw_aud_lider').value || 'Por asignar',
                estado: document.getElementById('sw_aud_est').value,
                alcance: document.getElementById('sw_aud_alcance').value.trim()
            }};
        }}
    }}).then(async r => {{
        if(!r.isConfirmed) return;
        if(!sgcData.auditorias) sgcData.auditorias = [];
        sgcData.auditorias.push(r.value);
        renderAuditoriasTable();
        await saveSGCData(sgcData);
    }});
}}

function openEditAuditoriaModal(idx){{
    const a = sgcData.auditorias[idx];
    if(!a) return;
    Swal.fire({{
        title: `Editar Auditoría: ${{a.codigo}}`,
        width: '650px',
        html: `<div style="text-align:left;font-size:.86rem;">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Código</label><input id="sw_aud_cod" class="swal2-input" value="${{a.codigo||''}}" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                <div><label style="font-weight:bold;">Tipo</label><select id="sw_aud_tipo" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="Interna (1ra Parte)" ${{a.tipo==='Interna (1ra Parte)'?'selected':''}}>Interna (1ra Parte)</option><option value="Proveedor (2da Parte)" ${{a.tipo==='Proveedor (2da Parte)'?'selected':''}}>Proveedor (2da Parte)</option><option value="Certificación (3ra Parte)" ${{a.tipo==='Certificación (3ra Parte)'?'selected':''}}>Certificación (3ra Parte)</option><option value="Seguimiento / Ente de Control" ${{a.tipo==='Seguimiento / Ente de Control'?'selected':''}}>Seguimiento / Ente de Control</option></select></div>
            </div>
            <div style="margin-bottom:10px;"><label style="font-weight:bold;">Título</label><input id="sw_aud_tit" class="swal2-input" value="${{a.titulo||''}}" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Fecha Inicio</label><input id="sw_aud_fini" type="date" class="swal2-input" value="${{a.fecha_inicio||''}}" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                <div><label style="font-weight:bold;">Fecha Fin</label><input id="sw_aud_ffin" type="date" class="swal2-input" value="${{a.fecha_fin||''}}" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Auditor Líder</label>${{buildUserSelect('sw_aud_lider', a.auditor_lider, 'Seleccionar auditor líder...')}}</div>
                <div><label style="font-weight:bold;">Estado</label><select id="sw_aud_est" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="Programada" ${{a.estado==='Programada'?'selected':''}}>Programada</option><option value="En Ejecución" ${{a.estado==='En Ejecución'?'selected':''}}>En Ejecución</option><option value="Completada" ${{a.estado==='Completada'?'selected':''}}>Completada</option></select></div>
            </div>
            <div style="margin-bottom:10px;"><label style="font-weight:bold;">Alcance y Criterios</label><textarea id="sw_aud_alcance" class="swal2-input" style="width:100%;height:55px;margin-top:4px;box-sizing:border-box;">${{a.alcance||''}}</textarea></div>
        </div>`,
        showCancelButton: true, confirmButtonText: 'Actualizar', cancelButtonText: 'Cancelar',
        preConfirm: () => {{
            return {{
                ...a,
                codigo: document.getElementById('sw_aud_cod').value.trim(),
                titulo: document.getElementById('sw_aud_tit').value.trim(),
                tipo: document.getElementById('sw_aud_tipo').value,
                fecha_inicio: document.getElementById('sw_aud_fini').value,
                fecha_fin: document.getElementById('sw_aud_ffin').value,
                auditor_lider: document.getElementById('sw_aud_lider').value,
                estado: document.getElementById('sw_aud_est').value,
                alcance: document.getElementById('sw_aud_alcance').value.trim()
            }};
        }}
    }}).then(async res => {{
        if(!res.isConfirmed) return;
        sgcData.auditorias[idx] = res.value;
        renderAuditoriasTable();
        await saveSGCData(sgcData);
    }});
}}

function deleteAuditoria(idx){{
    Swal.fire({{
        title: '¿Eliminar Auditoría?',
        text: 'Se eliminará del programa de auditorías.',
        icon: 'warning', showCancelButton: true, confirmButtonText: 'Sí, eliminar', cancelButtonText: 'Cancelar', confirmButtonColor: '#ef4444'
    }}).then(async r => {{
        if(!r.isConfirmed) return;
        sgcData.auditorias.splice(idx, 1);
        renderAuditoriasTable();
        await saveSGCData(sgcData);
    }});
}}

/* ============================================================
   MÓDULO 3: MATRIZ DE NO CONFORMIDADES & INCIDENCIAS (CLÁUSULA 10.2)
   ============================================================ */
function renderNCTable(){{
    const tbody = document.getElementById('tbody_nc');
    if(!tbody) return;
    populateNCFilters();

    const fp = document.getElementById('filter_nc_proceso')?.value || '';
    const fc = document.getElementById('filter_nc_clasificacion')?.value || '';
    const fe = document.getElementById('filter_nc_estado')?.value || '';

    const ncs = sgcData.no_conformidades || [];
    let ab = 0, pr = 0, vf = 0, cr = 0;
    ncs.forEach(n => {{
        if(n.estado === 'Cerrada') cr++;
        else if(n.estado === 'Verificada') vf++;
        else if(n.estado === 'En progreso') pr++;
        else ab++;
    }});

    const elAb = document.getElementById('stat_nc_abiertas'); if(elAb) elAb.textContent = ab;
    const elPr = document.getElementById('stat_nc_progreso'); if(elPr) elPr.textContent = pr;
    const elVf = document.getElementById('stat_nc_verificadas'); if(elVf) elVf.textContent = vf;
    const elCr = document.getElementById('stat_nc_cerradas'); if(elCr) elCr.textContent = cr;

    let fil = ncs;
    if(fp) fil = fil.filter(n => n.proceso === fp);
    if(fc) fil = fil.filter(n => n.clasificacion === fc);
    if(fe) fil = fil.filter(n => n.estado === fe);

    if(!fil.length){{
        tbody.innerHTML = '<tr><td colspan="12" style="text-align:center;padding:30px;color:#94a3b8;"><i class="fas fa-check-circle" style="font-size:2rem;color:#10b981;margin-bottom:8px;display:block;"></i>No hay no conformidades registradas con los filtros seleccionados.</td></tr>';
        return;
    }}

    let h = '';
    fil.forEach((n, idx) => {{
        const clsBadge = n.clasificacion === 'Mayor' ? '<span class="badge-nc-mayor">🔴 Mayor</span>' : '<span class="badge-nc-menor">🟡 Menor</span>';
        const stBadge = n.estado === 'Cerrada' ? '<span class="badge-nc-cerrada">🟢 Cerrada</span>' : n.estado === 'Verificada' ? '<span class="badge-nc-verificada">🟣 Verificada</span>' : n.estado === 'En progreso' ? '<span class="badge-nc-progreso">🔵 En Progreso</span>' : '<span class="badge-nc-abierta">🔴 Abierta</span>';
        
        h += `<tr>
            <td><strong>${{n.codigo||('NC-00'+(idx+1))}}</strong></td>
            <td><small>${{n.fecha||'—'}}</small></td>
            <td><strong>${{n.proceso}}</strong></td>
            <td>${{clsBadge}}</td>
            <td><small style="font-weight:bold;color:#2563eb;">Cl. ${{n.clausula||'10.2'}}</small></td>
            <td style="max-width:180px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${{n.descripcion||''}}">${{n.descripcion||'—'}}</td>
            <td style="max-width:140px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${{n.causa_raiz||''}}"><small>${{n.metodo_causa?`[${{n.metodo_causa}}] `:''}}${{n.causa_raiz||'Pendiente'}}</small></td>
            <td style="max-width:150px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${{n.accion_correctiva||''}}"><small>${{n.accion_correctiva||'Sin plan'}}</small></td>
            <td><small><i class="fas fa-user-circle"></i> ${{n.responsable||'Sin asignar'}}</small></td>
            <td><small>${{n.plazo||'—'}}</small></td>
            <td>${{stBadge}}</td>
            <td>
                <div style="display:flex;gap:4px;">
                    <button class="btn-action" style="background:#2563eb;padding:3px 7px;font-size:.74rem;" onclick="openEditNCModal(${{idx}})" title="Gestionar / ACC"><i class="fas fa-tools"></i></button>
                    <button class="btn-action" style="background:#ef4444;padding:3px 7px;font-size:.74rem;" onclick="deleteNC(${{idx}})" title="Eliminar"><i class="fas fa-trash-alt"></i></button>
                </div>
            </td>
        </tr>`;
    }});
    tbody.innerHTML = h;
}}

function populateNCFilters(){{
    const sel = document.getElementById('filter_nc_proceso');
    if(!sel || sel.children.length > 1) return;
    Object.keys(sgcData.processes).forEach(pName => {{
        const o = document.createElement('option'); o.value = pName; o.textContent = pName;
        sel.appendChild(o);
    }});
}}

function openAddNCModal(preselectedProc = null){{
    const procOptions = Object.keys(sgcData.processes).map(p => `<option value="${{p}}" ${{p===preselectedProc?'selected':''}}>${{p}}</option>`).join('');
    const audOptions = `<option value="">-- Sin auditoría vinculada --</option>` + (sgcData.auditorias||[]).map(a => `<option value="${{a.id}}">${{a.codigo}} - ${{a.titulo}}</option>`).join('');

    Swal.fire({{
        title: 'Registrar No Conformidad / Hallazgo',
        width: '720px',
        html: `<div style="text-align:left;font-size:.86rem;">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Código NC *</label><input id="sw_nc_cod" class="swal2-input" value="NC-${{new Date().getFullYear()}}-0${{(sgcData.no_conformidades||[]).length+1}}" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                <div><label style="font-weight:bold;">Fecha de Detección</label><input id="sw_nc_fecha" type="date" value="${{new Date().toISOString().split('T')[0]}}" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
            </div>
            <div style="display:grid;grid-template-columns:1.5fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Proceso Afectado *</label><select id="sw_nc_proc" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;">${{procOptions}}</select></div>
                <div><label style="font-weight:bold;">Clasificación de Gravedad</label><select id="sw_nc_clasif" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="Menor">🟡 Menor (Falla puntual/aislada)</option><option value="Mayor">🔴 Mayor (Afectación sistémica/crítica)</option></select></div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1.5fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Cláusula ISO 9001</label><input id="sw_nc_clausula" class="swal2-input" placeholder="Ej. 7.5, 8.1, 9.2..." value="10.2" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                <div><label style="font-weight:bold;">Auditoría de Origen</label><select id="sw_nc_aud" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;">${{audOptions}}</select></div>
            </div>
            <div style="margin-bottom:10px;"><label style="font-weight:bold;">Descripción del Hallazgo / No Conformidad *</label><textarea id="sw_nc_desc" class="swal2-input" style="width:100%;height:65px;margin-top:4px;box-sizing:border-box;" placeholder="Redacte la evidencia objetiva del incumplimiento..."></textarea></div>
            <div style="margin-bottom:10px;background:#f8fafc;padding:10px;border-radius:8px;border:1px solid #e2e8f0;">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:8px;">
                    <div><label style="font-weight:bold;">Método de Análisis Causa Raíz</label><select id="sw_nc_metodo" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="5 Porqués">5 Porqués</option><option value="Diagrama de Ishikawa">Diagrama de Ishikawa (6M)</option><option value="Árbol de Fallas">Árbol de Fallas</option></select></div>
                    <div><label style="font-weight:bold;">Causa Raíz Identificada</label><input id="sw_nc_causa" class="swal2-input" placeholder="Causa raíz de fondo..." style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                </div>
                <div><label style="font-weight:bold;">Plan de Acción Correctiva (ACC)</label><textarea id="sw_nc_acc" class="swal2-input" style="width:100%;height:50px;margin-top:4px;box-sizing:border-box;" placeholder="Acciones para eliminar la causa y evitar recurrencia..."></textarea></div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">
                <div><label style="font-weight:bold;">Responsable ACC</label>${{buildUserSelect('sw_nc_resp', '', 'Seleccionar responsable...')}}</div>
                <div><label style="font-weight:bold;">Fecha Límite</label><input id="sw_nc_plazo" type="date" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                <div><label style="font-weight:bold;">Estado</label><select id="sw_nc_est" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="Abierta">🔴 Abierta</option><option value="En progreso">🔵 En progreso</option><option value="Verificada">🟣 Verificada</option><option value="Cerrada">🟢 Cerrada</option></select></div>
            </div>
        </div>`,
        showCancelButton: true, confirmButtonText: 'Registrar NC', cancelButtonText: 'Cancelar',
        preConfirm: () => {{
            const cod = document.getElementById('sw_nc_cod').value.trim();
            const desc = document.getElementById('sw_nc_desc').value.trim();
            if(!cod || !desc){{ Swal.showValidationMessage('Código y Descripción son obligatorios.'); return false; }}
            return {{
                id: generateId(),
                codigo: cod,
                fecha: document.getElementById('sw_nc_fecha').value,
                proceso: document.getElementById('sw_nc_proc').value,
                clasificacion: document.getElementById('sw_nc_clasif').value,
                clausula: document.getElementById('sw_nc_clausula').value.trim(),
                auditoria_id: document.getElementById('sw_nc_aud').value,
                descripcion: desc,
                metodo_causa: document.getElementById('sw_nc_metodo').value,
                causa_raiz: document.getElementById('sw_nc_causa').value.trim(),
                accion_correctiva: document.getElementById('sw_nc_acc').value.trim(),
                responsable: document.getElementById('sw_nc_resp').value,
                plazo: document.getElementById('sw_nc_plazo').value,
                estado: document.getElementById('sw_nc_est').value
            }};
        }}
    }}).then(async r => {{
        if(!r.isConfirmed) return;
        if(!sgcData.no_conformidades) sgcData.no_conformidades = [];
        sgcData.no_conformidades.push(r.value);
        renderNCTable();
        if(currentActiveProcess) renderProcessNCTab(currentActiveProcess);
        await saveSGCData(sgcData);
    }});
}}

function openEditNCModal(idx){{
    const n = sgcData.no_conformidades[idx];
    if(!n) return;
    const procOptions = Object.keys(sgcData.processes).map(p => `<option value="${{p}}" ${{p===n.proceso?'selected':''}}>${{p}}</option>`).join('');
    const audOptions = `<option value="">-- Sin auditoría --</option>` + (sgcData.auditorias||[]).map(a => `<option value="${{a.id}}" ${{a.id===n.auditoria_id?'selected':''}}>${{a.codigo}} - ${{a.titulo}}</option>`).join('');

    Swal.fire({{
        title: `Gestión de No Conformidad: ${{n.codigo||('NC-'+(idx+1))}}`,
        width: '720px',
        html: `<div style="text-align:left;font-size:.86rem;">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Código</label><input id="sw_nc_cod" class="swal2-input" value="${{n.codigo||''}}" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                <div><label style="font-weight:bold;">Fecha Detección</label><input id="sw_nc_fecha" type="date" value="${{n.fecha||''}}" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
            </div>
            <div style="display:grid;grid-template-columns:1.5fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Proceso Afectado</label><select id="sw_nc_proc" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;">${{procOptions}}</select></div>
                <div><label style="font-weight:bold;">Clasificación</label><select id="sw_nc_clasif" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="Menor" ${{n.clasificacion==='Menor'?'selected':''}}>🟡 Menor</option><option value="Mayor" ${{n.clasificacion==='Mayor'?'selected':''}}>🔴 Mayor</option></select></div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1.5fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Cláusula</label><input id="sw_nc_clausula" class="swal2-input" value="${{n.clausula||'10.2'}}" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                <div><label style="font-weight:bold;">Auditoría</label><select id="sw_nc_aud" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;">${{audOptions}}</select></div>
            </div>
            <div style="margin-bottom:10px;"><label style="font-weight:bold;">Descripción del Hallazgo</label><textarea id="sw_nc_desc" class="swal2-input" style="width:100%;height:65px;margin-top:4px;box-sizing:border-box;">${{n.descripcion||''}}</textarea></div>
            <div style="margin-bottom:10px;background:#f8fafc;padding:10px;border-radius:8px;border:1px solid #e2e8f0;">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:8px;">
                    <div><label style="font-weight:bold;">Método Causa Raíz</label><select id="sw_nc_metodo" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="5 Porqués" ${{n.metodo_causa==='5 Porqués'?'selected':''}}>5 Porqués</option><option value="Diagrama de Ishikawa" ${{n.metodo_causa==='Diagrama de Ishikawa'?'selected':''}}>Diagrama de Ishikawa</option><option value="Árbol de Fallas" ${{n.metodo_causa==='Árbol de Fallas'?'selected':''}}>Árbol de Fallas</option></select></div>
                    <div><label style="font-weight:bold;">Causa Raíz</label><input id="sw_nc_causa" class="swal2-input" value="${{n.causa_raiz||''}}" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                </div>
                <div><label style="font-weight:bold;">Plan de Acción Correctiva (ACC)</label><textarea id="sw_nc_acc" class="swal2-input" style="width:100%;height:50px;margin-top:4px;box-sizing:border-box;">${{n.accion_correctiva||''}}</textarea></div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">
                <div><label style="font-weight:bold;">Responsable</label>${{buildUserSelect('sw_nc_resp', n.responsable, 'Seleccionar responsable...')}}</div>
                <div><label style="font-weight:bold;">Fecha Límite</label><input id="sw_nc_plazo" type="date" class="swal2-input" value="${{n.plazo||''}}" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                <div><label style="font-weight:bold;">Estado</label><select id="sw_nc_est" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="Abierta" ${{n.estado==='Abierta'?'selected':''}}>🔴 Abierta</option><option value="En progreso" ${{n.estado==='En progreso'?'selected':''}}>🔵 En progreso</option><option value="Verificada" ${{n.estado==='Verificada'?'selected':''}}>🟣 Verificada</option><option value="Cerrada" ${{n.estado==='Cerrada'?'selected':''}}>🟢 Cerrada</option></select></div>
            </div>
        </div>`,
        showCancelButton: true, confirmButtonText: 'Actualizar NC', cancelButtonText: 'Cancelar',
        preConfirm: () => {{
            return {{
                ...n,
                codigo: document.getElementById('sw_nc_cod').value.trim(),
                fecha: document.getElementById('sw_nc_fecha').value,
                proceso: document.getElementById('sw_nc_proc').value,
                clasificacion: document.getElementById('sw_nc_clasif').value,
                clausula: document.getElementById('sw_nc_clausula').value.trim(),
                auditoria_id: document.getElementById('sw_nc_aud').value,
                descripcion: document.getElementById('sw_nc_desc').value.trim(),
                metodo_causa: document.getElementById('sw_nc_metodo').value,
                causa_raiz: document.getElementById('sw_nc_causa').value.trim(),
                accion_correctiva: document.getElementById('sw_nc_acc').value.trim(),
                responsable: document.getElementById('sw_nc_resp').value,
                plazo: document.getElementById('sw_nc_plazo').value,
                estado: document.getElementById('sw_nc_est').value
            }};
        }}
    }}).then(async res => {{
        if(!res.isConfirmed) return;
        sgcData.no_conformidades[idx] = res.value;
        renderNCTable();
        if(currentActiveProcess) renderProcessNCTab(currentActiveProcess);
        await saveSGCData(sgcData);
    }});
}}

function deleteNC(idx){{
    Swal.fire({{
        title: '¿Eliminar No Conformidad?',
        text: 'Se eliminará el registro de la matriz.',
        icon: 'warning', showCancelButton: true, confirmButtonText: 'Sí, eliminar', cancelButtonText: 'Cancelar', confirmButtonColor: '#ef4444'
    }}).then(async r => {{
        if(!r.isConfirmed) return;
        sgcData.no_conformidades.splice(idx, 1);
        renderNCTable();
        if(currentActiveProcess) renderProcessNCTab(currentActiveProcess);
        await saveSGCData(sgcData);
    }});
}}

function renderProcessNCTab(pName){{
    const cont = document.getElementById('proc_nc_container');
    if(!cont) return;
    const ncs = (sgcData.no_conformidades||[]).filter(n => n.proceso === pName);
    if(!ncs.length){{
        cont.innerHTML = `<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:25px;text-align:center;color:#94a3b8;">
            <i class="fas fa-shield-check" style="font-size:2rem;color:#10b981;margin-bottom:8px;display:block;"></i>
            No se han registrado no conformidades asociadas a este proceso.
        </div>`;
        return;
    }}

    let h = `<table class="sgc-table"><thead><tr><th>ID</th><th>Fecha</th><th>Clasificación</th><th>Descripción</th><th>Causa Raíz</th><th>ACC</th><th>Estado</th></tr></thead><tbody>`;
    ncs.forEach(n => {{
        const clsBadge = n.clasificacion === 'Mayor' ? '<span class="badge-nc-mayor">🔴 Mayor</span>' : '<span class="badge-nc-menor">🟡 Menor</span>';
        const stBadge = n.estado === 'Cerrada' ? '<span class="badge-nc-cerrada">🟢 Cerrada</span>' : n.estado === 'Verificada' ? '<span class="badge-nc-verificada">🟣 Verificada</span>' : n.estado === 'En progreso' ? '<span class="badge-nc-progreso">🔵 En Progreso</span>' : '<span class="badge-nc-abierta">🔴 Abierta</span>';
        h += `<tr>
            <td><strong>${{n.codigo||n.id}}</strong></td>
            <td>${{n.fecha || '-'}}</td>
            <td>${{clsBadge}}</td>
            <td>${{n.descripcion || '-'}}</td>
            <td>${{n.causa_raiz || '-'}}</td>
            <td>${{n.accion_correctiva || '-'}}</td>
            <td>${{stBadge}}</td>
        </tr>`;
    }});
    h += `</tbody></table>`;
    cont.innerHTML = h;
}}

/* ============================================================
   MÓDULO 4: MATRIZ DE RIESGOS & OPORTUNIDADES (CLÁUSULA 6.1)
   ============================================================ */
function renderRiesgosTable(){{
    const tbody = document.getElementById('tbody_riesgos');
    if(!tbody) return;
    populateRiskFilters();

    const fp = document.getElementById('filter_risk_proceso')?.value || '';
    const fc = document.getElementById('filter_risk_cat')?.value || '';
    const fn = document.getElementById('filter_risk_nivel')?.value || '';

    const risks = sgcData.riesgos || [];
    let cr = 0, al = 0, bj = 0, op = 0;
    risks.forEach(r => {{
        if(r.categoria === 'Oportunidad') op++;
        else {{
            const pxi = (parseInt(r.probabilidad)||1) * (parseInt(r.impacto)||1);
            if(pxi >= 15) cr++;
            else if(pxi >= 10) al++;
            else bj++;
        }}
    }});

    const elCr = document.getElementById('stat_risk_criticos'); if(elCr) elCr.textContent = cr;
    const elAl = document.getElementById('stat_risk_altos'); if(elAl) elAl.textContent = al;
    const elBj = document.getElementById('stat_risk_bajos'); if(elBj) elBj.textContent = bj;
    const elOp = document.getElementById('stat_oportunidades'); if(elOp) elOp.textContent = op;

    let fil = risks;
    if(fp) fil = fil.filter(r => r.proceso === fp);
    if(fc) fil = fil.filter(r => r.categoria === fc);
    if(fn) fil = fil.filter(r => {{
        const pxi = (parseInt(r.probabilidad)||1) * (parseInt(r.impacto)||1);
        if(fn === 'Crítico') return pxi >= 15;
        if(fn === 'Alto') return pxi >= 10 && pxi < 15;
        if(fn === 'Medio') return pxi >= 5 && pxi < 10;
        if(fn === 'Bajo') return pxi < 5;
        return true;
    }});

    if(!fil.length){{
        tbody.innerHTML = '<tr><td colspan="12" style="text-align:center;padding:30px;color:#94a3b8;"><i class="fas fa-shield-alt" style="font-size:2rem;color:#059669;margin-bottom:8px;display:block;"></i>No hay riesgos u oportunidades registrados con los filtros seleccionados.</td></tr>';
        return;
    }}

    let h = '';
    fil.forEach((r, idx) => {{
        const pxi = (parseInt(r.probabilidad)||1) * (parseInt(r.impacto)||1);
        let riskBadge = '';
        if(r.categoria === 'Oportunidad') riskBadge = `<span style="background:#eff6ff;color:#1d4ed8;font-weight:bold;padding:3px 8px;border-radius:6px;">🌟 PxI: ${{pxi}}</span>`;
        else if(pxi >= 15) riskBadge = `<span class="risk-critico">🔴 Crítico (${{pxi}})</span>`;
        else if(pxi >= 10) riskBadge = `<span class="risk-alto">🟠 Alto (${{pxi}})</span>`;
        else if(pxi >= 5) riskBadge = `<span class="risk-medio">🟡 Medio (${{pxi}})</span>`;
        else riskBadge = `<span class="risk-bajo">🟢 Bajo (${{pxi}})</span>`;

        h += `<tr>
            <td><strong>R-${{idx+1}}</strong></td>
            <td><span style="font-size:.78rem;font-weight:bold;color:${{r.categoria==='Oportunidad'?'#1d4ed8':'#d97706'}};">${{r.categoria==='Oportunidad'?'🌟 Oportunidad':'⚠️ Riesgo'}}</span></td>
            <td><strong>${{r.proceso}}</strong></td>
            <td style="max-width:200px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${{r.descripcion||''}}">${{r.descripcion||'—'}}</td>
            <td>${{r.probabilidad||1}}</td>
            <td>${{r.impacto||1}}</td>
            <td>${{riskBadge}}</td>
            <td style="max-width:160px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${{r.mitigacion||''}}"><small>${{r.mitigacion||'—'}}</small></td>
            <td><small><i class="fas fa-user-circle"></i> ${{r.responsable||'Sin asignar'}}</small></td>
            <td><small>${{r.plazo||'—'}}</small></td>
            <td><span style="font-size:.78rem;background:#f1f5f9;padding:2px 6px;border-radius:6px;">${{r.estado||'Planificado'}}</span></td>
            <td>
                <div style="display:flex;gap:4px;">
                    <button class="btn-action" style="background:#64748b;padding:3px 7px;font-size:.74rem;" onclick="openEditRiesgoModal(${{idx}})" title="Editar"><i class="fas fa-edit"></i></button>
                    <button class="btn-action" style="background:#ef4444;padding:3px 7px;font-size:.74rem;" onclick="deleteRiesgo(${{idx}})" title="Eliminar"><i class="fas fa-trash-alt"></i></button>
                </div>
            </td>
        </tr>`;
    }});
    tbody.innerHTML = h;
}}

function populateRiskFilters(){{
    const sel = document.getElementById('filter_risk_proceso');
    if(!sel || sel.children.length > 1) return;
    Object.keys(sgcData.processes).forEach(pName => {{
        const o = document.createElement('option'); o.value = pName; o.textContent = pName;
        sel.appendChild(o);
    }});
}}

function openAddRiesgoModal(){{
    const procOptions = Object.keys(sgcData.processes).map(p => `<option value="${{p}}">${{p}}</option>`).join('');
    Swal.fire({{
        title: 'Nuevo Riesgo u Oportunidad',
        width: '650px',
        html: `<div style="text-align:left;font-size:.86rem;">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Categoría</label><select id="sw_r_cat" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="Riesgo">⚠️ Riesgo de Calidad</option><option value="Oportunidad">🌟 Oportunidad de Mejora</option></select></div>
                <div><label style="font-weight:bold;">Proceso Vinculado *</label><select id="sw_r_proc" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;">${{procOptions}}</select></div>
            </div>
            <div style="margin-bottom:10px;"><label style="font-weight:bold;">Descripción del Evento / Riesgo *</label><textarea id="sw_r_desc" class="swal2-input" style="width:100%;height:65px;margin-top:4px;box-sizing:border-box;" placeholder="Ej. Retraso en entrega de calificaciones por falla en plataforma..."></textarea></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Probabilidad (1 a 5)</label><select id="sw_r_prob" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="1">1 - Muy Baja</option><option value="2">2 - Baja</option><option value="3" selected>3 - Media</option><option value="4">4 - Alta</option><option value="5">5 - Muy Alta</option></select></div>
                <div><label style="font-weight:bold;">Impacto (1 a 5)</label><select id="sw_r_imp" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="1">1 - Leve</option><option value="2">2 - Menor</option><option value="3" selected>3 - Moderado</option><option value="4">4 - Grave</option><option value="5">5 - Crítico / Catastrófico</option></select></div>
            </div>
            <div style="margin-bottom:10px;"><label style="font-weight:bold;">Acción de Mitigación / Contingencia</label><textarea id="sw_r_mit" class="swal2-input" style="width:100%;height:55px;margin-top:4px;box-sizing:border-box;" placeholder="Controles preventivos a implementar..."></textarea></div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">
                <div><label style="font-weight:bold;">Responsable</label>${{buildUserSelect('sw_r_resp', '', 'Seleccionar responsable...')}}</div>
                <div><label style="font-weight:bold;">Fecha Límite</label><input id="sw_r_plazo" type="date" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                <div><label style="font-weight:bold;">Estado</label><select id="sw_r_estado" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="Planificado">Planificado</option><option value="Implementado">Implementado</option><option value="Controlado / Mitigado">Controlado / Mitigado</option></select></div>
            </div>
        </div>`,
        showCancelButton: true, confirmButtonText: 'Guardar Riesgo', cancelButtonText: 'Cancelar',
        preConfirm: () => {{
            const desc = document.getElementById('sw_r_desc').value.trim();
            if(!desc){{ Swal.showValidationMessage('La descripción del riesgo es obligatoria.'); return false; }}
            return {{
                id: generateId(),
                categoria: document.getElementById('sw_r_cat').value,
                proceso: document.getElementById('sw_r_proc').value,
                descripcion: desc,
                probabilidad: parseInt(document.getElementById('sw_r_prob').value)||1,
                impacto: parseInt(document.getElementById('sw_r_imp').value)||1,
                mitigacion: document.getElementById('sw_r_mit').value.trim(),
                responsable: document.getElementById('sw_r_resp').value,
                plazo: document.getElementById('sw_r_plazo').value,
                estado: document.getElementById('sw_r_estado').value
            }};
        }}
    }}).then(async r => {{
        if(!r.isConfirmed) return;
        if(!sgcData.riesgos) sgcData.riesgos = [];
        sgcData.riesgos.push(r.value);
        renderRiesgosTable();
        await saveSGCData(sgcData);
    }});
}}

function openEditRiesgoModal(idx){{
    const r = sgcData.riesgos[idx];
    if(!r) return;
    const procOptions = Object.keys(sgcData.processes).map(p => `<option value="${{p}}" ${{p===r.proceso?'selected':''}}>${{p}}</option>`).join('');

    Swal.fire({{
        title: `Editar Registro de Riesgo: R-${{idx+1}}`,
        width: '650px',
        html: `<div style="text-align:left;font-size:.86rem;">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Categoría</label><select id="sw_r_cat" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="Riesgo" ${{r.categoria==='Riesgo'?'selected':''}}>⚠️ Riesgo</option><option value="Oportunidad" ${{r.categoria==='Oportunidad'?'selected':''}}>🌟 Oportunidad</option></select></div>
                <div><label style="font-weight:bold;">Proceso Vinculado</label><select id="sw_r_proc" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;">${{procOptions}}</select></div>
            </div>
            <div style="margin-bottom:10px;"><label style="font-weight:bold;">Descripción</label><textarea id="sw_r_desc" class="swal2-input" style="width:100%;height:65px;margin-top:4px;box-sizing:border-box;">${{r.descripcion||''}}</textarea></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                <div><label style="font-weight:bold;">Probabilidad (1-5)</label><select id="sw_r_prob" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="1" ${{r.probabilidad==1?'selected':''}}>1</option><option value="2" ${{r.probabilidad==2?'selected':''}}>2</option><option value="3" ${{r.probabilidad==3?'selected':''}}>3</option><option value="4" ${{r.probabilidad==4?'selected':''}}>4</option><option value="5" ${{r.probabilidad==5?'selected':''}}>5</option></select></div>
                <div><label style="font-weight:bold;">Impacto (1-5)</label><select id="sw_r_imp" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="1" ${{r.impacto==1?'selected':''}}>1</option><option value="2" ${{r.impacto==2?'selected':''}}>2</option><option value="3" ${{r.impacto==3?'selected':''}}>3</option><option value="4" ${{r.impacto==4?'selected':''}}>4</option><option value="5" ${{r.impacto==5?'selected':''}}>5</option></select></div>
            </div>
            <div style="margin-bottom:10px;"><label style="font-weight:bold;">Mitigación</label><textarea id="sw_r_mit" class="swal2-input" style="width:100%;height:55px;margin-top:4px;box-sizing:border-box;">${{r.mitigacion||''}}</textarea></div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">
                <div><label style="font-weight:bold;">Responsable</label>${{buildUserSelect('sw_r_resp', r.responsable, 'Seleccionar responsable...')}}</div>
                <div><label style="font-weight:bold;">Plazo</label><input id="sw_r_plazo" type="date" class="swal2-input" value="${{r.plazo||''}}" style="width:100%;margin-top:4px;box-sizing:border-box;"></div>
                <div><label style="font-weight:bold;">Estado</label><select id="sw_r_estado" class="swal2-input" style="width:100%;margin-top:4px;box-sizing:border-box;"><option value="Planificado" ${{r.estado==='Planificado'?'selected':''}}>Planificado</option><option value="Implementado" ${{r.estado==='Implementado'?'selected':''}}>Implementado</option><option value="Controlado / Mitigado" ${{r.estado==='Controlado / Mitigado'?'selected':''}}>Controlado / Mitigado</option></select></div>
            </div>
        </div>`,
        showCancelButton: true, confirmButtonText: 'Actualizar', cancelButtonText: 'Cancelar',
        preConfirm: () => {{
            return {{
                ...r,
                categoria: document.getElementById('sw_r_cat').value,
                proceso: document.getElementById('sw_r_proc').value,
                descripcion: document.getElementById('sw_r_desc').value.trim(),
                probabilidad: parseInt(document.getElementById('sw_r_prob').value)||1,
                impacto: parseInt(document.getElementById('sw_r_imp').value)||1,
                mitigacion: document.getElementById('sw_r_mit').value.trim(),
                responsable: document.getElementById('sw_r_resp').value,
                plazo: document.getElementById('sw_r_plazo').value,
                estado: document.getElementById('sw_r_estado').value
            }};
        }}
    }}).then(async res => {{
        if(!res.isConfirmed) return;
        sgcData.riesgos[idx] = res.value;
        renderRiesgosTable();
        await saveSGCData(sgcData);
    }});
}}

function deleteRiesgo(idx){{
    Swal.fire({{
        title: '¿Eliminar Riesgo?',
        text: 'Se eliminará de la matriz.',
        icon: 'warning', showCancelButton: true, confirmButtonText: 'Sí, eliminar', cancelButtonText: 'Cancelar', confirmButtonColor: '#ef4444'
    }}).then(async r => {{
        if(!r.isConfirmed) return;
        sgcData.riesgos.splice(idx, 1);
        renderRiesgosTable();
        await saveSGCData(sgcData);
    }});
}}

/* ============================================================
   MÓDULO 6: CHECKLIST DE AUDITORÍA (CLÁUSULAS 4 A 10)
   ============================================================ */
function renderChecklist(){{
    const cont = document.getElementById('checklist_container');
    if(!cont) return;
    const items = sgcData.checklist || DEFAULT_CHECKLIST;

    let cumpleCount = 0;
    items.forEach(i => {{ if(i.estado === 'Cumple') cumpleCount++; }});
    const scorePct = items.length > 0 ? Math.round((cumpleCount / items.length) * 100) : 100;
    const elScore = document.getElementById('checklist_score'); if(elScore) elScore.textContent = `${{scorePct}}%`;

    let h = '';
    items.forEach((item, idx) => {{
        const clsSel = item.estado === 'Cumple' ? 'chk-cumple' : item.estado === 'En Progreso' ? 'chk-progreso' : 'chk-nocumple';
        h += `<div class="chk-card">
            <div class="chk-header">
                <div>
                    <span class="chk-clausula">Cláusula ${{item.clausula}}</span>
                    <strong style="margin-left:8px;color:#1e3a8a;font-size:.92rem;">${{item.clausula_nombre}}</strong>
                </div>
                <select class="chk-select ${{clsSel}}" onchange="updateChecklistItem(${{idx}}, 'estado', this.value)">
                    <option value="Cumple" ${{item.estado==='Cumple'?'selected':''}}>🟢 Cumple (Conforme)</option>
                    <option value="En Progreso" ${{item.estado==='En Progreso'?'selected':''}}>🟡 En Progreso</option>
                    <option value="No Cumple" ${{item.estado==='No Cumple'?'selected':''}}>🔴 No Cumple (NC Potencial)</option>
                </select>
            </div>
            <div style="font-weight:600;color:#0f172a;font-size:.88rem;margin-bottom:6px;">${{item.pregunta}}</div>
            <div style="font-size:.8rem;color:#475569;background:#f8fafc;padding:8px 12px;border-radius:6px;margin-bottom:8px;border-left:3px solid #3b82f6;">
                <strong>Criterio de Conformidad para el Auditor:</strong> ${{item.criterio}}
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                <div>
                    <label style="font-size:.75rem;font-weight:bold;color:#64748b;">Evidencia Documentada / Registro:</label>
                    <input type="text" value="${{item.evidencia||''}}" onchange="updateChecklistItem(${{idx}}, 'evidencia', this.value)" style="width:100%;padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:.82rem;box-sizing:border-box;">
                </div>
                <div>
                    <label style="font-size:.75rem;font-weight:bold;color:#64748b;">Observaciones / Hallazgos del Auditor:</label>
                    <input type="text" value="${{item.hallazgos||''}}" placeholder="Notas de la visita..." onchange="updateChecklistItem(${{idx}}, 'hallazgos', this.value)" style="width:100%;padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:.82rem;box-sizing:border-box;">
                </div>
            </div>
        </div>`;
    }});
    cont.innerHTML = h;
}}

function updateChecklistItem(idx, field, value){{
    if(!sgcData.checklist) sgcData.checklist = JSON.parse(JSON.stringify(DEFAULT_CHECKLIST));
    if(sgcData.checklist[idx]){{
        sgcData.checklist[idx][field] = value;
        renderChecklist();
        saveSGCData(sgcData);
    }}
}}
'''

# Update openProcessModal to include loading of proc NCs
pos_open_proc = text.find('function openProcessModal(')
if pos_open_proc != -1:
    pos_open_end = text.find('}', text.find('document.getElementById(\'processModal\').style.display', pos_open_proc))
    text = text[:pos_open_end] + '\n    renderProcessNCTab(pName);\n' + text[pos_open_end:]

# Update DOMContentLoaded to initialize all views
dom_needle = "document.addEventListener('DOMContentLoaded',async()=>{await initHeader();await loadSGC();await loadPlanningTree();await loadSystemUsers();renderProcessMap();renderBancoIndicadores();});"
dom_repl = "document.addEventListener('DOMContentLoaded',async()=>{\n    await initHeader();\n    await loadSGC();\n    await loadPlanningTree();\n    await loadSystemUsers();\n    renderProcessMap();\n    renderAuditoriasTable();\n    renderNCTable();\n    renderRiesgosTable();\n    renderBancoIndicadores();\n    renderChecklist();\n});"
text = text.replace(dom_needle, dom_repl)

# Update loadSGC to populate auditorias, NCs, riesgos, checklist
load_needle = "if(d&&Object.keys(d).length>0){"
load_repl = """if(d&&Object.keys(d).length>0){
                if(d.auditorias && Array.isArray(d.auditorias)) sgcData.auditorias = d.auditorias;
                if(d.no_conformidades && Array.isArray(d.no_conformidades)) sgcData.no_conformidades = d.no_conformidades;
                if(d.riesgos && Array.isArray(d.riesgos)) sgcData.riesgos = d.riesgos;
                if(d.checklist && Array.isArray(d.checklist) && d.checklist.length > 0) sgcData.checklist = d.checklist;"""
text = text.replace(load_needle, load_repl, 1)

# Append new JS helpers before closing </script>
pos_script_end = text.rfind('</script>')
if pos_script_end != -1:
    text = text[:pos_script_end] + '\n' + js_add + '\n' + text[pos_script_end:]

with open('templates/empresa_iso.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done building full ISO view')
