import re

file_path = 'c:/SIAC/templates/evidencias.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix escaped backticks
content = content.replace('\\`', '`')
# Fix escaped dollar signs
content = content.replace('\\$', '$')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed syntax errors in evidencias.html")
