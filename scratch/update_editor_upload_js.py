import re

file_path = 'c:/SIAC/templates/formacion.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Inject Quill Initialization in window.onload = init;
init_str = "window.onload = init;"
if "let quillEditorInstance = null;" not in content:
    quill_init = """let quillEditorInstance = null;
        function initQuill() {
            if (!quillEditorInstance && document.getElementById('quillEditor')) {
                quillEditorInstance = new Quill('#quillEditor', {
                    theme: 'snow',
                    modules: {
                        toolbar: [
                            [{ 'header': [1, 2, 3, false] }],
                            ['bold', 'italic', 'underline', 'strike'],
                            [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                            [{ 'color': [] }, { 'background': [] }],
                            ['link', 'image', 'video'],
                            ['clean']
                        ]
                    }
                });
            }
        }
        
        // Custom generic uploader
        async function uploadFileToLMS(file) {
            const formData = new FormData();
            formData.append('file', file);
            try {
                const res = await fetch('/api/upload', { method: 'POST', body: formData });
                const data = await res.json();
                if(data.status === 'success') return data.url;
                else throw new Error(data.message);
            } catch(e) {
                console.error("Upload error:", e);
                alert("Error al subir archivo: " + e.message);
                return null;
            }
        }
        
        window.onload = function() {
            init();
            initQuill();
        };"""
    content = content.replace(init_str, quill_init)

# 2. Update topic editor functions
old_open_topic = """        function openTopicEditorModal(unitIdx, topicIdx) {
            document.getElementById('editorUnitIdx').value = unitIdx;
            document.getElementById('editorTopicIdx').value = topicIdx;
            
            const u = currentCourse.units[unitIdx];
            const t = u.topics[topicIdx];
            
            document.getElementById('topicEditorModalTitle').textContent = `Editor de Tema: ${t.title || 'Tema'}`;
            document.getElementById('richTextEditorBox').innerHTML = t.content || '<p><br></p>';
            
            document.getElementById('topicEditorModal').style.display = 'flex';
        }"""
new_open_topic = """        function openTopicEditorModal(unitIdx, topicIdx) {
            document.getElementById('editorUnitIdx').value = unitIdx;
            document.getElementById('editorTopicIdx').value = topicIdx;
            
            const u = currentCourse.units[unitIdx];
            const t = u.topics[topicIdx];
            
            document.getElementById('topicEditorModalTitle').textContent = `Editor de Tema: ${t.title || 'Tema'}`;
            if(quillEditorInstance) {
                quillEditorInstance.root.innerHTML = t.content || '<p><br></p>';
            }
            
            document.getElementById('topicEditorModal').style.display = 'flex';
        }"""
content = content.replace(old_open_topic, new_open_topic)

old_save_topic = """        async function saveTopicContent() {
            const unitIdx = document.getElementById('editorUnitIdx').value;
            const topicIdx = document.getElementById('editorTopicIdx').value;
            const htmlContent = document.getElementById('richTextEditorBox').innerHTML;"""
new_save_topic = """        async function saveTopicContent() {
            const unitIdx = document.getElementById('editorUnitIdx').value;
            const topicIdx = document.getElementById('editorTopicIdx').value;
            const htmlContent = quillEditorInstance ? quillEditorInstance.root.innerHTML : '';"""
content = content.replace(old_save_topic, new_save_topic)

# 3. Update submitAddUnitResource
old_add_res = """        async function submitAddUnitResource() {
            const unitIdx = document.getElementById('resourceUnitIdx').value;
            const name = document.getElementById('res_name').value;
            const type = document.getElementById('res_type').value;
            const url = document.getElementById('res_url').value;
            
            if (!name) return alert("El nombre del recurso es obligatorio.");
            
            if (!currentCourse.units[unitIdx].resources) {
                currentCourse.units[unitIdx].resources = [];
            }
            
            currentCourse.units[unitIdx].resources.push({
                name: name,
                type: type,
                url: url
            });
            
            const saved = await saveCurrentCourse();"""
new_add_res = """        async function submitAddUnitResource() {
            const unitIdx = document.getElementById('resourceUnitIdx').value;
            const name = document.getElementById('res_name').value;
            const type = document.getElementById('res_type').value;
            const fileInput = document.getElementById('res_file');
            let url = document.getElementById('res_url').value;
            
            if (!name) return alert("El nombre del recurso es obligatorio.");
            
            // Si hay un archivo, subirlo
            if (fileInput.files.length > 0) {
                const uploadedUrl = await uploadFileToLMS(fileInput.files[0]);
                if(uploadedUrl) url = uploadedUrl;
                else return; // falló subida
            }
            
            if (!currentCourse.units[unitIdx].resources) {
                currentCourse.units[unitIdx].resources = [];
            }
            
            currentCourse.units[unitIdx].resources.push({
                name: name,
                type: type,
                url: url
            });
            
            const saved = await saveCurrentCourse();"""
content = content.replace(old_add_res, new_add_res)

# 4. Update submitActivityDelivery
old_submit_act = """        async function submitActivityDelivery(courseId, unitId, actId, title) {
            const answer = prompt(`Ingresa tu respuesta o la direcci\\u00f3n/enlace de tu entrega (Google Drive, OneDrive, etc.) para la actividad:\\n"${title}"`);
            if (answer && answer.trim() !== '') {
                try {
                    // Buscar si existe una entrega anterior para actualizarla
                    const checkResp = await fetch(`/api/submissions?course_id=${courseId}&student_email=${user.email}&activity_id=${actId}&inst_id=${getInstId()}&program_id=${getProgramId()}`);
                    const existingSubs = await checkResp.json();
                    
                    const subData = {
                        course_id: courseId,
                        unit_id: unitId,
                        activity_id: actId,
                        student_email: user.email,
                        student_name: user.name || user.email.split('@')[0],
                        content: answer.trim(),
                        submitted_at: new Date().toISOString(),
                        status: 'pending'
                    };
                    
                    if (existingSubs && existingSubs.length > 0) {
                        subData.id = existingSubs[0].id;
                    }
                    
                    const response = await fetch(`/api/submissions?inst_id=${getInstId()}&program_id=${getProgramId()}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(subData)
                    });
                    
                    if (response.ok) {
                        alert("Actividad enviada exitosamente. \u00a1Buen trabajo!");
                        openStudentCourse(courseId);
                    } else {
                        alert("Error al enviar la actividad.");
                    }
                } catch(e) {
                    console.error(e);
                    alert("Error de conexión al enviar actividad.");
                }
            }
        }"""
        
# Fix regex / literal matching issues by just replacing the whole function body.
new_submit_act = """        async function submitActivityDelivery(courseId, unitId, actId, title) {
            document.getElementById('submitCourseId').value = courseId;
            document.getElementById('submitUnitId').value = unitId;
            document.getElementById('submitActId').value = actId;
            document.getElementById('submitActivityTitleDesc').textContent = "Actividad: " + title;
            document.getElementById('submitTextContent').value = '';
            document.getElementById('submitFile').value = '';
            document.getElementById('studentSubmitActivityModal').style.display = 'flex';
        }
        
        async function confirmActivityDelivery() {
            const btn = document.getElementById('btnConfirmDelivery');
            btn.textContent = "Subiendo...";
            btn.disabled = true;
            
            const courseId = document.getElementById('submitCourseId').value;
            const unitId = document.getElementById('submitUnitId').value;
            const actId = document.getElementById('submitActId').value;
            let contentText = document.getElementById('submitTextContent').value;
            const fileInput = document.getElementById('submitFile');
            
            // Subir archivo si existe
            if (fileInput.files.length > 0) {
                const fileUrl = await uploadFileToLMS(fileInput.files[0]);
                if(fileUrl) {
                    contentText += "\\n\\nArchivo adjunto: " + fileUrl;
                } else {
                    btn.textContent = "Enviar Actividad";
                    btn.disabled = false;
                    return;
                }
            }
            
            if (contentText.trim() === '') {
                alert("Debes escribir un mensaje o adjuntar un archivo.");
                btn.textContent = "Enviar Actividad";
                btn.disabled = false;
                return;
            }
            
            try {
                // Buscar si existe una entrega anterior para actualizarla
                const checkResp = await fetch(`/api/submissions?course_id=${courseId}&student_email=${user.email}&activity_id=${actId}&inst_id=${getInstId()}&program_id=${getProgramId()}`);
                const existingSubs = await checkResp.json();
                
                const subData = {
                    course_id: courseId,
                    unit_id: unitId,
                    activity_id: actId,
                    student_email: user.email,
                    student_name: user.name || user.email.split('@')[0],
                    content: contentText.trim(),
                    submitted_at: new Date().toISOString(),
                    status: 'pending'
                };
                
                if (existingSubs && existingSubs.length > 0) {
                    subData.id = existingSubs[0].id;
                }
                
                const response = await fetch(`/api/submissions?inst_id=${getInstId()}&program_id=${getProgramId()}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(subData)
                });
                
                if (response.ok) {
                    alert("Actividad enviada exitosamente. ¡Buen trabajo!");
                    document.getElementById('studentSubmitActivityModal').style.display = 'none';
                    openStudentCourse(courseId);
                } else {
                    alert("Error al enviar la actividad.");
                }
            } catch(e) {
                console.error(e);
                alert("Error de conexión al enviar actividad.");
            }
            btn.textContent = "Enviar Actividad";
            btn.disabled = false;
        }"""

# Use regex to find and replace submitActivityDelivery robustly because of encoding differences in prompt string
content = re.sub(r'async function submitActivityDelivery[\s\S]*?}\n\s*}', new_submit_act, content, count=1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("JS logic updated successfully.")
