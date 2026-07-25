with open('c:/SIAC/templates/informes.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'const RRC_CONDICIONES' in line or 'RRC_CONDICIONES =' in line:
        safe_line = line.strip().encode('ascii', 'ignore').decode('ascii')
        print(f"{i+1}: {safe_line}")
