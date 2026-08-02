with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

pos1 = content.find('<script>\n    let _globalPermissions = {};')
pos2 = content.find('<script>\n    let _globalPermissions = {};', pos1 + 10)

print("First permissions block at:", pos1)
print("Second permissions block at:", pos2)

if pos1 != -1 and pos2 != -1:
    # Remove from pos1 up to pos2
    content = content[:pos1] + content[pos2:]
    print("Removed duplicate permissions block successfully!")

with open(r'c:\SIAC\templates\informes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("informes.html updated!")
