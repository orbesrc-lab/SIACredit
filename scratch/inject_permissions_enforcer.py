import os
import glob

# Path to templates
templates_dir = r"c:\SIAC\templates"
script_tag = """    <script src="{{ url_for('static', filename='permissions_enforcer.js') }}"></script>\n</body>"""

# Files to skip (public pages or pages that don't need the enforcer)
skip_files = [
    "login.html",
    "registro.html",
    "index.html",
    "index_backup.html",
    "encuesta_publica.html"
]

def inject_enforcer():
    html_files = glob.glob(os.path.join(templates_dir, "*.html"))
    count = 0
    
    for filepath in html_files:
        filename = os.path.basename(filepath)
        if filename in skip_files:
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "permissions_enforcer.js" not in content:
            # Replace the last occurrence of </body> or just the </body> tag
            if "</body>" in content:
                # We do a standard replace, assuming </body> is standard
                # But it's safer to rsplit and join to replace only the last occurrence
                parts = content.rsplit("</body>", 1)
                new_content = parts[0] + script_tag + (parts[1] if len(parts) > 1 else "")
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Injected into {filename}")
                count += 1
            else:
                print(f"Warning: No </body> tag found in {filename}")
        else:
            print(f"Already injected in {filename}")

    print(f"\nTotal files updated: {count}")

if __name__ == "__main__":
    inject_enforcer()
