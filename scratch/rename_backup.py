import os
import glob

def rename_backup_button():
    templates_dir = 'c:\\SIAC\\templates'
    html_files = glob.glob(os.path.join(templates_dir, '*.html'))
    
    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if ">💾 Backup<" in content:
            content = content.replace(">💾 Backup<", ">🛡️ Backup y Seguridad<")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Renamed button in {os.path.basename(file_path)}")

if __name__ == '__main__':
    rename_backup_button()
