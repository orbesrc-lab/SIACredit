import re

# 1. Update permissions_enforcer.js
js_file = r'c:\SIAC\static\permissions_enforcer.js'
with open(js_file, 'r', encoding='utf-8') as f:
    js_content = f.read()

# Replace the role mapping block
old_mapping = """    // MAPEO DE ROLES REALES (DB) A COLUMNAS DE LA MATRIZ:
    // Ahora la matriz tiene columnas independientes para: super_admin, admin, lider, operativo, consultor, auditor, profesor, estudiante
    let mappedRole = originalRole;
    if (originalRole === 'inst_admin') {
        mappedRole = 'admin'; // Administrador Institucional usa la columna de Administrador
    }
    
    if (mappedRole === 'super_admin') return; // Bypass global"""

new_mapping = """    // MAPEO DE ROLES REALES (DB) A COLUMNAS DE LA MATRIZ:
    // El rol más alto en la base de datos es 'admin' (etiquetado como Super Admin en UI).
    // El administrador institucional es 'inst_admin' (etiquetado como Administrador en UI).
    let mappedRole = originalRole;
    
    // El Super Administrador (rol 'admin' en DB) nunca pierde acceso.
    if (mappedRole === 'admin') return; // Bypass global"""

js_content = js_content.replace(old_mapping, new_mapping)

with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_content)

# 2. Update configuracion.html Matrix Data Roles
html_file = r'c:\SIAC\templates\configuracion.html'
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# The first column was data-role="super_admin", change it to data-role="admin"
html_content = html_content.replace('data-role="super_admin"', 'data-role="admin"')

# The second column was data-role="admin", change it to data-role="inst_admin"
# We have to be careful because we just changed super_admin to admin.
# Let's use regex to replace specifically the exact checkboxes for the matrix.
# Wait, actually, let's just rebuild the tbody.

tbody_html = '<tbody id="rolePermsTableBody">\\n'
modules = [
    ('autoevaluacion', '<i class="fas fa-chart-line" style="color:#2563eb;"></i> Autoevaluación & Estadísticas Globales'),
    ('informes', '<i class="fas fa-file-alt" style="color:#0284c7;"></i> Informes Institucionales & PDF'),
    ('planificacion', '<i class="fas fa-project-diagram" style="color:#8b5cf6;"></i> Planificación Estratégica & PDI'),
    ('hub_estrategico', '<i class="fas fa-bullseye" style="color:#f59e0b;"></i> Hub Estratégico B2B<br><span style="font-size:0.75rem; font-weight:normal;">(MEFI/MEFE, Porter, Riesgos)</span>'),
    ('iso9001', '<i class="fas fa-certificate" style="color:#10b981;"></i> Sistema ISO 9001<br><span style="font-size:0.75rem; font-weight:normal;">(Mapa, SIPOC, PHVA)</span>'),
    ('capacitacion', '<i class="fas fa-chalkboard-teacher" style="color:#ec4899;"></i> Módulo de Capacitación & Cursos'),
    ('herramientas', '<i class="fas fa-tools" style="color:#64748b;"></i> Herramientas Gerenciales<br><span style="font-size:0.75rem; font-weight:normal;">(CRM B2B, Biblioteca, Backup)</span>')
]

roles = [
    ('admin', 'checked disabled'),       # Super Admin in UI
    ('inst_admin', 'checked'),           # Administrador in UI
    ('lider', 'checked'),
    ('operativo', ''),
    ('consultor', 'checked'),
    ('auditor', 'checked'),
    ('profesor', 'checked'),
    ('estudiante', '')
]

for mod_id, mod_label in modules:
    tbody_html += '                            <tr style="border-bottom: 1px solid #e2e8f0;">\\n'
    tbody_html += f'                                <td style="padding: 10px; text-align: left; font-weight: 600;">{mod_label}</td>\\n'
    for role_id, extra_attrs in roles:
        tbody_html += f'                                <td><input type="checkbox" class="perm-cb" data-module="{mod_id}" data-role="{role_id}" {extra_attrs}></td>\\n'
    tbody_html += '                            </tr>\\n'
tbody_html += '                        </tbody>'

html_content = re.sub(r'<tbody id="rolePermsTableBody">.*?</tbody>', tbody_html, html_content, flags=re.DOTALL)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Fix applied successfully.")
