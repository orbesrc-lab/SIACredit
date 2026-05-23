import re

with open('templates/evidencias.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Define the tables that need the 'Evidencia' column
tables_to_mod = [
    'Capacitacion', 'Evaluacion', 'Movilidad', 'Pasantias',
    'Convenios', 'Proyectos', 'Grupos', 'ProyectosInv', 'Publicaciones'
]

# Add Evidencia column header to HTML tables
for t in tables_to_mod:
    pattern = rf'(id="tabla{t}".*?<th>)Acción(</th>)'
    text = re.sub(pattern, r'\1Evidencia</th><th>Acción\2', text, flags=re.DOTALL)

# Update addRow functions to include adjunto
for t in tables_to_mod:
    sig_pattern = rf'(function addRow{t}\(data = {{.*?)(}}\))'
    text = re.sub(sig_pattern, r"\1, adjunto:''\2", text)
    
    row_pattern = rf'(function addRow{t}\(data.*?)(<td style="text-align:center;"><button class="btn-ghost" style="color:red;")'
    
    adjunto_html = r"""
        <td>
            ${data.adjunto ? 
                `<div style="display:flex; gap:5px; align-items:center;">
                    <a href="/api/download?url=${encodeURIComponent(data.adjunto)}&name=evidencia" target="_blank" class="btn-ghost" style="padding:2px 8px; font-size:0.75rem; border:1px solid #e2e8f0; border-radius:4px; text-decoration:none;">⬇️ Ver</a>
                    <button class="btn-ghost" style="color:red; font-size:0.75rem; padding:2px 5px; border:1px solid red; border-radius:4px;" onclick="this.closest('tr').dataset.adjunto=''; this.parentElement.innerHTML='<label style=\\'cursor:pointer; color:var(--primary-color); font-size:0.8rem;\\'>Subir...<input type=\\'file\\' style=\\'display:none\\' onchange=\\'uploadGridEvidence(this, \\"tabla""" + t + r"""\\")\\'></label>'">✕</button>
                 </div>` 
                : `<label style="cursor:pointer; color:var(--primary-color); font-size:0.8rem; text-decoration:underline; display:flex; align-items:center;">Subir...<input type="file" style="display:none;" onchange="uploadGridEvidence(this, 'tabla""" + t + r"""')"></label>`
            }
        </td>
        \2"""
    text = re.sub(row_pattern, adjunto_html, text, flags=re.DOTALL)
    
    tr_append_pattern = rf'(function addRow{t}\(data.*?)(tbody\.appendChild\(tr\);)'
    text = re.sub(tr_append_pattern, r"\1if(data.adjunto) tr.dataset.adjunto = data.adjunto;\n            \2", text, flags=re.DOTALL)

# Modify the extraction functions to skip file inputs
extract_func_bodies = re.findall(r'function extractFactor.*?\{.*?(?=\n\s*function|\n\s*\</script)', text, re.DOTALL)
for body in extract_func_bodies:
    new_body = body.replace("querySelectorAll('input')", "querySelectorAll('input:not([type=\"file\"])')")
    new_body = new_body.replace("querySelectorAll('input, select')", "querySelectorAll('input:not([type=\"file\"]), select')")
    text = text.replace(body, new_body)

# Append adjunto to the extraction objects
for t in tables_to_mod:
    push_pattern = rf"(document\.querySelectorAll\('#tabla{t} tbody tr'\)\.forEach\(tr => {{.*?(?:push)\({{.*?)(}} \);)"
    text = re.sub(push_pattern, r"\1, adjunto: tr.dataset.adjunto || '' \2", text, flags=re.DOTALL)

with open('templates/evidencias_mod.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Done")
