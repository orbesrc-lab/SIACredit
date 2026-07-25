import sys

html_file = 'c:/SIAC/templates/formacion.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add the Modal HTML just before </body>
modal_html = '''
    <!-- MODAL: ACTIVAR ASPIRANTE -->
    <div id="activateAspiranteModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:1001; align-items:center; justify-content:center;">
        <div style="background:white; border-radius:16px; padding:30px; width:500px; max-width:90vw; box-shadow:0 20px 60px rgba(0,0,0,0.3);">
            <h3 style="margin-bottom:10px; font-size:1.2rem;">Activar Aspirante</h3>
            <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 20px;">Selecciona a qué cursos tendrá acceso el estudiante al ser activado.</p>
            <input type="hidden" id="act_aspirante_email">
            <div id="actAspiranteCoursesList" style="max-height: 250px; overflow-y: auto; margin-bottom: 20px; border: 1px solid var(--border-color); border-radius: 8px; padding: 10px;">
                <!-- checkboxes dynamic -->
            </div>
            <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 25px;">
                <button class="btn-ghost" onclick="document.getElementById('activateAspiranteModal').style.display='none'" style="padding: 10px 20px; border-radius: 8px; border: 1px solid transparent; background: transparent; cursor: pointer;">Cancelar</button>
                <button class="btn-primary" onclick="submitActivateAspirante()" style="padding: 10px 20px; border-radius: 8px; background: var(--primary-gradient); color: white; border: none; cursor: pointer;">Confirmar Activación</button>
            </div>
        </div>
    </div>
'''

if 'activateAspiranteModal' not in content:
    content = content.replace('</body>', modal_html + '\n</body>')
    print("Added Activar modal")

# 2. Add the functions directly before the first activateAspirante occurrence
idx = content.find('async function activateAspirante(email, role')

if idx != -1 and 'submitActivateAspirante' not in content:
    new_funcs = '''function activateAspirante(email, role = 'estudiante') {
            openActivateAspiranteModal(email);
        }

        function openActivateAspiranteModal(email) {
            document.getElementById('act_aspirante_email').value = email;
            const student = allStudents.find(s => s.email === email || s.student_email === email);
            const preEnrolled = student && student.enrolled_courses ? student.enrolled_courses : [];
            const listDiv = document.getElementById('actAspiranteCoursesList');
            listDiv.innerHTML = '';
            if (courses.length === 0) {
                listDiv.innerHTML = '<p style="font-size:0.85rem; color:var(--text-muted);">No hay cursos creados.</p>';
            } else {
                courses.forEach(c => {
                    const isChecked = preEnrolled.includes(c.id) ? 'checked' : '';
                    listDiv.innerHTML += `
                        <label style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-size: 0.9rem; cursor: pointer;">
                            <input type="checkbox" class="act-course-checkbox" value="${c.id}" ${isChecked}>
                            ${escapeHtml(c.title || c.name)}
                        </label>
                    `;
                });
            }
            document.getElementById('activateAspiranteModal').style.display = 'flex';
        }

        async function submitActivateAspirante() {
            const email = document.getElementById('act_aspirante_email').value;
            const role = 'estudiante';
            const checkboxes = document.querySelectorAll('.act-course-checkbox:checked');
            const selectedCourses = Array.from(checkboxes).map(cb => cb.value);
            try {
                const uResp = await fetch(`/api/users?inst_id=${getInstId()}&program_id=0`);
                const users = await uResp.json();
                const userObj = users.find(u => u.email === email);
                if (userObj) {
                    const actResp = await fetch(`/api/users/${userObj.id}/activate`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ role: role })
                    });
                    const actRes = await actResp.json();
                    if (actRes.status === 'success') {
                        const student = allStudents.find(s => s.email === email || s.student_email === email);
                        if (student) {
                            student.enrolled_courses = selectedCourses;
                            if (student.name) student.name = student.name.replace(/\\[ASPIRANTE\\]\\s*/g, '').replace(/\\[PENDING[^\\]]*\\]\\s*/g, '').trim();
                            await fetch(`/api/students?inst_id=${getInstId()}`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify(student)
                            });
                        }
                        alert('¡Aspirante activado y matriculado en los cursos seleccionados!');
                        document.getElementById('activateAspiranteModal').style.display = 'none';
                        loadStudentsList();
                    } else {
                        alert('Error al activar: ' + actRes.message);
                    }
                } else {
                    alert('No se encontró una cuenta de usuario para este correo.');
                }
            } catch(e) {
                alert('Error de red al activar aspirante.');
            }
        }
        
        // --- RENAME OLD FUNCTION ---
        async function oldActivateAspirante(email, role'''

    content = content[:idx] + new_funcs + content[idx + len('async function activateAspirante(email, role'):]
    print("Replaced activateAspirante logic")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
