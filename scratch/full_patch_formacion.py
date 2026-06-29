import re

with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f'Original file length: {len(html)} chars')

# ==========================================
# PATCH 1: Iconos dinamicos en renderSyllabusList (docente)
# ==========================================
html = html.replace(
    "const t = typeof rawT === 'string' ? { id: 't_' + tIdx, title: rawT, content: \"\" } : rawT;\n                        topicsHtml += `\n                            <div class=\"topic-item\">\n                                <span style=\"font-weight:600; color:var(--text-main);\">📖 ${escapeHtml(t.title)}</span>",
    "const t = typeof rawT === 'string' ? { id: 't_' + tIdx, title: rawT, content: \"\", type: \"text\" } : rawT;\n                        const icon = t.type === 'video' ? '🎥' : (t.type === 'podcast' ? '🎙️' : (t.type === 'link' ? '🔗' : (t.type === 'file' ? '📄' : '📖')));\n                        topicsHtml += `\n                            <div class=\"topic-item\">\n                                <span style=\"font-weight:600; color:var(--text-main);\">${icon} ${escapeHtml(t.title)}</span>"
)

# Check
if '// PATCH1' not in html and 'const icon = t.type' in html:
    print('PATCH 1 applied: dynamic icons in renderSyllabusList')
else:
    print('PATCH 1 FAILED or already applied')

# ==========================================
# PATCH 2: Button "+ Tema" calls openAddTopicModal
# ==========================================
html = html.replace(
    "onclick=\"addTopicPrompt(${uIdx})\">+ Tema</button>",
    "onclick=\"openAddTopicModal(${uIdx})\">+ Tema</button>"
)
if 'openAddTopicModal' in html:
    print('PATCH 2 applied: + Tema button updated')
else:
    print('PATCH 2 FAILED')

# ==========================================
# PATCH 3: Iconos dinamicos en openStudentCourse (estudiante)
# ==========================================
html = html.replace(
    "const t = typeof rawT === 'string' ? { id: 't_' + tIdx, title: rawT, content: \"\" } : rawT;\n                                const hasContent = t.content && t.content.trim() !== \"\";\n                                \n                                topicsHtml += `\n                                    <div style=\"border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; background: rgba(99,102,241,0.02);\">\n                                        <div onclick=\"toggleTopicAccordion('${unit.id}_${t.id}')\" style=\"padding: 12px 18px; font-weight: 600; font-size: 0.88rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: rgba(99,102,241,0.04); color: var(--text-main); transition: background 0.2s;\">\n                                            <span>📖 ${escapeHtml(t.title)}</span>",
    "const t = typeof rawT === 'string' ? { id: 't_' + tIdx, title: rawT, content: \"\", type: \"text\" } : rawT;\n                                const hasContent = t.content && t.content.trim() !== \"\";\n                                const icon = t.type === 'video' ? '🎥' : (t.type === 'podcast' ? '🎙️' : (t.type === 'link' ? '🔗' : (t.type === 'file' ? '📄' : '📖')));\n                                \n                                topicsHtml += `\n                                    <div style=\"border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; background: rgba(99,102,241,0.02);\">\n                                        <div onclick=\"toggleTopicAccordion('${unit.id}_${t.id}')\" style=\"padding: 12px 18px; font-weight: 600; font-size: 0.88rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: rgba(99,102,241,0.04); color: var(--text-main); transition: background 0.2s;\">\n                                            <span>${icon} ${escapeHtml(t.title)}</span>"
)
print('PATCH 3 applied: dynamic icons in openStudentCourse')

# ==========================================
# PATCH 4: Progression logic - include evaluations check
# ==========================================
old_prog = """let currentUnitCompleted = true;
                        if (unit.activities && unit.activities.length > 0) {
                            // Todas las actividades deben tener al menos una entrega
                            const submittedCount = unit.activities.filter(act => 
                                studentSubmissions.some(s => s.activity_id === act.id)
                            ).length;
                            
                            if (submittedCount < unit.activities.length) {
                                currentUnitCompleted = false;
                            }
                        }"""

new_prog = """let currentUnitCompleted = true;
                        if (unit.activities && unit.activities.length > 0) {
                            // Todas las actividades deben tener al menos una entrega
                            const submittedCount = unit.activities.filter(act => 
                                studentSubmissions.some(s => s.activity_id === act.id)
                            ).length;
                            
                            if (submittedCount < unit.activities.length) {
                                currentUnitCompleted = false;
                            }
                        }
                        
                        // Evaluaciones también deben tener entrega
                        if (unit.evaluations && unit.evaluations.length > 0) {
                            const submittedEvalsCount = unit.evaluations.filter(ev => 
                                studentSubmissions.some(s => s.activity_id === ev.id)
                            ).length;
                            if (submittedEvalsCount < unit.evaluations.length) {
                                currentUnitCompleted = false;
                            }
                        }"""

if old_prog in html:
    html = html.replace(old_prog, new_prog)
    print('PATCH 4 applied: progression logic includes evaluations')
else:
    print('PATCH 4 FAILED: progression logic not found')

# ==========================================
# PATCH 5: Replace eval button in student view
# ==========================================
old_eval_btn_pattern = r'''<button class="btn-primary" style="padding:8px 16px; font-size:0.8rem; background: var\(--primary-gradient\); border:none; color:white; border-radius:10px;" onclick="presentQuiz\('.*?'\)">Presentar Examen</button>'''
new_eval_btn = """<button class="btn-primary" style="padding:8px 16px; font-size:0.8rem; background: var(--primary-gradient); border:none; color:white; border-radius:10px;" onclick="takeQuiz(${uIdx}, '${ev.id}')">Presentar Examen</button>"""

matches = re.findall(old_eval_btn_pattern, html, re.DOTALL)
if matches:
    html = re.sub(old_eval_btn_pattern, new_eval_btn, html, flags=re.DOTALL)
    print(f'PATCH 5 applied: replaced {len(matches)} eval button(s) in student view')
else:
    # Try to find it differently
    idx = html.find('Presentar Examen</button>')
    if idx > 0:
        start = html.rfind('<button', 0, idx)
        print(f'Found Presentar Examen at line, context: {html[start:idx+30][:200]}')
    print('PATCH 5: pattern not found, checking manually...')

# ==========================================
# PATCH 6: Add "Editar Preguntas" button in renderSyllabusList (docente)
# ==========================================
old_eval_btns = """                                <div style="display:flex; gap:10px;">
                                    <button class="btn-ghost" style="color:var(--primary-color); padding:0 5px;" onclick="presentQuiz('${escapeHtml(ev.title).replace(/'/g, \"\\\\'\")}', ${ev.min_grade || 3.0}, ${ev.max_grade || 5.0})">👁️ Vista Previa</button>
                                    <button class="btn-ghost" style="color:#ef4444; padding:0 5px;" onclick="removeUnitEvaluation(${uIdx}, ${evIdx})">🗑️</button>
                                </div>"""

new_eval_btns = """                                <div style="display:flex; gap:10px;">
                                    <button class="btn-ghost" style="color:var(--primary-color); padding:0 5px;" onclick="openQuizEditor(${uIdx}, ${evIdx})">📝 Preguntas (${(ev.questions || []).length})</button>
                                    <button class="btn-ghost" style="color:var(--primary-color); padding:0 5px;" onclick="presentQuiz('${escapeHtml(ev.title).replace(/'/g, \"\\\\'\")}', ${ev.min_grade || 3.0}, ${ev.max_grade || 5.0})">👁️ Vista Previa</button>
                                    <button class="btn-ghost" style="color:#ef4444; padding:0 5px;" onclick="removeUnitEvaluation(${uIdx}, ${evIdx})">🗑️</button>
                                </div>"""

if old_eval_btns in html:
    html = html.replace(old_eval_btns, new_eval_btns)
    print('PATCH 6 applied: added Preguntas button in docente view')
else:
    print('PATCH 6 FAILED: eval buttons block not found')

# ==========================================
# PATCH 7: Add topic modal HTML, quiz editor modal, quiz taker modal, and JS
# ==========================================

topic_modal = """
        <!-- Modal para Crear Tema con Tipo -->
        <div id="topicModal" class="modal-overlay" style="display: none;">
            <div class="modal-content" style="max-width:480px;">
                <div class="modal-header">
                    <h3 style="margin:0;">Nuevo Tema</h3>
                    <button class="close-btn" onclick="document.getElementById('topicModal').style.display='none'">&times;</button>
                </div>
                <input type="hidden" id="topicUnitIdx">
                <div style="padding:20px; display:flex; flex-direction:column; gap:15px;">
                    <div class="form-group">
                        <label>Nombre del Tema</label>
                        <input type="text" id="topicName" class="form-input" placeholder="Ej. Introducción al tema...">
                    </div>
                    <div class="form-group">
                        <label>Tipo de Recurso / Icono</label>
                        <select id="topicType" class="form-input">
                            <option value="text">📖 Texto / Clase Magistral</option>
                            <option value="video">🎥 Video</option>
                            <option value="podcast">🎙️ Podcast / Audio</option>
                            <option value="link">🔗 Hipervínculo / Web</option>
                            <option value="file">📄 Archivo / PDF</option>
                        </select>
                    </div>
                    <button class="btn-primary" onclick="submitAddTopic()">Guardar Tema</button>
                </div>
            </div>
        </div>

        <!-- Modal Creador de Cuestionarios (Docente) -->
        <div id="quizEditorModal" class="modal-overlay" style="display: none; z-index: 2500;">
            <div class="modal-content" style="max-width: 700px; width: 95%;">
                <div class="modal-header">
                    <h3 id="quizEditorTitle" style="margin:0;">Editor de Preguntas</h3>
                    <button class="close-btn" onclick="document.getElementById('quizEditorModal').style.display='none'">&times;</button>
                </div>
                <input type="hidden" id="quizEdUnitIdx">
                <input type="hidden" id="quizEdEvIdx">
                <div style="padding:0 20px 15px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size:0.85rem; color:var(--text-muted);">Crea y ordena las preguntas del examen.</span>
                    <button class="btn-primary" style="padding:6px 14px; font-size:0.8rem;" onclick="addQuizQuestion()">+ Nueva Pregunta</button>
                </div>
                <div id="quizQuestionsContainer" style="display: flex; flex-direction: column; gap: 15px; max-height: 50vh; overflow-y: auto; padding: 0 20px 10px;">
                </div>
                <div style="padding:20px; border-top:1px solid var(--border-color);">
                    <button class="btn-primary" style="width:100%;" onclick="saveQuizQuestions()">💾 Guardar Cuestionario</button>
                </div>
            </div>
        </div>

        <!-- Modal para Presentar Cuestionario (Estudiante) -->
        <div id="takeQuizModal" class="modal-overlay" style="display: none; z-index: 2600;">
            <div class="modal-content" style="max-width: 700px; width: 95%;">
                <div class="modal-header">
                    <h3 id="takeQuizTitle" style="margin:0;">Examen</h3>
                    <button class="close-btn" onclick="document.getElementById('takeQuizModal').style.display='none'">&times;</button>
                </div>
                <div id="takeQuizSub" style="font-size:0.85rem; color:var(--text-muted); padding: 5px 20px 15px;"></div>
                <input type="hidden" id="takeQuizUnitIdx">
                <input type="hidden" id="takeQuizEvId">
                <div id="takeQuizQuestionsContainer" style="display: flex; flex-direction: column; gap: 20px; max-height: 55vh; overflow-y: auto; padding: 0 20px 10px;">
                </div>
                <div style="padding: 20px; border-top: 1px solid var(--border-color);">
                    <button class="btn-primary" style="width:100%; background: linear-gradient(135deg,#10b981,#059669); border:none; color:white; font-weight:700;" onclick="submitQuizAnswers()">📨 Enviar Respuestas</button>
                </div>
            </div>
        </div>
"""

quiz_js = """
        // --- CREACION DE TEMAS CON TIPO ---
        function openAddTopicModal(unitIdx) {
            document.getElementById('topicUnitIdx').value = unitIdx;
            document.getElementById('topicName').value = '';
            document.getElementById('topicType').value = 'text';
            document.getElementById('topicModal').style.display = 'flex';
        }
        async function submitAddTopic() {
            const unitIdx = parseInt(document.getElementById('topicUnitIdx').value);
            const name = document.getElementById('topicName').value.trim();
            const type = document.getElementById('topicType').value;
            if (!name) { alert('El nombre del tema es obligatorio.'); return; }
            if (!activeCourse.units[unitIdx].topics) activeCourse.units[unitIdx].topics = [];
            activeCourse.units[unitIdx].topics.push({ id: 't_' + Math.random().toString(36).substr(2, 5), title: name, type: type, content: '' });
            document.getElementById('topicModal').style.display = 'none';
            renderSyllabusList();
            await updateCourseOnServer();
        }

        // --- QUIZ BUILDER (DOCENTE) ---
        let currentQuizQuestions = [];

        function openQuizEditor(unitIdx, evIdx) {
            document.getElementById('quizEdUnitIdx').value = unitIdx;
            document.getElementById('quizEdEvIdx').value = evIdx;
            const ev = activeCourse.units[unitIdx].evaluations[evIdx];
            document.getElementById('quizEditorTitle').textContent = 'Preguntas: ' + ev.title;
            currentQuizQuestions = ev.questions ? JSON.parse(JSON.stringify(ev.questions)) : [];
            renderQuizEditorQuestions();
            document.getElementById('quizEditorModal').style.display = 'flex';
        }

        function renderQuizEditorQuestions() {
            const container = document.getElementById('quizQuestionsContainer');
            container.innerHTML = '';
            if (currentQuizQuestions.length === 0) {
                container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-muted); font-size:0.9rem; border:2px dashed #cbd5e1; border-radius:8px;">Sin preguntas. Haz clic en "+ Nueva Pregunta".</div>';
                return;
            }
            currentQuizQuestions.forEach((q, qIdx) => {
                const qBox = document.createElement('div');
                qBox.style = 'border:1px solid var(--border-color); border-radius:8px; padding:15px; background:var(--bg-main); position:relative;';
                let optionsHtml = '';
                if (['multiple','single'].includes(q.type)) {
                    optionsHtml = `
                        <div style="margin-top:10px;">
                            <label style="font-size:0.8rem; font-weight:600;">Opciones (separadas por coma):</label>
                            <input type="text" class="form-input" style="margin:4px 0 8px;" value="${escapeHtml((q.options||[]).join(', '))}" oninput="currentQuizQuestions[${qIdx}].options=this.value.split(',').map(s=>s.trim())">
                            <label style="font-size:0.8rem; font-weight:600;">Respuesta Correcta:</label>
                            <input type="text" class="form-input" value="${escapeHtml(q.correctAnswer||'')}" oninput="currentQuizQuestions[${qIdx}].correctAnswer=this.value.trim()">
                        </div>`;
                } else if (q.type === 'truefalse') {
                    optionsHtml = `
                        <div style="margin-top:10px;">
                            <label style="font-size:0.8rem; font-weight:600;">Respuesta Correcta:</label>
                            <select class="form-input" onchange="currentQuizQuestions[${qIdx}].correctAnswer=this.value">
                                <option value="Verdadero" ${q.correctAnswer==='Verdadero'?'selected':''}>Verdadero</option>
                                <option value="Falso" ${q.correctAnswer==='Falso'?'selected':''}>Falso</option>
                            </select>
                        </div>`;
                }
                qBox.innerHTML = `
                    <button style="position:absolute;top:8px;right:8px;color:#ef4444;background:none;border:none;cursor:pointer;font-size:1rem;" onclick="currentQuizQuestions.splice(${qIdx},1);renderQuizEditorQuestions()">🗑️</button>
                    <div style="display:flex;gap:10px;margin-bottom:10px;align-items:center;">
                        <span style="font-weight:700;color:var(--primary-color);min-width:24px;">#${qIdx+1}</span>
                        <select class="form-input" style="width:auto;padding:4px 8px;font-size:0.8rem;" onchange="currentQuizQuestions[${qIdx}].type=this.value;renderQuizEditorQuestions()">
                            <option value="single" ${q.type==='single'?'selected':''}>Única Respuesta</option>
                            <option value="multiple" ${q.type==='multiple'?'selected':''}>Selección Múltiple</option>
                            <option value="truefalse" ${q.type==='truefalse'?'selected':''}>Verdadero/Falso</option>
                            <option value="likert" ${q.type==='likert'?'selected':''}>Escala Likert</option>
                            <option value="open" ${q.type==='open'?'selected':''}>Respuesta Abierta</option>
                        </select>
                    </div>
                    <textarea class="form-input" rows="2" placeholder="Escribe el enunciado de la pregunta..." oninput="currentQuizQuestions[${qIdx}].text=this.value">${escapeHtml(q.text||'')}</textarea>
                    ${optionsHtml}
                `;
                container.appendChild(qBox);
            });
        }

        function addQuizQuestion() {
            currentQuizQuestions.push({ type: 'single', text: '', options: ['Opción A', 'Opción B'], correctAnswer: 'Opción A' });
            renderQuizEditorQuestions();
        }

        async function saveQuizQuestions() {
            const unitIdx = parseInt(document.getElementById('quizEdUnitIdx').value);
            const evIdx = parseInt(document.getElementById('quizEdEvIdx').value);
            for (let i=0; i<currentQuizQuestions.length; i++) {
                if (!currentQuizQuestions[i].text.trim()) { alert(`La pregunta #${i+1} no tiene enunciado.`); return; }
            }
            activeCourse.units[unitIdx].evaluations[evIdx].questions = currentQuizQuestions;
            document.getElementById('quizEditorModal').style.display = 'none';
            renderSyllabusList();
            await updateCourseOnServer();
            alert(`✅ ${currentQuizQuestions.length} pregunta(s) guardada(s) exitosamente.`);
        }

        // --- QUIZ TAKER (ESTUDIANTE) ---
        let currentTakingQuiz = [];
        let currentTakingEv = null;

        function takeQuiz(uIdx, evId) {
            const unit = activeCourse.units[uIdx];
            const ev = unit.evaluations.find(e => e.id === evId);
            if (!ev) return;
            currentTakingEv = ev;
            document.getElementById('takeQuizUnitIdx').value = uIdx;
            document.getElementById('takeQuizEvId').value = evId;
            document.getElementById('takeQuizTitle').textContent = ev.title;
            document.getElementById('takeQuizSub').innerHTML = `Evaluación CNA &mdash; Aprobación: <strong>${(ev.min_grade||3.0).toFixed(1)}</strong> / Máxima: <strong>${(ev.max_grade||5.0).toFixed(1)}</strong>`;
            currentTakingQuiz = ev.questions || [];
            const container = document.getElementById('takeQuizQuestionsContainer');
            container.innerHTML = '';
            if (currentTakingQuiz.length === 0) {
                container.innerHTML = '<div style="color:var(--text-muted);text-align:center;padding:20px;">Este examen aún no tiene preguntas configuradas.</div>';
            } else {
                currentTakingQuiz.forEach((q, qIdx) => {
                    const qBox = document.createElement('div');
                    qBox.style = 'border:1px solid var(--border-color);border-radius:8px;padding:15px;background:var(--bg-main);';
                    let inputHtml = '';
                    if (q.type === 'single') {
                        inputHtml = (q.options||[]).map(opt => `<label style="display:block;margin:5px 0;cursor:pointer;"><input type="radio" name="qans_${qIdx}" value="${escapeHtml(opt)}"> ${escapeHtml(opt)}</label>`).join('');
                    } else if (q.type === 'multiple') {
                        inputHtml = (q.options||[]).map(opt => `<label style="display:block;margin:5px 0;cursor:pointer;"><input type="checkbox" name="qans_${qIdx}" value="${escapeHtml(opt)}"> ${escapeHtml(opt)}</label>`).join('');
                    } else if (q.type === 'truefalse') {
                        inputHtml = `<label style="margin-right:15px;cursor:pointer;"><input type="radio" name="qans_${qIdx}" value="Verdadero"> Verdadero</label><label style="cursor:pointer;"><input type="radio" name="qans_${qIdx}" value="Falso"> Falso</label>`;
                    } else if (q.type === 'likert') {
                        inputHtml = `<div style="display:flex;gap:15px;align-items:flex-end;margin-top:8px;">${[1,2,3,4,5].map(v=>`<label style="text-align:center;cursor:pointer;"><input type="radio" name="qans_${qIdx}" value="${v}"><br>${v}</label>`).join('')}</div><div style="display:flex;justify-content:space-between;font-size:0.7rem;color:var(--text-muted);max-width:220px;margin-top:3px;"><span>Muy en desacuerdo</span><span>Muy de acuerdo</span></div>`;
                    } else if (q.type === 'open') {
                        inputHtml = `<textarea id="open_ans_${qIdx}" class="form-input" rows="3" style="margin-top:8px;" placeholder="Escribe tu respuesta..."></textarea>`;
                    }
                    qBox.innerHTML = `<p style="font-weight:600;margin:0 0 10px;">${qIdx+1}. ${escapeHtml(q.text)}</p>${inputHtml}`;
                    container.appendChild(qBox);
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
            let requiresManual = false;
            let correctCount = 0;
            let countable = 0;
            const studentAnswers = [];
            for (let i=0; i<currentTakingQuiz.length; i++) {
                const q = currentTakingQuiz[i];
                let ans = null;
                if (['single','truefalse','likert'].includes(q.type)) {
                    const sel = document.querySelector(`input[name="qans_${i}"]:checked`);
                    if (sel) ans = sel.value;
                } else if (q.type === 'multiple') {
                    const checked = [...document.querySelectorAll(`input[name="qans_${i}"]:checked`)];
                    if (checked.length > 0) ans = checked.map(c=>c.value).join('||');
                } else if (q.type === 'open') {
                    const ta = document.getElementById(`open_ans_${i}`);
                    if (ta && ta.value.trim()) ans = ta.value.trim();
                }
                if (!ans) { alert(`Por favor responde la pregunta #${i+1}`); return; }
                studentAnswers.push({ q: q.text, type: q.type, answer: ans });
                if (q.type === 'open') { requiresManual = true; }
                else if (q.type !== 'likert') {
                    countable++;
                    if (ans === q.correctAnswer) correctCount++;
                } else { countable++; correctCount++; }
            }
            let finalGrade = 0;
            let status = 'pending';
            if (!requiresManual && countable > 0) {
                finalGrade = Math.round(((correctCount / countable) * ((ev.max_grade||5.0) - 1.0) + 1.0) * 10) / 10;
                status = 'graded';
            }
            const payload = {
                user_id: userEmail,
                course_id: activeCourse.course_id,
                unit_id: unit.id,
                activity_id: evId,
                content: JSON.stringify(studentAnswers)
            };
            try {
                const res = await fetch(`https://siacmen.vercel.app/api/submissions?inst_id=${window.INST_ID}`, {
                    method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)
                });
                if (res.ok && status === 'graded') {
                    await fetch(`https://siacmen.vercel.app/api/submissions?inst_id=${window.INST_ID}`, {
                        method: 'PUT', headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({ user_id: userEmail, course_id: activeCourse.course_id, activity_id: evId, grade: finalGrade, feedback: 'Calificado automáticamente por el sistema.' })
                    });
                }
                if (res.ok) {
                    document.getElementById('takeQuizModal').style.display = 'none';
                    const msg = requiresManual
                        ? '✅ Respuestas enviadas. Pendiente de revisión por el docente.'
                        : `✅ Examen enviado. Tu nota es: ${finalGrade.toFixed(1)} / ${(ev.max_grade||5.0).toFixed(1)}`;
                    alert(msg);
                    openStudentCourse(activeCourse.course_id);
                } else {
                    alert('Error al enviar el examen. Intenta nuevamente.');
                }
            } catch(e) { console.error(e); alert('Error de conexión.'); }
        }
"""

# Insert modals before </body>
if 'id="topicModal"' not in html:
    html = html.replace('</body>', topic_modal + '\n</body>')
    print('PATCH 7a: topic, quiz editor, quiz taker modals inserted')
else:
    print('PATCH 7a: modals already exist (skipped)')

# Insert JS before closing </script>
if 'function openAddTopicModal' not in html:
    last_script = html.rfind('</script>')
    html = html[:last_script] + quiz_js + '\n    </script>' + html[last_script+len('</script>'):]
    print('PATCH 7b: JS functions inserted')
else:
    print('PATCH 7b: JS already exists (skipped)')

# ==========================================
# PATCH 8: Fix student view eval button to call takeQuiz
# ==========================================
old_btn = """<button class="btn-primary" style="padding:8px 16px; font-size:0.8rem; background: var(--primary-gradient); border:none; color:white; border-radius:10px;" onclick="presentQuiz('${escapeHtml(ev.title).replace(/'/g, &quot;\\\\'&quot;)}', ${ev.min_grade || 3.0}, ${ev.max_grade || 5.0})">Presentar Examen</button>"""

# Try a regex approach for the student eval button
pattern = r'onclick="presentQuiz\([^)]+\)">Presentar Examen</button>'
matches = re.findall(pattern, html)
if matches:
    html = re.sub(pattern, r"onclick=\"takeQuiz(\${uIdx}, '\${ev.id}')\">Presentar Examen</button>", html)
    print(f'PATCH 8 applied: replaced {len(matches)} presentQuiz button(s) in student view')
else:
    print('PATCH 8: No presentQuiz eval buttons found (check manually)')

with open('c:\\SIAC\\templates\\formacion.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\\nFinal file length: {len(html)} chars')
# Verify final state
if 'takeQuizModal' in html:
    print('✅ takeQuizModal present')
if 'quizEditorModal' in html:
    print('✅ quizEditorModal present')
if 'topicModal' in html:
    print('✅ topicModal present')
if 'function takeQuiz' in html:
    print('✅ function takeQuiz present')
if 'function openQuizEditor' in html:
    print('✅ function openQuizEditor present')
if 'function submitAddTopic' in html:
    print('✅ function submitAddTopic present')
