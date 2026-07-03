import os
import glob

def fix_visibility():
    templates_dir = 'c:\\SIAC\\templates'
    html_files = glob.glob(os.path.join(templates_dir, '*.html'))
    
    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        modified = False
        if "['admin', 'inst_admin', 'lider'].includes(role)" in content:
            content = content.replace("['admin', 'inst_admin', 'lider'].includes(role)", "['admin', 'super_admin', 'inst_admin', 'lider'].includes(role)")
            modified = True
        
        if "['admin','inst_admin','lider'].includes(role)" in content:
            content = content.replace("['admin','inst_admin','lider'].includes(role)", "['admin', 'super_admin', 'inst_admin', 'lider'].includes(role)")
            modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed {os.path.basename(file_path)}")

if __name__ == '__main__':
    fix_visibility()
