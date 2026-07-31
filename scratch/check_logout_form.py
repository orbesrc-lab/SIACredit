with open(r'c:\SIAC\templates\formacion.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if 'logout()' in l:
        print(f'{i}: {l.strip().encode("utf-8")}')
