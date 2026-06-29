import re

with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the exact onclick for the Presentar Examen button
for m in re.finditer(r'<button[^>]*onclick="([^"]*)"[^>]*>[^<]*Presentar Examen', html):
    print(f'Found button onclick: {m.group(1)[:200]}')
    print(f'Full match: {m.group()[:300]}')
    print()
