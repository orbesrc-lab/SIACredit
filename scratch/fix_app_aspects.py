import re

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the Supabase select queries
content = content.replace("aspects(id,name)", "aspects(id,text)")

# 2. Fix the variable assignment
content = content.replace("an = _safe_filename(a.get('name') or a.get('id'))", "an = _safe_filename((a.get('text') or str(a.get('id')))[:50])")
content = content.replace("an = _safe_filename(a.get('name') or a['id'])", "an = _safe_filename((a.get('text') or str(a['id']))[:50])")

with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("app.py patched!")
