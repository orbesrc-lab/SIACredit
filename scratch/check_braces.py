with open('c:/SIAC/scratch/extracted.js', 'r', encoding='utf-8') as f:
    code = f.read()

stack = [] # Stack of open structures: ('{', line, col), ('(', line, col), etc.
mode_stack = ['normal'] # Stack of modes

line_num = 1
i = 0

while i < len(code):
    char = code[i]
    current_mode = mode_stack[-1]
    
    # Handle newlines for line counting
    if char == '\n':
        line_num += 1
        if current_mode == 'comment_single':
            mode_stack.pop()
        i += 1
        continue
        
    # --- MULTILINE COMMENT MODE ---
    if current_mode == 'comment_multi':
        if code[i:i+2] == '*/':
            mode_stack.pop()
            i += 2
        else:
            i += 1
        continue
        
    # --- SINGLE LINE COMMENT MODE ---
    if current_mode == 'comment_single':
        i += 1
        continue
        
    # --- STRING MODES ---
    if current_mode in ('string_single', 'string_double'):
        if char == '\\':
            i += 2
            continue
        expected_quote = "'" if current_mode == 'string_single' else '"'
        if char == expected_quote:
            mode_stack.pop()
        i += 1
        continue
        
    # --- TEMPLATE LITERAL MODE ---
    if current_mode == 'template':
        if char == '\\':
            i += 2
            continue
        if code[i:i+2] == '${':
            mode_stack.append('normal') # Inside ${}, we parse normal JS expressions!
            i += 2
            continue
        if char == '`':
            mode_stack.pop()
            i += 1
            continue
        i += 1
        continue

    # --- NORMAL JS MODE ---
    # Check for comments
    if code[i:i+2] == '//':
        mode_stack.append('comment_single')
        i += 2
        continue
    if code[i:i+2] == '/*':
        mode_stack.append('comment_multi')
        i += 2
        continue
        
    # Check for string literals
    if char == "'":
        mode_stack.append('string_single')
        i += 1
        continue
    if char == '"':
        mode_stack.append('string_double')
        i += 1
        continue
    if char == '`':
        mode_stack.append('template')
        i += 1
        continue
        
    # Brackets and parentheses
    if char == '{':
        stack.append(('{', line_num))
    elif char == '}':
        # CRITICAL: If we are in normal mode and the parent mode is template,
        # then this '}' closes the '${' and NOT a normal '{' from stack!
        if len(mode_stack) > 1 and mode_stack[-2] == 'template':
            mode_stack.pop() # Return to template literal mode
        else:
            if stack and stack[-1][0] == '{':
                stack.pop()
            else:
                print(f"Unmatched closing brace '}}' at line {line_num}")
                if stack:
                    print(f"Top of stack is: {stack[-1]}")
                else:
                    print("Stack is empty.")
    elif char == '(':
        stack.append(('(', line_num))
    elif char == ')':
        if stack and stack[-1][0] == '(':
            stack.pop()
        else:
            print(f"Unmatched closing paren ')' at line {line_num}")
    elif char == '[':
        stack.append(('[', line_num))
    elif char == ']':
        if stack and stack[-1][0] == '[':
            stack.pop()
        else:
            print(f"Unmatched closing bracket ']' at line {line_num}")
            
    i += 1

print("\n--- Summary ---")
print("Remaining items in stack:", stack)
print("Remaining modes in mode_stack:", mode_stack)
