import os
import re

tools = [
    'empresa_matrices.html',
    'empresa_riesgos.html',
    'empresa_stakeholders.html'
]

date_ui = r'''
            <div style="margin-bottom: 20px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <label style="font-weight: bold; font-size: 0.9rem; color: #475569;">📅 Fecha de Levantamiento de Información:</label>
                <input type="date" id="eval_date" style="margin-left: 10px; padding: 8px; border-radius: 4px; border: 1px solid #cbd5e1;">
            </div>
'''

for tool in tools:
    file_path = os.path.join(r'c:\SIAC\templates', tool)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "Fecha de Levantamiento" not in content:
        # Insert after <div class="matrices-header"> or something similar
        if tool == 'empresa_matrices.html':
            content = re.sub(r'(<div class="matrices-header">.*?</div>)', r'\1\n' + date_ui, content, count=1, flags=re.DOTALL)
            # Add to save payload
            content = content.replace('mefiData }', 'mefiData, eval_date: document.getElementById("eval_date") ? document.getElementById("eval_date").value : "" }')
            content = content.replace('mefeData }', 'mefeData, eval_date: document.getElementById("eval_date") ? document.getElementById("eval_date").value : "" }')
        
        elif tool == 'empresa_riesgos.html':
            content = re.sub(r'(<h1>Registro de Riesgos.*?</h1>.*?</div>)', r'\1\n' + date_ui, content, count=1, flags=re.DOTALL)
            content = content.replace('risks }', 'risks, eval_date: document.getElementById("eval_date") ? document.getElementById("eval_date").value : "" }')
            
        elif tool == 'empresa_stakeholders.html':
            content = re.sub(r'(<h1>Matriz de Stakeholders.*?</h1>.*?</div>)', r'\1\n' + date_ui, content, count=1, flags=re.DOTALL)
            content = content.replace('stakeholders }', 'stakeholders, eval_date: document.getElementById("eval_date") ? document.getElementById("eval_date").value : "" }')

        # To load the date: We won't strictly enforce load here to keep it simple, 
        # but the data will be saved. We can patch the load function if we want.
        if tool == 'empresa_matrices.html':
            content = content.replace('renderMefi();', 'renderMefi(); if(data.data.eval_date && document.getElementById("eval_date")) document.getElementById("eval_date").value = data.data.eval_date;')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            print(f"Patched {tool} with Date field")
