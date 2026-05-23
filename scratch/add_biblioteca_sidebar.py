import os
import glob

def update_sidebars():
    templates_dir = r"c:\SIAC\templates"
    for file_path in glob.glob(os.path.join(templates_dir, "*.html")):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if it has a sidebar-menu
        if '<div class="sidebar-menu">' in content and '📚 Biblioteca' not in content:
            # We want to insert the link before ⚙️ Configuración, or at the end
            # Configuración usually looks like: <a href="configuracion.html" class="sidebar-item">⚙️ Configuración</a>
            # We will replace it with Biblioteca + Configuracion
            if 'href="configuracion.html"' in content:
                content = content.replace(
                    '<a href="configuracion.html"',
                    '<a href="biblioteca.html" class="sidebar-item">📚 Biblioteca</a>\n            <a href="configuracion.html"'
                )
                
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated {os.path.basename(file_path)}")

if __name__ == "__main__":
    update_sidebars()
