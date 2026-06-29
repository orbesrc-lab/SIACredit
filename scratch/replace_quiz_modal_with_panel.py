with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Strategy: replace the modal approach with a slide-in panel approach
# The quizEditorModal will become a fixed sidebar/panel that doesn't compete with other modals
# This ensures it's ALWAYS on top and inputs work

# Replace the quizEditorModal HTML entirely
old_quiz_modal_start = '        <!-- Modal Creador de Cuestionarios (Docente) -->'
old_quiz_modal_end = '        </div>\n\n        <!-- Modal para Presentar Cuestionario (Estudiante) -->'

start_idx = html.find(old_quiz_modal_start)
end_idx = html.find('        <!-- Modal para Presentar Cuestionario (Estudiante) -->')

if start_idx < 0 or end_idx < 0:
    print(f'START IDX: {start_idx}, END IDX: {end_idx}')
    print('Could not find markers, aborting')
else:
    new_quiz_panel = """        <!-- Panel Creador de Cuestionarios (Docente) -->
        <div id="quizEditorPanel" style="display:none; position:fixed; top:0; right:0; bottom:0; width:min(700px,100vw); background:#fff; z-index:9999; box-shadow:-4px 0 40px rgba(0,0,0,0.25); flex-direction:column; overflow:hidden;">
            <div style="background:linear-gradient(135deg,#6366f1,#a855f7); padding:18px 24px; display:flex; justify-content:space-between; align-items:center; flex-shrink:0;">
                <h3 id="quizEditorTitle" style="margin:0; color:white; font-size:1.05rem; font-weight:700;">Editor de Preguntas</h3>
                <button onclick="document.getElementById('quizEditorPanel').style.display='none'" style="background:rgba(255,255,255,0.25); border:none; color:white; border-radius:50%; width:34px; height:34px; font-size:1.3rem; cursor:pointer; line-height:1;">&times;</button>
            </div>
            <input type="hidden" id="quizEdUnitIdx">
            <input type="hidden" id="quizEdEvIdx">
            <div style="padding:12px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e2e8f0; flex-shrink:0; background:#f8fafc;">
                <span style="font-size:0.85rem; color:#64748b;">Construye las preguntas del examen.</span>
                <button onclick="addQuizQuestion()" style="background:linear-gradient(135deg,#6366f1,#a855f7); color:white; border:none; border-radius:8px; padding:7px 14px; font-size:0.82rem; font-weight:600; cursor:pointer;">+ Nueva Pregunta</button>
            </div>
            <div id="quizQuestionsContainer" style="flex:1; overflow-y:auto; padding:16px 20px; display:flex; flex-direction:column; gap:12px;">
            </div>
            <div style="padding:14px 20px; border-top:1px solid #e2e8f0; flex-shrink:0; background:#f8fafc;">
                <button onclick="saveQuizQuestions()" style="width:100%; background:linear-gradient(135deg,#10b981,#059669); color:white; border:none; border-radius:10px; padding:12px; font-size:0.95rem; font-weight:700; cursor:pointer;">Guardar Cuestionario</button>
            </div>
        </div>

        """
    
    html = html[:start_idx] + new_quiz_panel + html[end_idx:]
    print(f'Replaced quiz editor modal with side panel')
    print(f'New quiz panel found: {"quizEditorPanel" in html}')

# Update JS to use quizEditorPanel instead of quizEditorModal
html = html.replace(
    "document.getElementById('quizEditorModal').style.display = 'flex';",
    "document.getElementById('quizEditorPanel').style.display = 'flex';"
)
html = html.replace(
    "document.getElementById('quizEditorModal').style.display = 'none';",
    "document.getElementById('quizEditorPanel').style.display = 'none';"
)

# Also update the openQuizEditor function reference
print(f'quizEditorModal references remaining: {html.count("quizEditorModal")}')
print(f'quizEditorPanel references: {html.count("quizEditorPanel")}')

with open('c:\\SIAC\\templates\\formacion.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done')
