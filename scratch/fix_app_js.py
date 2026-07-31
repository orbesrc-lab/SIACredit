import os

files_to_fix = [
    "c:/SIAC/templates/empresa_matrices.html",
    "c:/SIAC/templates/empresa_bcg.html",
    "c:/SIAC/templates/empresa_dofa.html"
]

target_script = "<script src=\"{{ url_for('static', filename='data.js') }}\"></script>"
insert_script = "<script src=\"{{ url_for('static', filename='app.js') }}\"></script>\n    " + target_script

for filepath in files_to_fix:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "app.js" not in content:
        content = content.replace(target_script, insert_script)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"Already fixed {filepath}")
