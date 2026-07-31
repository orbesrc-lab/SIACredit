import os

file_path = r'c:\SIAC\templates\empresa_matrices.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = "Swal.fire('¡Éxito!', 'Matrices pobladas desde DOFA/PESTA.', 'success');"
replacement = "Swal.fire('¡Éxito!', 'Matrices pobladas desde DOFA/PESTA.', 'success');\n                            await saveAllMatrices();"

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Auto-save added to Poblar")
else:
    print("Target not found.")
