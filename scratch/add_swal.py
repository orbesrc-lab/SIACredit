import os

file_path = r'c:\SIAC\templates\empresa_matrices.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

swal_script = '<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>'

if swal_script not in content:
    # insert before </head>
    content = content.replace('</head>', f'    {swal_script}\n</head>')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SweetAlert2 added to empresa_matrices.html")
else:
    print("Already there.")
