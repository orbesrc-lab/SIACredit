import re

with open('c:/SIAC/templates/formacion.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace the presentQuiz call
content = re.sub(
    r'onclick="presentQuiz\([^)]+\)"',
    r'onclick="presentQuiz(\'${courseId}\', \'${unit.id}\', \'${ev.id}\', \'${escapeHtml(ev.title).replace(/\\\'/g, \\"\\\\\\\\\'\\")}\', ${ev.min_grade || 3.0}, ${ev.max_grade || 5.0}, \'${escapeHtml(JSON.stringify(ev.questions || [])).replace(/\\\'/g, \\"\\\\\\\\\'\\")}\')"',
    content
)

# 2. Add Quiz Modal Content HTML
old_modal = """    <div id="quizModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:1001; align-items:center; justify-content:center;">
        <div style="background:white; border-radius:16px; width:90%; max-width:600px; max-height:90vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);">
            <div style="padding:25px; border-bottom:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center; background:linear-gradient(to right, #f8fafc, #ffffff);">
                <div>
                    <h3 id="quizModalTitle" style="margin:0; font-size:1.4rem; color: #0f172a; font-weight:700;">Examen: CNA</h3>
                    <p style="margin:5px 0 0 0; color:var(--text-muted); font-size:0.9rem;">Responde las siguientes preguntas para completar tu evaluación.</p>
                </div>
                <button class="btn-ghost" onclick="closeQuizModal()" style="width:40px; height:40px; padding:0; display:flex; align-items:center; justify-content:center; border-radius:50%; background:#f1f5f9;">
                    <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>
            
            <div id="quizModalContent" style="padding:25px; overflow-y:auto; flex:1; background:#f8fafc;">
                <!-- Gamificación: Información del examen -->
                <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:15px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:0.85rem; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Nota Mínima Requerida</div>
                        <div id="quizMinGrade" style="font-size:1.2rem; font-weight:700; color:#10b981;">3.0</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:0.85rem; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Recompensa</div>
                        <div style="font-size:1.2rem; font-weight:700; color:#f59e0b; display:flex; align-items:center; gap:5px; justify-content:flex-end;">
                            +50 <svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path></svg>
                        </div>
                    </div>
                </div>

                <div id="quizQuestionsContainer" style="display:flex; flex-direction:column; gap:25px;">
                    <!-- Las preguntas se cargarán aquí dinámicamente -->
                </div>
            </div>
            
            <div id="quizModalFooter" style="padding:20px 25px; border-top:1px solid #e2e8f0; display:flex; justify-content:flex-end; gap:12px; background:white;">
                <button class="btn-ghost" onclick="closeQuizModal()" style="font-weight:600;">Cancelar</button>
                <button class="btn-primary" style="background: linear-gradient(135deg, #10b981, #059669); border:none; color: white;" onclick="submitQuiz()">Enviar Respuestas</button>
            </div>
        </div>
    </div>"""

# Replace the gamification quiz modal with our version. We'll just replace the inner questions container
new_modal_injection = """<input type="hidden" id="takeQuizCourseId" value="">
                <input type="hidden" id="takeQuizUnitId" value="">
                <input type="hidden" id="takeQuizEvalId" value="">
                <div id="quizQuestionsContainer" style="display:flex; flex-direction:column; gap:25px;">"""

content = content.replace('<div id="quizQuestionsContainer" style="display:flex; flex-direction:column; gap:25px;">', new_modal_injection)

with open('c:/SIAC/templates/formacion.html', 'w', encoding='utf-8') as f:
    f.write(content)
