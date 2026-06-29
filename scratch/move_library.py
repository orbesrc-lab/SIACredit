import codecs
import re

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

# Locate the librarySectionBottom up to its closing tag.
# We know it starts at <div id="librarySectionBottom"
# It ends right before "Favoritos Guardados" or after "containerOvas".
# Actually, I'll use regex to extract it safely.

pattern = re.compile(r'(<div id="librarySectionBottom".*?)(<!-- Favoritos Guardados -->)', re.DOTALL)
match = pattern.search(content)

if match:
    library_html = match.group(1)
    
    # Remove it from its current location inside courseEditorSection
    content = content[:match.start()] + '<!-- Favoritos Guardados -->' + content[match.end():]
    
    # Now, where to put it?
    # Let's put it right before "<!-- Modal: Añadir Unidad -->"
    # This is outside of all tabs and course editors, at the bottom of the main content area.
    modal_marker = "<!-- Modal: Añadir Unidad -->"
    if modal_marker in content:
        content = content.replace(modal_marker, library_html + "\n\n" + modal_marker)
        with codecs.open(path, 'w', 'utf-8') as f:
            f.write(content)
        print("Moved successfully")
    else:
        print("Modal marker not found")
else:
    print("librarySectionBottom not found")
