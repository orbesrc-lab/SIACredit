import os

files_to_check = [r"c:\SIAC\templates\index.html", r"c:\SIAC\static\landing.css", r"c:\SIAC\app.py"]

for fpath in files_to_check:
    if not os.path.exists(fpath): continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We will replace the .png with .webp ONLY if the .webp file exists in static
    static_dir = r"c:\SIAC\static"
    webp_files = [f for f in os.listdir(static_dir) if f.endswith('.webp')]
    
    for webp in webp_files:
        png_name = webp.replace(".webp", ".png")
        content = content.replace(png_name, webp)
        
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {os.path.basename(fpath)}")
