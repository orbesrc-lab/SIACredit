import os

file_informes = r'c:\SIAC\templates\informes.html'
with open(file_informes, 'r', encoding='utf-8') as f:
    content = f.read()

print_func = """
    function imprimirInformeCompleto() {
        window.print();
    }
"""

if "function imprimirInformeCompleto()" not in content:
    content = content.replace("function aplicarPermisosEnUI() {", print_func + "\n    function aplicarPermisosEnUI() {")

with open(file_informes, 'w', encoding='utf-8') as f:
    f.write(content)

print("imprimirInformeCompleto function defined in informes.html!")
