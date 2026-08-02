import re

file_path = r'c:\SIAC\templates\configuracion.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the roles dropdowns using exact string replacement (regex without DOTALL)
content = re.sub(
    r'<select id="inv_role"[^>]*>.*?<option value="inst_admin"',
    '<select id="inv_role" style="width:100%; padding:10px; border:1px solid var(--border-color); border-radius:8px;">\n'
    '                            <option value="estudiante">Estudiante / Participante</option>\n'
    '                            <option value="profesor">Profesor / Docente</option>\n'
    '                            <option value="lider">Líder de Factor</option>\n'
    '                            <option value="operativo">Operativo</option>\n'
    '                            <option value="consultor">Consultor B2B</option>\n'
    '                            <option value="auditor">Auditor Calidad</option>\n'
    '                            <option value="inst_admin"',
    content,
    flags=re.DOTALL
)

content = re.sub(
    r'<select id="changeRoleSelect"[^>]*>.*?<option value="inst_admin"',
    '<select id="changeRoleSelect" style="width:100%; padding:10px; border:1px solid #d1d5db; border-radius:8px; font-size:0.95rem;" onchange="onChangeRoleSelectChanged(this.value)">\n'
    '                        <option value="estudiante">Estudiante / Participante</option>\n'
    '                        <option value="profesor">Profesor / Docente</option>\n'
    '                        <option value="lider">Líder de Factor</option>\n'
    '                        <option value="operativo">Operativo</option>\n'
    '                        <option value="consultor">Consultor B2B</option>\n'
    '                        <option value="auditor">Auditor Calidad</option>\n'
    '                        <option value="inst_admin"',
    content,
    flags=re.DOTALL
)

# Define the new header
new_header = """<th style="padding: 12px;">👑 Super Admin</th>
                                <th style="padding: 12px;">🏢 Administrador</th>
                                <th style="padding: 12px;">⭐ Líder</th>
                                <th style="padding: 12px;">⚙️ Operativo</th>
                                <th style="padding: 12px;">💼 Consultor</th>
                                <th style="padding: 12px;">🔍 Auditor</th>
                                <th style="padding: 12px;">👨‍🏫 Docente</th>
                                <th style="padding: 12px;">🎓 Estudiante</th>
                            </tr>"""

# Replace header carefully by matching the exact table header row for permissions
content = re.sub(
    r'<th style="padding: 12px; width: 14%;">👑 Super Admin</th>.*?<th style="padding: 12px; width: 14%;">👨‍🏫 Docente / Usuario</th>\s*</tr>',
    new_header,
    content,
    flags=re.DOTALL
)

# Define rows
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
    ('super_admin', 'checked disabled'),
    ('admin', 'checked'),
    ('lider', 'checked'),
    ('operativo', ''),
    ('consultor', 'checked'),
    ('auditor', 'checked'),
    ('profesor', 'checked'),
    ('estudiante', '')
]

tbody_html = '<tbody id="rolePermsTableBody">\n'
for mod_id, mod_label in modules:
    tbody_html += '                            <tr style="border-bottom: 1px solid #e2e8f0;">\n'
    tbody_html += f'                                <td style="padding: 10px; text-align: left; font-weight: 600;">{mod_label}</td>\n'
    
    for role_id, extra_attrs in roles:
        tbody_html += f'                                <td><input type="checkbox" class="perm-cb" data-module="{mod_id}" data-role="{role_id}" {extra_attrs}></td>\n'
        
    tbody_html += '                            </tr>\n'
tbody_html += '                        </tbody>'

# Replace tbody carefully
content = re.sub(
    r'<tbody id="rolePermsTableBody">.*?</tbody>',
    tbody_html,
    content,
    flags=re.DOTALL
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Matrix updated successfully.")
