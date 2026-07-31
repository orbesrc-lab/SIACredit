import re

with open(r'c:\SIAC\templates\formacion.html', 'r', encoding='utf-8') as f:
    content = f.read()

# I will find the exact string that was placed and fix it.
pattern = r'// Verificar rol de usuario\s*if \(user && user\.role === \'estudiante\'\) \{\s*overflow: visible !important;\s*padding-bottom: 80px !important;\s*\}\s*\.content-area \{\s*display: block !important;\s*height: auto !important;\s*overflow: visible !important;\s*max-width: 1000px !important;\s*margin: 0 auto !important;\s*\}\s*/\* Ocultar posibles modales buggeados que bloquean clicks \*/\s*\.modal-backdrop \{ display: none !important; \}\s*`;\s*document\.head\.appendChild\(scrollFix\);\s*\}'

match = re.search(pattern, content)
if match:
    print("Found broken code!")
    new_content = content.replace(match.group(0), '')
    with open(r'c:\SIAC\templates\formacion.html', 'w', encoding='utf-8') as out:
        out.write(new_content)
else:
    print("Could not find broken code, maybe regex failed.")
