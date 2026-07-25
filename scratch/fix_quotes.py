import codecs

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

content = content.replace("switchSubTab(\\'library\\')", "switchSubTab('library')")

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)
print("Fixed quotes!")
