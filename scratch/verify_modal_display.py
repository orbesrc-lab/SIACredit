with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
# Find all places where these modals are shown
for modal in ['quizEditorModal', 'takeQuizModal', 'topicModal']:
    shows = re.findall(rf'getElementById\(\'{modal}\'\)\.style\.display\s*=\s*[\'"]([^\'"]*)[\'"]', html)
    print(f'{modal} display values set: {shows}')
