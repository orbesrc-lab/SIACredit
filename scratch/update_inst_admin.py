import glob

replacement = """        if (user) {
            const rL = { admin: 'Super Admin', inst_admin: 'Admin Inst.', lider: 'Líder', operativo: 'Operativo', estudiante: 'Estudiante', profesor: 'Profesor' };
            const rName = rL[user.role] || (user.role ? user.role.toUpperCase() : 'USUARIO');
            const bClass = (user.role === 'admin' || user.role === 'inst_admin') ? 'aprobado' : 'revision';
            document.getElementById('userInfo').innerHTML = `<span>${user.email}</span> <span class="status ${bClass}" style="margin-left:10px; padding:2px 8px; border-radius:12px; font-size:0.7rem;">${rName}</span>`;
        }"""

for fn in glob.glob(r'c:\SIAC\templates\*.html'):
    with open(fn, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Update menuCrm display logic
    content = content.replace("if(role === 'admin') {", "if(role === 'admin' || role === 'inst_admin') {")
    content = content.replace('if(role === "admin") {', 'if(role === "admin" || role === "inst_admin") {')
    
    # 2. Update userInfo presentation
    content = content.replace("document.getElementById('userInfo').textContent = user ? user.email : '';", replacement)
    content = content.replace('document.getElementById("userInfo").textContent = user ? user.email : "";', replacement)
    
    if content != original_content:
        print(f'Updated {fn}')
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(content)

print('Done!')
