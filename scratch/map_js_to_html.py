"""
Find the exact HTML line numbers corresponding to JS line 1290 and 1437.
"""
import re

with open('c:/SIAC/templates/formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract all <script> blocks with their HTML positions
script_blocks = []
for m in re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
    start = m.start(1)
    content = m.group(1)
    script_blocks.append((start, content))

# Combine JS and track line offsets
js_line = 0
for html_start, content in script_blocks:
    lines = content.split('\n')
    html_line_start = html[:html_start].count('\n') + 1
    
    target_js_lines = {1290, 1437, 1465, 1467, 1471, 1738}
    
    for i, line in enumerate(lines):
        js_line += 1
        if js_line in target_js_lines:
            html_actual = html_line_start + i
            print(f"JS line {js_line} -> HTML line {html_actual}: {line.strip()[:100]}")
