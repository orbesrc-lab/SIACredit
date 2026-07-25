import os

files = ['c:/SIAC/templates/evidencias.html', 'c:/SIAC/templates/evidencias_mod.html']
for filepath in files:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    print(f"=== {os.path.basename(filepath)} ===")
    for i, line in enumerate(lines):
        if 'tr.dataset' in line or 'adjunto:' in line:
            print(f"{i+1}: {line.strip()}")
