
with open('c:/SIAC/static/app.js', 'r', encoding='utf-8') as f:
    text = f.read()
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if 'isAdmin =' in line:
            print(repr(line))

