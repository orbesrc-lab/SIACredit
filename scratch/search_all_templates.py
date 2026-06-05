import os

templates_dir = 'c:/SIAC/templates'
for filename in os.listdir(templates_dir):
    path = os.path.join(templates_dir, filename)
    if os.path.isfile(path) and filename.endswith('.html'):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if 'adjunto: tr.dataset.adjunto' in content:
            print(f"Found in {filename}")
