import re

def fix_backup_html():
    with open('c:\\SIAC\\templates\\dashboard.html', 'r', encoding='utf-8') as f:
        dash_content = f.read()

    # Extract sidebar from dashboard
    match = re.search(r'(<aside class="sidebar".*?</aside>)', dash_content, re.DOTALL)
    if not match:
        print("Could not find sidebar in dashboard.html")
        return
    sidebar_html = match.group(1)

    with open('c:\\SIAC\\templates\\backup.html', 'r', encoding='utf-8') as f:
        backup_content = f.read()

    # 1. Replace old sidebar with the new one
    backup_content = re.sub(r'<aside class="sidebar".*?</aside>', sidebar_html, backup_content, flags=re.DOTALL)

    # 2. Inject Modal and Logs just before </main>
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
                <table style="width:100%; border-collapse:collapse; color:#333; text-align:left;">
                    <thead>
                        <tr style="border-bottom:1px solid #eee;">
                            <th style="padding:10px;">Fecha</th>
                            <th style="padding:10px;">Usuario</th>
                            <th style="padding:10px;">Tipo</th>
                            <th style="padding:10px;">Estado</th>
                        </tr>
                    </thead>
                    <tbody id="securityLogsBody">
                        <tr><td colspan="4" style="padding:10px; color:#999;">Haz clic en Actualizar Logs</td></tr>
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
    
    # Remove it if it was somehow injected before but brokenly
    backup_content = backup_content.replace(modal_and_logs, "")
    
    # Inject before </main>
    backup_content = backup_content.replace('</main>', modal_and_logs + '\n</main>')

    # 3. Inject app.js before </body> if not present
    if 'app.js' not in backup_content:
        backup_content = backup_content.replace('</body>', '<script src="{{ url_for(\'static\', filename=\'app.js\') }}?v=3.3"></script>\n</body>')

    # Remove buggy onclick="requireSecurity(..., [])" if it was corrupted
    backup_content = backup_content.replace("onclick=\"requireSecurity(startFullBackup, [])\"", "onclick=\"requireSecurity(startFullBackup, [])\"")

    with open('c:\\SIAC\\templates\\backup.html', 'w', encoding='utf-8') as f:
        f.write(backup_content)
    print("backup.html fully fixed.")

if __name__ == '__main__':
    fix_backup_html()
