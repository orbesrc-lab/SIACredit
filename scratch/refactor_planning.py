import re

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1

for i, line in enumerate(lines):
    if "PLANIFICACI" in line and "CONTROL" in line:
        start_idx = i
        break

if start_idx != -1:
    extract_lines = []
    main_block = []
    in_main = False
    
    for line in lines[start_idx:]:
        if "if __name__ == '__main__':" in line:
            in_main = True
            main_block.append(line)
        elif in_main and line.startswith("    "):
            main_block.append(line)
        elif in_main:
            in_main = False
            extract_lines.append(line)
        else:
            extract_lines.append(line)
            
    
    bp_code = "from flask import Blueprint, jsonify, request\n"
    bp_code += "from utils.db import supabase, get_active_inst_id\n"
    bp_code += "import traceback\n\n"
    
    bp_code += "planning_bp = Blueprint('planning', __name__)\n\n"
    
    for line in extract_lines:
        line = line.replace("@app.route", "@planning_bp.route")
        bp_code += line
        
    with open(r'c:\SIAC\routes\planning.py', 'w', encoding='utf-8') as f:
        f.write(bp_code)
        
    new_app = "".join(lines[:start_idx]) + "".join(main_block)
    
    with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
        f.write(new_app)
        
    print(f"Extracted {len(extract_lines)} lines for planning blueprint.")
else:
    print(f"Could not find section boundaries. Start: {start_idx}")
