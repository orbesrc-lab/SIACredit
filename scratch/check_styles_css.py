with open('c:\\SIAC\\static\\styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

import re
# Find modal-overlay CSS
idx = css.find('.modal-overlay')
while idx >= 0:
    print(f'At {idx}:')
    print(css[idx:idx+400].encode('ascii','ignore').decode('ascii'))
    print('---')
    idx = css.find('.modal-overlay', idx+1)

print('\n=== .modal-content ===')
idx = css.find('.modal-content')
while idx >= 0:
    print(f'At {idx}:')
    print(css[idx:idx+400].encode('ascii','ignore').decode('ascii'))
    print('---')
    idx = css.find('.modal-content', idx+1)
