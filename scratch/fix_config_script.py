import os

file_config = r'c:\SIAC\templates\configuracion.html'
with open(file_config, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the call at line 2657 and define the functions
functions_code = """
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
    # Insert functions right after init()
    target = "init();\n            loadRolePermissions();"
    if target in content:
        content = content.replace(target, "init();\n            loadRolePermissions();\n" + functions_code)
    else:
        # Fallback target
        content = content.replace("function updateDefaultAIModel() {", functions_code + "\n        function updateDefaultAIModel() {")

with open(file_config, 'w', encoding='utf-8') as f:
    f.write(content)

print("configuracion.html patched with loadRolePermissions and saveRolePermissions functions!")
