import sys

with open('c:/SIAC/scratch/test.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
text = re.sub(r'//.*', '', text)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

def remove_strings(t):
    in_str = False
    str_char = ''
    escape = False
    res = []
    for c in t:
        if escape:
            escape = False
            res.append('X')
            continue
        if c == '\\':
            escape = True
            res.append('X')
            continue
        if not in_str:
            if c in ['"', "'", '`']:
                in_str = True
                str_char = c
                res.append(c)
            else:
                res.append(c)
        else:
            if c == str_char:
                in_str = False
                res.append(c)
            else:
                res.append('X')
    return ''.join(res)

clean_text = remove_strings(text)

stack = []
for i, c in enumerate(clean_text):
    if c in '{[(':
        stack.append((c, i))
    elif c in '}])':
        if not stack:
            print(f"Unmatched {c} at index {i}")
            sys.exit(1)
        top, top_i = stack.pop()
        if (c == '}' and top != '{') or (c == ']' and top != '[') or (c == ')' and top != '('):
            print(f"Mismatched {c} at index {i}, expected match for {top} (opened at {top_i})")
            
            # Print the context in the ORIGINAL text
            start = max(0, i - 100)
            end = min(len(text), i + 100)
            print("Context around error:")
            print(text[start:end])
            
            start_open = max(0, top_i - 100)
            end_open = min(len(text), top_i + 100)
            print("\nContext around opening bracket:")
            print(text[start_open:end_open])
            
            sys.exit(1)
