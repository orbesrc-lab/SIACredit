import os

file_path = r'c:\SIAC\templates\empresa_iso.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add planningTree state and loadPlanningTree() function
state_addition = """
        let planningTreeData = [];

        async function loadPlanningTree() {
            try {
                const resp = await fetch(`/api/planning/tree?inst_id=${getInstId()}&program_id=${getProgramId()}`);
                if (resp.ok) {
                    const data = await resp.json();
                    if (data.status === 'success' && data.tree) {
                        planningTreeData = data.tree;
                    }
                }
            } catch(e) { console.error("Error loading planning tree:", e); }
        }
"""

if "let planningTreeData" not in content:
    content = content.replace("let sgcData = {", state_addition + "\n        let sgcData = {")

# Update DOMContentLoaded to load planning tree before rendering map
content = content.replace("await loadSGC();", "await loadSGC();\n            await loadPlanningTree();")

# Update renderProcessMap to count linked objectives
old_render_card = """                const cardHTML = `
                <div class="proc-card ${cssClass}" onclick="openProcessModal('${pName}')">
                    <div class="proc-header">
                        <div class="proc-name"><i class="fas fa-cog" style="color:#3b82f6; margin-right:4px;"></i> ${pName}</div>
                        <div class="proc-actions">
                            <button class="btn-card-del" onclick="event.stopPropagation(); quickDeleteProcess('${pName}')" title="Eliminar Proceso"><i class="fas fa-trash-alt"></i></button>
                        </div>
                    </div>
                    <div class="proc-body">
                        <div><i class="fas fa-user-tag" style="width:14px;"></i> ${pData.leader || 'Sin Líder'}</div>
                    </div>
                    <div class="proc-footer">
                        ${statusBadge}
                        <span style="color:#3b82f6; font-weight:bold;">Editar PHVA <i class="fas fa-chevron-right"></i></span>
                    </div>
                </div>`;"""

new_render_card = """                // Count linked planning objectives
                let linkedCount = countLinkedObjs(pName);
                let planBadge = linkedCount > 0 ? 
                    `<div style="font-size:0.75rem; color:#1d4ed8; background:#eff6ff; border:1px solid #bfdbfe; padding:2px 6px; border-radius:8px; margin-top:4px; font-weight:bold;"><i class="fas fa-bullseye"></i> ${linkedCount} Obj. Planificación</div>` : '';

                const cardHTML = `
                <div class="proc-card ${cssClass}" onclick="openProcessModal('${pName}')">
                    <div class="proc-header">
                        <div class="proc-name"><i class="fas fa-cog" style="color:#3b82f6; margin-right:4px;"></i> ${pName}</div>
                        <div class="proc-actions">
                            <button class="btn-card-del" onclick="event.stopPropagation(); quickDeleteProcess('${pName}')" title="Eliminar Proceso"><i class="fas fa-trash-alt"></i></button>
                        </div>
                    </div>
                    <div class="proc-body">
                        <div><i class="fas fa-user-tag" style="width:14px;"></i> ${pData.leader || 'Sin Líder'}</div>
                        ${planBadge}
                    </div>
                    <div class="proc-footer">
                        ${statusBadge}
                        <span style="color:#3b82f6; font-weight:bold;">Editar PHVA <i class="fas fa-chevron-right"></i></span>
                    </div>
                </div>`;"""

content = content.replace(old_render_card.replace('\r\n', '\n'), new_render_card.replace('\r\n', '\n'))
content = content.replace(old_render_card, new_render_card)

# Helper function countLinkedObjs and populateHacerTab
helpers_code = """
        function countLinkedObjs(pName) {
            let count = 0;
            (planningTreeData || []).forEach(axis => {
                (axis.strategies || []).forEach(st => {
                    (st.general_objectives || []).forEach(go => {
                        if (go.alignment_pdi && go.alignment_pdi.includes(`[ISO: ${pName}]`)) {
                            count++;
                        }
                    });
                });
            });
            return count;
        }

        function populateHacerFromPlanning(pName) {
            let linkedObjs = [];
            (planningTreeData || []).forEach(axis => {
                (axis.strategies || []).forEach(st => {
                    (st.general_objectives || []).forEach(go => {
                        if (go.alignment_pdi && go.alignment_pdi.includes(`[ISO: ${pName}]`)) {
                            linkedObjs.push({
                                axisName: axis.name,
                                stratDesc: st.description,
                                genObj: go
                            });
                        }
                    });
                });
            });

            if (linkedObjs.length === 0) {
                return `<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:15px; font-size:0.88rem; color:#64748b;">
                    <p style="margin:0;"><i class="fas fa-info-circle" style="color:#3b82f6;"></i> No hay Objetivos de Planificación articulados a este proceso aún.</p>
                    <small style="margin-top:5px; display:block;">Vaya al módulo de <strong>Planificación</strong>, cree o edite un Objetivo General y seleccione <em>"Articular a Proceso ISO 9001: ${pName}"</em>.</small>
                </div>`;
            }

            let html = `<div style="margin-bottom:15px;"><strong style="color:#1e3a8a;">🎯 Objetivos y Actividades Articuladas desde Planificación (${linkedObjs.length}):</strong></div>`;

            linkedObjs.forEach(item => {
                const go = item.genObj;
                html += `
                <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px; padding:12px; margin-bottom:12px;">
                    <div style="font-weight:bold; color:#1e3a8a; font-size:0.92rem;"><i class="fas fa-bullseye" style="color:#2563eb;"></i> ${go.description}</div>
                    <div style="font-size:0.78rem; color:#64748b; margin-top:2px;">Eje: ${item.axisName} | Estrategia: ${item.stratDesc}</div>
                `;

                if (go.specific_objectives && go.specific_objectives.length > 0) {
                    html += `<div style="margin-top:8px; font-weight:bold; font-size:0.85rem; color:#334155;">Objetivos Específicos e Indicadores:</div>`;
                    go.specific_objectives.forEach(so => {
                        html += `
                        <div style="background:white; border:1px solid #cbd5e1; border-radius:6px; padding:8px; margin-top:5px; font-size:0.85rem;">
                            <div><strong>• ${so.description}</strong></div>
                            <div style="font-size:0.78rem; color:#64748b;">Indicador: ${so.indicator_type || '-'} (${so.indicator_description || '-'}) | Peso: ${so.weight_percentage || 0}%</div>
                        `;

                        if (so.activities && so.activities.length > 0) {
                            html += `<div style="margin-top:4px; font-size:0.8rem; font-weight:bold; color:#475569;">Actividades en Ejecución (HACER):</div>`;
                            so.activities.forEach(act => {
                                html += `<div style="font-size:0.78rem; color:#334155; padding:2px 0;">- ${act.description} | Meta: ${act.goal || '-'} | Resp: ${act.responsible || '-'}</div>`;
                            });
                        }
                        html += `</div>`;
                    });
                }

                html += `</div>`;
            });

            return html;
        }
"""

if "function countLinkedObjs" not in content:
    content = content.replace("function openProcessModal(", helpers_code + "\n        function openProcessModal(")

# Inject populateHacerFromPlanning into openProcessModal
old_open_modal = "document.getElementById('phva_hacer').value = p.hacer || '';"
new_open_modal = """document.getElementById('phva_hacer').value = p.hacer || '';
            const planExecHTML = populateHacerFromPlanning(pName);
            if(document.getElementById('planExecContainer')) {
                document.getElementById('planExecContainer').innerHTML = planExecHTML;
            }"""

content = content.replace(old_open_modal, new_open_modal)

# Add planExecContainer into tabHacer HTML
old_tab_hacer = """            <!-- Panel Hacer -->
            <div class="phva-panel" id="tabHacer">
                <h4 style="color:#1e3a8a;">Ejecución de Actividades (Módulo de Planificación)</h4>
                <p style="font-size:0.88rem; color:#64748b;">Actividades de operación ejecutadas dentro del período evaluado:</p>
                <textarea id="phva_hacer" style="width:100%; height:120px; padding:10px; border:1px solid #cbd5e1; border-radius:8px;" placeholder="Ej. Ejecución de talleres de capacitación docentes. Implementación de nueva plataforma digital..."></textarea>
            </div>"""

new_tab_hacer = """            <!-- Panel Hacer -->
            <div class="phva-panel" id="tabHacer">
                <h4 style="color:#1e3a8a;"><i class="fas fa-cogs" style="color:#2563eb;"></i> ⚙️ H - HACER: Ejecución Operativa del Proceso (ISO 9001 Cláusula 8)</h4>
                <div id="planExecContainer" style="margin-bottom:15px;"></div>
                <label style="font-weight:bold; color:#334155; font-size:0.88rem; display:block; margin-bottom:5px;">Notas Adicionales de Ejecución Operativa:</label>
                <textarea id="phva_hacer" style="width:100%; height:80px; padding:10px; border:1px solid #cbd5e1; border-radius:8px;" placeholder="Ej. Ejecución de talleres de capacitación docentes. Implementación de nueva plataforma digital..."></textarea>
            </div>"""

content = content.replace(old_tab_hacer.replace('\r\n', '\n'), new_tab_hacer.replace('\r\n', '\n'))
content = content.replace(old_tab_hacer, new_tab_hacer)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("empresa_iso.html patched with automatic Planning execution under HACER tab!")
