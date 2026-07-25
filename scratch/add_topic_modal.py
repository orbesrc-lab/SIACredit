import re

with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_modal = """
        <!-- Modal para Crear/Editar Tema -->
        <div id="topicModal" class="modal-overlay" style="display: none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 id="topicModalTitle">Nuevo Tema</h3>
                    <button class="close-btn" onclick="document.getElementById('topicModal').style.display='none'">&times;</button>
                </div>
                <input type="hidden" id="topicUnitIdx">
                <div class="form-group">
                    <label>Nombre del Tema</label>
                    <input type="text" id="topicName" class="form-input" placeholder="Ej. Introducción">
                </div>
                <div class="form-group">
                    <label>Tipo de Recurso (Icono)</label>
                    <select id="topicType" class="form-input">
                        <option value="text">Texto/General (📖)</option>
                        <option value="video">Video (🎥)</option>
                        <option value="podcast">Podcast (🎙️)</option>
                        <option value="link">Enlace/Web (🔗)</option>
                        <option value="file">Archivo/PDF (📄)</option>
                    </select>
                </div>
                <button class="btn-primary" style="width:100%;" onclick="submitAddTopic()">Guardar Tema</button>
            </div>
        </div>
"""

js_funcs = """
        function openAddTopicModal(unitIdx) {
            document.getElementById('topicUnitIdx').value = unitIdx;
            document.getElementById('topicName').value = '';
            document.getElementById('topicType').value = 'text';
            document.getElementById('topicModalTitle').textContent = 'Nuevo Tema';
            document.getElementById('topicModal').style.display = 'flex';
        }

        async function submitAddTopic() {
            const unitIdx = parseInt(document.getElementById('topicUnitIdx').value);
            const name = document.getElementById('topicName').value.trim();
            const type = document.getElementById('topicType').value;
            
            if (!name) { alert('El nombre es obligatorio.'); return; }
            
            if (!activeCourse.units[unitIdx].topics) activeCourse.units[unitIdx].topics = [];
            activeCourse.units[unitIdx].topics.push({ id: 't_' + Math.random().toString(36).substr(2, 5), title: name, type: type, content: '' });
            
            document.getElementById('topicModal').style.display = 'none';
            renderSyllabusList();
            await updateCourseOnServer();
        }
"""

for i in range(len(lines)-1, -1, -1):
    if '<!-- Modal para Crear Nuevo Curso -->' in lines[i] or 'id="courseModal"' in lines[i]:
        lines.insert(i, new_modal)
        break

for i in range(len(lines)-1, -1, -1):
    if '</script>' in lines[i]:
        lines.insert(i, js_funcs)
        break

with open('c:\\SIAC\\templates\\formacion.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)
