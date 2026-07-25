with open('c:/SIAC/templates/evidencias.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'function saveFactor' in line:
        print(f"Line {i+1}: {line.strip()}")
        # print the next 15 lines
        for k in range(i, min(i+15, len(lines))):
            print(f"  {k+1}: {lines[k].strip().encode('ascii', 'ignore').decode('ascii')}")
