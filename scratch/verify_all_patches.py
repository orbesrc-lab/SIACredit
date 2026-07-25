with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

checks = [
    ('takeQuizModal', 'id="takeQuizModal"'),
    ('quizEditorModal', 'id="quizEditorModal"'),
    ('topicModal', 'id="topicModal"'),
    ('function takeQuiz', 'function takeQuiz'),
    ('function openQuizEditor', 'function openQuizEditor'),
    ('function submitAddTopic', 'function submitAddTopic'),
    ('function openAddTopicModal', 'function openAddTopicModal'),
    ('saveQuizQuestions', 'function saveQuizQuestions'),
    ('submitQuizAnswers', 'function submitQuizAnswers'),
    ('dynamic icon in student view', 'const icon = t.type'),
    ('eval progression', 'submittedEvalsCount'),
    ('openAddTopicModal button', 'onclick="openAddTopicModal'),
    ('Editar Preguntas button', 'openQuizEditor('),
]

print('--- VERIFICATION REPORT ---')
all_ok = True
for label, pattern in checks:
    found = pattern in html
    status = 'OK' if found else 'MISSING'
    if not found:
        all_ok = False
    print(f'  [{status}] {label}')

# Check for remaining presentQuiz in student view
import re
pq = re.findall(r'Presentar Examen', html)
print(f'\n  Presentar Examen buttons found: {len(pq)}')

# Find exactly where 'Presentar Examen' buttons are
for m in re.finditer(r'onclick="[^"]*">[^<]*Presentar Examen', html):
    print(f'  Button onclick: {m.group()[:100]}')

lines = html.count('\n')
print(f'\nTotal lines: {lines}')
print('All checks OK:', all_ok)
