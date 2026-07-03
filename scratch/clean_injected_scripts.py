import glob
import re

injected_script = """<script>
(function(){
    const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
    const role = user.role || localStorage.getItem('user_role') || '';
    if(['admin', 'super_admin', 'inst_admin', 'lider'].includes(role)){
        const b = document.getElementById('menuBackup');
        if(b) b.style.display = 'block';
    }
})();
</script>
</body>"""

for f in glob.glob('c:\\SIAC\\templates\\*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if injected_script in content:
        # Remove ALL instances
        content = content.replace(injected_script, "</body>")
        # Add it back ONLY at the very last </body> tag
        # We do this by replacing the last occurrence of </body>
        parts = content.rsplit("</body>", 1)
        if len(parts) == 2:
            content = parts[0] + injected_script + parts[1]
            
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Fixed {f}")
