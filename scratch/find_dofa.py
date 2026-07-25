with open('c:/SIAC/templates/informes.html', 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f):
        if 'id="dofaOverlay"' in line:
            print(f'Line {i+1}: {line.strip()}')
