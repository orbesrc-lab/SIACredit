
// User Management Functions for SIACredit - V2.1 (Event Delegation)
console.log("SIACredit: users_v2.js loaded - using delegation");

// Create a small debug indicator
(function() {
    const div = document.createElement('div');
    div.style.cssText = "position:fixed; bottom:10px; right:10px; background:rgba(0,0,0,0.7); color:white; padding:5px 10px; border-radius:5px; font-size:10px; z-index:9999; pointer-events:none;";
    div.innerText = "SIAC User Logic Active (v2.1)";
    document.body.appendChild(div);
})();

window.loadUsersFromAPI = async function() {
    const container = document.getElementById('usersTable');
    if (!container) return;
    
    try {
        const instId = typeof getInstId === 'function' ? getInstId() : 0;
        const programId = typeof getProgramId === 'function' ? getProgramId() : 0;
        
        const resp = await fetch(`/api/users?inst_id=${instId}&program_id=${programId}`);
        const users = await resp.json();
        
        if (!Array.isArray(users) || users.length === 0) {
            container.innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-muted);">No hay usuarios registrados.</div>';
            return;
        }

        let currentUser = { role: 'guest', email: '' };
        try {
            const stored = localStorage.getItem('siac_user');
            if (stored) currentUser = JSON.parse(stored);
        } catch(e) {}

        container.innerHTML = users.map(u => {
            const isPending = u.name && u.name.startsWith('[PENDING]');
            const cleanName = u.name ? u.name.replace('[PENDING] ', '').replace('[PENDING]', '') : u.email.split('@')[0];
            const effectiveRole = isPending ? 'pending' : (u.role || 'operativo');
            const isCurrentUser = currentUser && u.email === currentUser.email;
            const canManage = currentUser && (currentUser.role === 'admin' || currentUser.role === 'inst_admin');
            
            const roleBadge = (effectiveRole === 'admin' || effectiveRole === 'inst_admin') ? 'role-admin' : (effectiveRole === 'pending' ? '' : 'role-leader');
            const roleLabel = { admin: 'Super Admin', inst_admin: 'Admin Inst.', lider: 'Líder', operativo: 'Operativo', pending: 'Pendiente' }[effectiveRole] || effectiveRole;

            return `
                <div class="user-item">
                    <div class="user-info">
                        <span class="user-name">${cleanName}</span>
                        <span class="user-role">${u.email} &middot; <em>${roleLabel}</em>${isCurrentUser ? ' • (Tú)' : ''}</span>
                    </div>
                    <div class="user-actions" style="display:flex; align-items:center; gap:8px; flex-wrap: wrap; justify-content: flex-end;">
                        <span class="role-badge ${roleBadge}" style="${isPending ? 'background:#fef3c7; color:#d97706;' : ''}">${roleLabel.toUpperCase()}</span>
                        
                        ${isPending && canManage ? 
                            `<button data-action="activate" data-id="${u.id}" data-email="${u.email}" data-role="${u.role}" class="btn-primary" style="font-size:0.7rem; padding: 4px 10px;">Activar</button>` : ''}
                        
                        ${!isCurrentUser && !isPending && canManage ? 
                            `<button data-action="changeRole" data-id="${u.id}" data-email="${u.email}" data-role="${u.role}" class="btn-ghost" style="font-size:0.7rem; color:var(--primary-color); border: 1px solid var(--primary-color); padding: 3px 8px; border-radius: 4px;">Cambiar Rol</button>` : ''}
                        
                        ${!isCurrentUser && !isPending ? 
                            `<button data-action="resetPass" data-id="${u.id}" data-email="${u.email}" class="btn-ghost" style="font-size:0.7rem; color:var(--text-muted); border: 1px solid #ddd; padding: 3px 8px; border-radius: 4px;">Resetear Clave</button>` : ''}
                        
                        ${!isCurrentUser && canManage ? 
                            `<button data-action="delete" data-id="${u.id}" data-email="${u.email}" class="btn-ghost" style="font-size:0.7rem; color:#ef4444; border: 1px solid #ef4444; padding: 3px 8px; border-radius: 4px;">Eliminar</button>` : ''}
                    </div>
                </div>`;
        }).join('');
    } catch(e) {
        container.innerHTML = '<div style="padding:20px; color:#ef4444;">Error al cargar usuarios.</div>';
    }
};

// Global Event Listener for Delegation
document.addEventListener('click', async function(e) {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    
    const action = btn.getAttribute('data-action');
    const userId = btn.getAttribute('data-id');
    const email = btn.getAttribute('data-email');
    const currentRole = btn.getAttribute('data-role');

    if (action === 'activate') {
        let roleToSet = currentRole;
        if (currentRole === 'lider' || !currentRole || currentRole === 'pending' || currentRole === 'undefined') {
            const choice = confirm(`¿Activar usuario ${email} como Líder de Factor?\n\n(Pulsa CANCELAR si quieres activarlo como Administrador Institucional)`);
            roleToSet = choice ? 'lider' : 'inst_admin';
        }
        try {
            const resp = await fetch(`/api/users/${userId}/activate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: roleToSet })
            });
            if (resp.ok) { alert(`✅ Usuario activado.`); window.loadUsersFromAPI(); }
        } catch(err) { alert('❌ Error'); }
    }

    if (action === 'changeRole') {
        const newRole = prompt(`Cambiar rol para ${email}\n\nRoles: lider, operativo, inst_admin`, currentRole);
        if (!newRole) return;
        const cleanRole = newRole.trim().toLowerCase();
        try {
            const resp = await fetch(`/api/users/${userId}/activate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: cleanRole })
            });
            if (resp.ok) { alert('✅ Rol actualizado.'); window.loadUsersFromAPI(); }
        } catch(err) { alert('❌ Error'); }
    }

    if (action === 'resetPass') {
        if (!confirm(`¿Resetear contraseña de ${email}?`)) return;
        try {
            const resp = await fetch(`/api/users/${userId}/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            const result = await resp.json();
            if (result.status === 'success') alert(`✅ Nueva contraseña: ${result.temp_password}`);
        } catch(err) { alert('❌ Error'); }
    }

    if (action === 'delete') {
        if (!confirm(`⚠️ ¿ELIMINAR a ${email}?`)) return;
        try {
            const resp = await fetch(`/api/users/${userId}`, { method: 'DELETE' });
            if (resp.ok) { alert('✅ Eliminado.'); window.loadUsersFromAPI(); }
            else { const data = await resp.json(); alert('❌ Error: ' + (data.message || 'Error')); }
        } catch(err) { alert('❌ Error'); }
    }
});
