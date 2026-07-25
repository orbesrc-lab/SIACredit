import os

files = ['c:/SIAC/templates/evidencias.html', 'c:/SIAC/templates/evidencias_mod.html']
for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        print(f"--- File: {os.path.basename(filepath)} ---")
        for i, line in enumerate(lines):
            if 'Error de conexi' in line or 'Guardar Todos' in line or 'saveCuadros' in line or 'uploadFile' in line or 'save_cuadros' in line:
                print(f"{i+1}: {line.strip().encode('ascii', 'ignore').decode('ascii')}")
