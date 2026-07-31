"""
Script to fix sidebar role visibility across all HTML templates.

Rules:
- 'Capacitación' (formacion.html): ONLY admin, super_admin  (HIDE from inst_admin, lider, etc.)
- 'B2B CRM' (crm.html): ONLY admin, super_admin
- 'Consultoría B2B' (menuConsultoriaB2B): admin, super_admin, empresa_admin  
- 'Backup y Seguridad' (menuBackup): admin, super_admin, inst_admin, lider, empresa_admin
- 'Herramientas Gerenciales' (menuCrm is inside this... not the same!)
"""
import os
import glob
import re

template_dir = 'c:/SIAC/templates'
files_updated = []

MASTER_ROLE_SCRIPT = """<script>
document.addEventListener("DOMContentLoaded", () => {
    const _u = JSON.parse(localStorage.getItem('siac_user') || '{}');
    const _r = _u.role || localStorage.getItem('user_role') || '';
    
    // Herramientas de super administrador
    const _adminOnly = ['admin', 'super_admin'];
    
    // CRM B2B link (dentro de Herramientas Gerenciales)
    const _crm = document.getElementById('menuCrm');
    if(_crm) _crm.style.display = _adminOnly.includes(_r) ? 'block' : 'none';
    
    // Capacitacion / Formacion
    const _cap = document.getElementById('menuCapacitacion');
    if(_cap) _cap.style.display = _adminOnly.includes(_r) ? 'block' : 'none';
    
    // Backup y Seguridad
    const _bk = document.getElementById('menuBackup');
    if(_bk) _bk.style.display = ['admin', 'super_admin', 'inst_admin', 'lider', 'empresa_admin'].includes(_r) ? 'block' : 'none';
    
    // Consultoria B2B section
    const _b2b = document.getElementById('menuConsultoriaB2B');
    if(_b2b) _b2b.style.display = ['admin', 'super_admin', 'empresa_admin'].includes(_r) ? 'block' : 'none';
});
</script>"""

STALE_PATTERNS = [
    # old CRM-only admin block
    r"<script>\s*document\.addEventListener\(\"DOMContentLoaded\",\s*\(\)\s*=>\s*\{\s*const\s+user\s*=\s*JSON\.parse[^;]+;\s*(?:const\s+role\s*=\s*[^;]+;\s*)?(?:if\([^)]+\)\s*\{[^}]*menuCrm[^}]*\}[^}]*){1,5}\}\s*\}\);\s*</script>",
    # previous version with inst_admin access 
    r"<script>\s*document\.addEventListener\(\"DOMContentLoaded\",\s*\(\)\s*=>\s*\{\s*const\s+usr?\s*=[^;]+;\s*const\s+r(?:ole)?\s*=[^;]+;\s*if\([^)]+\)\s*\{\s*const\s+crmLink[^}]+\}[^}]*if\([^)]+\)\s*\{\s*const\s+backupLink[^}]+\}[^}]*if\([^)]+\)\s*\{\s*const\s+b2bMenu[^}]+\}\s*\}\);\s*</script>",
    # empresa_matrices pattern
    r"<script>\s*document\.addEventListener\(\"DOMContentLoaded\",\s*\(\)\s*=>\s*\{\s*const\s+usr\s*=[^;]+;\s*const\s+r\s*=[^;]+;\s*if\(\['admin'[^\]]*\]\.includes\(r\)\)\s*\{\s*const\s+b2b\s*=[^;]+;\s*if\(b2b\)\s*b2b\.style\.display\s*=\s*'block';\s*\}\s*\}\);\s*</script>",
]

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    original = content
    
    # 1. Give menuCapacitacion an id (if not already)
    # Pattern: <a href="formacion.html" class="sidebar-item" (optional style)>...Capacitación</a>
    if 'formacion.html' in content and 'id="menuCapacitacion"' not in content:
        # We match the anchor tag and insert the id + display:none
        content = re.sub(
            r'(<a\s+)(href="formacion\.html"\s+class="sidebar-item")',
            r'\1id="menuCapacitacion" \2 style="display:none;"',
            content
        )
    
    # 2. Remove stale role-based scripts
    for pat in STALE_PATTERNS:
        content = re.sub(pat, '', content, flags=re.DOTALL)
    
    # 3. Remove the inline DOMContentLoaded block that only shows CRM for admin
    # These are often in individual pages like configuracion.html 
    stale_simple = re.compile(
        r"<script>\s*document\.addEventListener\(\"DOMContentLoaded\",\s*\(\)\s*=>\s*\{\s*const\s+user\s*=\s*JSON\.parse\(localStorage\.getItem\('siac_user'\)\s*\|\|\s*'\{\}'\);\s*if\(user\.role\s*===\s*'admin'\)\s*\{\s*const\s+crmLink\s*=\s*document\.getElementById\('menuCrm'\);\s*if\(crmLink\)\s*crmLink\.style\.display\s*=\s*'block';\s*\}\s*\}\);\s*</script>",
        re.DOTALL
    )
    content = stale_simple.sub('', content)
    
    # 4. Inject master script before </body>  (only if not already present)
    if 'const _adminOnly' not in content:
        content = content.replace('</body>', MASTER_ROLE_SCRIPT + '\n</body>')
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

for filepath in glob.glob(os.path.join(template_dir, '*.html')):
    if update_file(filepath):
        files_updated.append(os.path.basename(filepath))

print(f"Updated {len(files_updated)} files:")
for f in files_updated:
    print(f"  - {f}")
