import os
import re

tools = [
    'empresa_matrices.html',
    'empresa_porter.html',
    'empresa_riesgos.html',
    'empresa_stakeholders.html',
    'empresa_iso.html',
    'empresa_comunicacion.html'
]

volver_btn = """
    <div style="margin-bottom: 20px;">
        <a href="empresa_dashboard.html" style="display: inline-block; padding: 10px 20px; background: #e2e8f0; color: #334155; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 0.95rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: background 0.2s;">
            ⬅️ Volver al Hub Estratégico
        </a>
    </div>
"""

porter_save_btn = """
            <button onclick="saveMatrixData()" style="width:100%; margin-top:15px; padding:12px; border-radius:8px; border:none; background:#10b981; color:white; font-weight:bold; cursor:pointer; font-size:1rem; box-shadow:0 4px 6px rgba(16,185,129,0.3);">
                💾 Guardar Matriz de Porter
            </button>
"""

porter_save_script = """
        async function saveMatrixData() {
            const current_user = JSON.parse(localStorage.getItem('siac_user') || '{}');
            
            // Collect the inputs
            let inputs = [];
            for(let i=1; i<=5; i++) {
                inputs.push(document.getElementById('f'+i).value.trim());
            }
            
            const payload = {
                inst_id: getInstId(),
                user_id: current_user.id || 1,
                data: { inputs: inputs },
                results: (typeof window.lastPorterAnalysis !== 'undefined') ? window.lastPorterAnalysis : {}
            };
            
            try {
                const resp = await fetch('/api/business/matrix/PORTER', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(resp.ok) {
                    alert("✅ Matriz de Porter guardada con éxito.");
                } else {
                    alert("Error al guardar.");
                }
            } catch(e) {
                alert("Error al guardar: " + e.message);
            }
        }
"""

for tool in tools:
    path = os.path.join(r'c:\SIAC\templates', tool)
    if not os.path.exists(path):
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 1. Inject Volver button
    if '⬅️ Volver al Hub Estratégico' not in content:
        # Find the end of tool-header or dofa-header
        if '</div>' in content and ('class="tool-header"' in content or 'class="dofa-header"' in content):
            # Regex to inject after the closing div of the header
            content = re.sub(r'(<div class="(?:tool-header|dofa-header)".*?</div>)', r'\1\n' + volver_btn, content, count=1, flags=re.DOTALL)
            
    # 2. Fix `user.id` in JS payload
    content = content.replace('user_id: user.id', "user_id: (JSON.parse(localStorage.getItem('siac_user') || '{}')).id || 1")
    content = content.replace('alert("Error de red.");', 'alert("Error de red: " + e.message);')
    
    # 3. Add Save button to Porter
    if tool == 'empresa_porter.html':
        if 'saveMatrixData()' not in content:
            content = content.replace('<button class="btn-primary" onclick="generatePorter()"', porter_save_btn + '\n            <button class="btn-primary" onclick="generatePorter()"')
            # Add script
            content = content.replace('</script>', porter_save_script + '\n    </script>')
            # also, we need to save the analysis to window.lastPorterAnalysis
            content = content.replace('const data = await res.json();', 'const data = await res.json();\n                    window.lastPorterAnalysis = data;')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Tools fixed!")
