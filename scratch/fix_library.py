import codecs
import re

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

# I need to find the START of librarySectionBottom and the END of librarySectionBottom.
# It starts at `<div id="librarySectionBottom"`
# Inside it, we have containerOpenAlex, containerOvas, savedResourcesContainer.
# Let's extract by using the exact string markers.
start_marker = '<div id="librarySectionBottom"'
end_marker = '<!-- Favoritos Guardados -->\n                        <div id="savedResourcesContainer" style="display: none;">'

# Find start
start_idx = content.find(start_marker)

# Find the end marker
end_marker_idx = content.find(end_marker)

# Find the </div> that closes savedResourcesContainer.
# We know savedResourcesContainer is relatively short.
# Let's find it.
partial_end = content[end_marker_idx:]
# The end of savedResourcesContainer is followed by </div> </div> </div>
# In the original, it looks like this:
#                        <!-- Favoritos Guardados -->
#                        <div id="savedResourcesContainer" style="display: none;">
#                            <h3 ...>...</h3>
#                            <div id="savedResourcesGrid" ...>
#                                <!-- Se llenará vía JS -->
#                            </div>
#                        </div>
#                    </div>
# </div>

# So from end_marker_idx, we find the second '</div>\n                    </div>'
block_end_idx = content.find('                    </div>\n</div>', end_marker_idx)

if start_idx != -1 and block_end_idx != -1:
    # Extract the block! We want to include the '</div>\n' before '</div>\n</div>'
    library_html = content[start_idx:block_end_idx + 26] # "                    </div>" length is 26
    
    # Remove it from its original place.
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
