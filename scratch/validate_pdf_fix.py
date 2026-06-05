import ast, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app.py', encoding='utf-8') as f: src = f.read()
ast.parse(src)
print(f'app.py OK - {len(src.splitlines())} lineas')

with open('templates/informes.html', encoding='utf-8') as f: html = f.read()
print(f'informes.html OK - {len(html.splitlines())} lineas')

checks = [
    ('btnImprimir llama imprimirInformeCompleto',  'imprimirInformeCompleto()' in html),
    ('window.print() directo eliminado del boton', 'onclick="window.print()"' not in html),
    ('imprimirRRC usa abrirVentanaImpresion',       'abrirVentanaImpresion(htmlDoc' in html),
    ('function imprimirInformeCompleto definida',   'function imprimirInformeCompleto' in html),
    ('function abrirVentanaImpresion definida',     'function abrirVentanaImpresion' in html),
    ('Portada RRC en PDF',                          'class="portada"' in html),
    ('Resumen ejecutivo tabla en PDF',              'tabla-resumen' in html),
    ('condicion-bloque por condicion',              'condicion-bloque' in html),
    ('Semaforo en documento PDF',                   'sem-verde' in html),
    ('Analisis IA extraido del DOM',                'ai-content' in html),
    ('Print-color-adjust para colores',             'print-color-adjust:exact' in html),
    ('page-break-after portada',                    'page-break-after:always' in html),
]

all_ok = True
for desc, ok in checks:
    status = 'OK' if ok else '!! FALLA !!'
    if not ok: all_ok = False
    print(f'  [{status}] {desc}')

print(f'\nwindow.print() restante en archivo: {html.count("window.print()")} (debe ser 1, en abrirVentanaImpresion)')
print('\n=== TODO CORRECTO ===' if all_ok else '\n=== HAY ERRORES ===')
