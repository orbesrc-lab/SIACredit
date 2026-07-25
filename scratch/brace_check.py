import re

filepath = 'c:\\SIAC\\templates\\configuracion.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all script blocks
script_regex = re.compile(r'<script.*?>([\s\S]*?)</script>', re.IGNORECASE)
matches = list(script_regex.finditer(content))

for idx, match in enumerate(matches):
    js = match.group(1)
    # Let's count open/close braces, brackets, and parentheses
    brace_count = 0
    paren_count = 0
    bracket_count = 0
    
    # We should skip contents inside comments and strings to be accurate
    # But a simple char-by-char scanner is easy to write
    in_string = False
    string_char = None
    in_line_comment = False
    in_block_comment = False
    
    lines = js.split('\n')
    for line_idx, line in enumerate(lines):
        i = 0
        while i < len(line):
            c = line[i]
            if in_line_comment:
                break # rest of line is comment
            elif in_block_comment:
                if c == '*' and i + 1 < len(line) and line[i+1] == '/':
                    in_block_comment = False
                    i += 1
            elif in_string:
                if c == '\\':
                    i += 1 # skip escaped char
                elif c == string_char:
                    in_string = False
                    string_char = None
            else:
                if c == '/' and i + 1 < len(line) and line[i+1] == '/':
                    in_line_comment = True
                    i += 1
                elif c == '/' and i + 1 < len(line) and line[i+1] == '*':
                    in_block_comment = True
                    i += 1
                elif c in ['"', "'", '`']:
                    in_string = True
                    string_char = c
                elif c == '{':
                    brace_count += 1
                elif c == '}':
                    brace_count -= 1
                    if brace_count < 0:
                        print(f"Error: unmatched closing brace '}}' in Block {idx+1} at line {line_idx+1}: {line}")
                elif c == '(':
                    paren_count += 1
                elif c == ')':
                    paren_count -= 1
                    if paren_count < 0:
                        print(f"Error: unmatched closing parenthesis ')' in Block {idx+1} at line {line_idx+1}: {line}")
                elif c == '[':
                    bracket_count += 1
                elif c == ']':
                    bracket_count -= 1
                    if bracket_count < 0:
                        print(f"Error: unmatched closing bracket ']' in Block {idx+1} at line {line_idx+1}: {line}")
            i += 1
        in_line_comment = False # line comment ends at newline
        
    print(f"Block {idx+1}: brace balance: {brace_count}, paren balance: {paren_count}, bracket balance: {bracket_count}")
