import os

tools = [
    'empresa_porter.html',
    'empresa_riesgos.html',
    'empresa_stakeholders.html',
    'empresa_comunicacion.html'
]

print_css = """
    <style id="printStyle">
        @media print {
            body * { visibility: hidden !important; }
            #printSection, #printSection * { visibility: visible !important; }
            #printSection { position: absolute !important; left: 0 !important; top: 0 !important; width: 100% !important; display: block !important; background: white !important; padding: 20px !important; color: #0f172a !important; font-family: 'Segoe UI', Arial, sans-serif !important; }
            .no-print { display: none !important; }
        }
        #printSection { display: none; }
    </style>
</head>"""

for tool in tools:
    file_path = os.path.join(r'c:\SIAC\templates', tool)
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "id=\"printStyle\"" not in content:
        content = content.replace('</head>', print_css)
        
    if '<div id="printSection"></div>' not in content:
        content = content.replace('</body>', '<div id="printSection"></div>\n</body>')
        
    # Replace window.open pattern in exportPDF
    if 'const win = window.open' in content:
        old_export = content[content.find('function exportPDF()'):content.find('</script>', content.find('function exportPDF()'))]
        
        # Rewrite exportPDF to use #printSection
        new_export = old_export.replace("const win = window.open('', '_blank');", "// Native print")
        new_export = new_export.replace("if (win) { win.document.open(); win.document.write(printHTML); win.document.close(); }", "document.getElementById('printSection').innerHTML = printHTML; window.print();")
        
        content = content.replace(old_export, new_export)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Patched native print for {tool}")
