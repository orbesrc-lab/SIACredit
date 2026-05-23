import re

with open('templates/evidencias.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update the chartFormacionDedicacion to group by period
chart_pattern = r"const stats = { 'Pregrado': 0, 'Especialización': 0, 'Maestría': 0, 'Doctorado': 0 };.*?options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } }\s*}\);"

new_chart = """const statsByPeriod = {};
            data.profesores.forEach(p => {
                if(!p.periodo) return;
                if(!statsByPeriod[p.periodo]) statsByPeriod[p.periodo] = { 'Pregrado': 0, 'Especialización': 0, 'Maestría': 0, 'Doctorado': 0 };
                if (p.formacion && statsByPeriod[p.periodo][p.formacion] !== undefined) {
                    statsByPeriod[p.periodo][p.formacion]++;
                }
            });
            
            const periods = Object.keys(statsByPeriod).sort();
            const pregradoData = periods.map(per => statsByPeriod[per]['Pregrado']);
            const especializacionData = periods.map(per => statsByPeriod[per]['Especialización']);
            const maestriaData = periods.map(per => statsByPeriod[per]['Maestría']);
            const doctoradoData = periods.map(per => statsByPeriod[per]['Doctorado']);
            
            const ctxFormacion = document.getElementById('chartFormacionDedicacion');
            if (ctxFormacion) {
                if (chartFormacion) chartFormacion.destroy();
                chartFormacion = new Chart(ctxFormacion, {
                    type: 'bar',
                    data: {
                        labels: periods,
                        datasets: [
                            { label: 'Pregrado', data: pregradoData, backgroundColor: '#94a3b8' },
                            { label: 'Especialización', data: especializacionData, backgroundColor: '#3b82f6' },
                            { label: 'Maestría', data: maestriaData, backgroundColor: '#8b5cf6' },
                            { label: 'Doctorado', data: doctoradoData, backgroundColor: '#ec4899' }
                        ]
                    },
                    options: { 
                        responsive: true, 
                        maintainAspectRatio: false, 
                        scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } },
                        plugins: { legend: { position: 'bottom' } } 
                    }
                });"""

text = re.sub(chart_pattern, new_chart, text, flags=re.DOTALL)

# We need the icons safely escaped. In Javascript template literals, we can use SVG string directly,
# but for the `onclick="... innerHTML='... SVG ...'"` we must escape `"` to `&quot;`.

icon_view = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>'
icon_upload = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>'
icon_del = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>'

# To inject inside innerHTML="" inside an onclick="", all double quotes must be &quot;
# Because `<button onclick="this.parentElement.innerHTML='<label...><svg width=&quot;20&quot;...'"></button>`
icon_upload_escaped = icon_upload.replace('"', '&quot;')

# 2. Add Evidencia to all missing tables (like Profesores, Historico, Asignaturas, etc)
all_tables = re.findall(r'id="(tabla\w+)"', text)
for table_id in set(all_tables):
    t_name = table_id.replace('tabla', '')
    
    # Check if table has <th>Acción</th> but NOT <th>Evidencia</th>
    table_html_match = re.search(rf'(id="{table_id}".*?</thead>)', text, flags=re.DOTALL)
    if table_html_match:
        table_html = table_html_match.group(1)
        if '<th>Acción</th>' in table_html and 'Evidencia' not in table_html:
            # We need to add the Evidencia header
            pattern = rf'(id="{table_id}".*?<th>)Acción(</th>)'
            text = re.sub(pattern, r'\1Evidencia</th><th>Acción\2', text, flags=re.DOTALL)
            
            # Update addRow function signature if it exists
            sig_pattern = rf'(function addRow{t_name}\(data = {{.*?)(}}\))'
            if re.search(sig_pattern, text):
                text = re.sub(sig_pattern, r"\1, adjunto:''\2", text)
            
            # THE BUG WAS HERE: We MUST keep \1!
            # We look for the Acción <td> which is <td style="text-align:center;"><button...
            row_pattern = rf'(function addRow{t_name}\(data.*?)(<td style="text-align:center;"><button[^>]*>[✕X]</button></td>)'
            
            adjunto_html = r"""\1
        <td>
            ${data.adjunto ? 
                `<div style="display:flex; gap:5px; align-items:center;">
                    <a href="/api/download?url=${encodeURIComponent(data.adjunto)}&name=evidencia" target="_blank" class="btn-ghost" style="padding:4px 8px; font-size:0.8rem; border:1px solid #e2e8f0; border-radius:6px; color:#3b82f6;" title="Ver/Descargar Evidencia">ICON_VIEW</a>
                    <button class="btn-ghost" style="color:#ef4444; padding:4px 8px; border:1px solid #fca5a5; border-radius:6px;" onclick="this.closest('tr').dataset.adjunto=''; this.parentElement.innerHTML='<label style=\\'cursor:pointer; color:#3b82f6; display:flex; align-items:center; justify-content:center; padding:4px; border:1px dashed #93c5fd; border-radius:6px;\\' title=\\'Subir evidencia\\'>ICON_UPLOAD_ESCAPED<input type=\\'file\\' style=\\'display:none\\' onchange=\\'uploadGridEvidence(this, &quot;tabla""" + t_name + r"""&quot;)\\'></label>'">ICON_DEL</button>
                 </div>` 
                : `<label style="cursor:pointer; color:#3b82f6; display:flex; align-items:center; justify-content:center; padding:6px; border:1px dashed #93c5fd; border-radius:6px; transition:0.2s;" title="Subir evidencia" onmouseover="this.style.background='#eff6ff'" onmouseout="this.style.background='transparent'">ICON_UPLOAD<input type="file" style="display:none;" onchange="uploadGridEvidence(this, 'tabla""" + t_name + r"""')"></label>`
            }
        </td>
        \2"""
            
            # Replace placeholders
            adjunto_html = adjunto_html.replace('ICON_VIEW', icon_view)
            adjunto_html = adjunto_html.replace('ICON_UPLOAD_ESCAPED', icon_upload_escaped)
            adjunto_html = adjunto_html.replace('ICON_UPLOAD', icon_upload)
            adjunto_html = adjunto_html.replace('ICON_DEL', icon_del)
            
            text = re.sub(row_pattern, adjunto_html, text, flags=re.DOTALL)
            
            # Append dataset adjunto
            tr_append_pattern = rf'(function addRow{t_name}\(data.*?)(tbody\.appendChild\(tr\);)'
            text = re.sub(tr_append_pattern, r"\1if(data.adjunto) tr.dataset.adjunto = data.adjunto;\n            \2", text, flags=re.DOTALL)
            
            # Modify the X button of Action to be an SVG too
            # This is \2 in the row_pattern. We can just globally replace the button later, but better to do it now.
            
            push_pattern = rf"(document\.querySelectorAll\('#{table_id} tbody tr'\)\.forEach\(tr => {{.*?(?:push)\({{.*?)(}} \);)"
            text = re.sub(push_pattern, r"\1, adjunto: tr.dataset.adjunto || '' \2", text, flags=re.DOTALL)

# Modify extraction functions to ignore file inputs
extract_func_bodies = re.findall(r'function extractFactor.*?\{.*?(?=\n\s*function|\n\s*\</script)', text, re.DOTALL)
for body in extract_func_bodies:
    new_body = body.replace("querySelectorAll('input')", "querySelectorAll('input:not([type=\"file\"])')")
    new_body = new_body.replace("querySelectorAll('input, select')", "querySelectorAll('input:not([type=\"file\"]), select')")
    text = text.replace(body, new_body)

# Replace all old text X buttons with ICON_DEL
text = re.sub(r'<button class="btn-ghost" style="color:red;" onclick="(.*?)">[✕X]</button>', r'<button class="btn-ghost" style="color:#ef4444;" onclick="\1" title="Eliminar fila">' + icon_del + '</button>', text)

upload_func = f"""
        async function uploadGridEvidence(fileInput, tableId) {{
            if (!fileInput.files || fileInput.files.length === 0) return;
            const file = fileInput.files[0];
            const td = fileInput.closest('td');
            const tr = fileInput.closest('tr');
            const progId = getProgramId();
            if (!progId || progId == 0) {{
                alert("Debes seleccionar un programa antes de subir evidencias.");
                return;
            }}

            const formData = new FormData();
            formData.append('file', file);
            formData.append('inst_id', getInstId());
            formData.append('program_id', progId);
            formData.append('aspect_id', 'STAT_' + tableId);
            formData.append('period', 'Estadisticas');
            formData.append('email', user.email);

            td.innerHTML = '<span style="color:var(--primary-color)">⏳ Subiendo...</span>';

            try {{
                const res = await fetch('/api/upload', {{
                    method: 'POST',
                    body: formData
                }});
                const data = await res.json();
                if (data.status === 'success') {{
                    tr.dataset.adjunto = data.url;
                    td.innerHTML = `
                        <div style="display:flex; gap:5px; align-items:center;">
                            <a href="/api/download?url=${{encodeURIComponent(data.url)}}&name=evidencia" target="_blank" class="btn-ghost" style="padding:4px 8px; font-size:0.8rem; border:1px solid #e2e8f0; border-radius:6px; color:#3b82f6;" title="Ver/Descargar Evidencia">{icon_view}</a>
                            <button class="btn-ghost" style="color:#ef4444; padding:4px 8px; border:1px solid #fca5a5; border-radius:6px;" onclick="this.closest('tr').dataset.adjunto=''; this.parentElement.innerHTML='<label style=\\'cursor:pointer; color:#3b82f6; display:flex; align-items:center; justify-content:center; padding:4px; border:1px dashed #93c5fd; border-radius:6px;\\' title=\\'Subir evidencia\\'>{icon_upload_escaped}<input type=\\'file\\' style=\\'display:none\\' onchange=\\'uploadGridEvidence(this, &quot;${{tableId}}&quot;)\\'></label>'">{icon_del}</button>
                        </div>`;
                    
                    const saveBtn = document.querySelector('button[onclick^="saveFactor"]');
                    if(saveBtn) saveBtn.style.boxShadow = "0 0 10px var(--primary-color)";
                }} else {{
                    alert('Error al subir: ' + (data.message || 'Error'));
                    td.innerHTML = `<label style="cursor:pointer; color:#3b82f6; display:flex; align-items:center; justify-content:center; padding:6px; border:1px dashed #93c5fd; border-radius:6px; transition:0.2s;" title="Subir evidencia">{icon_upload}<input type="file" style="display:none;" onchange="uploadGridEvidence(this, '${{tableId}}')"></label>`;
                }}
            }} catch(err) {{
                console.error(err);
                alert('Error de red al subir la evidencia.');
                td.innerHTML = `<label style="cursor:pointer; color:#3b82f6; display:flex; align-items:center; justify-content:center; padding:6px; border:1px dashed #93c5fd; border-radius:6px; transition:0.2s;" title="Subir evidencia">{icon_upload}<input type="file" style="display:none;" onchange="uploadGridEvidence(this, '${{tableId}}')"></label>`;
            }}
        }}
"""

text = text.replace('</script>\n    <script src=', upload_func + '\n</script>\n    <script src=')

with open('templates/evidencias.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Safe update applied to evidencias.html")
