import re

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

routes = re.findall(r"@app\.route\('([^']+)'", content)
prefixes = set()
for r in routes:
    parts = r.split('/')
    if len(parts) > 2:
        if parts[1] == 'api':
            prefixes.add('/api/' + parts[2])
        else:
            prefixes.add('/' + parts[1])
    else:
        prefixes.add(r)

for p in sorted(list(prefixes)):
    print(p)
