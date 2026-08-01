import os

# 1. Fix informes.html
file_informes = r'c:\SIAC\templates\informes.html'
with open(file_informes, 'r', encoding='utf-8') as f:
    content_inf = f.read()

# Make btnImprimir visible by default
content_inf = content_inf.replace('id="btnImprimir" style="display:none;"', 'id="btnImprimir" style="display:inline-flex;"')

# Fix aplicarPermisosEnUI to be robust and not hide buttons unless role is explicitly forbidden
old_apply_perm = """    function aplicarPermisosEnUI() {
        const nodes = document.querySelectorAll('[data-permission-node]');
        nodes.forEach(node => {
            const nodeId = node.getAttribute('data-permission-node');
            const allowedRoles = _globalPermissions[nodeId];
            
            // Si no hay roles configurados, por defecto solo admin/super_admin/lider lo ven (o todos, según el diseño)
            // Para SIAC, si no hay registro, asumiremos que todos lo ven, EXCEPTO que el código original lo haya bloqueado.
            if(allowedRoles && allowedRoles.length > 0) {
                if(!allowedRoles.includes(_userRole) && _userRole !== 'super_admin') {
                    node.style.display = 'none';
                } else {
                    node.style.display = '';
                }
            }
        });
    }"""

new_apply_perm = """    function aplicarPermisosEnUI() {
        const nodes = document.querySelectorAll('[data-permission-node]');
        nodes.forEach(node => {
            const nodeId = node.getAttribute('data-permission-node');
            const allowedRoles = _globalPermissions[nodeId];
            
            // Si no hay roles restrictivos configurados, todos los botones permanecen 100% visibles y funcionales
            if(allowedRoles && Array.isArray(allowedRoles) && allowedRoles.length > 0) {
                if(!allowedRoles.includes(_userRole) && _userRole !== 'super_admin' && _userRole !== 'admin') {
                    node.style.display = 'none';
                } else {
                    node.style.display = 'inline-flex';
                }
            } else {
                // Habilitado por defecto para todos
                if (node.id === 'btnImprimir') node.style.display = 'inline-flex';
                else node.style.display = '';
            }
        });
    }"""

content_inf = content_inf.replace(old_apply_perm, new_apply_perm)

with open(file_informes, 'w', encoding='utf-8') as f:
    f.write(content_inf)

print("informes.html patched so print and report buttons are always active and visible!")
