import os

file_path = r'c:\SIAC\templates\empresa_matrices.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Cut exportPDF code from outside </html>
if '</html>' in content:
    parts = content.split('</html>')
    html_part = parts[0]
    extra_part = parts[1] if len(parts) > 1 else ''
    
    # If exportPDF is in extra_part or near end
    if 'function exportPDF()' in extra_part:
        pdf_code = extra_part[extra_part.find('function exportPDF()'):]
        extra_part = extra_part[:extra_part.find('function exportPDF()')]
        
        # Insert pdf_code before the last </script> in html_part
        last_script_idx = html_part.rfind('</script>')
        if last_script_idx != -1:
            html_part = html_part[:last_script_idx] + "\n" + pdf_code + "\n" + html_part[last_script_idx:]
            
    content = html_part + '</html>' + extra_part

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed exportPDF placement inside script tags in empresa_matrices.html")
