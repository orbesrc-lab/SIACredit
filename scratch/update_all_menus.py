import os
import glob

# Find all HTML files in templates directory
html_files = glob.glob('c:/SIAC/templates/*.html')

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

js_target = "if(['admin', 'super_admin', 'inst_admin', 'lider'].includes(role)) {"
js_replacement = """if(['admin', 'super_admin', 'inst_admin', 'lider', 'empresa_admin'].includes(role)) {
                const backupLink = document.getElementById('menuBackup');
                if(backupLink) backupLink.style.display = 'block';
            }
            if(['admin', 'super_admin', 'empresa_admin'].includes(role)) {
                const b2bMenu = document.getElementById('menuConsultoriaB2B');
                if(b2bMenu) b2bMenu.style.display = 'block';
            }"""

for filepath in html_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    updated = False
    
    # 1. Inject HTML Menu
    if "Consultoría B2B" not in content and "menuConsultoriaB2B" not in content:
        # We need to find Herramientas Gerenciales
        # Look for this exact or similar block:
        # <div class="sidebar-group">
        #     <div class="sidebar-group-title" onclick="toggleSidebarGroup(this)">
        #         <div class="group-icon">
        #             <span>🛠️</span>
        #             <span>Herramientas Gerenciales</span>
        
        # It's safer to use regex or string find
        hg_idx = content.find('<span>Herramientas Gerenciales</span>')
        if hg_idx != -1:
            # Backtrack to find the <div class="sidebar-group"> that contains this
            group_start = content.rfind('<div class="sidebar-group">', 0, hg_idx)
            # Also check for <!-- Herramientas Gerenciales -->
            comment_start = content.rfind('<!-- Herramientas Gerenciales -->', 0, hg_idx)
            
            insert_pos = group_start
            if comment_start != -1 and group_start - comment_start < 100:
                insert_pos = comment_start
                
            if insert_pos != -1:
                content = content[:insert_pos] + menu_code + '\n' + content[insert_pos:]
                updated = True
                
    # 2. Inject JS Logic
    if "menuConsultoriaB2B" in content and "b2bMenu.style.display" not in content:
        if js_target in content:
            content = content.replace(js_target, js_replacement)
            updated = True
            
    if updated:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {os.path.basename(filepath)}")
