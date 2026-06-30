import os

def insert_crm_link(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if 'href="crm.html"' in content:
        return
        
    # Find configuracion.html link in sidebar
    target = '<a href="configuracion.html"'
    if target in content:
        # We will dynamically show the CRM link via JS, or just add it and hide via CSS for non-admins
        replacement = """<a href="crm.html" class="sidebar-item" id="menuCrm" style="display:none; color: #10b981;">🚀 CRM B2B</a>
            <a href="configuracion.html" """
        content = content.replace(target, replacement)
        
        # We also need a small script to show the link if user.role == 'admin'
        script_tag = """<script>
        document.addEventListener("DOMContentLoaded", () => {
            const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
            if(user.role === 'admin') {
                const crmLink = document.getElementById('menuCrm');
                if(crmLink) crmLink.style.display = 'block';
            }
        });
        </script>"""
        
        if "</body>" in content:
            content = content.replace("</body>", script_tag + "\n</body>")
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filepath}")

import glob

template_dir = r"c:\SIAC\templates"
for filepath in glob.glob(os.path.join(template_dir, "*.html")):
    if not filepath.endswith("crm.html"):
        insert_crm_link(filepath)
