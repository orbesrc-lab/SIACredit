import codecs

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

start_marker = '<div id="librarySectionBottom"'
start_idx = content.find(start_marker)

end_marker = '<!-- Favoritos Guardados -->'
end_marker_idx = content.find(end_marker, start_idx)

# Find the exact closing tags after Favoritos Guardados
block_end_idx = content.find('                    </div>\n</div>', end_marker_idx)

if start_idx != -1 and block_end_idx != -1:
    # We want to grab everything up to "                    </div>" (length 26)
    library_html = content[start_idx:block_end_idx + 26]
    
    # Remove from original place
    content = content[:start_idx] + content[block_end_idx + 26:]
    
    target_marker = "</div> <!-- END settings-card -->"
    
    if target_marker in content:
        wrapped_library = f"""
            <!-- REPOSITORIO GLOBAL -->
            <div id="globalLibraryContainer" class="editor-container" style="margin-top: 50px; margin-bottom: 20px;">
                <h2 style="font-size: 1.5rem; color: #1e293b; margin-bottom: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 15px;">📚 Biblioteca y Metabuscador Global</h2>
                <p style="color: var(--text-muted); margin-bottom: 30px;">Busca recursos académicos, simuladores y juegos educativos para integrarlos en tus clases o estudiar por tu cuenta.</p>
                {library_html}
            </div>
            {target_marker}
"""
        content = content.replace(target_marker, wrapped_library)
        
        with codecs.open(path, 'w', 'utf-8') as f:
            f.write(content)
        print("Successfully extracted and inserted.")
    else:
        print("Target marker not found")
else:
    print("Could not find block boundaries")
