with open(r'c:\SIAC\templates\planificacion.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(r"\'${axisKey}\'", "'${axisKey}'")

with open(r'c:\SIAC\templates\planificacion.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed axis key quote.")
