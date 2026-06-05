with open('c:/SIAC/templates/evidencias.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

found = False
for i, line in enumerate(lines):
    if 'function saveFactor4Data' in line:
        found = True
        print(f"--- saveFactor4Data start line: {i+1} ---")
        for j in range(i, min(i+150, len(lines))):
            print(f"{j+1}: {lines[j].strip().encode('ascii', 'ignore').decode('ascii')}")
        break
