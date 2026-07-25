import re

upload_func = """
        async function uploadGridEvidence(fileInput, tableId) {
            if (!fileInput.files || fileInput.files.length === 0) return;
            const file = fileInput.files[0];
            const td = fileInput.closest('td');
            const tr = fileInput.closest('tr');
            const progId = getProgramId();
            if (!progId || progId == 0) {
                alert("Debes seleccionar un programa antes de subir evidencias.");
                return;
            }

            const formData = new FormData();
            formData.append('file', file);
            formData.append('inst_id', getInstId());
            formData.append('program_id', progId);
            formData.append('aspect_id', 'STAT_' + tableId);
            formData.append('period', 'Estadisticas');
            formData.append('email', user.email);

            td.innerHTML = '<span style="color:var(--primary-color)">⏳ Subiendo...</span>';

            try {
                const res = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.status === 'success') {
                    tr.dataset.adjunto = data.url;
                    td.innerHTML = `
                        <div style="display:flex; gap:5px; align-items:center;">
                            <a href="/api/download?url=${encodeURIComponent(data.url)}&name=evidencia" target="_blank" class="btn-ghost" style="padding:2px 8px; font-size:0.75rem; border:1px solid #e2e8f0; border-radius:4px; text-decoration:none;">⬇️ Ver</a>
                            <button class="btn-ghost" style="color:red; font-size:0.75rem; padding:2px 5px; border:1px solid red; border-radius:4px;" onclick="this.closest('tr').dataset.adjunto=''; this.parentElement.innerHTML='<label style=\\'cursor:pointer; color:var(--primary-color); font-size:0.8rem;\\'>Subir...<input type=\\'file\\' style=\\'display:none\\' onchange=\\'uploadGridEvidence(this, &quot;${tableId}&quot;)\\'></label>'">✕</button>
                        </div>`;
                    
                    // Simular clic en el botón de guardar si existe, o mostrar un banner
                    const saveBtn = document.querySelector('button[onclick^="saveFactor"]');
                    if(saveBtn) saveBtn.style.boxShadow = "0 0 10px var(--primary-color)";
                } else {
                    alert('Error al subir: ' + (data.message || 'Error'));
                    td.innerHTML = `<label style="cursor:pointer; color:var(--primary-color); font-size:0.8rem; text-decoration:underline; display:flex; align-items:center;">Subir...<input type="file" style="display:none;" onchange="uploadGridEvidence(this, '${tableId}')"></label>`;
                }
            } catch(err) {
                console.error(err);
                alert('Error de red al subir la evidencia.');
                td.innerHTML = `<label style="cursor:pointer; color:var(--primary-color); font-size:0.8rem; text-decoration:underline; display:flex; align-items:center;">Subir...<input type="file" style="display:none;" onchange="uploadGridEvidence(this, '${tableId}')"></label>`;
            }
        }
"""

with open('templates/evidencias_mod.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Insert before the last </script>
text = text.replace('</script>\n    <script src=', upload_func + '\n</script>\n    <script src=')

with open('templates/evidencias.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("uploadGridEvidence function injected into evidencias.html")
