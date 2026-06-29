with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

take_quiz_modal = """
        <!-- Modal para Presentar Cuestionario (Estudiante) -->
        <div id="takeQuizModal" class="modal-overlay" style="display: none; z-index: 2600;">
            <div class="modal-content" style="max-width: 700px; width: 95%;">
                <div class="modal-header">
                    <h3 id="takeQuizTitle" style="margin:0;">Examen</h3>
                    <button class="close-btn" onclick="document.getElementById('takeQuizModal').style.display='none'">&times;</button>
                </div>
                <div id="takeQuizSub" style="font-size:0.85rem; color:var(--text-muted); margin: 10px 20px;"></div>
                <input type="hidden" id="takeQuizUnitIdx">
                <input type="hidden" id="takeQuizEvId">
                <div id="takeQuizQuestionsContainer" style="display: flex; flex-direction: column; gap: 20px; max-height: 60vh; overflow-y: auto; padding: 0 20px 10px;">
                    <!-- Preguntas renderizadas -->
                </div>
                <div style="padding: 20px; border-top: 1px solid var(--border-color);">
                    <button class="btn-primary" style="width:100%; background: var(--success-gradient); border:none; color:white; font-weight:700;" onclick="submitQuizAnswers()">Enviar Respuestas</button>
                </div>
            </div>
        </div>
"""

# Insert modal before </body>
html = html.replace('</body>', take_quiz_modal + '\n</body>')

# Now fix the student course view button - find the 'Presentar Examen' button and replace with takeQuiz call.
# The old code: onclick="presentQuiz('${escapeHtml(ev.title)...', ...)"
# The new code: onclick="takeQuiz(${uIdx}, '${ev.id}')"
# Since this is inside a template literal, we use the JS var uIdx (loop variable in openStudentCourse)

old_eval_btn = """<button class="btn-primary" style="padding:8px 16px; font-size:0.8rem; background: var(--primary-gradient); border:none; color:white; border-radius:10px;" onclick="presentQuiz('${escapeHtml(ev.title).replace(/'/g, "\\\\'")}'"""

if old_eval_btn in html:
    print("Found old eval button - will replace")
    # Find the full old button
    start_idx = html.find(old_eval_btn)
    end_idx = html.find('</button>', start_idx) + len('</button>')
    old_btn = html[start_idx:end_idx]
    print("Old button:", old_btn[:200])
    
    new_btn = '<button class="btn-primary" style="padding:8px 16px; font-size:0.8rem; background: var(--primary-gradient); border:none; color:white; border-radius:10px;" onclick="takeQuiz(${uIdx}, \'${ev.id}\')">Presentar Examen</button>'
    html = html[:start_idx] + new_btn + html[end_idx:]
    print("Replaced eval button")
else:
    print("Old eval button NOT found - checking for patterns...")
    import re
    # Try a more flexible search
    matches = list(re.finditer(r'onclick="presentQuiz\([^"]+\)"', html))
    print(f"Found {len(matches)} presentQuiz patterns:")
    for m in matches:
        print(" ", m.group()[:150])

with open('c:\\SIAC\\templates\\formacion.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
