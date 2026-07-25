import re

with open('c:/SIAC/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '@app.route' in line or 'render_template' in line:
        print(f"{i+1}: {line.strip()}")
