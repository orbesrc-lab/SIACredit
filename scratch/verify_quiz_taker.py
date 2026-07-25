with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        stripped = line.strip().encode('ascii', 'ignore').decode('ascii')
        if 'takeQuiz' in stripped or 'QUIZ TAKER' in stripped or 'takeQuizModal' in stripped:
            print(f'Line {i+1}: {stripped[:120]}')
