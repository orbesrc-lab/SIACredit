import re

with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Clean up imprimirRRC()
fn_start = content.find('function imprimirRRC()')
if fn_start != -1:
    # Find end of imprimirRRC (it ends right before function generarInformeIA())
    fn_next = content.find('function generarInformeIA()', fn_start)
    if fn_next != -1:
        clean_imprimirRRC = '''function imprimirRRC() {
            if (!_rrcCondData) {
                alert('Primero genera el soporte antes de imprimir.');
                return;
            }
            const rrcContent = document.getElementById('rrcReportContainer');
            if (!rrcContent) return;
            const win = window.open('', '_blank', 'width=900,height=700');
            win.document.write(`<!DOCTYPE html><html><head><title>Soporte Registro Calificado</title><style>body{font-family:Inter,sans-serif;padding:30px;color:#333;line-height:1.6}h1,h2,h3{color:#1e3a8a}table{border-collapse:collapse;width:100%}td,th{border:1px solid #e2e8f0;padding:8px}</style></head><body>${rrcContent.innerHTML}</body></html>`);
            win.document.close();
            win.focus();
            setTimeout(() => win.print(), 500);
        }

        '''
        content = content[:fn_start] + clean_imprimirRRC + content[fn_next:]
        print("imprimirRRC cleaned successfully!")

# 2. Check for duplicate functions after cleaning
matches = [(m.start(), m.end(), m.group(1)) for m in re.finditer(r'function\s+([a-zA-Z0-9_]+)\s*\(', content)]
seen = set()
to_remove = []

# Find second occurrences of duplicated top-level functions at the bottom of main script block
for start, end, fn in matches:
    if fn in ('generarInformeIA', 'renderInformeIA', 'abrirModalDOFA', 'cerrarModalDOFA', 
              'generarDOFAInterno', 'abrirModalPESTA', 'cerrarModalPESTA', 'generarDOFAExterno', 
              'renderPESTA', 'imprimirPESTA', 'aplicarPermisosEnUI', 'togglePermEditMode', 
              'onNodeClickForPerm', 'abrirModalPermisos', 'cerrarModalPermisos', 'guardarPermisosNodo', 
              'renderDOFA', 'speakColombianVoice'):
        if fn in seen:
            print(f"Duplicate function to remove: {fn} at pos {start}")
        else:
            seen.add(fn)

with open(r'c:\SIAC\templates\informes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("informes.html updated!")
