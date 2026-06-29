with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
# Get the CSS block with input styling
style_blocks = re.findall(r'<style>(.*?)</style>', html, re.DOTALL)
for sb in style_blocks:
    if 'input' in sb.lower():
        # Find lines around 'body, input'
        lines = sb.split('\n')
        for i, line in enumerate(lines):
            if 'input' in line.lower() and ('form' in line.lower() or 'body' in line.lower()):
                start = max(0, i)
                end = min(len(lines), i + 15)
                for l in lines[start:end]:
                    print(l.encode('ascii','ignore').decode('ascii'))
                print('---')
                break
