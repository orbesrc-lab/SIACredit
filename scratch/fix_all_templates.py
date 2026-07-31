import os
import re

template_dir = r'c:\SIAC\templates'

new_menu = """<div class="sidebar-submenu-inner">
                        <a href="empresa_dashboard.html" class="sidebar-item">📊 Hub Estratégico</a>
                        <a href="empresa_informe_gerencial.html" class="sidebar-item">📑 Informe Gerencial Integral</a>
                    </div>"""

for filename in os.listdir(template_dir):
    if not filename.endswith('.html'):
        continue
        
    path = os.path.join(template_dir, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original_content = content
    
    # 1. Replace the B2B submenu
    # Find id="menuConsultoriaB2B" ... up to the next </div></div></div>
    # A safer way: regex search for <div class="sidebar-group" id="menuConsultoriaB2B".*?<div class="sidebar-submenu-inner">.*?</div>
    pattern = r'(id="menuConsultoriaB2B".*?<div class="sidebar-submenu-inner">).*?(</div>\s*</div>\s*</div>)'
    content = re.sub(pattern, r'\1\n                        <a href="empresa_dashboard.html" class="sidebar-item">📊 Hub Estratégico</a>\n                        <a href="empresa_informe_gerencial.html" class="sidebar-item">📑 Informe Gerencial Integral</a>\n                    \2', content, flags=re.DOTALL)
    
    # 2. Add initPage(); to B2B tools if they don't have it
    if filename.startswith('empresa_'):
        # Check if initPage() is called
        if 'initPage();' not in content:
            content = content.replace('</body>', '    <script>\n        setTimeout(() => { if(typeof initPage === "function") initPage(); }, 200);\n    </script>\n</body>')
            
    if content != original_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filename}")

print("All files updated successfully.")
