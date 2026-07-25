"""
The SyntaxError 'Unexpected token catch' usually means a try block without a body OR
a try-catch split by something invalid. Let me search more broadly.
Also check if the browser line number might be different from local because of 
Vercel serving a slightly different version.

Let me also search for:
1. try {} catch - try with empty body  
2. } catch(e) { without proper try
3. Any line with just 'catch' alone
"""
with open('c:/SIAC/templates/formacion.html', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print("=== Searching for problematic catch patterns ===")
for i, line in enumerate(lines):
    s = line.strip()
    # Try block with empty body: try {} catch or try{\n} catch
    if s == 'try {' or s == 'try{':
        # Look at very next non-empty line
        for j in range(i+1, min(i+3, len(lines))):
            ns = lines[j].strip()
            if ns.startswith('} catch') or ns.startswith('}catch'):
                print(f"EMPTY TRY at HTML line {i+1}: {line.rstrip()}")
                print(f"  -> {lines[j].rstrip()}")
    
    # 'catch' appearing on its own line without a preceding }
    if s.startswith('catch') and not s.startswith('catch('):
        print(f"Weird catch at line {i+1}: {line.rstrip()}")
    
    # try without opening brace on same line: "try" alone 
    if s == 'try':
        print(f"Bare 'try' at line {i+1}")

print("\n=== Checking for missing try body ===")
# Find all 'try {' and verify next non-whitespace line isn't '} catch'
import re
for m in re.finditer(r'\btry\s*\{', content):
    pos = m.end()
    # Find what's after the {
    rest = content[pos:]
    next_content = rest.lstrip()
    if next_content.startswith('} catch') or next_content.startswith('}catch'):
        line_num = content[:m.start()].count('\n') + 1
        print(f"Empty try block at HTML line {line_num}: {lines[line_num-1].strip()}")

print("\nDone.")
