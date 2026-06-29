import codecs

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    lines = f.readlines()

start_idx = -1
for i, line in enumerate(lines):
    if '<div id="librarySectionBottom"' in line:
        start_idx = i
        break

saved_idx = -1
for i in range(start_idx, len(lines)):
    if '<div id="savedResourcesContainer"' in lines[i]:
        saved_idx = i
        break

end_idx = -1
for i in range(saved_idx, len(lines)):
    if lines[i].startswith('                    </div>'):
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    library_lines = lines[start_idx : end_idx + 1]
    
    # Remove it from its original place
    del lines[start_idx : end_idx + 1]
    
    # Now find where to insert it.
    settings_end_idx = -1
    for i, line in enumerate(lines):
        if '<!-- END settings-card -->' in line:
            settings_end_idx = i
            break
            
    if settings_end_idx != -1:
        # We wrap it with the new class
        insertion = [
            '            <!-- REPOSITORIO GLOBAL -->\n',
            '            <div id="globalLibraryContainer" class="editor-container" style="margin-top: 50px; margin-bottom: 20px;">\n',
            '                <h2 style="font-size: 1.5rem; color: #1e293b; margin-bottom: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 15px;">📚 Biblioteca y Metabuscador Global</h2>\n',
            '                <p style="color: var(--text-muted); margin-bottom: 30px;">Busca recursos académicos, simuladores y juegos educativos para integrarlos en tus clases o estudiar por tu cuenta.</p>\n'
        ] + library_lines + [
            '            </div>\n'
        ]
        
        lines[settings_end_idx:settings_end_idx] = insertion
        
        with codecs.open(path, 'w', 'utf-8') as f:
            f.writelines(lines)
        print("Success! Extracted from line", start_idx, "to", end_idx)
    else:
        print("Could not find settings-card end")
else:
    print("Could not find boundaries")
