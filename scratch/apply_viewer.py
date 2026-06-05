import os, re

templates_dir = 'templates'
html_files = [os.path.join(templates_dir, f) for f in os.listdir(templates_dir) if f.endswith('.html')]

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    # 1. Inject viewer.js if not present
    if 'viewer.js' not in content and 'downloader.js' in content:
        content = content.replace(
            '<script src="{{ url_for(\'static\', filename=\'downloader.js\') }}"></script>',
            '<script src="{{ url_for(\'static\', filename=\'downloader.js\') }}"></script>\n    <script src="{{ url_for(\'static\', filename=\'viewer.js\') }}"></script>'
        )
        modified = True

    # 2. Fix viewFile in evidencias.html and evidencias_mod.html
    if 'evidencias' in filepath.lower():
        # Replace the entire viewFile function
        viewfile_regex = re.compile(r'function viewFile\(url, name\)\s*\{.*?\n        \}', re.DOTALL)
        if viewfile_regex.search(content):
            new_viewfile = """function viewFile(url, name) {
            if (typeof abrirVisor === 'function') {
                abrirVisor(url, name);
            } else {
                forceDownload(url, name);
            }
        }"""
            content = viewfile_regex.sub(new_viewfile, content)
            modified = True
            
        # Optional: remove the viewerModal HTML
        modal_regex = re.compile(r'<div id="viewerModal".*?<!-- FIN MODAL VISOR -->', re.DOTALL)
        content = modal_regex.sub('', content)

    # 3. Fix estadisticas.html (add Ver button)
    if 'estadisticas' in filepath.lower():
        if 'abrirVisor' not in content:
            # Add Ver button before Download button
            download_btn = """<button onclick="forceDownload('${adj.url}','${(adj.name || \\'archivo\\').replace(/\\'/g, \\"\\\\\\'\\")}')" title="${adj.name}" style="font-size:0.75rem; padding:4px 8px; background:#e0e7ff; color:#4338ca; border-radius:4px; border:none; cursor:pointer; font-weight:600; white-space:nowrap;">
                                        ⬇️ ${displayName}
                                    </button>"""
            
            new_btns = """<button onclick="abrirVisor('${adj.url}','${(adj.name || \\'archivo\\').replace(/\\'/g, \\"\\\\\\'\\")}')" title="Ver" style="font-size:0.75rem; padding:4px 8px; background:#f0fdf4; color:#166534; border-radius:4px; border:none; cursor:pointer; font-weight:600; white-space:nowrap; margin-right:4px;">
                                        👁️ Ver
                                    </button>
                                    <button onclick="forceDownload('${adj.url}','${(adj.name || \\'archivo\\').replace(/\\'/g, \\"\\\\\\'\\")}')" title="${adj.name}" style="font-size:0.75rem; padding:4px 8px; background:#e0e7ff; color:#4338ca; border-radius:4px; border:none; cursor:pointer; font-weight:600; white-space:nowrap;">
                                        ⬇️ Descargar
                                    </button>"""
            
            content = content.replace(download_btn, new_btns)
            modified = True
            
    # 4. Fix informes.html (clickable evidences)
    if 'informes' in filepath.lower():
        if 'abrirVisor' not in content:
            old_li = "evidencesHtml += `<li><b>[A${a.number}]</b> ${ev.name}</li>`;"
            new_li = "evidencesHtml += `<li><b>[A${a.number}]</b> <a href=\"javascript:void(0)\" onclick=\"abrirVisor('${ev.file_url}', '${ev.name}')\" style=\"color:var(--primary-color); text-decoration:none;\">👁️ ${ev.name}</a></li>`;"
            if old_li in content:
                content = content.replace(old_li, new_li)
                modified = True
                
            # Also in RRC (Condición -> evidencias)
            old_rrc_evid = ".map(e=>`<li>${e.nombre}</li>`)"
            new_rrc_evid = ".map(e=>`<li><a href=\"javascript:void(0)\" onclick=\"abrirVisor('${e.url || \\'\\'}', '${e.nombre}')\" style=\"color:#2563eb;text-decoration:none;\">👁️ ${e.nombre}</a></li>`)"
            if old_rrc_evid in content:
                content = content.replace(old_rrc_evid, new_rrc_evid)
                modified = True

    # 5. Fix biblioteca.html (add Ver button)
    if 'biblioteca' in filepath.lower():
        if 'abrirVisor' not in content:
            old_download = '<button class="btn-ghost" onclick="forceDownload(`${doc.url}`, `${doc.name}`)" title="Descargar" style="font-size: 1rem; color: #4b5563;">⬇️</button>'
            new_download = '<button class="btn-ghost" onclick="abrirVisor(`${doc.url}`, `${doc.name}`)" title="Ver" style="font-size: 1rem; color: #166534; margin-right: 5px;">👁️</button>' + old_download
            if old_download in content:
                content = content.replace(old_download, new_download)
                modified = True
            
            old_docbtn = "<button onclick=\"forceDownload('${doc.url}', '${doc.name}')\" style=\"padding: 8px 12px; background: #e2e8f0; border: none; border-radius: 6px; cursor: pointer; color: #1e293b; font-weight: 500;\">⬇️ Descargar ${doc.name}</button>"
            new_docbtn = "<button onclick=\"abrirVisor('${doc.url}', '${doc.name}')\" style=\"padding: 8px 12px; background: #dcfce7; border: none; border-radius: 6px; cursor: pointer; color: #166534; font-weight: 500; margin-right: 8px;\">👁️ Ver</button>" + old_docbtn
            if old_docbtn in content:
                content = content.replace(old_docbtn, new_docbtn)
                modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"No changes needed for {filepath}")
