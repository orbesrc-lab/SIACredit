import os
import glob
import re

files = glob.glob('templates/*.html')
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Update static links
    content = content.replace('href="styles.css"', 'href="{{ url_for(\'static\', filename=\'styles.css\') }}"')
    content = content.replace('src="data.js"', 'src="{{ url_for(\'static\', filename=\'data.js\') }}"')
    content = content.replace('src="app.js"', 'src="{{ url_for(\'static\', filename=\'app.js\') }}"')
    content = content.replace('src="plantilla.png"', 'src="{{ url_for(\'static\', filename=\'plantilla.png\') }}"')

    # Find the main init functions and wrap them
    # configuracion.html uses renderModelEditor();
    # autoevaluacion.html uses renderSidebar();
    # evidencias.html uses renderSidebar();
    
    if "renderModelEditor();" in content and "async function init()" not in content:
        content = content.replace("renderModelEditor();", "async function init() {\n            await loadDataFromAPI();\n            renderModelEditor();\n        }\n        init();")
        
    if "renderSidebar();" in content and "async function init()" not in content:
        # Avoid replacing inside functions, look for the global call at the end
        # We can just do a regex replace for the top-level call.
        content = re.sub(r'(?<!function )renderSidebar\(\);', 'async function init() {\n            await loadDataFromAPI();\n            renderSidebar();\n        }\n        init();', content, count=1)

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
print("Archivos HTML actualizados con éxito.")
