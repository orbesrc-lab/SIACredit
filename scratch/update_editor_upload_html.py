import os
import re

file_path = 'c:/SIAC/templates/formacion.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Quill CDN in <head>
if 'quill.snow.css' not in content:
    head_end = content.find('</head>')
    quill_scripts = """
    <!-- Quill.js for Advanced Editor -->
    <link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
    <script src="https://cdn.quilljs.com/1.3.6/quill.min.js"></script>
    <style>
        .ql-container { font-family: 'Outfit', sans-serif !important; font-size: 1rem; border-radius: 0 0 8px 8px; }
        .ql-toolbar { border-radius: 8px 8px 0 0; background: #f8fafc; }
    </style>
"""
    content = content[:head_end] + quill_scripts + content[head_end:]

# 2. Update topicEditorModal HTML
old_topic_editor = """            <!-- Barra de Herramientas del Editor -->
            <div style="background:#f1f5f9; border:1px solid #cbd5e1; border-bottom:none; border-radius:8px 8px 0 0; padding:8px; display:flex; gap:6px; flex-wrap:wrap; align-items:center;">
                <button class="btn-editor-tool" onclick="execEditorCommand('bold')" title="Negrita"><b>B</b></button>
                <button class="btn-editor-tool" onclick="execEditorCommand('italic')" title="Cursiva"><i>I</i></button>
                <button class="btn-editor-tool" onclick="execEditorCommand('underline')" title="Subrayado"><u>U</u></button>
                <div style="width:1px; height:20px; background:#cbd5e1; margin:0 4px;"></div>
                <button class="btn-editor-tool" onclick="execEditorCommand('justifyLeft')" title="Alinear izquierda">Align Left</button>
                <button class="btn-editor-tool" onclick="execEditorCommand('justifyCenter')" title="Centrar">Align Center</button>
                <button class="btn-editor-tool" onclick="execEditorCommand('justifyRight')" title="Alinear derecha">Align Right</button>
                <div style="width:1px; height:20px; background:#cbd5e1; margin:0 4px;"></div>
                <button class="btn-editor-tool" onclick="promptInsertImage()" title="Insertar Imagen">🖼️ Imagen</button>
                <button class="btn-editor-tool" onclick="promptInsertVideo()" title="Embeber Video">🎥 Video</button>
                <button class="btn-editor-tool" onclick="promptInsertLink()" title="Insertar Enlace">🔗 Enlace</button>
                <button class="btn-editor-tool" onclick="execEditorCommand('removeFormat')" title="Limpiar Formato">🧹 Limpiar</button>
            </div>
            
            <!-- Área de Edición -->
            <div id="richTextEditorBox" contenteditable="true" style="flex:1; border:1px solid #cbd5e1; border-radius:0 0 8px 8px; padding:20px; overflow-y:auto; font-size:1rem; line-height:1.6; outline:none; background:white; min-height: 400px;">
                Escribe o pega el contenido aquí...
            </div>"""

new_topic_editor = """            <!-- Quill.js Editor Container -->
            <div id="quillEditor" style="min-height: 400px; background:white;"></div>"""
content = content.replace(old_topic_editor, new_topic_editor)

# 3. Update unitResourceModal (Change URL to File)
old_res_url = """            <div class="form-group" style="margin-top: 15px;">
                <label>URL / Enlace del Archivo</label>
                <input type="url" id="res_url" placeholder="https://drive.google.com/file/... o Youtube">
            </div>"""
new_res_url = """            <div class="form-group" style="margin-top: 15px;">
                <label>Archivo a Adjuntar o Enlace</label>
                <input type="file" id="res_file" style="margin-bottom: 10px;">
                <input type="url" id="res_url" placeholder="O ingresa un enlace (Ej: Youtube)">
                <small style="color: #64748b; font-size: 0.8rem;">Sube un archivo directo o ingresa un enlace externo.</small>
            </div>"""
content = content.replace(old_res_url, new_res_url)

# 4. Add Student Submit Activity Modal
if 'id="studentSubmitActivityModal"' not in content:
    student_submit_modal = """
    <!-- MODAL: ESTUDIANTE ENVIAR ACTIVIDAD -->
    <div id="studentSubmitActivityModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:1005; align-items:center; justify-content:center;">
        <div style="background:white; border-radius:16px; padding:30px; width:500px; max-width:90vw; box-shadow:0 20px 60px rgba(0,0,0,0.3);">
            <h3 style="margin-bottom:20px; font-size:1.2rem;">Enviar Actividad</h3>
            <p id="submitActivityTitleDesc" style="font-size:0.9rem; color:var(--text-muted); margin-bottom:15px;"></p>
            <input type="hidden" id="submitCourseId">
            <input type="hidden" id="submitUnitId">
            <input type="hidden" id="submitActId">
            
            <div class="form-group">
                <label>Mensaje o Respuesta</label>
                <textarea id="submitTextContent" rows="4" placeholder="Escribe aquí tu respuesta..."></textarea>
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label>Adjuntar Archivo (Opcional)</label>
                <input type="file" id="submitFile">
            </div>
            <div style="display:flex; gap:10px; justify-content:flex-end; margin-top:25px;">
                <button class="btn-ghost" onclick="document.getElementById('studentSubmitActivityModal').style.display='none'">Cancelar</button>
                <button class="btn-primary" onclick="confirmActivityDelivery()" id="btnConfirmDelivery">Enviar Actividad</button>
            </div>
        </div>
    </div>
"""
    body_end = content.find('</body>')
    content = content[:body_end] + student_submit_modal + content[body_end:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML structure updated successfully.")
