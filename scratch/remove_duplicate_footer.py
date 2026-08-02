with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

pos_start = content.find('<script>window.onload = function() { setTimeout(()=> { window.print()')
pos_end = content.find('<script>\n    let _globalPermissions = {};', pos_start + 10)

print("Duplicate block range:", pos_start, "to", pos_end)
if pos_start != -1 and pos_end != -1:
    content = content[:pos_start] + content[pos_end:]
    print("Duplicate block removed!")

with open(r'c:\SIAC\templates\informes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("informes.html saved!")
