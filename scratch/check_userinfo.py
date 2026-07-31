with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'id="userInfo"' in line or "id='userInfo'" in line:
            print(f'Line {i+1}: {line.strip()}')
