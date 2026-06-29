with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# The inline style for inputs/selects/textarea used throughout the app
INPUT_STYLE = 'width:100%; padding:10px 12px; border:1px solid #cbd5e1; border-radius:8px; font-size:0.9rem; font-family:var(--font-main,sans-serif); background:#ffffff; color:#0f172a; box-sizing:border-box; outline:none;'
SELECT_STYLE = 'padding:6px 10px; border:1px solid #cbd5e1; border-radius:8px; font-size:0.82rem; font-family:var(--font-main,sans-serif); background:#ffffff; color:#0f172a;'

# Replace form-input class with inline styles in the renderQuizEditorQuestions function
# We need to surgically update the JS function

old_render = """        function renderQuizEditorQuestions() {
            const container = document.getElementById('quizQuestionsContainer');
            container.innerHTML = '';
            if (currentQuizQuestions.length === 0) {
                container.innerHTML = '<div style="text-align:center; padding:30px; color:var(--text-muted); font-size:0.9rem; border:2px dashed #cbd5e1; border-radius:8px;">Sin preguntas. Haz clic en "+ Nueva Pregunta".</div>';
                return;
            }
            currentQuizQuestions.forEach((q, qIdx) => {
                const qBox = document.createElement('div');
                qBox.style.cssText = 'border:1px solid var(--border-color); border-radius:10px; padding:18px; background:var(--bg-main); position:relative; margin-bottom:5px;';

                // Header row: number + type selector + delete
                const header = document.createElement('div');
                header.style.cssText = 'display:flex; gap:10px; margin-bottom:12px; align-items:center;';

                const numSpan = document.createElement('span');
                numSpan.style.cssText = 'font-weight:700; color:var(--primary-color); min-width:28px; font-size:0.9rem;';
                numSpan.textContent = '#' + (qIdx + 1);
                header.appendChild(numSpan);

                const typeSelect = document.createElement('select');
                typeSelect.className = 'form-input';
                typeSelect.style.cssText = 'flex:1; padding:6px 10px; font-size:0.82rem;';"""

new_render = """        function renderQuizEditorQuestions() {
            const container = document.getElementById('quizQuestionsContainer');
            container.innerHTML = '';
            if (currentQuizQuestions.length === 0) {
                container.innerHTML = '<div style="text-align:center; padding:30px; color:#64748b; font-size:0.9rem; border:2px dashed #cbd5e1; border-radius:8px;">Sin preguntas. Haz clic en \"+ Nueva Pregunta\".</div>';
                return;
            }
            currentQuizQuestions.forEach((q, qIdx) => {
                const qBox = document.createElement('div');
                qBox.style.cssText = 'border:1px solid #e2e8f0; border-radius:10px; padding:18px; background:#f8fafc; position:relative; margin-bottom:5px;';

                // Header row: number + type selector + delete
                const header = document.createElement('div');
                header.style.cssText = 'display:flex; gap:10px; margin-bottom:12px; align-items:center;';

                const numSpan = document.createElement('span');
                numSpan.style.cssText = 'font-weight:700; color:#6366f1; min-width:28px; font-size:0.9rem;';
                numSpan.textContent = '#' + (qIdx + 1);
                header.appendChild(numSpan);

                const typeSelect = document.createElement('select');
                typeSelect.style.cssText = 'flex:1; padding:6px 10px; border:1px solid #cbd5e1; border-radius:8px; font-size:0.82rem; font-family:sans-serif; background:#fff; color:#0f172a;';"""

if old_render in html:
    html = html.replace(old_render, new_render)
    print('Replaced render header block')
else:
    print('HEADER BLOCK NOT FOUND')

# Fix the textarea inside renderQuizEditorQuestions
old_ta = """                const ta = document.createElement('textarea');
                ta.id = 'qtext_' + qIdx;
                ta.className = 'form-input';
                ta.rows = 2;
                ta.placeholder = 'Escribe el enunciado de la pregunta aquí...';
                ta.value = q.text || '';
                ta.style.cssText = 'width:100%; resize:vertical; min-height:60px; box-sizing:border-box;';
                qBox.appendChild(ta);"""

new_ta = """                const ta = document.createElement('textarea');
                ta.id = 'qtext_' + qIdx;
                ta.rows = 3;
                ta.placeholder = 'Escribe el enunciado de la pregunta aquí...';
                ta.value = q.text || '';
                ta.style.cssText = 'width:100%; padding:10px 12px; border:1px solid #cbd5e1; border-radius:8px; font-size:0.9rem; font-family:sans-serif; background:#ffffff; color:#0f172a; box-sizing:border-box; resize:vertical; min-height:70px; display:block;';
                qBox.appendChild(ta);"""

if old_ta in html:
    html = html.replace(old_ta, new_ta)
    print('Replaced textarea block')
else:
    print('TEXTAREA BLOCK NOT FOUND')

# Fix options input
old_opts_in = """                    optsIn.type = 'text';
                    optsIn.id = 'qopts_' + qIdx;
                    optsIn.className = 'form-input';
                    optsIn.value = (q.options || []).join(', ');
                    optsIn.placeholder = 'Ej: Opción A, Opción B, Opción C';
                    optsIn.style.marginBottom = '8px';"""

new_opts_in = """                    optsIn.type = 'text';
                    optsIn.id = 'qopts_' + qIdx;
                    optsIn.value = (q.options || []).join(', ');
                    optsIn.placeholder = 'Ej: Opción A, Opción B, Opción C';
                    optsIn.style.cssText = 'width:100%; padding:10px 12px; border:1px solid #cbd5e1; border-radius:8px; font-size:0.9rem; font-family:sans-serif; background:#fff; color:#0f172a; box-sizing:border-box; margin-bottom:8px; display:block;';"""

if old_opts_in in html:
    html = html.replace(old_opts_in, new_opts_in)
    print('Replaced options input block')
else:
    print('OPTIONS INPUT BLOCK NOT FOUND')

# Fix correct answer input
old_corr_in = """                    corrIn.type = 'text';
                    corrIn.id = 'qcorr_' + qIdx;
                    corrIn.className = 'form-input';
                    corrIn.value = q.correctAnswer || '';
                    corrIn.placeholder = 'Ej: Opción A';"""

new_corr_in = """                    corrIn.type = 'text';
                    corrIn.id = 'qcorr_' + qIdx;
                    corrIn.value = q.correctAnswer || '';
                    corrIn.placeholder = 'Ej: Opción A';
                    corrIn.style.cssText = 'width:100%; padding:10px 12px; border:1px solid #cbd5e1; border-radius:8px; font-size:0.9rem; font-family:sans-serif; background:#fff; color:#0f172a; box-sizing:border-box; display:block;';"""

if old_corr_in in html:
    html = html.replace(old_corr_in, new_corr_in)
    print('Replaced correct answer input block')
else:
    print('CORRECT ANSWER INPUT BLOCK NOT FOUND')

# Fix truefalse select
old_tf_sel = """                    tfSel.id = 'qtf_' + qIdx;
                    tfSel.className = 'form-input';"""

new_tf_sel = """                    tfSel.id = 'qtf_' + qIdx;
                    tfSel.style.cssText = 'width:100%; padding:10px 12px; border:1px solid #cbd5e1; border-radius:8px; font-size:0.9rem; font-family:sans-serif; background:#fff; color:#0f172a; box-sizing:border-box;';"""

if old_tf_sel in html:
    html = html.replace(old_tf_sel, new_tf_sel)
    print('Replaced truefalse select block')
else:
    print('TRUEFALSE SELECT BLOCK NOT FOUND')

# Also fix the takeQuizModal textarea for open answers
old_open_ta = """inputHtml = `<textarea id="open_ans_${qIdx}" class="form-input" rows="3" style="margin-top:8px;" placeholder="Escribe tu respuesta..."></textarea>`;"""
new_open_ta = """inputHtml = `<textarea id="open_ans_${qIdx}" rows="3" style="margin-top:8px; width:100%; padding:10px 12px; border:1px solid #cbd5e1; border-radius:8px; font-size:0.9rem; font-family:sans-serif; background:#fff; color:#0f172a; box-sizing:border-box; resize:vertical;" placeholder="Escribe tu respuesta..."></textarea>`;"""

if old_open_ta in html:
    html = html.replace(old_open_ta, new_open_ta)
    print('Replaced open answer textarea')
else:
    print('OPEN TA BLOCK NOT FOUND')

with open('c:\\SIAC\\templates\\formacion.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('\nDone! All inline styles applied.')
