import codecs

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    lines = f.readlines()

# librarySectionBottom starts at line 795 (index 794)
# It ends at line 870 (index 869)
# Let's search for '<div id="librarySectionBottom"' to be safe.
start_idx = -1
for i, line in enumerate(lines):
    if '<div id="librarySectionBottom"' in line:
        start_idx = i
        break

end_idx = -1
# Find '<!-- Favoritos Guardados -->' after start_idx
fav_idx = -1
for i in range(start_idx, len(lines)):
    if '<!-- Favoritos Guardados -->' in line:
        fav_idx = i
        break

# The </div> closing librarySectionBottom is right before '</div>' that closes courseEditorSection.
# Let's find '<!-- TAB: TEACHERS (Admin) -->' and go backwards to find the 3 divs.
teachers_idx = -1
for i in range(start_idx, len(lines)):
    if '<!-- TAB: TEACHERS (Admin) -->' in lines[i]:
        teachers_idx = i
        break

# The lines before teachers_idx are:
# </div> (coursesTab)
# </div> (courseEditorSection)
# </div> (librarySectionBottom)
# </div> (savedResourcesContainer)
# So if we look backwards from teachers_idx, we see a blank line, then the divs.
# Let's just find "savedResourcesContainer" and find its closing div, and the next closing div is librarySectionBottom.
saved_idx = -1
for i in range(start_idx, len(lines)):
    if '<div id="savedResourcesContainer"' in lines[i]:
        saved_idx = i
        break

# From saved_idx, find the second '</div>'
div_count = 0
lib_end_idx = -1
for i in range(saved_idx + 1, len(lines)):
    if '</div>' in lines[i]:
        div_count += 1
        if div_count == 2:
            lib_end_idx = i
            break

if start_idx != -1 and lib_end_idx != -1:
    library_lines = lines[start_idx : lib_end_idx + 1]
    
    # Remove from lines
    del lines[start_idx : lib_end_idx + 1]
    
    # Now find '<!-- END settings-card -->'
    settings_end_idx = -1
    for i, line in enumerate(lines):
        if '<!-- END settings-card -->' in line:
            settings_end_idx = i
            break
            
    if settings_end_idx != -1:
        # Insert before settings_end_idx
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
        print("Done!")
    else:
        print("settings-card end not found")
else:
    print("library not found")
