import os
import re

NEW_SIDEBAR_MENU = """        <div class="sidebar-menu" id="accordionSidebar">
            <div class="sidebar-group">
                <div class="sidebar-group-title" onclick="toggleSidebarGroup(this)">
                    <div class="group-icon">
                        <span>📂</span>
                        <span>Autoevaluación global</span>
                    </div>
                    <svg class="chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </div>
                <div class="sidebar-submenu">
                    <div class="sidebar-submenu-inner">
                        <a href="dashboard.html" class="sidebar-item">📊 Dashboard Global</a>
                        <a href="autoevaluacion.html" class="sidebar-item">📝 Autoevaluación</a>
                        <a href="evidencias.html" class="sidebar-item">📁 Evidencias</a>
                        <a href="encuestas.html" class="sidebar-item">📋 Encuestas</a>
                        <a href="estadisticas.html" class="sidebar-item">📈 Estadísticas</a>
                    </div>
                </div>
            </div>
            <div class="sidebar-group">
                <div class="sidebar-group-title" onclick="toggleSidebarGroup(this)">
                    <div class="group-icon">
                        <span>📊</span>
                        <span>Análisis Institucional</span>
                    </div>
                    <svg class="chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </div>
                <div class="sidebar-submenu">
                    <div class="sidebar-submenu-inner">
                        <a href="informes.html" class="sidebar-item">📄 Informes</a>
                        <a href="dofa.html" class="sidebar-item">🎯 Diagnóstico DOFA</a>
                    </div>
                </div>
            </div>
            <div class="sidebar-group">
                <div class="sidebar-group-title" onclick="toggleSidebarGroup(this)">
                    <div class="group-icon">
                        <span>⚖️</span>
                        <span>Autorregulación</span>
                    </div>
                    <svg class="chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </div>
                <div class="sidebar-submenu">
                    <div class="sidebar-submenu-inner">
                        <a href="planificacion.html" class="sidebar-item">🗓️ Planificación</a>
                    </div>
                </div>
            </div>
            <a href="formacion.html" class="sidebar-item" style="margin-top: 5px;">🎓 Capacitación</a>
            <div class="sidebar-group">
                <div class="sidebar-group-title" onclick="toggleSidebarGroup(this)">
                    <div class="group-icon">
                        <span>🛠️</span>
                        <span>Herramientas Gerenciales</span>
                    </div>
                    <svg class="chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </div>
                <div class="sidebar-submenu">
                    <div class="sidebar-submenu-inner">
                        <a href="biblioteca.html" class="sidebar-item">📚 Biblioteca</a>
                        <a href="crm.html" class="sidebar-item" id="menuCrm" style="display:none; color: #10b981;">🚀 B2B CRM</a>
                        <a href="/backup" class="sidebar-item" id="menuBackup" style="display:none;">🛡️ Backup y Seguridad</a>
                    </div>
                </div>
            </div>
            <a href="configuracion.html" class="sidebar-item">⚙️ Configuración</a>
        </div>"""

files_to_fix = ['configuracion.html', 'crm.html', 'estadisticas.html']
for fn in files_to_fix:
    path = os.path.join(r'c:\SIAC\templates', fn)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'id="accordionSidebar"' not in content:
        # manual replace
        start_idx = content.find('<div class="sidebar-menu">')
        if start_idx != -1:
            end_idx = content.find('<div style="padding', start_idx)
            if end_idx != -1:
                content = content[:start_idx] + NEW_SIDEBAR_MENU + '\n        ' + content[end_idx:]
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed {fn}")
