import re

def patch_backup_html():
    with open('c:\\SIAC\\templates\\backup.html', 'r', encoding='utf-8') as f:
        content = f.read()

    if 'id="securityModal"' in content:
        print("Already patched.")
        return

    # 1. Inject Modal and Logs Table HTML before <script>
    modal_and_logs = """
    <!-- Logs de Seguridad -->
    <div class="backup-card" style="margin-top:20px;">
        <div class="card-header">
            <div class="card-icon c-red"><i class="fas fa-shield-alt"></i></div>
            <div><div class="card-title">Auditoría de Seguridad</div><div class="card-subtitle">Registro de descargas de backups</div></div>
        </div>
        <div class="card-body">
            <button class="btn-backup" style="background:#1e293b; color:white; width:auto; margin-bottom:15px;" onclick="loadSecurityLogs()"><i class="fas fa-sync"></i> Actualizar Logs</button>
            <div style="overflow-x:auto;">
                <table style="width:100%; border-collapse:collapse; color:white; text-align:left;">
                    <thead>
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.1);">
                            <th style="padding:10px;">Fecha</th>
                            <th style="padding:10px;">Usuario</th>
                            <th style="padding:10px;">Tipo</th>
                            <th style="padding:10px;">Estado</th>
                        </tr>
                    </thead>
                    <tbody id="securityLogsBody">
                        <tr><td colspan="4" style="padding:10px; color:rgba(255,255,255,0.5);">Haz clic en Actualizar Logs</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Security Modal -->
    <div id="securityModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:9999; justify-content:center; align-items:center;">
        <div style="background:#1e293b; padding:30px; border-radius:12px; width:400px; max-width:90%; border:1px solid rgba(255,255,255,0.1); box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
            <h3 style="color:white; margin-top:0; display:flex; align-items:center; gap:10px;"><i class="fas fa-lock" style="color:#ef4444;"></i> Autenticación Requerida</h3>
            <p style="color:rgba(255,255,255,0.7); font-size:14px; margin-bottom:20px;">Por seguridad, debes ingresar tu contraseña para generar y descargar este archivo. El ZIP estará encriptado con esta misma clave.</p>
            <input type="password" id="securityPassword" placeholder="Contraseña de administrador" style="width:100%; padding:12px; border-radius:6px; border:1px solid rgba(255,255,255,0.2); background:rgba(0,0,0,0.2); color:white; margin-bottom:20px; box-sizing:border-box;">
            <div style="display:flex; gap:10px; justify-content:flex-end;">
                <button onclick="document.getElementById('securityModal').style.display='none'" style="padding:10px 15px; border-radius:6px; border:none; background:rgba(255,255,255,0.1); color:white; cursor:pointer;">Cancelar</button>
                <button onclick="confirmSecurity()" style="padding:10px 15px; border-radius:6px; border:none; background:#3b82f6; color:white; cursor:pointer; font-weight:bold;"><i class="fas fa-check"></i> Verificar y Descargar</button>
            </div>
        </div>
    </div>
"""
    content = content.replace("</div>\n    <script>", modal_and_logs + "</div>\n    <script>")

    # 2. Inject Security JS
    security_js = """
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
"""
    content = content.replace("<script>\n", "<script>\n" + security_js)

    # 3. Modify onclick handlers to use requireSecurity
    content = content.replace('onclick="startFullBackup()"', 'onclick="requireSecurity(startFullBackup, [])"')
    content = content.replace('onclick="startFactorBackup()"', 'onclick="requireSecurity(startFactorBackup, [])"')
    content = content.replace('onclick="startEvidenciasBackup()"', 'onclick="requireSecurity(startEvidenciasBackup, [])"')
    content = content.replace('onclick="exportarTodoCsv()"', 'onclick="requireSecurity(exportarTodoCsv, [])"')
    # Fix exportarModulo to pass the arg
    content = re.sub(r'onclick="exportarModulo\(\'([^\']+)\'\)"', r'onclick="requireSecurity(exportarModulo, [\'\1\'])"', content)

    # 4. Modify the JS functions to accept authData and pass it
    content = content.replace('async function startFullBackup() {', 'async function startFullBackup(authData) {')
    content = content.replace('inst_id: getIid(),\n                scope: currentScope,', 'inst_id: getIid(),\n                scope: currentScope,\n                ...authData,')
    
    content = content.replace('async function startFactorBackup() {', 'async function startFactorBackup(authData) {')
    content = content.replace('inst_id: getIid(), factor_id: fId, caracteristica_id: cId, year: y', 'inst_id: getIid(), factor_id: fId, caracteristica_id: cId, year: y, ...authData')
    
    content = content.replace('async function startEvidenciasBackup() {', 'async function startEvidenciasBackup(authData) {')
    content = content.replace('inst_id: getIid(), program_id: p, year: y', 'inst_id: getIid(), program_id: p, year: y, ...authData')
    
    content = content.replace('async function exportarTodoCsv() {', 'async function exportarTodoCsv(authData) {')
    content = content.replace('{inst_id: currentInstId}', '{inst_id: currentInstId, ...authData}')

    content = content.replace('async function exportarModulo(tipo) {', 'async function exportarModulo(authData, tipo) {')
    # Change GET to POST by changing the last arg of downloadBlob from false to true (or leaving it empty as default is true)
    content = content.replace('downloadBlob(\'/api/backup/csv/\' + tipo, {inst_id: currentInstId}, tipo + \'_\' + new Date().toISOString().substring(0,10) + \'.csv\', false)', 'downloadBlob(\'/api/backup/csv/\' + tipo, {inst_id: currentInstId, ...authData}, tipo + \'_\' + new Date().toISOString().substring(0,10) + \'.csv\')')

    with open('c:\\SIAC\\templates\\backup.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("backup.html successfully patched.")

if __name__ == '__main__':
    patch_backup_html()
