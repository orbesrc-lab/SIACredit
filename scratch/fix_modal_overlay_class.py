with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace quizEditorModal overlay class with direct inline styling
# Also fix takeQuizModal and topicModal

# Fix quizEditorModal
html = html.replace(
    '<div id="quizEditorModal" class="modal-overlay" style="display: none; z-index: 2500;">',
    '<div id="quizEditorModal" style="display: none; position:fixed; inset:0; background:rgba(15,23,42,0.65); backdrop-filter:blur(4px); z-index: 2500; align-items:center; justify-content:center;">'
)

html = html.replace(
    '<div class="modal-content" style="max-width: 700px; width: 95%;">\n                <div class="modal-header">\n                    <h3 id="quizEditorTitle" style="margin:0;">Editor de Preguntas</h3>',
    '<div style="background:#ffffff; border-radius:16px; padding:0; width:95%; max-width:720px; max-height:90vh; display:flex; flex-direction:column; box-shadow:0 25px 60px rgba(0,0,0,0.3); pointer-events:auto; overflow:hidden;">\n                <div style="background: linear-gradient(135deg,#6366f1,#a855f7); padding:20px 25px; display:flex; justify-content:space-between; align-items:center; flex-shrink:0;">\n                    <h3 id="quizEditorTitle" style="margin:0; color:white; font-size:1.1rem;">Editor de Preguntas</h3>'
)

# Fix quizEditorModal close button style  
html = html.replace(
    '<button class="close-btn" onclick="document.getElementById(\'quizEditorModal\').style.display=\'none\'">&times;</button>\n                </div>',
    '<button onclick="document.getElementById(\'quizEditorModal\').style.display=\'none\'" style="background:rgba(255,255,255,0.2); border:none; color:white; border-radius:50%; width:32px; height:32px; font-size:1.2rem; cursor:pointer; display:flex; align-items:center; justify-content:center;">&times;</button>\n                </div>',
    1  # only first occurrence
)

# Fix the inner toolbar div
html = html.replace(
    '<div style="padding:0 20px 15px; display: flex; justify-content: space-between; align-items: center;">',
    '<div style="padding:15px 20px 10px; display: flex; justify-content: space-between; align-items: center; flex-shrink:0; border-bottom:1px solid #e2e8f0;">',
    1
)

# Fix the questions container
html = html.replace(
    '<div id="quizQuestionsContainer" style="display: flex; flex-direction: column; gap: 15px; max-height: 50vh; overflow-y: auto; padding: 0 20px 10px;">',
    '<div id="quizQuestionsContainer" style="display: flex; flex-direction: column; gap: 12px; flex:1; overflow-y: auto; padding: 15px 20px;">',
    1
)

# Fix the footer save button div
html = html.replace(
    '<div style="padding:20px; border-top:1px solid var(--border-color);">',
    '<div style="padding:15px 20px; border-top:1px solid #e2e8f0; flex-shrink:0;">',
    1
)

# Fix takeQuizModal similarly
html = html.replace(
    '<div id="takeQuizModal" class="modal-overlay" style="display: none; z-index: 2600;">',
    '<div id="takeQuizModal" style="display: none; position:fixed; inset:0; background:rgba(15,23,42,0.65); backdrop-filter:blur(4px); z-index: 2600; align-items:center; justify-content:center;">'
)

# Fix topicModal similarly
html = html.replace(
    '<div id="topicModal" class="modal-overlay" style="display: none;">',
    '<div id="topicModal" style="display: none; position:fixed; inset:0; background:rgba(15,23,42,0.65); backdrop-filter:blur(4px); z-index: 2400; align-items:center; justify-content:center;">'
)

print('Checking fixes...')
checks = [
    ('quizEditorModal fixed', 'id="quizEditorModal" style="display: none; position:fixed'),
    ('takeQuizModal fixed', 'id="takeQuizModal" style="display: none; position:fixed'),
    ('topicModal fixed', 'id="topicModal" style="display: none; position:fixed'),
]
for label, pattern in checks:
    print(f'  [{" OK " if pattern in html else "FAIL"}] {label}')

with open('c:\\SIAC\\templates\\formacion.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved.')
