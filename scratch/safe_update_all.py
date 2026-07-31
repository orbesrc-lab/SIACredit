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

TOGGLE_SCRIPT = """
    <script>
    function toggleSidebarGroup(element) {
        const group = element.parentElement;
        const allGroups = document.querySelectorAll('.sidebar-group');
        allGroups.forEach(g => {
            if(g !== group) g.classList.remove('active');
        });
        group.classList.toggle('active');
    }
    </script>
"""

t_dir = r'c:\SIAC\templates'
for fn in os.listdir(t_dir):
    if not fn.endswith('.html') or fn == 'dashboard.html' or fn in ['configuracion.html', 'crm.html', 'estadisticas.html']:
        continue # Already processed these safely!
        
    path = os.path.join(t_dir, fn)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if '<aside class="sidebar">' not in content:
        continue

    # 1. Replace the sidebar menu block safely
    if 'id="accordionSidebar"' not in content:
        # We find the exact start and end of sidebar-menu
        start_idx = content.find('<div class="sidebar-menu">')
        if start_idx != -1:
            end_idx = content.find('<div class="sidebar-footer">', start_idx)
            if end_idx == -1:
                end_idx = content.find('<div style="padding:20px;', start_idx)
            if end_idx == -1:
                end_idx = content.find('<div style="padding: 20px;', start_idx)
            if end_idx != -1:
                content = content[:start_idx] + NEW_SIDEBAR_MENU + '\n        ' + content[end_idx:]
            else:
                print(f"Warning: Could not replace menu in {fn} (no footer found)")
                
    # 2. Add dashboard-container wrapper
    if '<div class="dashboard-container">\n    <aside class="sidebar">' not in content:
        content = content.replace('<aside class="sidebar">', '<div class="dashboard-container">\n    <aside class="sidebar">', 1)
        content = content.replace('</main>', '</main>\n</div>', 1)

    # 3. Add script if missing
    if 'function toggleSidebarGroup' not in content:
        content = content.replace('</body>', f'{TOGGLE_SCRIPT}\n</body>')

    # 4. Highlight active group
    content = content.replace('class="sidebar-item active"', 'class="sidebar-item"')
    content = content.replace(f'href="{fn}" class="sidebar-item"', f'href="{fn}" class="sidebar-item active"')
    
    if fn in ['autoevaluacion.html', 'evidencias.html', 'encuestas.html', 'evidencias_mod.html']:
        content = re.sub(r'(<div class="sidebar-group")>\s*<div class="sidebar-group-title" onclick="toggleSidebarGroup\(this\)">\s*<div class="group-icon">\s*<span>📂</span>', r'\1 active">\n                <div class="sidebar-group-title" onclick="toggleSidebarGroup(this)">\n                    <div class="group-icon">\n                        <span>📂</span>', content)
    elif fn in ['informes.html', 'dofa.html']:
        content = re.sub(r'(<div class="sidebar-group")>\s*<div class="sidebar-group-title" onclick="toggleSidebarGroup\(this\)">\s*<div class="group-icon">\s*<span>📊</span>', r'\1 active">\n                <div class="sidebar-group-title" onclick="toggleSidebarGroup(this)">\n                    <div class="group-icon">\n                        <span>📊</span>', content)
    elif fn in ['planificacion.html']:
        content = re.sub(r'(<div class="sidebar-group")>\s*<div class="sidebar-group-title" onclick="toggleSidebarGroup\(this\)">\s*<div class="group-icon">\s*<span>⚖️</span>', r'\1 active">\n                <div class="sidebar-group-title" onclick="toggleSidebarGroup(this)">\n                    <div class="group-icon">\n                        <span>⚖️</span>', content)
    elif fn in ['biblioteca.html', 'backup.html']:
        content = re.sub(r'(<div class="sidebar-group")>\s*<div class="sidebar-group-title" onclick="toggleSidebarGroup\(this\)">\s*<div class="group-icon">\s*<span>🛠️</span>', r'\1 active">\n                <div class="sidebar-group-title" onclick="toggleSidebarGroup(this)">\n                    <div class="group-icon">\n                        <span>🛠️</span>', content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Successfully processed {fn}")
