import re

with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

take_quiz_modal = """
        <!-- Modal para Presentar Cuestionario (Estudiante/Preview) -->
        <div id="takeQuizModal" class="modal-overlay" style="display: none; z-index: 2600;">
            <div class="modal-content" style="max-width: 700px; width: 95%;">
                <div class="modal-header">
                    <h3 id="takeQuizTitle" style="margin:0;">Examen</h3>
                    <button class="close-btn" onclick="document.getElementById('takeQuizModal').style.display='none'">&times;</button>
                </div>
                <div id="takeQuizSub" style="font-size:0.85rem; color:var(--text-muted); margin-bottom:15px;"></div>
                
                <input type="hidden" id="takeQuizUnitIdx">
                <input type="hidden" id="takeQuizEvId">
                
                <div id="takeQuizQuestionsContainer" style="display: flex; flex-direction: column; gap: 20px; max-height: 60vh; overflow-y: auto; padding-right: 5px;">
                    <!-- Preguntas renderizadas -->
                </div>
                
                <button class="btn-primary" style="width:100%; margin-top: 20px; background: var(--success-gradient);" onclick="submitQuizAnswers()">Enviar Respuestas</button>
            </div>
        </div>
"""

take_quiz_js = """
        // --- QUIZ TAKER (ESTUDIANTE) ---
        let currentTakingQuiz = [];
        
        function takeQuiz(uIdx, evId) {
            const unit = activeCourse.units[uIdx];
            const ev = unit.evaluations.find(e => e.id === evId);
            if (!ev) return;
            
            document.getElementById('takeQuizUnitIdx').value = uIdx;
            document.getElementById('takeQuizEvId').value = evId;
            document.getElementById('takeQuizTitle').textContent = ev.title;
            document.getElementById('takeQuizSub').innerHTML = `Evaluación formativa en Escala CNA (Aprobación: <strong>${(ev.min_grade||3.0).toFixed(1)}</strong> / Máxima: <strong>${(ev.max_grade||5.0).toFixed(1)}</strong>)`;
            
            currentTakingQuiz = ev.questions || [];
            const container = document.getElementById('takeQuizQuestionsContainer');
            container.innerHTML = '';
            
            if (currentTakingQuiz.length === 0) {
                container.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Este examen aún no tiene preguntas.</div>';
            } else {
                currentTakingQuiz.forEach((q, qIdx) => {
                    const qBox = document.createElement('div');
                    qBox.style = 'border:1px solid var(--border-color); border-radius:8px; padding:15px; background:var(--bg-main);';
                    qBox.innerHTML = `<strong>${qIdx+1}. ${escapeHtml(q.text)}</strong><br><div style="margin-top:10px;" id="qA_${qIdx}"></div>`;
                    
                    container.appendChild(qBox);
                    const ansContainer = document.getElementById(`qA_${qIdx}`);
                    
                    if (q.type === 'single') {
                        (q.options || []).forEach((opt, oIdx) => {
                            ansContainer.innerHTML += `
                                <label style="display:block; margin-bottom:5px; cursor:pointer;">
                                    <input type="radio" name="ans_${qIdx}" value="${escapeHtml(opt)}"> ${escapeHtml(opt)}
                                </label>`;
                        });
                    } else if (q.type === 'multiple') {
                        (q.options || []).forEach((opt, oIdx) => {
                            ansContainer.innerHTML += `
                                <label style="display:block; margin-bottom:5px; cursor:pointer;">
                                    <input type="checkbox" name="ans_${qIdx}" value="${escapeHtml(opt)}"> ${escapeHtml(opt)}
                                </label>`;
                        });
                    } else if (q.type === 'truefalse') {
                        ansContainer.innerHTML += `
                            <label style="display:inline-block; margin-right:15px; cursor:pointer;"><input type="radio" name="ans_${qIdx}" value="true"> Verdadero</label>
                            <label style="display:inline-block; cursor:pointer;"><input type="radio" name="ans_${qIdx}" value="false"> Falso</label>`;
                    } else if (q.type === 'likert') {
                        ansContainer.innerHTML += `
                            <div style="display:flex; justify-content:space-between; max-width:300px; margin-top:5px;">
                                <label><input type="radio" name="ans_${qIdx}" value="1"><br>1</label>
                                <label><input type="radio" name="ans_${qIdx}" value="2"><br>2</label>
                                <label><input type="radio" name="ans_${qIdx}" value="3"><br>3</label>
                                <label><input type="radio" name="ans_${qIdx}" value="4"><br>4</label>
                                <label><input type="radio" name="ans_${qIdx}" value="5"><br>5</label>
                            </div>
                            <div style="display:flex; justify-content:space-between; max-width:300px; font-size:0.7rem; color:var(--text-muted);">
                                <span>Totalmente en desacuerdo</span>
                                <span>Totalmente de acuerdo</span>
                            </div>`;
                    } else if (q.type === 'open') {
                        ansContainer.innerHTML += `<textarea id="ans_${qIdx}" class="form-input" rows="3" placeholder="Escribe tu respuesta..."></textarea>`;
                    }
                });
            }
            
            document.getElementById('takeQuizModal').style.display = 'flex';
        }

        async function submitQuizAnswers() {
            if (currentTakingQuiz.length === 0) {
                document.getElementById('takeQuizModal').style.display = 'none';
                return;
            }
            
            const uIdx = document.getElementById('takeQuizUnitIdx').value;
            const evId = document.getElementById('takeQuizEvId').value;
            const unit = activeCourse.units[uIdx];
            const ev = unit.evaluations.find(e => e.id === evId);
            
            let allAnswered = true;
            let correctCount = 0;
            let requiresManualGrading = false;
            const studentAnswers = [];
            
            for (let i = 0; i < currentTakingQuiz.length; i++) {
                const q = currentTakingQuiz[i];
                let ans = null;
                
                if (q.type === 'single' || q.type === 'truefalse' || q.type === 'likert') {
                    const selected = document.querySelector(`input[name="ans_${i}"]:checked`);
                    if (selected) ans = selected.value;
                } else if (q.type === 'multiple') {
                    const checked = Array.from(document.querySelectorAll(`input[name="ans_${i}"]:checked`));
                    if (checked.length > 0) ans = checked.map(c => c.value).join(',');
                } else if (q.type === 'open') {
                    const txt = document.getElementById(`ans_${i}`).value.trim();
                    if (txt) ans = txt;
                }
                
                if (!ans) {
                    alert(`Por favor responde la pregunta #${i+1}`);
                    return;
                }
                
                studentAnswers.push({ qIdx: i, answer: ans });
                
                if (q.type === 'open') {
                    requiresManualGrading = true;
                } else if (q.type !== 'likert') {
                    // Objective grading
                    if (ans === q.correctAnswer) correctCount++;
                } else {
                    // Likert has no correct answer, we just count it as correct for progression sake or ignore.
                    // Let's count it as correct for auto-grading if it's just a survey.
                    correctCount++;
                }
            }
            
            let finalGrade = 0;
            let status = 'pending';
            
            if (!requiresManualGrading) {
                // Auto calculate
                finalGrade = (correctCount / currentTakingQuiz.length) * (ev.max_grade || 5.0);
                status = 'graded';
            }
            
            try {
                const payload = {
                    course_id: activeCourse.course_id,
                    unit_id: unit.id,
                    activity_id: ev.id,
                    content: JSON.stringify(studentAnswers)
                };
                
                const res = await fetch('https://siacmen.vercel.app/api/submissions?inst_id=' + window.INST_ID, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        ...payload,
                        user_id: userEmail
                    })
                });
                
                if (res.ok) {
                    // Immediately try to grade if auto-graded
                    if (status === 'graded') {
                        const r2 = await fetch('https://siacmen.vercel.app/api/submissions?inst_id=' + window.INST_ID, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                course_id: activeCourse.course_id,
                                activity_id: ev.id,
                                user_id: userEmail,
                                grade: finalGrade,
                                feedback: 'Calificado automáticamente.'
                            })
                        });
                    }
                    alert(requiresManualGrading ? 'Respuestas enviadas. Pendiente de calificación por el docente.' : `Examen enviado. Tu nota es: ${finalGrade.toFixed(1)}`);
                    document.getElementById('takeQuizModal').style.display = 'none';
                    openStudentCourse(activeCourse.course_id); // refresh
                } else {
                    alert('Error al enviar el examen.');
                }
            } catch (e) {
                console.error(e);
                alert('Error de conexión.');
            }
        }
"""

# Insert takeQuizModal
if '<!-- Modal para Presentar Cuestionario' not in html:
    html = html.replace('<!-- Modal de Calificación -->', take_quiz_modal + '\n        <!-- Modal de Calificación -->')

# Insert take_quiz_js
if '// --- QUIZ TAKER' not in html:
    html = html.replace('</script>', take_quiz_js + '\n    </script>')

# Replace presentQuiz with takeQuiz in renderSyllabusList
html = re.sub(r'onclick="presentQuiz\([^)]+\)"', r'onclick="takeQuiz(${uIdx}, \'${ev.id}\')"', html)

# Replace presentQuiz with takeQuiz in student course view
# Wait, student course view uses presentQuiz('${escapeHtml(ev.title).replace(...)', ...)
# Let's just do a blanket regex replacement if we can safely find it.
# Actually, the previous regex will catch ALL presentQuiz. 
# But wait, we need `${uIdx}` for student course view too?
# In student course view, it's `uIdx`. Yes, `uIdx` is available in `openStudentCourse`.

with open('c:\\SIAC\\templates\\formacion.html', 'w', encoding='utf-8') as f:
    f.write(html)
