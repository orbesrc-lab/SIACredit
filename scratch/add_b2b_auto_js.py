import os
import re

filepath = "c:/SIAC/templates/empresa_matrices.html"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Header
header_original = """    <div class="dofa-header">
        <h1>🛠️ Matrices MEFI y MEFE</h1>
        <p>Evaluación cuantitativa de Factores Internos (MEFI) y Externos (MEFE).</p>
    </div>"""

header_new = """    <div class="dofa-header" style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
        <div>
            <h1>🛠️ Matrices MEFI y MEFE</h1>
            <p>Evaluación cuantitativa de Factores Internos (MEFI) y Externos (MEFE).</p>
        </div>
        <button id="btnAutoPopulate" class="btn-primary" onclick="fetchAutoPopulate()" style="background: linear-gradient(135deg, #8b5cf6, #6366f1); border: none; font-weight: bold; display: flex; align-items: center; gap: 8px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
            Autocompletar IA desde Evaluación
        </button>
    </div>"""

if header_original in content:
    content = content.replace(header_original, header_new)

# 2. Add Javascript function
js_to_add = """
        async function fetchAutoPopulate() {
            const btn = document.getElementById('btnAutoPopulate');
            const originalHtml = btn.innerHTML;
            btn.innerHTML = '✨ IA procesando autoevaluación... (puede tardar un poco)';
            btn.disabled = true;
            
            try {
                const resp = await fetch('/api/business/auto-populate-matrices', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ inst_id: getInstId(), program_id: getProgramId() })
                });
                
                const data = await resp.json();
                if (!resp.ok) throw new Error(data.error || 'Error al conectar con la IA');
                
                // Limpiar matrices
                document.getElementById('mefiBody').innerHTML = '';
                document.getElementById('mefeBody').innerHTML = '';
                
                // Llenar MEFI
                if (data.mefi) {
                    (data.mefi.fortalezas || []).forEach(item => addMatrixRow('mefi', { name: item.name, type: 'Fortaleza', weight: item.weight, rating: item.rating }));
                    (data.mefi.debilidades || []).forEach(item => addMatrixRow('mefi', { name: item.name, type: 'Debilidad', weight: item.weight, rating: item.rating }));
                }
                
                // Llenar MEFE
                if (data.mefe) {
                    (data.mefe.oportunidades || []).forEach(item => addMatrixRow('mefe', { name: item.name, type: 'Oportunidad', weight: item.weight, rating: item.rating }));
                    (data.mefe.amenazas || []).forEach(item => addMatrixRow('mefe', { name: item.name, type: 'Amenaza', weight: item.weight, rating: item.rating }));
                }
                
                alert("✨ ¡La IA ha estructurado tus matrices basándose en la Autoevaluación! Por favor revisa los pesos y calificaciones, y luego haz clic en 'Guardar MEFI' y 'Guardar MEFE'.");
                
            } catch (e) {
                alert("Error de IA: " + e.message);
            } finally {
                btn.innerHTML = originalHtml;
                btn.disabled = false;
            }
        }
"""

if "fetchAutoPopulate()" not in content:
    # insert before </script> at the end
    last_script = content.rfind("</script>")
    content = content[:last_script] + js_to_add + content[last_script:]
    
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated empresa_matrices.html with AI injection script")
