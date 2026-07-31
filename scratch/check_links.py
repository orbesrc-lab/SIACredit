import re
content = open(r'c:\SIAC\templates\formacion.html', 'r', encoding='utf-8').read()
for match in re.finditer(r'<a[^>]+class=[\"\'][^\"\']*sidebar-item[^>]+>', content):
    print(match.group(0))
