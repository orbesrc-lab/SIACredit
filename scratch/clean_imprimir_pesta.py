with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

fn_start = content.find('function imprimirPESTA()')
if fn_start != -1:
    fn_end = content.find('let _globalPermissions = {};', fn_start)
    if fn_end != -1:
        clean_pesta = '''function imprimirPESTA() {
            const contenido = document.getElementById('pestaMarkdownReport').innerHTML;
            const win = window.open('', '_blank', 'width=900,height=700');
            win.document.write(`<!DOCTYPE html><html><head><title>Informe PESTA</title><style>body{font-family:Inter,sans-serif;padding:40px;color:#333;line-height:1.6}h1,h2,h3{color:#0284c7}</style></head><body>${contenido}</body></html>`);
            win.document.close();
            win.focus();
            setTimeout(() => win.print(), 500);
        }

        '''
        content = content[:fn_start] + clean_pesta + content[fn_end:]
        print("imprimirPESTA cleaned successfully!")

with open(r'c:\SIAC\templates\informes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("informes.html saved!")
