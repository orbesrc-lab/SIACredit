
        const user = JSON.parse(localStorage.getItem('siac_user')) || { email: 'orbesrc@gmail.com', role: 'admin' };
        const roleLabel = user.role ? user.role.toUpperCase() : 'ADMIN';
        document.getElementById('userInfo').innerHTML = `<span>${user.email}</span> <span class="status ${user.role === 'admin' || user.role === 'inst_admin' ? 'aprobado' : 'revision'}" style="margin-left:10px; padding:2px 8px; border-radius:12px; font-size:0.7rem;">${roleLabel}</span>`;
        
        function logout() { localStorage.removeItem('siac_user'); window.location.href = 'login.html'; }

        async function loadInstitution() {
            const resp = await fetch(`/api/institution?inst_id=${getInstId()}`);
            const data = await resp.json();
            document.getElementById('inst_name_display').textContent = data.name;
            if (data.logo_url) {
                const img = document.getElementById('inst_logo_img');
                img.src = data.logo_url; img.style.display = 'block';
            }
        }
        loadInstitution();
        loadNotifications();
        updateContextBreadcrumb();

        // --- FUNCIONES GESTIÓN DE NOTIFICACIONES ---
        async function loadNotifications() {
            const user = JSON.parse(localStorage.getItem('siac_user'));
            if (!user || !user.email) return;
            
            try {
                const resp = await fetch(`/api/notificaciones?inst_id=${getInstId()}&program_id=${getProgramId()}&email=${user.email}`);
                const notifications = await resp.json();
                
                const bell = document.getElementById('notifBell');
                const badge = document.getElementById('notifBadge');
                const list = document.getElementById('notifList');
                
                const unreadCount = notifications.filter(n => !n.leido).length;
                
                if (unreadCount > 0) {
                    badge.style.display = 'flex';
                    badge.textContent = unreadCount;
                } else {
                    badge.style.display = 'none';
                }
                
                if (notifications.length === 0) {
                    list.innerHTML = `<div class="notif-empty">No tienes notificaciones.</div>`;
                    return;
                }
                
                let html = '';
                notifications.forEach(n => {
                    const unreadClass = n.leido ? '' : 'unread';
                    const timeStr = new Date(n.created_at).toLocaleString();
                    html += `
                        <div class="notif-item ${unreadClass}" onclick="markAsRead(${n.id})">
                            <div class="notif-title">${n.titulo}</div>
                            <div class="notif-desc">${n.mensaje}</div>
                            <span class="notif-time">${timeStr}</span>
                        </div>
                    `;
                });
                list.innerHTML = html;
            } catch (e) {
                console.error("Error loading notifications:", e);
            }
        }
        
        async function markAsRead(id) {
            try {
                const resp = await fetch(`/api/notificaciones/${id}/read`, { method: 'POST' });
                if (resp.ok) {
                    loadNotifications();
                }
            } catch(e) { console.error(e); }
        }
        
        async function markAllAsRead() {
            const user = JSON.parse(localStorage.getItem('siac_user'));
            if (!user || !user.email) return;
            
            try {
                const resp = await fetch(`/api/notificaciones/read-all?inst_id=${getInstId()}&program_id=${getProgramId()}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: user.email })
                });
                if (resp.ok) {
                    loadNotifications();
                }
            } catch(e) { console.error(e); }
        }
        
        function toggleNotifDropdown(e) {
            e.stopPropagation();
            document.getElementById('notifDropdown').classList.toggle('show');
        }
        
        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            const dd = document.getElementById('notifDropdown');
            if (dd) dd.classList.remove('show');
        });
        
        // --- EXPORTAR PLAN DE MEJORAMIENTO A EXCEL ---
        function exportPlanesExcel() {
            const table = document.getElementById('tablaPlanesMejora');
            if (!table) {
                alert("Primero genere el informe para cargar los planes de mejora.");
                return;
            }
            
            // Estilos CSS para dar presentación premium al archivo de Excel
            const styles = `
                <style>
                    table { border-collapse: collapse; width: 100%; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
                    th { background-color: #d97706; color: white; font-weight: bold; text-align: left; padding: 12px; border: 1px solid #e2e8f0; }
                    td { padding: 10px; border: 1px solid #e2e8f0; }
                    tr:nth-child(even) { background-color: #f9fafb; }
                    .badge-completado { background-color: #dcfce7; color: #166534; font-weight: bold; border-radius: 4px; padding: 2px 6px; }
                    .badge-vencido { background-color: #fee2e2; color: #991b1b; font-weight: bold; border-radius: 4px; padding: 2px 6px; }
                    .badge-proceso { background-color: #dbeafe; color: #1e40af; font-weight: bold; border-radius: 4px; padding: 2px 6px; }
                    .badge-pendiente { background-color: #fef3c7; color: #92400e; font-weight: bold; border-radius: 4px; padding: 2px 6px; }
                </style>
            `;
            
            // Clean table for excel presentation
            const tempTable = table.cloneNode(true);
            
            // Replace progress bar with text (progress is column index 10, status is column index 11)
            tempTable.querySelectorAll('tr').forEach(row => {
                const progressCell = row.cells[10];
                if (progressCell && progressCell.querySelector('span')) {
                    const val = progressCell.querySelector('span').textContent;
                    progressCell.innerHTML = val;
                }
                const badgeCell = row.cells[11];
                if (badgeCell && badgeCell.querySelector('span')) {
                    const badge = badgeCell.querySelector('span');
                    const text = badge.textContent;
                    let styleClass = 'badge-pendiente';
                    if (text === 'Completado') styleClass = 'badge-completado';
                    else if (text === 'Vencido') styleClass = 'badge-vencido';
                    else if (text === 'En proceso') styleClass = 'badge-proceso';
                    
                    badgeCell.innerHTML = `<span class="${styleClass}">${text}</span>`;
                }
            });
            
            const html = `
                <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
                <head>
                    <meta charset="UTF-8">
                    \${styles}
                </head>
                <body>
                    <h2>Plan de Mejoramiento Consolidado — \${document.getElementById('inst_name_display').textContent}</h2>
                    <br>
                    \${tempTable.outerHTML}
                

    <script>
    function toggleSidebarGroup(element) {
        const group = element.parentElement;
        const allGroups = document.querySelectorAll('.sidebar-group');
        allGroups.forEach(g => {
            if(g !== group) g.classList.remove('active');
        });
        group.classList.toggle('active');
    }
    