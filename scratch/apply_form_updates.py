import os

filepath = "templates/autoevaluacion.html"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace the edit plan responsable layout block
target_edit_block = """                                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px;">
                                    <div>
                                        <label style="display:block; font-size:0.7rem; font-weight:600; color:#475569; margin-bottom:2px;">Rol Responsable</label>
                                        <select id="edit_plan_responsable_rol_${plan.id}" onchange="updateResponsableNamesDropdown('edit_plan_responsable_rol_${plan.id}', 'edit_plan_responsable_name_${plan.id}', 'edit_plan_responsable_${plan.id}')" style="width:100%; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-size:0.8rem; box-sizing:border-box;">
                                            <option value="lider" ${plan.responsable_rol === 'lider' ? 'selected' : ''}>LÍDER</option>
                                            <option value="admin" ${plan.responsable_rol === 'admin' ? 'selected' : ''}>ADMINISTRADOR</option>
                                            <option value="operativo" ${plan.responsable_rol === 'operativo' ? 'selected' : ''}>OPERATIVO</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label style="display:block; font-size:0.7rem; font-weight:600; color:#475569; margin-bottom:2px;">Nombre Responsable *</label>
                                        <select id="edit_plan_responsable_name_${plan.id}" onchange="updateResponsableEmailFromSelect('edit_plan_responsable_name_${plan.id}', 'edit_plan_responsable_${plan.id}')" style="width:100%; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-size:0.8rem; box-sizing:border-box;">
                                            <option value="">Cargando...</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label style="display:block; font-size:0.7rem; font-weight:600; color:#475569; margin-bottom:2px;">Email Responsable</label>
                                        <input type="email" id="edit_plan_responsable_${plan.id}" value="${plan.responsable}" readonly style="width:100%; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-size:0.8rem; box-sizing:border-box; background:#f1f5f9; cursor:not-allowed;">
                                    </div>
                                </div>"""

replacement_edit_block = """                                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                                     <div>
                                         <label style="display:block; font-size:0.7rem; font-weight:600; color:#475569; margin-bottom:2px;">Rol Responsable</label>
                                         <select id="edit_plan_responsable_rol_${plan.id}" onchange="updateResponsableNamesDropdown('edit_plan_responsable_rol_${plan.id}', 'edit_plan_responsable_name_${plan.id}', 'edit_plan_responsable_${plan.id}')" style="width:100%; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-size:0.8rem; box-sizing:border-box;">
                                             <option value="lider" ${plan.responsable_rol === 'lider' ? 'selected' : ''}>LÍDER</option>
                                             <option value="admin" ${plan.responsable_rol === 'admin' ? 'selected' : ''}>ADMINISTRADOR</option>
                                             <option value="operativo" ${plan.responsable_rol === 'operativo' ? 'selected' : ''}>OPERATIVO</option>
                                         </select>
                                     </div>
                                     <div>
                                         <label style="display:block; font-size:0.7rem; font-weight:600; color:#475569; margin-bottom:2px;">Nombre Responsable *</label>
                                         <select id="edit_plan_responsable_name_${plan.id}" onchange="updateResponsableEmailFromSelect('edit_plan_responsable_name_${plan.id}', 'edit_plan_responsable_${plan.id}')" style="width:100%; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-size:0.8rem; box-sizing:border-box;">
                                             <option value="">Cargando...</option>
                                         </select>
                                     </div>
                                     <input type="hidden" id="edit_plan_responsable_${plan.id}" value="${plan.responsable}">
                                 </div>"""

# Check for soft matching since there might be encoding/newline issues
normalized_content = content.replace("\r\n", "\n")
normalized_target = target_edit_block.replace("\r\n", "\n")
normalized_replacement = replacement_edit_block.replace("\r\n", "\n")

# Replace in content
if normalized_target in normalized_content:
    normalized_content = normalized_content.replace(normalized_target, normalized_replacement)
    print("Successfully replaced edit form layout block.")
else:
    # Try finding with flexible line replacement or print what is close
    print("Warning: Target edit form layout block not found as exact string. Doing fallback replace...")
    # We can do a simpler replace by targeting some unique parts
    normalized_content = normalized_content.replace(
        'id="edit_plan_responsable_${plan.id}" value="${plan.responsable}" readonly style="width:100%; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-size:0.8rem; box-sizing:border-box; background:#f1f5f9; cursor:not-allowed;">\n                                    </div>\n                                </div>',
        'id="edit_plan_responsable_${plan.id}" value="${plan.responsable}" readonly style="width:100%; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-size:0.8rem; box-sizing:border-box; background:#f1f5f9; cursor:not-allowed;">\n                                    </div>\n                                </div>'
    )

# 2. Replace showAddPlanForm
target_show_form = """        function showAddPlanForm() {
            document.getElementById('addPlanFormContainer').style.display = 'block';
            document.getElementById('new_plan_fecha_inicio').value = new Date().toISOString().substring(0, 10);
            updateResponsableNamesDropdown('new_plan_responsable_rol', 'new_plan_responsable_name', 'new_plan_responsable');
        }"""

replacement_show_form = """        async function showAddPlanForm() {
            document.getElementById('addPlanFormContainer').style.display = 'block';
            document.getElementById('new_plan_fecha_inicio').value = new Date().toISOString().substring(0, 10);
            await updateResponsableNamesDropdown('new_plan_responsable_rol', 'new_plan_responsable_name', 'new_plan_responsable');
        }"""

normalized_target_show = target_show_form.replace("\r\n", "\n")
normalized_replacement_show = replacement_show_form.replace("\r\n", "\n")

if normalized_target_show in normalized_content:
    normalized_content = normalized_content.replace(normalized_target_show, normalized_replacement_show)
    print("Successfully replaced showAddPlanForm function.")
else:
    print("Warning: showAddPlanForm function not found as exact string.")

# 3. Replace toggleEditPlanForm
target_toggle_form = """        function toggleEditPlanForm(planId) {
            const card = document.getElementById(`planCard_${planId}`);
            const form = document.getElementById(`planEditForm_${planId}`);
            if (!card || !form) return;
            
            if (form.style.display === 'none') {
                card.style.display = 'none';
                form.style.display = 'flex';
                
                const plan = window.currentPlanesList.find(p => p.id === planId);
                if (plan) {
                    updateResponsableNamesDropdown(
                        `edit_plan_responsable_rol_${planId}`,
                        `edit_plan_responsable_name_${planId}`,
                        `edit_plan_responsable_${planId}`,
                        plan.responsable
                    );
                }"""

replacement_toggle_form = """        async function toggleEditPlanForm(planId) {
            const card = document.getElementById(`planCard_${planId}`);
            const form = document.getElementById(`planEditForm_${planId}`);
            if (!card || !form) return;
            
            if (form.style.display === 'none') {
                card.style.display = 'none';
                form.style.display = 'flex';
                
                const plan = window.currentPlanesList.find(p => p.id === planId);
                if (plan) {
                    await updateResponsableNamesDropdown(
                        `edit_plan_responsable_rol_${planId}`,
                        `edit_plan_responsable_name_${planId}`,
                        `edit_plan_responsable_${planId}`,
                        plan.responsable
                    );
                }"""

normalized_target_toggle = target_toggle_form.replace("\r\n", "\n")
normalized_replacement_toggle = replacement_toggle_form.replace("\r\n", "\n")

if normalized_target_toggle in normalized_content:
    normalized_content = normalized_content.replace(normalized_target_toggle, normalized_replacement_toggle)
    print("Successfully replaced toggleEditPlanForm function.")
else:
    print("Warning: toggleEditPlanForm function not found as exact string.")

# Write it back using UTF-8 and CRLF line endings to be consistent
content_to_write = normalized_content.replace("\n", "\r\n")
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content_to_write)
print("Finished writing changes to autoevaluacion.html")
