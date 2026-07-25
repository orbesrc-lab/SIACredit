with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find a working textarea in an existing modal
import re
# Look for any textarea in a modal
textareas = list(re.finditer(r'<textarea[^>]*>',html))
for m in textareas:
    print(f'Pos {m.start()}: {m.group().encode("ascii","ignore").decode("ascii")}')
