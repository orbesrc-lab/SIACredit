import os

file_path = r'c:\SIAC\templates\empresa_matrices.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace </body> and </html> inside exportPDF JavaScript string with \x3c/body\x3e or <\/body>
if 'const printHTML = `' in content:
    idx = content.find('const printHTML = `')
    end_idx = content.find('`;', idx)
    
    if idx != -1 and end_idx != -1:
        template_str = content[idx:end_idx]
        fixed_template_str = template_str.replace('</body>', '<\\/body>').replace('</html>', '<\\/html>')
        content = content[:idx] + fixed_template_str + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Escaped </body> and </html> inside JS string in empresa_matrices.html")
