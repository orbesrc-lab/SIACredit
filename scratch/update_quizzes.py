import re

file_path = 'c:/SIAC/templates/formacion.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update unitEvaluationModal
old_eval_modal_pattern = r'<div id="unitEvaluationModal".*?Crear Evaluaci\\?n.*?</div>\s*</div>\s*</div>'
# We will just replace it by searching for the start and end since regex with newlines can be tricky
start_eval = content.find('id="unitEvaluationModal"')
start_eval = content.rfind('<div', 0, start_eval)
end_eval = content.find('</div>\n    </div>', start_eval) + 16

new_eval_modal = """<div id="unitEvaluationModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:1001; align-items:center; justify-content:center;">
        <div style="background:white; border-radius:16px; padding:30px; width:700px; max-width:95vw; max-height:90vh; display:flex; flex-direction:column; box-shadow:0 20px 60px rgba(0,0,0,0.3);">
            <h3 style="margin-bottom:20px; font-size:1.2rem;">Constructor de Examen</h3>
            <div style="overflow-y:auto; flex:1; padding-right:10px;">
                <input type="hidden" id="evaluationUnitIdx">
                <div class="form-group">
                    <label>Título del Examen</label>
                    <input type="text" id="eval_title" placeholder="Ej: Examen Final - Unidad 1">
                </div>
                <div class="form-grid" style="margin-top:15px; grid-template-columns:1fr 1fr;">
                    <div class="form-group">
                        <label>Nota Mínima (Aprobación)</label>
                        <input type="number" id="eval_min" step="0.1" min="1.0" max="5.0" value="3.0">
                    </div>
                    <div class="form-group">
                        <label>Nota Máxima</label>
                        <input type="number" id="eval_max" step="0.1" min="1.0" max="5.0" value="5.0">
                    </div>
                </div>
                
                <hr style="border:none; border-top:1px solid #e2e8f0; margin:20px 0;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                    <h4 style="margin:0; color:#0f172a;">Preguntas del Examen</h4>
                    <button class="btn-secondary" onclick="addQuizBuilderQuestion()" style="padding:6px 12px; font-size:0.8rem;">+ Añadir Pregunta</button>
                </div>
                <div id="quizBuilderContainer" style="display:flex; flex-direction:column; gap:15px;">
                    <!-- Preguntas dinámicas -->
                </div>
            </div>
            <div style="display:flex; gap:10px; justify-content:flex-end; margin-top:25px; padding-top:15px; border-top:1px solid #e2e8f0;">
                <button class="btn-ghost" onclick="closeUnitEvaluationModal()">Cancelar</button>
                <button class="btn-primary" onclick="submitAddUnitEvaluation()">Guardar Examen</button>
            </div>
        </div>
    </div>"""

content = content[:start_eval] + new_eval_modal + content[end_eval:]

# 2. Update Quiz Modal
start_quiz = content.find('id="quizModal"')
start_quiz = content.rfind('<div', 0, start_quiz)
end_quiz = content.find('</div>\n    </div>', start_quiz) + 16

new_quiz_modal = """<div id="quizModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:2000; align-items:center; justify-content:center; backdrop-filter:blur(5px);">
        <div style="background:white; border-radius:20px; width:650px; max-width:95vw; max-height:90vh; display:flex; flex-direction:column; box-shadow:0 25px 50px -12px rgba(0,0,0,0.25);">
            <div style="padding:25px; border-bottom:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h3 id="quizModalTitle" style="font-size:1.3rem; margin:0; color: #0f172a;">Examen Formativo</h3>
                    <p id="quizModalSub" style="font-size:0.85rem; color:var(--text-muted); margin:5px 0 0 0;">Evaluación</p>
                </div>
                <button class="btn-ghost" onclick="document.getElementById('quizModal').style.display='none'" style="font-size:1.5rem; padding:0 10px;">&times;</button>
            </div>
            
            <div id="quizModalContent" style="padding:25px; overflow-y:auto; flex:1;">
                <input type="hidden" id="takeQuizCourseId">
                <input type="hidden" id="takeQuizUnitId">
                <input type="hidden" id="takeQuizEvalId">
                <div id="quizQuestionsContainer" style="display:flex; flex-direction:column; gap:25px;">
                    <!-- Preguntas -->
                </div>
            </div>
            
            <div id="quizModalFooter" style="padding:20px 25px; border-top:1px solid #e2e8f0; display:flex; justify-content:flex-end; gap:10px; background:#f8fafc; border-radius:0 0 20px 20px;">
                <button class="btn-ghost" onclick="document.getElementById('quizModal').style.display='none'">Cancelar</button>
                <button class="btn-primary" onclick="submitQuiz()" id="btnSubmitQuiz">Enviar Examen</button>
            </div>
        </div>
    </div>"""

content = content[:start_quiz] + new_quiz_modal + content[end_quiz:]

# 3. Inject JS Functions (at the end before window.onload = init)
js_injection = """
        // --- CONSTRUCTOR DE EXAMENES ---
        let quizBuilderQuestions = [];
        
        function addQuizBuilderQuestion() {
            quizBuilderQuestions.push({
                text: '',
                options: ['', '', '', ''],
                correct: 0
            });
            renderQuizBuilder();
        }
        
        function removeQuizBuilderQuestion(idx) {
            quizBuilderQuestions.splice(idx, 1);
            renderQuizBuilder();
        }
        
        function updateQuizBuilderQuestion(idx, field, value, optIdx = null) {
            if (field === 'text') quizBuilderQuestions[idx].text = value;
            else if (field === 'correct') quizBuilderQuestions[idx].correct = parseInt(value);
            else if (field === 'option') quizBuilderQuestions[idx].options[optIdx] = value;
        }
        
        function renderQuizBuilder() {
            const container = document.getElementById('quizBuilderContainer');
            if (quizBuilderQuestions.length === 0) {
                container.innerHTML = '<p style="color:#64748b; font-size:0.9rem; text-align:center;">No hay preguntas. Haz clic en "Añadir Pregunta".</p>';
                return;
            }
            
            container.innerHTML = quizBuilderQuestions.map((q, qIdx) => `
                <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:15px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <strong style="font-size:0.9rem;">Pregunta ${qIdx + 1}</strong>
                        <button class="btn-ghost" style="color:#ef4444; padding:2px 8px; font-size:0.8rem;" onclick="removeQuizBuilderQuestion(${qIdx})">Eliminar</button>
                    </div>
                    <input type="text" style="width:100%; margin-bottom:10px; padding:8px; border:1px solid #cbd5e1; border-radius:6px;" placeholder="Enunciado de la pregunta" value="${escapeHtml(q.text)}" onchange="updateQuizBuilderQuestion(${qIdx}, 'text', this.value)">
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                        ${q.options.map((opt, oIdx) => `
                            <div style="display:flex; align-items:center; gap:5px;">
                                <input type="radio" name="correct_${qIdx}" value="${oIdx}" ${q.correct === oIdx ? 'checked' : ''} onchange="updateQuizBuilderQuestion(${qIdx}, 'correct', this.value)">
                                <input type="text" style="flex:1; padding:6px; border:1px solid #cbd5e1; border-radius:6px; font-size:0.85rem;" placeholder="Opción ${oIdx + 1}" value="${escapeHtml(opt)}" onchange="updateQuizBuilderQuestion(${qIdx}, 'option', this.value, ${oIdx})">
                            </div>
                        `).join('')}
                    </div>
                </div>
            `).join('');
        }

        // Overwrite openAddEvaluationModal
        window.openAddEvaluationModal = function(unitIdx) {
            document.getElementById('evaluationUnitIdx').value = unitIdx;
            document.getElementById('eval_title').value = '';
            document.getElementById('eval_min').value = '3.0';
            document.getElementById('eval_max').value = '5.0';
            quizBuilderQuestions = [];
            renderQuizBuilder();
            document.getElementById('unitEvaluationModal').style.display = 'flex';
        };

        // Overwrite submitAddUnitEvaluation
        window.submitAddUnitEvaluation = async function() {
            const unitIdx = parseInt(document.getElementById('evaluationUnitIdx').value);
            const title = document.getElementById('eval_title').value.trim();
            const min_grade = parseFloat(document.getElementById('eval_min').value) || 3.0;
            const max_grade = parseFloat(document.getElementById('eval_max').value) || 5.0;
            
            if (!title) { alert("El título es obligatorio."); return; }
            if (min_grade < 1.0 || max_grade > 5.0 || min_grade > max_grade) {
                alert("Calificaciones inválidas en Escala CNA (1.0 - 5.0)."); return;
            }
            if (quizBuilderQuestions.length === 0) {
                if(!confirm("El examen no tiene preguntas. ¿Deseas guardarlo de todos modos?")) return;
            }
            
            // Validate questions
            for(let i=0; i<quizBuilderQuestions.length; i++) {
                if(!quizBuilderQuestions[i].text) {
                    alert(`La pregunta ${i+1} no tiene enunciado.`); return;
                }
            }
            
            const newEval = { 
                id: 'eval_' + Math.random().toString(36).substr(2, 5), 
                title: title, 
                min_grade: min_grade, 
                max_grade: max_grade,
                questions: JSON.parse(JSON.stringify(quizBuilderQuestions))
            };
            
            if (!activeCourse.units[unitIdx].evaluations) activeCourse.units[unitIdx].evaluations = [];
            activeCourse.units[unitIdx].evaluations.push(newEval);
            
            closeUnitEvaluationModal();
            renderSyllabusList();
            updateCourseOnServer();
        };

        // --- TOMAR EXAMEN (STUDENT) ---
        let currentQuizQuestions = [];
        
        window.presentQuiz = function(courseId, unitId, evalId, title, minGrade, maxGrade, questionsJsonString) {
            currentQuizTitle = title;
            currentQuizMinGrade = parseFloat(minGrade);
            currentQuizMaxGrade = parseFloat(maxGrade);
            
            document.getElementById('takeQuizCourseId').value = courseId;
            document.getElementById('takeQuizUnitId').value = unitId;
            document.getElementById('takeQuizEvalId').value = evalId;
            
            try {
                currentQuizQuestions = JSON.parse(questionsJsonString);
            } catch(e) {
                currentQuizQuestions = [];
            }
            
            document.getElementById('quizModalTitle').textContent = title;
            document.getElementById('quizModalSub').innerHTML = `Evaluación formativa del LMS en Escala CNA (Aprobación: <strong>${currentQuizMinGrade.toFixed(1)}</strong> / Máxima: <strong>${currentQuizMaxGrade.toFixed(1)}</strong>)`;
            
            const container = document.getElementById('quizQuestionsContainer');
            
            if (currentQuizQuestions.length === 0) {
                container.innerHTML = '<p style="text-align:center; padding:20px; color:#64748b;">Este examen no tiene preguntas configuradas.</p>';
                document.getElementById('btnSubmitQuiz').style.display = 'none';
            } else {
                document.getElementById('btnSubmitQuiz').style.display = 'block';
                container.innerHTML = currentQuizQuestions.map((item, qIdx) => `
                    <div style="border-bottom:1px solid #f1f5f9; padding-bottom:15px;">
                        <strong style="display:block; font-size:0.95rem; margin-bottom:10px; color: #1e293b;">${qIdx + 1}. ${escapeHtml(item.text)}</strong>
                        <div style="display:flex; flex-direction:column; gap:8px;">
                            ${item.options.map((opt, oIdx) => `
                                <label style="display:flex; align-items:center; gap:8px; font-size:0.9rem; cursor:pointer; color: #475569; padding:8px; border-radius:6px; transition: background 0.2s;" onmouseover="this.style.background='#f1f5f9'" onmouseout="this.style.background='transparent'">
                                    <input type="radio" name="q_${qIdx}" value="${oIdx}">
                                    ${escapeHtml(opt)}
                                </label>
                            `).join('')}
                        </div>
                    </div>
                `).join('');
            }
            
            document.getElementById('quizModalFooter').style.display = 'flex';
            // Restore modal content in case it was showing results
            const contentDiv = document.getElementById('quizModalContent');
            const originalContent = contentDiv.innerHTML;
            if (contentDiv.querySelector('div[style*="font-size:4rem"]')) {
               // Need to rebuild if it showed results previously
               contentDiv.innerHTML = `
                <input type="hidden" id="takeQuizCourseId" value="${courseId}">
                <input type="hidden" id="takeQuizUnitId" value="${unitId}">
                <input type="hidden" id="takeQuizEvalId" value="${evalId}">
                <div id="quizQuestionsContainer" style="display:flex; flex-direction:column; gap:25px;"></div>
               `;
               // recall to set html
               presentQuiz(courseId, unitId, evalId, title, minGrade, maxGrade, questionsJsonString);
               return;
            }
            
            document.getElementById('quizModal').style.display = 'flex';
        };

        window.submitQuiz = async function() {
            if (currentQuizQuestions.length === 0) return;
            
            let correctAnswers = 0;
            let answeredCount = 0;
            
            currentQuizQuestions.forEach((item, qIdx) => {
                const selected = document.querySelector(`input[name="q_${qIdx}"]:checked`);
                if (selected) {
                    answeredCount++;
                    if (parseInt(selected.value) === item.correct) {
                        correctAnswers++;
                    }
                }
            });
            
            if (answeredCount < currentQuizQuestions.length) {
                alert("Por favor, responde todas las preguntas del cuestionario antes de enviar.");
                return;
            }
            
            const btn = document.getElementById('btnSubmitQuiz');
            btn.disabled = true;
            btn.textContent = "Evaluando...";
            
            // Calculate grade
            // Formula: Note = 1.0 + (correct / total) * 4.0
            const grade = 1.0 + (correctAnswers / currentQuizQuestions.length) * 4.0;
            const approved = grade >= currentQuizMinGrade;
            
            const courseId = document.getElementById('takeQuizCourseId').value;
            const unitId = document.getElementById('takeQuizUnitId').value;
            const evalId = document.getElementById('takeQuizEvalId').value;
            
            // Post submission to backend
            try {
                const subData = {
                    course_id: courseId,
                    unit_id: unitId,
                    activity_id: evalId,
                    student_email: user.email,
                    student_name: user.name || user.email.split('@')[0],
                    content: `Examen: ${correctAnswers}/${currentQuizQuestions.length} correctas.`,
                    submitted_at: new Date().toISOString(),
                    status: 'graded',
                    grade: grade.toFixed(1),
                    feedback: 'Calificación automática del sistema.'
                };
                
                const checkResp = await fetch(`/api/submissions?course_id=${courseId}&student_email=${user.email}&activity_id=${evalId}&inst_id=${getInstId()}&program_id=${getProgramId()}`);
                const existingSubs = await checkResp.json();
                if (existingSubs && existingSubs.length > 0) {
                    subData.id = existingSubs[0].id;
                }
                
                await fetch(`/api/submissions?inst_id=${getInstId()}&program_id=${getProgramId()}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(subData)
                });
                
            } catch(e) {
                console.error("Error saving quiz score", e);
            }
            
            // Show results UI
            const modalContent = document.getElementById('quizModalContent');
            modalContent.innerHTML = `
                <div style="text-align:center; padding:20px; color: #0f172a;">
                    <div style="font-size:4rem; margin-bottom:15px; animation: bounce 1s infinite;">
                        ${approved ? '🏆' : '⚠️'}
                    </div>
                    <h3 style="font-size:1.4rem; font-weight:800; margin-bottom:8px; color: ${approved ? '#10b981' : '#ef4444'};">
                        ${approved ? 'Examen Aprobado' : 'Examen Reprobado'}
                    </h3>
                    <p style="font-size:0.95rem; color:var(--text-muted); margin-bottom:20px;">
                        Tus respuestas han sido evaluadas.
                    </p>
                    
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:15px 20px; display:inline-block; margin-bottom:25px;">
                        <div style="font-size:0.85rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:1px; margin-bottom:5px;">Tu Calificación CNA</div>
                        <div style="font-size:2.5rem; font-weight:900; color: ${approved ? '#10b981' : '#ef4444'}; line-height:1;">
                            ${grade.toFixed(1)}
                        </div>
                        <div style="font-size:0.8rem; color:var(--text-muted); margin-top:5px;">
                            (Aprobación requerida: ${currentQuizMinGrade.toFixed(1)})
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('quizModalFooter').style.display = 'none';
            btn.disabled = false;
            btn.textContent = "Enviar Examen";
            
            // Reload course to update progress bar
            openStudentCourse(courseId);
        };
"""

# Replace the old `presentQuiz` and `submitQuiz`
# Because `presentQuiz` and `submitQuiz` were previously defined, we can just append our new definitions 
# to the end before `window.onload`, since `window.` assignment overrides them globally.
content = content.replace("window.onload = init;", js_injection + "\n        window.onload = init;")

# Finally, patch the presentQuiz call inside `evaluationsHtml`
old_call = """onclick="presentQuiz('${escapeHtml(ev.title).replace(/'/g, "\\\\'")}', ${ev.min_grade || 3.0}, ${ev.max_grade || 5.0})\""""
new_call = """onclick="presentQuiz('${courseId}', '${unit.id}', '${ev.id}', '${escapeHtml(ev.title).replace(/'/g, "\\\\'")}', ${ev.min_grade || 3.0}, ${ev.max_grade || 5.0}, '${escapeHtml(JSON.stringify(ev.questions || [])).replace(/'/g, "\\\\'")}')\""""
content = content.replace(old_call, new_call)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully")
