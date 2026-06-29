with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
# Get the modal-overlay and modal-content CSS
style_blocks = re.findall(r'<style>(.*?)</style>', html, re.DOTALL)
for sb in style_blocks:
    lines = sb.split('\n')
    for i, line in enumerate(lines):
        if 'modal' in line.lower():
            # print surrounding context
            start = max(0, i)
            end = min(len(lines), i + 20)
            for l in lines[start:end]:
                print(l.encode('ascii','ignore').decode('ascii'))
            print('---')
            break
