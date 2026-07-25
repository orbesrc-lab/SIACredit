with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
# find all input class usages
classes = re.findall(r'<input[^>]*class="([^"]*)"', html)
sel_classes = re.findall(r'<select[^>]*class="([^"]*)"', html)
ta_classes = re.findall(r'<textarea[^>]*class="([^"]*)"', html)

from collections import Counter
print('Input classes:', Counter(classes).most_common(10))
print('Select classes:', Counter(sel_classes).most_common(10))
print('Textarea classes:', Counter(ta_classes).most_common(10))

# Also check if form-control is defined in CSS
if 'form-control' in html:
    idx = html.find('.form-control')
    print('\n.form-control CSS:')
    print(html[idx:idx+200].encode('ascii','ignore').decode('ascii'))
