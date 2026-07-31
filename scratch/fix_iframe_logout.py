import glob, re

for fn in glob.glob(r'c:\SIAC\templates\*.html') + glob.glob(r'c:\SIAC\static\*.js'):
    with open(fn, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Update all window.location.href redirects to index or login
    content = re.sub(r'window\.location\.href\s*=\s*([\'"`])(index\.html|login\.html)[\'"`]', r'window.top.location.href = \g<1>\g<2>\g<1>', content)
    
    # Also update the dashboard.html redirects
    content = re.sub(r'window\.location\.href\s*=\s*([\'"`])dashboard\.html[\'"`]', r'window.top.location.href = \g<1>dashboard.html\g<1>', content)
    
    if content != original:
        print(f'Fixed redirects in {fn}')
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(content)
print('Done!')
