// SIACredit - User Management v3 (onclick directo)
console.log('[SIAC] users_v2.js v3 cargado');

window._siacUsers_loadUsersFromAPI = async function() {
    var container = document.getElementById('usersTable');
    if (!container) { console.warn('[SIAC] usersTable not found'); return; }

    container.innerHTML = '<div style="padding:20px;text-align:center;color:#888;">Cargando...</div>';

    var instId = 0, programId = 0, currentUser = { role: 'guest', email: '' };
    try {
        var stored = localStorage.getItem('siac_user');
        if (stored) currentUser = JSON.parse(stored);
        instId = currentUser.inst_id || 0;
        programId = currentUser.program_id || 0;
    } catch(e) {}

    try {
        var resp = await fetch('/api/users?inst_id=' + instId + '&program_id=' + programId);
        var users = await resp.json();

        if (!Array.isArray(users) || users.length === 0) {
            container.innerHTML = '<div style="padding:20px;text-align:center;color:#888;">No hay usuarios en este programa. Selecciona un programa primero.</div>';
            return;
        }

        var canManage = (currentUser.role === 'admin' || currentUser.role === 'inst_admin');
        var html = '';

        for (var i = 0; i < users.length; i++) {
            var u = users[i];
            var isPending = u.name && u.name.indexOf('[PENDING]') === 0;
            var cleanName = u.name ? u.name.replace('[PENDING] ', '').replace('[PENDING]', '') : u.email.split('@')[0];
            var effectiveRole = isPending ? 'pending' : (u.role || 'operativo');
            var isCurrentUser = (u.email === currentUser.email);

            var roleLabels = { admin: 'Super Admin', inst_admin: 'Admin Inst.', lider: 'Líder', operativo: 'Operativo', pending: 'Pendiente' };
            var roleLabel = roleLabels[effectiveRole] || effectiveRole;
            var badgeStyle = isPending
                ? 'background:#fef3c7;color:#d97706;padding:3px 8px;border-radius:12px;font-size:0.72rem;font-weight:700;'
                : (effectiveRole === 'admin' || effectiveRole === 'inst_admin')
                    ? 'background:#fee2e2;color:#b91c1c;padding:3px 8px;border-radius:12px;font-size:0.72rem;font-weight:700;'
                    : 'background:#e0e7ff;color:#4338ca;padding:3px 8px;border-radius:12px;font-size:0.72rem;font-weight:700;';

            html += '<div class="user-item" style="display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:1px solid #e5e7eb;background:#fafafa;">';
            html += '<div>';
            html += '<div style="font-weight:600;font-size:0.95rem;">' + cleanName + (isCurrentUser ? ' <em style="color:#888;font-size:0.8rem;">(Tú)</em>' : '') + '</div>';
            html += '<div style="font-size:0.8rem;color:#6b7280;">' + u.email + ' · ' + roleLabel + '</div>';
            html += '</div>';

            html += '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:flex-end;">';
            html += '<span style="' + badgeStyle + '">' + roleLabel.toUpperCase() + '</span>';

            if (isPending && canManage) {
                html += '<button style="font-size:0.72rem;padding:4px 10px;background:#5b45ff;color:white;border:none;border-radius:5px;cursor:pointer;" onclick="window.siacActivateUser(' + u.id + ', \'' + u.email + '\', \'' + (u.role || '') + '\')">Activar</button>';
            }
            if (!isCurrentUser && !isPending && canManage) {
                html += '<button style="font-size:0.72rem;padding:3px 10px;background:white;color:#5b45ff;border:1px solid #5b45ff;border-radius:5px;cursor:pointer;" onclick="window.siacChangeRole(' + u.id + ', \'' + u.email + '\', \'' + (u.role || '') + '\')">Cambiar Rol</button>';
            }
            if (!isCurrentUser && !isPending) {
                html += '<button style="font-size:0.72rem;padding:3px 10px;background:white;color:#6b7280;border:1px solid #d1d5db;border-radius:5px;cursor:pointer;" onclick="window.siacResetPass(' + u.id + ', \'' + u.email + '\')">Resetear Clave</button>';
            }
            if (!isCurrentUser && canManage) {
                html += '<button style="font-size:0.72rem;padding:3px 10px;background:white;color:#ef4444;border:1px solid #ef4444;border-radius:5px;cursor:pointer;" onclick="window.siacDeleteUser(' + u.id + ', \'' + u.email + '\')">Eliminar</button>';
            }

            html += '</div></div>';
        }

        container.innerHTML = html;
    } catch(err) {
        console.error('[SIAC] Error loading users:', err);
        container.innerHTML = '<div style="padding:20px;color:#ef4444;">Error al cargar usuarios: ' + err.message + '</div>';
    }
};

// Alias global para compatibilidad con el init()
window.loadUsersFromAPI = window._siacUsers_loadUsersFromAPI;

window.siacActivateUser = async function(userId, email, currentRole) {
    var choice = confirm('¿Activar ' + email + ' como Líder?\n\nPresione CANCELAR para activar como Administrador Institucional.');
    var roleToSet = choice ? 'lider' : 'inst_admin';
    try {
        var resp = await fetch('/api/users/' + userId + '/activate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: roleToSet })
        });
        if (resp.ok) { alert('✅ Usuario activado como ' + (roleToSet === 'inst_admin' ? 'Admin Inst.' : 'Líder')); window.loadUsersFromAPI(); }
        else { alert('❌ Error al activar.'); }
    } catch(e) { alert('❌ Error de red.'); }
};

window.siacChangeRole = async function(userId, email, currentRole) {
    var newRole = prompt('Nuevo rol para ' + email + '\n\nOpciones: lider, operativo, inst_admin', currentRole);
    if (!newRole) return;
    newRole = newRole.trim().toLowerCase();
    if (!['lider', 'operativo', 'inst_admin'].includes(newRole)) { alert('❌ Rol inválido.'); return; }
    try {
        var resp = await fetch('/api/users/' + userId + '/activate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: newRole })
        });
        if (resp.ok) { alert('✅ Rol actualizado a: ' + newRole); window.loadUsersFromAPI(); }
        else { alert('❌ Error al cambiar rol.'); }
    } catch(e) { alert('❌ Error de red.'); }
};

window.siacResetPass = async function(userId, email) {
    if (!confirm('¿Resetear contraseña de ' + email + '?')) return;
    try {
        var resp = await fetch('/api/users/' + userId + '/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        var result = await resp.json();
        if (result.status === 'success') {
            alert('✅ Contraseña temporal: ' + result.temp_password);
        } else {
            alert('❌ Error: ' + result.message);
        }
    } catch(e) { alert('❌ Error de red.'); }
};

window.siacDeleteUser = async function(userId, email) {
    if (!confirm('⚠️ ¿Eliminar a ' + email + '? Esta acción es irreversible.')) return;
    try {
        var resp = await fetch('/api/users/' + userId, { method: 'DELETE' });
        if (resp.ok) { alert('✅ Usuario eliminado.'); window.loadUsersFromAPI(); }
        else {
            var data = await resp.json();
            alert('❌ Error: ' + (data.message || 'No se pudo eliminar.'));
        }
    } catch(e) { alert('❌ Error de red.'); }
};
