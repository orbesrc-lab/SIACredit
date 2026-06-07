import sys

with open('c:/SIAC/scratch/test.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove comments and strings to safely check braces
import re
text = re.sub(r'//.*', '', text)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

# Simplified string removal
def remove_strings(t):
    in_str = False
    str_char = ''
    escape = False
    res = []
    for c in t:
        if escape:
            escape = False
            continue
        if c == '\\':
            escape = True
            continue
        if not in_str:
            if c in ['"', "'", '`']:
                in_str = True
                str_char = c
            else:
                res.append(c)
        else:
            if c == str_char:
                in_str = False
                res.append('""') # Placeholder
    return ''.join(res)

clean_text = remove_strings(text)

stack = []
for i, c in enumerate(clean_text):
    if c in '{[(':
        stack.append(c)
    elif c in '}])':
        if not stack:
            print(f"Unmatched {c} at index {i}")
            sys.exit(1)
        top = stack.pop()
        if (c == '}' and top != '{') or (c == ']' and top != '[') or (c == ')' and top != '('):
            print(f"Mismatched {c} at index {i}, expected match for {top}")
            sys.exit(1)

if stack:
    print(f"Unmatched opening braces left: {stack}")
else:
    print("Braces are PERFECTLY MATCHED!")
