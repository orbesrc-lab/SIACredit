with open(r'c:\SIAC\templates\configuracion.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'function saveGlobalSettings' in line:
        for j in range(i+30, i+55):
            if j < len(lines):
                print(lines[j].strip().encode('utf-8'))
        break
