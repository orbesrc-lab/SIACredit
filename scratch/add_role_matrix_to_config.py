import os

file_config = r'c:\SIAC\templates\configuracion.html'
with open(file_config, 'r', encoding='utf-8') as f:
    content = f.read()

role_matrix_html = """
            <!-- Matriz de Control de Acceso y Permisos por Rol -->
            <div id="rolePermissionsCard" class="settings-card" style="border-left: 5px solid #6366f1; background: white; padding: 22px; border-radius: 12px; margin-top: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 15px;">
                    <div>
                        <h3 style="margin:0; color:#1e3a8a; font-size:1.25rem;"><i class="fas fa-user-shield" style="color:#6366f1; margin-right:8px;"></i> Matriz de Control de Acceso y Permisos por Rol</h3>
                        <p style="font-size:0.88rem; color:#64748b; margin:4px 0 0;">Active o desactive qué módulos y herramientas puede ver y manipular cada rol en la plataforma.</p>
                    </div>
                    <button class="btn-primary" onclick="saveRolePermissions()" style="background:linear-gradient(135deg, #4f46e5, #6366f1); border:none; padding:8px 16px; border-radius:8px; font-weight:bold; cursor:pointer;"><i class="fas fa-save"></i> Guardar Permisos por Rol</button>
                </div>

                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; text-align: center;">
                        <thead>
                            <tr style="background-color: #f8fafc; color: #334155; border-bottom: 2px solid #cbd5e1;">
                                <th style="padding: 12px; text-align: left; width: 30%;">Módulo / Funcionalidad</th>
                                <th style="padding: 12px; width: 14%;">👑 Super Admin</th>
                                <th style="padding: 12px; width: 14%;">🏢 Administrador</th>
                                <th style="padding: 12px; width: 14%;">💼 Consultor B2B</th>
                                <th style="padding: 12px; width: 14%;">🔍 Auditor Calidad</th>
                                <th style="padding: 12px; width: 14%;">👤 Docente / Usuario</th>
                            </tr>
                        </thead>
                        <tbody id="rolePermsTableBody">
                            <tr style="border-bottom: 1px solid #e2e8f0;">
                                <td style="padding: 10px; text-align: left; font-weight: 600;"><i class="fas fa-chart-line" style="color:#2563eb;"></i> Autoevaluación & Estadísticas Globales</td>
                                <td><input type="checkbox" class="perm-cb" data-module="autoevaluacion" data-role="super_admin" checked disabled></td>
                                <td><input type="checkbox" class="perm-cb" data-module="autoevaluacion" data-role="admin" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="autoevaluacion" data-role="consultor" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="autoevaluacion" data-role="auditor" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="autoevaluacion" data-role="user" checked></td>
                            </tr>
                            <tr style="border-bottom: 1px solid #e2e8f0;">
                                <td style="padding: 10px; text-align: left; font-weight: 600;"><i class="fas fa-file-alt" style="color:#0284c7;"></i> Informes Institucionales & PDF</td>
                                <td><input type="checkbox" class="perm-cb" data-module="informes" data-role="super_admin" checked disabled></td>
                                <td><input type="checkbox" class="perm-cb" data-module="informes" data-role="admin" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="informes" data-role="consultor" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="informes" data-role="auditor" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="informes" data-role="user"></td>
                            </tr>
                            <tr style="border-bottom: 1px solid #e2e8f0;">
                                <td style="padding: 10px; text-align: left; font-weight: 600;"><i class="fas fa-calendar-alt" style="color:#10b981;"></i> Planificación Estratégica & PDI</td>
                                <td><input type="checkbox" class="perm-cb" data-module="planificacion" data-role="super_admin" checked disabled></td>
                                <td><input type="checkbox" class="perm-cb" data-module="planificacion" data-role="admin" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="planificacion" data-role="consultor" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="planificacion" data-role="auditor"></td>
                                <td><input type="checkbox" class="perm-cb" data-module="planificacion" data-role="user" checked></td>
                            </tr>
                            <tr style="border-bottom: 1px solid #e2e8f0;">
                                <td style="padding: 10px; text-align: left; font-weight: 600;"><i class="fas fa-briefcase" style="color:#6366f1;"></i> Hub Estratégico B2B (MEFI/MEFE, Porter, Riesgos)</td>
                                <td><input type="checkbox" class="perm-cb" data-module="hub_estrategico" data-role="super_admin" checked disabled></td>
                                <td><input type="checkbox" class="perm-cb" data-module="hub_estrategico" data-role="admin" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="hub_estrategico" data-role="consultor" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="hub_estrategico" data-role="auditor" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="hub_estrategico" data-role="user"></td>
                            </tr>
                            <tr style="border-bottom: 1px solid #e2e8f0;">
                                <td style="padding: 10px; text-align: left; font-weight: 600;"><i class="fas fa-award" style="color:#8b5cf6;"></i> Sistema ISO 9001 (Mapa, SIPOC, PHVA)</td>
                                <td><input type="checkbox" class="perm-cb" data-module="iso9001" data-role="super_admin" checked disabled></td>
                                <td><input type="checkbox" class="perm-cb" data-module="iso9001" data-role="admin" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="iso9001" data-role="consultor" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="iso9001" data-role="auditor" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="iso9001" data-role="user"></td>
                            </tr>
                            <tr style="border-bottom: 1px solid #e2e8f0;">
                                <td style="padding: 10px; text-align: left; font-weight: 600;"><i class="fas fa-graduation-cap" style="color:#f59e0b;"></i> Módulo de Capacitación & Cursos</td>
                                <td><input type="checkbox" class="perm-cb" data-module="capacitacion" data-role="super_admin" checked disabled></td>
                                <td><input type="checkbox" class="perm-cb" data-module="capacitacion" data-role="admin" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="capacitacion" data-role="consultor" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="capacitacion" data-role="auditor"></td>
                                <td><input type="checkbox" class="perm-cb" data-module="capacitacion" data-role="user" checked></td>
                            </tr>
                            <tr style="border-bottom: 1px solid #e2e8f0;">
                                <td style="padding: 10px; text-align: left; font-weight: 600;"><i class="fas fa-tools" style="color:#ec4899;"></i> Herramientas Gerenciales (CRM B2B, Biblioteca, Backup)</td>
                                <td><input type="checkbox" class="perm-cb" data-module="herramientas" data-role="super_admin" checked disabled></td>
                                <td><input type="checkbox" class="perm-cb" data-module="herramientas" data-role="admin" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="herramientas" data-role="consultor" checked></td>
                                <td><input type="checkbox" class="perm-cb" data-module="herramientas" data-role="auditor"></td>
                                <td><input type="checkbox" class="perm-cb" data-module="herramientas" data-role="user"></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
"""

# Insert role_matrix_html right after globalSettingsCard in configuracion.html
if "id=\"rolePermissionsCard\"" not in content:
    idx = content.find('</div>', content.find('id="globalSettingsCard"'))
    content = content[:idx + 6] + "\n" + role_matrix_html + content[idx + 6:]

# Add JS functions to save & load Role Permissions
role_perms_script = """
        async function loadRolePermissions() {
            try {
                const res = await fetch(`/api/permissions/form?inst_id=${getInstId()}&program_id=0`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.status === 'success' && data.permissions) {
                        const perms = data.permissions;
                        document.querySelectorAll('.perm-cb').forEach(cb => {
                            const mod = cb.getAttribute('data-module');
                            const role = cb.getAttribute('data-role');
                            if (role !== 'super_admin' && perms[mod]) {
                                cb.checked = perms[mod].includes(role);
                            }
                        });
                    }
                }
            } catch(e) { console.error("Error loading role perms:", e); }
        }

        async function saveRolePermissions() {
            let perms = {};
            document.querySelectorAll('.perm-cb').forEach(cb => {
                const mod = cb.getAttribute('data-module');
                const role = cb.getAttribute('data-role');
                if (!perms[mod]) perms[mod] = ['super_admin'];
                if (cb.checked && !perms[mod].includes(role)) {
                    perms[mod].push(role);
                }
            });

            try {
                const res = await fetch('/api/permissions/form', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        inst_id: getInstId(),
                        program_id: 0,
                        permissions: perms
                    })
                });
                if (res.ok) {
                    Swal.fire('¡Permisos Guardados!', 'La matriz de control de acceso por rol ha sido actualizada.', 'success');
                } else {
                    Swal.fire('Error', 'No se pudieron guardar los permisos.', 'error');
                }
            } catch(e) { Swal.fire('Error', 'Error de red al guardar permisos.', 'error'); }
        }
"""

if "function loadRolePermissions()" not in content:
    content = content.replace("document.addEventListener('DOMContentLoaded',", role_perms_script + "\n        document.addEventListener('DOMContentLoaded',")
    content = content.replace("init();", "init();\n            loadRolePermissions();")

with open(file_config, 'w', encoding='utf-8') as f:
    f.write(content)

print("configuracion.html updated with complete Role Access Control Matrix!")
