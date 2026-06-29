with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'presentQuiz' in line:
            print(f'Line {i+1}: {line.strip().encode("ascii", "ignore").decode("ascii")}')
