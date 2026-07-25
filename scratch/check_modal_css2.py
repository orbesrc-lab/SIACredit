with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find .modal-overlay CSS
idx = html.find('.modal-overlay')
while idx >= 0:
    # Check if it's in a style block
    ctx = html[max(0,idx-20):idx+300]
    if '{' in ctx:
        print(f'At {idx}:')
        print(ctx.encode('ascii','ignore').decode('ascii'))
        print('---')
    idx = html.find('.modal-overlay', idx+1)

# Also find .modal-content
print('\n\n=== .modal-content ===')
idx = html.find('.modal-content')
while idx >= 0:
    ctx = html[max(0,idx-20):idx+300]
    if '{' in ctx:
        print(f'At {idx}:')
        print(ctx.encode('ascii','ignore').decode('ascii'))
        print('---')
    idx = html.find('.modal-content', idx+1)
