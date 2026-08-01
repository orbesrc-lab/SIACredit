import re

with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all script tag positions with their indices
script_open = [(m.start(), m.end(), m.group()) for m in re.finditer(r'<script[^>]*>', content)]
script_close = [(m.start(), m.end()) for m in re.finditer(r'</script>', content)]

print(f"Script opens: {len(script_open)}")
for i, (s, e, g) in enumerate(script_open):
    print(f"  [{i}] pos={s}: {g[:60]}")

print(f"\nScript closes: {len(script_close)}")
for i, (s, e) in enumerate(script_close):
    print(f"  [{i}] pos={s}: {content[s-10:s+20]!r}")
