

    let pendingBackupAction = null;
    let pendingBackupArgs = null;

    function requireSecurity(actionFunc, args) {
        pendingBackupAction = actionFunc;
        pendingBackupArgs = args;
        document.getElementById('securityModal').style.display = 'flex';
        document.getElementById('securityPassword').value = '';
        document.getElementById('securityPassword').focus();
    }

    async function confirmSecurity() {
        const pwd = document.getElementById('securityPassword').value;
        if(!pwd) return alert('Ingresa tu contraseña.');
        document.getElementById('securityModal').style.display = 'none';
        
        const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
        const authData = { user_id: user.id, password: pwd };
        
        if(pendingBackupAction) {
            pendingBackupAction(authData, ...pendingBackupArgs);
        }
    }

    async function loadSecurityLogs() {
        try {
            const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
            const res = await fetch('/api/backup/logs', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({ user_id: user.id, inst_id: currentInstId })
            });
            const data = await res.json();
            const tbody = document.getElementById('securityLogsBody');
            if(data.status === 'success') {
                tbody.innerHTML = data.logs.map(l => `
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                        <td style="padding:10px; font-size:0.85rem;">${new Date(l.timestamp).toLocaleString()}</td>
                        <td style="padding:10px; font-size:0.85rem;">${l.user_email}</td>
                        <td style="padding:10px; font-size:0.85rem;"><span style="background:rgba(255,255,255,0.1); padding:2px 6px; border-radius:4px;">${l.action_type}</span></td>
                        <td style="padding:10px; font-size:0.85rem;">
                            <span style="color:${l.status === 'SUCCESS' ? '#10b981' : '#ef4444'}; font-weight:bold;">${l.status}</span>
                        </td>
                    </tr>
                `).join('');
                if(data.logs.length === 0) tbody.innerHTML = '<tr><td colspan="4" style="padding:10px;">No hay registros.</td></tr>';
            }
        } catch(e) {
            console.error('Error fetching logs', e);
        }
    }
    let currentInstId = 1;
    let currentScope = 'inst';
    let backupHistory = [];
    let factoresData = [];

    document.addEventListener('DOMContentLoaded', () => {
        currentInstId = parseInt(localStorage.getItem('inst_id') ||
            new URLSearchParams(window.location.search).get('inst_id') || 1);
        const role = localStorage.getItem('user_role') || '';
        if(role === 'admin') document.getElementById('scopeSuper').style.display = 'flex';
        loadStats();
        loadYearOptions();
        loadPrograms();
        loadFactors();
    });

    function setScope(s) {
        currentScope = s;
        document.querySelectorAll('.scope-pill').forEach(p => p.classList.remove('active'));
        document.getElementById(s === 'inst' ? 'scopeInst' : 'scopeSuper').classList.add('active');
        loadStats();
    }

    function getIid() { return currentScope === 'super' ? 0 : currentInstId; }

    async function loadStats() {
        try {
            const r = await fetch('/api/backup/stats?inst_id=' + getIid());
            const d = await r.json();
            document.getElementById('statEvidencias').textContent = (d.evidencias||0).toLocaleString('es-CO');
            document.getElementById('statFactores').textContent = (d.factores||0).toLocaleString('es-CO');
            document.getElementById('statUsers').textContent = (d.usuarios||0).toLocaleString('es-CO');
            document.getElementById('statInformes').textContent = (d.informes||0).toLocaleString('es-CO');
            document.getElementById('statActividades').textContent = (d.actividades||0).toLocaleString('es-CO');
        } catch(e) {}
    }

    function loadYearOptions() {
        const y0 = new Date().getFullYear();
        const years = Array.from({length:6}, (_,i) => y0 - i);
        ['yearFilter','yearFilter2','evidYearFilter'].forEach(id => {
            const sel = document.getElementById(id);
            years.forEach(y => { const o = document.createElement('option'); o.value = y; o.textContent = y; sel.appendChild(o); });
        });
    }

    async function loadPrograms() {
        try {
            const r = await fetch('/api/programs?inst_id=' + currentInstId);
            const d = await r.json();
            const sel = document.getElementById('programFilter');
            (d||[]).forEach(p => {
                const o = document.createElement('option'); o.value = p.id;
                o.textContent = p.name || ('Programa ' + p.id); sel.appendChild(o);
            });
        } catch(e) {}
    }

    async function loadFactors() {
        try {
            const r = await fetch('/api/factors?inst_id=' + currentInstId + '&program_id=0');
            const d = await r.json();
            factoresData = d || [];
            ['factorFilter','evidFactorFilter'].forEach(id => {
                const sel = document.getElementById(id);
                if(!sel) return;
                factoresData.forEach(f => {
                    const o = document.createElement('option'); o.value = f.id;
                    o.textContent = f.name || f.title || ('Factor ' + f.id); sel.appendChild(o);
                });
            });
        } catch(e) {}
    }

    function loadCaracteristicas() {
        const fid = document.getElementById('factorFilter').value;
        const sel = document.getElementById('caracFilter');
        sel.innerHTML = '<option value="">Todas las Características</option>';
        if(!fid) return;
        const factor = factoresData.find(f => String(f.id) === String(fid));
        if(!factor) return;
        (factor.characteristics || []).forEach(c => {
            const o = document.createElement('option'); o.value = c.id;
            o.textContent = c.name || c.title || ('Característica ' + c.id); sel.appendChild(o);
        });
    }

    function toggleModule(label) { label.classList.toggle('checked'); }

    function showProg(wrapId, fillId, pctId, pct, logId, msg) {
        const w = document.getElementById(wrapId); w.classList.add('visible');
        document.getElementById(fillId).style.width = pct + '%';
        document.getElementById(pctId).textContent = Math.round(pct) + '%';
        if(logId && msg) {
            const l = document.getElementById(logId);
            l.innerHTML += '<div>' + msg + '</div>'; l.scrollTop = l.scrollHeight;
        }
    }
    function updProg(fillId, pctId, pct) {
        document.getElementById(fillId).style.width = pct + '%';
        document.getElementById(pctId).textContent = Math.round(pct) + '%';
    }

    function addHistory(type, modules, status) {
        const now = new Date().toLocaleString('es-CO');
        backupHistory.unshift({now, type, modules, status});
        document.getElementById('historyBody').innerHTML = backupHistory.map(h => `
            <tr>
                <td>${h.now}</td><td><strong>${h.type}</strong></td>
                <td style="color:#64748b;font-size:0.78rem;">${h.modules}</td>
                <td><span class="status-badge ${h.status==='ok'?'badge-ok':'badge-err'}">${h.status==='ok'?'✓ Completado':'✗ Error'}</span></td>
                <td style="color:#94a3b8;font-size:0.75rem;">ZIP descargado</td>
            </tr>`).join('');
    }

    async function downloadBlob(endpoint, payload, filename, isPost=true) {
        const opts = isPost
            ? { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) }
            : { method:'GET' };
        const url = isPost ? endpoint : endpoint + '?' + new URLSearchParams(payload).toString();
        const response = await fetch(url, opts);
        if(!response.ok) {
            const err = await response.json().catch(() => ({message: 'Error ' + response.status}));
            throw new Error(err.message || ('HTTP ' + response.status));
        }
        const blob = await response.blob();
        const a = document.createElement('a');
        a.href = window.URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
    }

    async function startFullBackup(authData) {
        const btn = document.getElementById('btnFullBackup');
        btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
        const modules = [...document.querySelectorAll('#modulesGrid .module-check.checked input')].map(i => i.value);
        if(!modules.length) { alert('Selecciona al menos un módulo.'); btn.disabled=false; btn.innerHTML='<i class="fas fa-download"></i> Generar y Descargar Backup Completo'; return; }
        showProg('progressFull','progressFill','progressPct',10,'progressLog','▶ Conectando al servidor...');
        try {
            await downloadBlob('/api/backup/generate', {
                inst_id: getIid(),
                scope: currentScope,
                ...authData,
                modules,
                year: document.getElementById('yearFilter').value || null,
                program_id: document.getElementById('programFilter').value || null
            }, 'backup_SIAC_' + new Date().toISOString().substring(0,10) + '.zip');
            updProg('progressFill','progressPct',100);
            document.getElementById('progressLog').innerHTML += '<div style="color:#10b981;font-weight:bold;">✓ Backup descargado correctamente.</div>';
            addHistory('Completo', modules.join(', '), 'ok');
        } catch(e) {
            document.getElementById('progressLog').innerHTML += '<div style="color:#ef4444;">✗ Error: ' + e.message + '</div>';
            addHistory('Completo', modules.join(', '), 'error');
        }
        btn.disabled=false; btn.innerHTML='<i class="fas fa-download"></i> Generar y Descargar Backup Completo';
    }

    async function startFactorBackup(authData) {
        const fid = document.getElementById('factorFilter').value;
        if(!fid) { alert('Selecciona un factor primero.'); return; }
        const btn = document.getElementById('btnFactorBackup');
        btn.disabled=true; btn.innerHTML='<i class="fas fa-spinner fa-spin"></i> Generando...';
        showProg('progressFactor','progressFillFactor','progressPctFactor',10,'progressLogFactor','▶ Cargando datos...');
        try {
            await downloadBlob('/api/backup/factor', {
                inst_id: currentInstId,
                factor_id: fid,
                caracteristica_id: document.getElementById('caracFilter').value || null,
                year: document.getElementById('yearFilter2').value || null
            }, 'factor_backup_' + fid + '_' + new Date().toISOString().substring(0,10) + '.zip');
            updProg('progressFillFactor','progressPctFactor',100);
            document.getElementById('progressLogFactor').innerHTML += '<div style="color:#10b981;font-weight:bold;">✓ Descargado.</div>';
            addHistory('Por Factor', 'Factor ID ' + fid, 'ok');
        } catch(e) {
            document.getElementById('progressLogFactor').innerHTML += '<div style="color:#ef4444;">✗ ' + e.message + '</div>';
        }
        btn.disabled=false; btn.innerHTML='<i class="fas fa-download"></i> Descargar por Factor';
    }

    async function startEvidenciasBackup(authData) {
        const btn = document.getElementById('btnEvidBackup');
        btn.disabled=true; btn.innerHTML='<i class="fas fa-spinner fa-spin"></i> Empaquetando...';
        document.getElementById('progressEvidencias').classList.add('visible');
        try {
            await downloadBlob('/api/backup/evidencias', {
                inst_id: currentInstId,
                year: document.getElementById('evidYearFilter').value || null,
                status: document.getElementById('evidStatusFilter').value || null,
                factor_id: document.getElementById('evidFactorFilter').value || null
            }, 'evidencias_SIAC_' + new Date().toISOString().substring(0,10) + '.zip');
            updProg('progressFillEv','progressPctEv',100);
            addHistory('Evidencias', 'Según filtros seleccionados', 'ok');
        } catch(e) { alert('Error: ' + e.message); }
        btn.disabled=false; btn.innerHTML='<i class="fas fa-folder-download"></i> Descargar Evidencias en Carpetas';
    }

    async function exportarModulo(authData, tipo) {
        try {
            await downloadBlob('/api/backup/csv/' + tipo, {inst_id: currentInstId, ...authData}, tipo + '_' + new Date().toISOString().substring(0,10) + '.csv', false);
            addHistory('CSV', tipo, 'ok');
        } catch(e) { alert('Error: ' + e.message); }
    }

    async function exportarTodoCsv(authData) {
        try {
            await downloadBlob('/api/backup/csv/all', {inst_id: currentInstId, ...authData},
                'SIAC_datos_' + new Date().toISOString().substring(0,10) + '.zip');
            addHistory('CSV Completo', 'Todos los módulos', 'ok');
        } catch(e) { alert('Error: ' + e.message); }
    }
