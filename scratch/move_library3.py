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
    
    target_marker = "</div> <!-- END settings-card -->"
    if target_marker in content:
        wrapped_library = f"""
            <!-- REPOSITORIO GLOBAL -->
            <div id="globalLibraryContainer" style="margin-top: 50px; border-top: 4px solid #e2e8f0; padding-top: 40px; margin-bottom: 20px;">
                <h2 style="font-size: 1.5rem; color: #1e293b; margin-bottom: 20px;">📚 Biblioteca y Metabuscador Global</h2>
                <p style="color: var(--text-muted); margin-bottom: 30px;">Busca recursos académicos, simuladores y juegos educativos para integrarlos en tus clases o estudiar por tu cuenta.</p>
                {library_html}
            </div>
            {target_marker}
        """
        content = content.replace(target_marker, wrapped_library)
        
        with codecs.open(path, 'w', 'utf-8') as f:
            f.write(content)
        print("Moved successfully")
    else:
        print("Target marker not found")
else:
    print("librarySectionBottom not found")
