import os

files_to_update = [
    "c:/SIAC/templates/empresa_dashboard.html",
    "c:/SIAC/templates/empresa_matrices.html",
    "c:/SIAC/templates/empresa_porter.html"
]

menu_code = """
            <!-- Diagnóstico Empresarial -->
            <div class="sidebar-group" id="menuConsultoriaB2B" style="display:none;">
                <div class="sidebar-group-title" onclick="toggleSidebarGroup(this)">
                    <div class="group-icon">
                        <span>💼</span>
                        <span style="color: #6366f1; font-weight: 600;">Consultoría B2B</span>
                    </div>
                    <svg class="chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </div>
                <div class="sidebar-submenu">
                    <div class="sidebar-submenu-inner">
                        <a href="empresa_dashboard.html" class="sidebar-item">📊 Hub Estratégico</a>
                        <a href="empresa_matrices.html" class="sidebar-item">🛠️ Matrices (MEFI/MEFE)</a>
                        <a href="empresa_porter.html" class="sidebar-item">📈 Análisis Competitivo</a>
                    </div>
                </div>
            </div>
"""

for filepath in files_to_update:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "Consultoría B2B" not in content:
        # Insert before Herramientas Gerenciales
        target = '            <div class="sidebar-group">\n                <div class="sidebar-group-title" onclick="toggleSidebarGroup(this)">\n                    <div class="group-icon">\n                        <span>🛠️</span>\n                        <span>Herramientas Gerenciales</span>'
        
        if target in content:
            content = content.replace(target, menu_code + '\n' + target)
        
        # Also need to update the Javascript to unhide it
        js_target = "if(['admin', 'super_admin', 'inst_admin', 'lider'].includes(role)) {"
        js_replacement = """if(['admin', 'super_admin', 'inst_admin', 'lider', 'empresa_admin'].includes(role)) {
                const backupLink = document.getElementById('menuBackup');
                if(backupLink) backupLink.style.display = 'block';
            }
            if(['admin', 'super_admin', 'empresa_admin'].includes(role)) {
                const b2bMenu = document.getElementById('menuConsultoriaB2B');
                if(b2bMenu) b2bMenu.style.display = 'block';
            }"""
        content = content.replace("if(['admin', 'super_admin', 'inst_admin', 'lider'].includes(role)) {", js_replacement)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"Already updated {filepath}")
