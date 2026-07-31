import os

file_path = r'c:\SIAC\templates\empresa_matrices.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_fetch_saved = """        async function fetchSavedMatrices() {
            try {
                const instId = getInstId();
                const [mefiRes, mefeRes] = await Promise.all([
                    fetch(`/api/business/matrix/MEFI?inst_id=${instId}`).then(r => r.json()),
                    fetch(`/api/business/matrix/MEFE?inst_id=${instId}`).then(r => r.json())
                ]);

                let mefiObj = mefiRes && mefiRes.data ? mefiRes.data : null;
                if (typeof mefiObj === 'string') { try { mefiObj = JSON.parse(mefiObj); } catch(e){} }
                
                let mefeObj = mefeRes && mefeRes.data ? mefeRes.data : null;
                if (typeof mefeObj === 'string') { try { mefeObj = JSON.parse(mefeObj); } catch(e){} }

                if (mefiObj && mefiObj.factors) {
                    mefiData = mefiObj.factors.map(f => ({
                        ...f,
                        factor: cleanFactorText(f.factor)
                    }));
                    if (mefiObj.eval_date && document.getElementById('eval_date')) {
                        document.getElementById('eval_date').value = mefiObj.eval_date;
                    }
                }
                
                if (mefeObj && mefeObj.factors) {
                    mefeData = mefeObj.factors.map(f => ({
                        ...f,
                        factor: cleanFactorText(f.factor)
                    }));
                    if (mefeObj.eval_date && document.getElementById('eval_date')) {
                        document.getElementById('eval_date').value = mefeObj.eval_date;
                    }
                }

                renderMatrix('mefi', mefiData);
                renderMatrix('mefe', mefeData);
            } catch (error) {
                console.error("Error fetching matrices:", error);
            }
        }

        function cleanFactorText(text) {
            if (!text) return "";
            if (typeof text === 'object') {
                return text.descripcion || text.description || text.name || JSON.stringify(text);
            }
            if (typeof text === 'string' && text.trim().startsWith('{') && text.includes('descripcion')) {
                try {
                    // Fix single quotes to double quotes for JSON parsing if needed
                    const jsonStr = text.replace(/'/g, '"');
                    const obj = JSON.parse(jsonStr);
                    return obj.descripcion || obj.description || text;
                } catch(e) {
                    // Manual regex match for 'descripcion': '...'
                    const match = text.match(/'descripcion'\s*:\s*'([^']+)'/);
                    if (match) return match[1];
                }
            }
            return text;
        }"""

old_fetch_saved = """        async function fetchSavedMatrices() {
            try {
                const instId = getInstId();
                const [mefiRes, mefeRes] = await Promise.all([
                    fetch(`/api/business/matrix/MEFI?inst_id=${instId}`).then(r => r.json()),
                    fetch(`/api/business/matrix/MEFE?inst_id=${instId}`).then(r => r.json())
                ]);

                if (mefiRes && mefiRes.data && mefiRes.data.factors) {
                    mefiData = mefiRes.data.factors;
                }
                if (mefeRes && mefeRes.data && mefeRes.data.factors) {
                    mefeData = mefeRes.data.factors;
                }

                renderMatrix('mefi', mefiData);
                renderMatrix('mefe', mefeData);
            } catch (error) {
                console.error("Error fetching matrices:", error);
                Swal.fire('Error', 'No se pudieron cargar las matrices guardadas', 'error');
            }
        }"""

content = content.replace(old_fetch_saved.replace('\r\n', '\n'), new_fetch_saved.replace('\r\n', '\n'))
content = content.replace(old_fetch_saved, new_fetch_saved)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("empresa_matrices.html patched with cleanFactorText and resilient JSON loading")
