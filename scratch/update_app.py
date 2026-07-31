with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("response.headers['X-Frame-Options'] = 'DENY'", "response.headers['X-Frame-Options'] = 'SAMEORIGIN'")

with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
