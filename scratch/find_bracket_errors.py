"""
Find EXACTLY which lines have the JS bracket errors.
"""
import re

with open('c:/SIAC/templates/formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
all_js = '\n'.join(scripts)

# Map line numbers in JS back to HTML
script_start = html.find('<script>') + len('<script>')
lines_before = html[:script_start].count('\n') + 1

lines = all_js.split('\n')

opens = {'(': [], '{': [], '[': []}
closes = {')': '(', '}': '{', ']': '['}
in_string = False
string_char = ''
escape = False

errors = []
for line_idx, line in enumerate(lines):
    for col_idx, ch in enumerate(line):
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if not in_string:
            if ch in ('"', "'", '`'):
                in_string = True
                string_char = ch
            elif ch in opens:
                opens[ch].append(line_idx + 1)
            elif ch in closes:
                expected = closes[ch]
                if opens[expected]:
                    opens[expected].pop()
                else:
                    errors.append(f"Unexpected '{ch}' at JS line {line_idx+1}: {line.strip()[:80]}")
        else:
            if ch == string_char and string_char != '`':
                in_string = False
            elif ch == string_char and string_char == '`':
                in_string = False

print("Errors (unexpected close):")
for e in errors[:10]:
    print(" ", e)

print("\nUnclosed opens:")
for ch, positions in opens.items():
    if positions:
        # Show last few unclosed
        for p in positions[-3:]:
            print(f"  '{ch}' opened at JS line {p}: {lines[p-1].strip()[:80]}")
