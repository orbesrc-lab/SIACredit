import os
import glob
import re

html_files = glob.glob('c:/SIAC/templates/*.html')

for filepath in html_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    updated = False
    
    if "menuConsultoriaB2B" in content and "b2bMenu.style.display" not in content:
        # We need to inject the logic to show the menu
        # We can just look for "document.addEventListener("DOMContentLoaded"" or similar,
        # or just append a small script block before </body>
        
        script_to_inject = """
<script>
document.addEventListener("DOMContentLoaded", () => {
    const usr = JSON.parse(localStorage.getItem('siac_user') || '{}');
    const r = usr.role || localStorage.getItem('user_role') || '';
    if(['admin', 'super_admin', 'empresa_admin'].includes(r)) {
        const b2b = document.getElementById('menuConsultoriaB2B');
        if(b2b) b2b.style.display = 'block';
    }
});
</script>
</body>
"""
        content = content.replace("</body>", script_to_inject)
        updated = True
        
    if updated:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated JS in {os.path.basename(filepath)}")
