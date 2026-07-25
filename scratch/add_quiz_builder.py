import re

with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_modal = """
        <!-- Modal Creador de Cuestionarios (Quiz Builder) -->
        <div id="quizEditorModal" class="modal-overlay" style="display: none; z-index: 2500;">
            <div class="modal-content" style="max-width: 700px; width: 95%;">
                <div class="modal-header">
                    <h3 id="quizEditorTitle">Editor de Preguntas</h3>
                    <button class="close-btn" onclick="document.getElementById('quizEditorModal').style.display='none'">&times;</button>
                </div>
                <input type="hidden" id="quizEdUnitIdx">
                <input type="hidden" id="quizEdEvIdx">
                
                <div style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size:0.85rem; color:var(--text-muted);">Añade preguntas para esta evaluación.</span>
                    <button class="btn-primary" style="padding:6px 12px; font-size:0.8rem;" onclick="addQuizQuestion()">+ Nueva Pregunta</button>
                </div>
                
                <div id="quizQuestionsContainer" style="display: flex; flex-direction: column; gap: 15px; max-height: 50vh; overflow-y: auto; padding-right: 5px;">
                    <!-- Preguntas dinámicas -->
                </div>
                
                <button class="btn-primary" style="width:100%; margin-top: 20px;" onclick="saveQuizQuestions()">Guardar Cuestionario</button>
            </div>
        </div>
"""

js_funcs = """
        // --- QUIZ BUILDER (DOCENTE) ---
        let currentQuizQuestions = [];

        function openQuizEditor(unitIdx, evIdx) {
            document.getElementById('quizEdUnitIdx').value = unitIdx;
            document.getElementById('quizEdEvIdx').value = evIdx;
            
            const ev = activeCourse.units[unitIdx].evaluations[evIdx];
            document.getElementById('quizEditorTitle').textContent = 'Preguntas: ' + ev.title;
            
            currentQuizQuestions = ev.questions ? JSON.parse(JSON.stringify(ev.questions)) : [];
            renderQuizQuestions();
            
            document.getElementById('quizEditorModal').style.display = 'flex';
        }

        function renderQuizQuestions() {
            const container = document.getElementById('quizQuestionsContainer');
            container.innerHTML = '';
            
            if (currentQuizQuestions.length === 0) {
                container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-muted); font-size:0.9rem; border:1px dashed #cbd5e1; border-radius:8px;">No hay preguntas creadas. Haz clic en "+ Nueva Pregunta".</div>';
                return;
            }
            
            currentQuizQuestions.forEach((q, qIdx) => {
                const qBox = document.createElement('div');
                qBox.style = 'border:1px solid var(--border-color); border-radius:8px; padding:15px; background:var(--bg-main); position:relative;';
                
                let optionsHtml = '';
                if (['multiple', 'single'].includes(q.type)) {
                    optionsHtml = `
                        <div style="margin-top:10px;">
                            <label style="font-size:0.8rem;">Opciones (separadas por coma):</label>
                            <input type="text" class="form-input" style="margin-bottom:5px;" value="${escapeHtml((q.options || []).join(', '))}" onchange="updateQuizQuestion(${qIdx}, 'options', this.value.split(',').map(s=>s.trim()))">
                            <label style="font-size:0.8rem;">Respuesta Correcta (exacta):</label>
                            <input type="text" class="form-input" value="${escapeHtml(q.correctAnswer || '')}" onchange="updateQuizQuestion(${qIdx}, 'correctAnswer', this.value.trim())">
                        </div>`;
                } else if (q.type === 'truefalse') {
                    optionsHtml = `
                        <div style="margin-top:10px;">
                            <label style="font-size:0.8rem;">Respuesta Correcta:</label>
                            <select class="form-input" onchange="updateQuizQuestion(${qIdx}, 'correctAnswer', this.value)">
                                <option value="true" ${q.correctAnswer==='true'?'selected':''}>Verdadero</option>
                                <option value="false" ${q.correctAnswer==='false'?'selected':''}>Falso</option>
                            </select>
                        </div>`;
                }
                
                qBox.innerHTML = `
                    <button style="position:absolute; top:10px; right:10px; color:#ef4444; background:none; border:none; cursor:pointer;" onclick="removeQuizQuestion(${qIdx})">🗑️</button>
                    <div style="display:flex; gap:10px; margin-bottom:10px;">
                        <span style="font-weight:700; color:var(--primary-color);">#${qIdx+1}</span>
                        <select class="form-input" style="width:auto; padding:4px 8px; font-size:0.8rem;" onchange="updateQuizQuestion(${qIdx}, 'type', this.value)">
                            <option value="single" ${q.type==='single'?'selected':''}>Única Respuesta</option>
                            <option value="multiple" ${q.type==='multiple'?'selected':''}>Selección Múltiple</option>
                            <option value="truefalse" ${q.type==='truefalse'?'selected':''}>Verdadero/Falso</option>
                            <option value="likert" ${q.type==='likert'?'selected':''}>Escala Likert</option>
                            <option value="open" ${q.type==='open'?'selected':''}>Respuesta Abierta</option>
                        </select>
                    </div>
                    <textarea class="form-input" rows="2" placeholder="Escribe el enunciado de la pregunta..." onchange="updateQuizQuestion(${qIdx}, 'text', this.value)">${escapeHtml(q.text || '')}</textarea>
                    ${optionsHtml}
                `;
                container.appendChild(qBox);
            });
        }

        function addQuizQuestion() {
            currentQuizQuestions.push({ type: 'single', text: '', options: ['Opción A', 'Opción B'], correctAnswer: 'Opción A' });
            renderQuizQuestions();
        }

        function removeQuizQuestion(qIdx) {
            currentQuizQuestions.splice(qIdx, 1);
            renderQuizQuestions();
        }

        function updateQuizQuestion(qIdx, field, val) {
            currentQuizQuestions[qIdx][field] = val;
            if (field === 'type') renderQuizQuestions(); // Re-render to show/hide option fields
        }

        async function saveQuizQuestions() {
            const unitIdx = document.getElementById('quizEdUnitIdx').value;
            const evIdx = document.getElementById('quizEdEvIdx').value;
            
            // Basic validation
            for (let i=0; i<currentQuizQuestions.length; i++) {
                if (!currentQuizQuestions[i].text.trim()) {
                    alert('La pregunta #' + (i+1) + ' no tiene enunciado.');
                    return;
                }
            }
            
            activeCourse.units[unitIdx].evaluations[evIdx].questions = currentQuizQuestions;
            document.getElementById('quizEditorModal').style.display = 'none';
            await updateCourseOnServer();
            alert("Preguntas guardadas con éxito.");
        }
"""

for i in range(len(lines)-1, -1, -1):
    if '<!-- Modal Creador de Cuestionarios' in lines[i]:
        # Already exists
        break
    if '<!-- Modal para Crear/Editar Tema -->' in lines[i]:
        lines.insert(i, new_modal)
        break

for i in range(len(lines)-1, -1, -1):
    if '// --- QUIZ BUILDER' in lines[i]:
        # Already exists
        break
    if '</script>' in lines[i]:
        lines.insert(i, js_funcs)
        break

with open('c:\\SIAC\\templates\\formacion.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)
