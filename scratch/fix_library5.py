import codecs

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    lines = f.readlines()

# 1. Fix the extra </div>
for i in range(len(lines)):
    if '<!-- Favoritos Guardados -->' in lines[i]:
        # Look backwards for the extra </div>
        for j in range(i-1, i-5, -1):
            if '</div>' in lines[j]:
                print(f"Removing extra </div> at line {j+1}")
                lines[j] = '\n' # Remove it
                break
        break

# 2. Extract librarySectionBottom
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
    
    # Now find where to insert it. We want it INSIDE settings-card.
    # We will look for <!-- END settings-card --> and insert BEFORE it.
    settings_end_idx = -1
    for i, line in enumerate(lines):
        if '<!-- END settings-card -->' in line:
            # We want to insert just before the closing </div> of settings-card.
            # But wait, <!-- END settings-card --> might be on the same line or after.
            # Let's search for the line before it.
            settings_end_idx = i
            break
            
    if settings_end_idx != -1:
        # We need to make sure we insert BEFORE the </div> that closes settings-card
        insert_idx = settings_end_idx
        while insert_idx > 0 and '</div>' not in lines[insert_idx - 1]:
            insert_idx -= 1
        
        # Actually, let's just insert before the <!-- END settings-card --> line.
        # If the </div> is on the line above, we insert BEFORE the </div>.
        if '</div>' in lines[settings_end_idx - 1]:
            insert_idx = settings_end_idx - 1
        else:
            insert_idx = settings_end_idx
            
        insertion = [
            '            <!-- REPOSITORIO GLOBAL -->\n',
            '            <div id="globalLibraryContainer" style="margin-top: 50px; padding-top: 30px; border-top: 2px solid var(--border-color);">\n',
            '                <h2 style="font-size: 1.5rem; color: #1e293b; margin-bottom: 20px;">Y"s Repositorio SKEL y Metabuscador Global</h2>\n',
            '                <p style="color: var(--text-muted); margin-bottom: 30px;">Busca recursos acadǸmicos, simuladores y juegos educativos para integrarlos en tus clases o estudiar por tu cuenta.</p>\n'
        ] + library_lines + [
            '            </div>\n'
        ]
        
        # Replace librarySectionBottom style to not have top border since we added it to globalLibraryContainer
        for k in range(len(insertion)):
            if '<div id="librarySectionBottom"' in insertion[k]:
                insertion[k] = insertion[k].replace('border-top: 2px dashed #e2e8f0; ', '')
                break
                
        lines[insert_idx:insert_idx] = insertion
        
        with codecs.open(path, 'w', 'utf-8') as f:
            f.writelines(lines)
        print("Success! Extracted from line", start_idx, "to", end_idx)
    else:
        print("Could not find settings-card end")
else:
    print("Could not find boundaries")
