with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
# Find all modal-like elements with fixed/absolute positioning
# Find all divs with id ending in Modal or with class modal-overlay
divs = re.findall(r'<div\s+id="([^"]+)"[^>]+(?:modal-overlay|position:\s*fixed|z-index)[^>]*>', html)
print('Fixed/overlay divs:', divs[:30])

# Also look for any overlay without modal-overlay class
overlay_divs = re.findall(r'<div[^>]+style="[^"]*position:\s*fixed[^"]*"[^>]*>', html)
print('\nFixed position divs:')
for d in overlay_divs[:10]:
    print(' ', d[:150].encode('ascii','ignore').decode('ascii'))

# Now check the actual HTML near where the quiz editor opens
# Find where 'updateCourseOnServer' leaves the course editor open
# The course editor might be in a 'section' that overlaps
idx = html.find('id="courseEditorSection"')
print('\ncourseEditorSection:', idx)
if idx >= 0:
    print(html[idx:idx+200].encode('ascii','ignore').decode('ascii'))
