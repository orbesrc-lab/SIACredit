"""
Extract all JavaScript from formacion.html and check for syntax problems.
"""
import re

with open('c:/SIAC/templates/formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract all <script> content
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"Found {len(scripts)} script blocks")

all_js = '\n'.join(scripts)

# Check bracket balance
opens = {'(': 0, '{': 0, '[': 0}
closes = {')': '(', '}': '{', ']': '['}
in_string = False
string_char = ''
escape = False
in_template = False
template_depth = 0
line_num = 1

errors = []
for i, ch in enumerate(all_js):
    if ch == '\n':
        line_num += 1
    
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
            opens[ch] += 1
        elif ch in closes:
            expected = closes[ch]
            if opens[expected] <= 0:
                errors.append(f"Line ~{line_num}: Unexpected '{ch}'")
                if len(errors) > 5:
                    break
            else:
                opens[expected] -= 1
    else:
        if ch == string_char and string_char != '`':
            in_string = False
        elif ch == string_char and string_char == '`':
            in_string = False

print(f"\nBracket counts remaining (should be 0,0,0): ( {opens['(']}  {{ {opens['{']}  [ {opens['[']}")
if errors:
    print("\nErrors found:")
    for e in errors:
        print(" ", e)
else:
    print("\nNo unmatched brackets found!")

# Check for duplicate function definitions
funcs = re.findall(r'(?:function\s+(\w+)|window\.(\w+)\s*=)', all_js)
from collections import Counter
names = [f[0] or f[1] for f in funcs]
dups = {n: c for n, c in Counter(names).items() if c > 1}
if dups:
    print(f"\nDuplicate functions: {dups}")
else:
    print("No duplicate functions found.")
