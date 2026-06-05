with open('c:/SIAC/templates/informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
if scripts:
    with open('c:/SIAC/scratch/extracted.js', 'w', encoding='utf-8') as f_out:
        f_out.write(scripts[0])
    print("Script extracted to c:/SIAC/scratch/extracted.js")
else:
    print("No script tag content found")
