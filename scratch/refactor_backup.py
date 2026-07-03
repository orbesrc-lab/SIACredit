import re

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_backup = -1

for i, line in enumerate(lines):
    if "# BACKUP MODULE" in line:
        start_backup = i
        break

if start_backup != -1:
    backup_lines = lines[start_backup:]
    
    # We must filter out `if __name__ == '__main__':` and `app.run` if they exist in backup_lines
    final_backup_lines = []
    main_block = []
    in_main = False
    
    for line in backup_lines:
        if "if __name__ == '__main__':" in line:
            in_main = True
            main_block.append(line)
        elif in_main and line.startswith("    "):
            main_block.append(line)
        elif in_main:
            in_main = False
            final_backup_lines.append(line)
        else:
            final_backup_lines.append(line)
            
    
    bp_code = "from flask import Blueprint, jsonify, request, send_file, Response\n"
    bp_code += "from utils.db import supabase\n"
    bp_code += "import io\n"
    bp_code += "import csv\n"
    bp_code += "import traceback\n"
    bp_code += "import urllib.request as _ureq\n"
    bp_code += "import re\n\n"
    bp_code += "backup_bp = Blueprint('backup', __name__)\n\n"
    
    # add safe filename helper
    bp_code += "def _safe_filename(name):\n"
    bp_code += "    if not name: return 'archivo'\n"
    bp_code += "    return re.sub(r'[^\\w\\-]', '_', str(name))[:100]\n\n"
    
    bp_code += "def _fetch_file_bytes(url):\n"
    bp_code += "    try:\n"
    bp_code += "        req = _ureq.Request(url, headers={'User-Agent': 'Mozilla/5.0'})\n"
    bp_code += "        with _ureq.urlopen(req, timeout=10) as response:\n"
    bp_code += "            return response.read()\n"
    bp_code += "    except:\n"
    bp_code += "        return None\n\n"
    
    for line in final_backup_lines:
        line = line.replace("@app.route", "@backup_bp.route")
        bp_code += line
        
    with open(r'c:\SIAC\routes\backup.py', 'w', encoding='utf-8') as f:
        f.write(bp_code)
        
    new_app = "".join(lines[:start_backup]) + "".join(main_block)
    
    with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
        f.write(new_app)
        
    print(f"Extracted {len(final_backup_lines)} lines for backup blueprint.")
else:
    print("Could not find backup section.")
