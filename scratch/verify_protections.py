import os

print("Verificacion de logica en app.py...")
with open('c:/SIAC/app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'if inst_id == 1:' in content:
        print("OK: Proteccion de backend (if inst_id == 1) detectada.")
    else:
        print("ERROR: Proteccion de backend NO encontrada.")

with open('c:/SIAC/templates/configuracion.html', 'r', encoding='utf-8') as f:
    content = f.read()
    if "if (instId == '1')" in content or 'if(select.value == \'1\')' in content:
        print("OK: Proteccion de frontend detectada.")
    else:
        print("ERROR: Proteccion de frontend NO encontrada.")
