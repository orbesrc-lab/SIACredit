import re

def build_sidebar_additions():
    return """
                if (factor.number == 5 || String(factor.name).toLowerCase().includes('académicos') || String(factor.name).toLowerCase().includes('academicos')) {
                    html += `<div class="char-item" onclick="loadFactor5DataGrid('${factor.id}')" id="char_tab_data_5_${factor.id}">
                        <div class="char-title">📊 Cuadros de Datos (Curricular)</div>
                        <div class="char-progress"><span>Ver métricas y plantillas</span></div>
                    </div>`;
                }
                if (factor.number == 7 || String(factor.name).toLowerCase().includes('entorno') || String(factor.name).toLowerCase().includes('externo')) {
                    html += `<div class="char-item" onclick="loadFactor7DataGrid('${factor.id}')" id="char_tab_data_7_${factor.id}">
                        <div class="char-title">📊 Cuadros de Datos (Sector Externo)</div>
                        <div class="char-progress"><span>Ver métricas y plantillas</span></div>
                    </div>`;
                }
                if (factor.number == 8 || String(factor.name).toLowerCase().includes('investigaci')) {
                    html += `<div class="char-item" onclick="loadFactor8DataGrid('${factor.id}')" id="char_tab_data_8_${factor.id}">
                        <div class="char-title">📊 Cuadros de Datos (Investigación)</div>
                        <div class="char-progress"><span>Ver métricas y plantillas</span></div>
                    </div>`;
                }
                if (factor.number == 10 || String(factor.name).toLowerCase().includes('recursos') || String(factor.name).toLowerCase().includes('ambientes')) {
                    html += `<div class="char-item" onclick="loadFactor10DataGrid('${factor.id}')" id="char_tab_data_10_${factor.id}">
                        <div class="char-title">📊 Cuadros de Datos (Recursos y Ambientes)</div>
                        <div class="char-progress"><span>Ver métricas y plantillas</span></div>
                    </div>`;
                }
"""

def build_js_functions():
    with open('c:/SIAC/scratch/factors_js.js', 'r', encoding='utf-8') as f:
        return f.read()

def inject():
    with open('c:/SIAC/templates/evidencias.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Inject sidebar
    sidebar_target = "if (factor.number == 3 || String(factor.name).toLowerCase().includes('profesores')) {"
    if sidebar_target in content and "loadFactor5DataGrid" not in content:
        content = content.replace(sidebar_target, build_sidebar_additions() + "                " + sidebar_target)
    
    # 2. Inject JS functions at the end of the script tag
    js_target = "</script>\n</body>"
    if js_target in content and "function loadFactor5DataGrid" not in content:
        js_code = build_js_functions()
        content = content.replace("</script>", js_code + "\n</script>")
    
    with open('c:/SIAC/templates/evidencias.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    inject()
    print("Injected successfully.")
