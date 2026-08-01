with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
# Find ALL lines that open a print window template literal
for i, line in enumerate(lines, start=1):
    if 'win.document.write' in line or 'const html = `' in line or 'const htmlContent = `' in line:
        print(f'Line {i}: {repr(line[:120])}')
