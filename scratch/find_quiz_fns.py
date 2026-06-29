with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        keywords = ['function renderQuizEditorQuestions', 'function addQuizQuestion', 'function saveQuizQuestions', 'function openQuizEditor']
        for kw in keywords:
            if kw in line:
                print(f'Line {i+1}: {kw}')
