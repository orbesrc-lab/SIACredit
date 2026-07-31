import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'c:\SIAC\templates\formacion.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if '<aside class="sidebar">' in l:
        print(''.join(lines[i:i+30]))
        break
