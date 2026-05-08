
// User Management Functions for SIACredit

window.loadUsersFromAPI = async function() {
    const container = document.getElementById('usersTable');
    if (!container) return;
    
    try {
        const instId = getInstId();
        const programId = getProgramId();
        const resp = await fetch(`/api/users?inst_id=${instId}&program_id=${programId}`);
        const users = await resp.json();
        
        if (!Array.isArray(users) || users.length === 0) {
            container.innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-muted);">No hay usuarios registrados para esta institución.</div>';
            return;
        }

        const currentUser = JSON.parse(localStorage.getItem('siac_user'));

        container.innerHTML = users.map(u => {
            const isPending = u.name && u.name.startsWith('[PENDING]');
            const cleanName = u.name ? u.name.replace('[PENDING] ', '').replace('[PENDING]', '') : u.email.split('@')[0];
            const effectiveRole = isPending ? 'pending' : u.role;
            
            const roleBadge = effectiveRole === 'admin' || effectiveRole === 'inst_admin' ? 'role-admin' : (effectiveRole === 'pending' ? '' : 'role-leader');
            const roleLabel = { admin: 'Super Admin', inst_admin: 'Admin Inst.', lider: 'Líder', operativo: 'Operativo', pending: 'Pendiente' }[effectiveRole] || effectiveRole;
            const isCurrentUser = currentUser && u.email === currentUser.email;
            
            return `
                <div class="user-item">
                    <div class="user-info">
                        <span class="user-name">${cleanName}</span>
                        <span class="user-role">${u.email} &middot; <em>${roleLabel}</em>${isCurrentUser ? ' • (Tú)' : ''}</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; flex-wrap: wrap; justify-content: flex-end;">
                        <span class="role-badge ${roleBadge}" style="${isPending ? 'background:#fef3c7; color:#d97706;' : ''}">${roleLabel.toUpperCase()}</span>
                        ${isPending && (currentUser.role === 'admin' || currentUser.role === 'inst_admin') ? 
                            `<button onclick="window.activateUser(${u.id}, '${u.email}', '${u.role}')" class="btn-primary" style="font-size:0.7rem; padding: 4px 10px;">Activar</button>` : ''}
                        ${!isCurrentUser && !isPending && (currentUser.role === 'admin' || currentUser.role === 'inst_admin') ? 
                            `<button onclick="window.changeUserRole(${u.id}, '${u.email}', '${u.role}')" class="btn-ghost" style="font-size:0.7rem; color:var(--primary-color); border: 1px solid var(--primary-color); padding: 3px 8px; border-radius: 4px;">Cambiar Rol</button>` : ''}
                        ${!isCurrentUser && !isPending ? 
                            `<button onclick="window.resetUserPass(${u.id}, '${u.email}')" class="btn-ghost" style="font-size:0.7rem; color:var(--text-muted);">Resetear Clave</button>` : ''}
                        ${!isCurrentUser && (currentUser.role === 'admin' || currentUser.role === 'inst_admin') ? 
                            `<button onclick="window.deleteUserFromList(${u.id}, '${u.email}')" class="btn-ghost" style="font-size:0.7rem; color:#ef4444;">Eliminar</button>` : ''}
                    </div>
                </div>`;
        }).join('');
    } catch(e) {
        console.error("Error loading users:", e);
        container.innerHTML = '<div style="padding:20px; color:#ef4444;">Error al cargar usuarios.</div>';
    }
};

window.activateUser = async function(userId, email, currentRole) {
    console.log("Activating user:", email, "Role:", currentRole);
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
        if (resp.ok) {
            alert(`Usuario activado como ${roleToSet === 'inst_admin' ? 'Administrador Institucional' : 'Líder'}.`);
            window.loadUsersFromAPI();
        } else {
            alert('Error activando usuario.');
        }
    } catch(e) {
        alert('Error de conexión.');
    }
};

window.changeUserRole = async function(userId, email, currentRole) {
    console.log("Changing role for:", email, "Current:", currentRole);
    const newRole = prompt(`Cambiar rol para ${email}\n\nRoles disponibles: lider, operativo, inst_admin`, currentRole);
    if (!newRole || newRole === currentRole) return;
    
    if (!['lider', 'operativo', 'inst_admin'].includes(newRole.toLowerCase())) {
        alert("Rol no válido. Usa: lider, operativo o inst_admin");
        return;
    }

    try {
        const resp = await fetch(`/api/users/${userId}/activate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: newRole.toLowerCase() })
        });
        if (resp.ok) {
            alert('Rol actualizado correctamente.');
            window.loadUsersFromAPI();
        } else {
            alert('Error al actualizar el rol.');
        }
    } catch(e) {
        alert('Error de conexión.');
    }
};

window.resetUserPass = async function(userId, email) {
    console.log("Resetting password for:", email);
    if (!confirm(`¿Resetear contraseña de ${email}? Se asignará una temporal.`)) return;
    try {
        const resp = await fetch(`/api/users/${userId}/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        const result = await resp.json();
        if (result.status === 'success') {
            alert(`✅ Contraseña reseteada.\n\nNueva contraseña temporal: ${result.temp_password}\n\nCompartirla de forma segura con el usuario.`);
        } else {
            alert('Error: ' + result.message);
        }
    } catch(e) {
        alert('Error de conexión.');
    }
};

window.deleteUserFromList = async function(userId, email) {
    console.log("Deleting user:", email);
    if (!confirm(`¿Eliminar al usuario ${email}? Esta acción no se puede deshacer.`)) return;
    try {
        const resp = await fetch(`/api/users/${userId}`, { method: 'DELETE' });
        if (resp.ok) {
            window.loadUsersFromAPI();
        } else {
            const data = await resp.json();
            alert('Error al eliminar: ' + (data.message || 'Error desconocido'));
        }
    } catch(e) {
        alert('Error al eliminar usuario.');
    }
};
