import sys
import re

html_file = 'c:/SIAC/templates/formacion.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add the Change Password button to studentCourseSelectorBox
target_box = '<div id="studentCourseSelectorBox" class="editor-container" style="max-width: 1000px; margin: 0 auto;">\n                      <p style="font-size: 0.95rem; color: var(--text-muted); margin-bottom: 25px;">Selecciona uno de tus cursos asignados para ingresar al Aula Virtual y acceder a tus materiales de estudio.</p>'
replacement_box = '''<div id="studentCourseSelectorBox" class="editor-container" style="max-width: 1000px; margin: 0 auto;">
                      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                          <p style="font-size: 0.95rem; color: var(--text-muted); margin: 0;">Selecciona uno de tus cursos asignados para ingresar al Aula Virtual y acceder a tus materiales de estudio.</p>
                          <button class="btn-ghost" onclick="document.getElementById('studentPasswordModal').style.display='flex'" style="color: #6366f1; border: 1px solid rgba(99, 102, 241, 0.3); font-weight: 600; padding: 8px 16px; border-radius: 8px;">🔒 Cambiar Contraseña</button>
                      </div>'''

if target_box in content:
    content = content.replace(target_box, replacement_box)
    print("Replaced studentCourseSelectorBox")

# 2. Add the modal HTML just before the end of </body>
modal_html = '''
    <!-- MODAL: CAMBIAR CONTRASEÑA ESTUDIANTE -->
    <div id="studentPasswordModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:1001; align-items:center; justify-content:center;">
        <div style="background:white; border-radius:16px; padding:30px; width:400px; max-width:90vw; box-shadow:0 20px 60px rgba(0,0,0,0.3);">
            <h3 style="margin-bottom:20px; font-size:1.2rem;">Cambiar Contraseña</h3>
            <div class="form-group">
                <label>Contraseña Actual</label>
                <input type="password" id="stud_old_pwd" style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; outline: none;">
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label>Nueva Contraseña</label>
                <input type="password" id="stud_new_pwd" style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; outline: none;">
            </div>
            <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 25px;">
                <button class="btn-ghost" onclick="document.getElementById('studentPasswordModal').style.display='none'">Cancelar</button>
                <button class="btn-primary" onclick="submitStudentPasswordChange()">Cambiar</button>
            </div>
        </div>
    </div>
'''

if 'studentPasswordModal' not in content:
    content = content.replace('</body>', modal_html + '\n</body>')
    print("Added modal HTML")

# 3. Add the JS function
js_function = '''
        async function submitStudentPasswordChange() {
            const oldPwd = document.getElementById('stud_old_pwd').value;
            const newPwd = document.getElementById('stud_new_pwd').value;
            if(!oldPwd || !newPwd) { alert('Comleta ambos campos'); return; }
            
            const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
            
            try {
                const res = await fetch('/api/change-password', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        email: user.email,
                        old_password: oldPwd,
                        new_password: newPwd
                    })
                });
                const data = await res.json();
                if(data.status === 'success') {
                    alert('Contraseña actualizada con éxito');
                    document.getElementById('studentPasswordModal').style.display = 'none';
                    document.getElementById('stud_old_pwd').value = '';
                    document.getElementById('stud_new_pwd').value = '';
                } else {
                    alert('Error: ' + data.message);
                }
            } catch(e) { alert('Error de red'); }
        }
'''

if 'submitStudentPasswordChange' not in content:
    content = content.replace('</script>', js_function + '\n</script>')
    print("Added JS function")

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done.")
