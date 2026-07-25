import re

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "# --- API Endpoints con Supabase" in line:
        start_idx = i
    if start_idx != -1 and "# --- Dashboard Stats ---" in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    extract_lines = lines[start_idx:end_idx]
    
    bp_code = "from flask import Blueprint, jsonify, request, session, render_template\n"
    bp_code += "from utils.db import supabase, get_active_inst_id\n"
    bp_code += "from werkzeug.security import generate_password_hash, check_password_hash\n"
    bp_code += "import uuid\n"
    bp_code += "import json\n"
    bp_code += "import traceback\n\n"
    
    bp_code += "core_bp = Blueprint('core', __name__)\n\n"
    
    for line in extract_lines:
        line = line.replace("@app.route", "@core_bp.route")
        bp_code += line
        
    with open(r'c:\SIAC\routes\core.py', 'w', encoding='utf-8') as f:
        f.write(bp_code)
        
    new_app = "".join(lines[:start_idx]) + "".join(lines[end_idx:])
    
    with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
        f.write(new_app)
        
    print(f"Extracted {end_idx - start_idx} lines for core blueprint.")
else:
    print(f"Could not find section boundaries. Start: {start_idx}, End: {end_idx}")
