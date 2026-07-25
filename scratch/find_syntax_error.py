"""
Browser says SyntaxError at formacion.html:1542.
But that line looks fine locally. Browser line numbers include ALL HTML, not just JS.
The browser counts from line 1 of the HTML file.
Let me check what's around HTML line 1542 in the raw file.
"""
with open('c:/SIAC/templates/formacion.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Show lines 1535-1545
print("=== HTML lines 1535-1545 ===")
for i in range(1534, 1545):
    print(f"{i+1}: {lines[i].rstrip()}")

# Also scan for try { immediately followed by } catch or empty try blocks
print("\n=== Looking for empty/broken try blocks ===")
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped in ['try {', 'try{']:
        # Check if next non-empty line is catch
        for j in range(i+1, min(i+5, len(lines))):
            next_stripped = lines[j].strip()
            if next_stripped and next_stripped.startswith('catch'):
                print(f"Line {i+1}: empty try block! -> catch at line {j+1}")
                print(f"  try line: {lines[i].rstrip()}")
                print(f"  catch line: {lines[j].rstrip()}")
                break
            elif next_stripped:
                break
