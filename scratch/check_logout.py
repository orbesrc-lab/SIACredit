with open(r'c:\SIAC\templates\dashboard.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'logout()' in line:
            print(f'{i}: {line.strip().encode("utf-8")}')
