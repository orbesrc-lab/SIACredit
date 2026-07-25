import codecs
import re

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

pattern = re.compile(r'(<div id="librarySectionBottom".*?)(<!-- Favoritos Guardados -->)', re.DOTALL)
match = pattern.search(content)

if match:
    library_html = match.group(1)
    # Remove from current location
    content = content[:match.start()] + '<!-- Favoritos Guardados -->' + content[match.end():]
    
    modal_marker = "<!-- MODAL: CREAR CURSO -->"
    if modal_marker in content:
        # Give it a nice wrapper so it stands out globally
        wrapped_library = f"""
            <!-- REPOSITORIO GLOBAL -->
            <div id="globalLibraryContainer" style="margin-top: 50px; margin-bottom: 50px;">
                {library_html}
            </div>
            {modal_marker}
        """
        content = content.replace(modal_marker, wrapped_library)
        
        # We need to make sure librarySectionBottom doesn't have display:none initially if we want it to be always visible globally.
        # But wait! If we want to toggle it or leave it always visible?
        # In formacion.html it currently has: style="margin-top: 40px; border-top: 2px dashed #e2e8f0; padding-top: 30px;" (No display: none)
        
        with codecs.open(path, 'w', 'utf-8') as f:
            f.write(content)
        print("Moved successfully")
    else:
        print("Modal marker not found")
else:
    print("librarySectionBottom not found")
