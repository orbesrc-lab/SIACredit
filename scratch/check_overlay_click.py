with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Check if modal-overlay has onclick to close
import re

# Find all onclick on modal-overlay divs
overlays = list(re.finditer(r'<div[^>]+class="modal-overlay"[^>]*>', html))
print(f'Found {len(overlays)} modal-overlay divs:')
for m in overlays:
    tag = m.group()[:200]
    print(f'  {tag.encode("ascii","ignore").decode("ascii")}')
    print()

# Check styles.css for any pointer-events
with open('c:\\SIAC\\static\\styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

print('\n=== pointer-events in styles.css ===')
for i, line in enumerate(css.split('\n')):
    if 'pointer' in line.lower():
        print(f'Line {i}: {line.encode("ascii","ignore").decode("ascii")}')
