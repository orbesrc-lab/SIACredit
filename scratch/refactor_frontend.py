import re

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_frontend = -1
end_frontend = -1

for i, line in enumerate(lines):
    if "# --- Rutas para SEO (Indexación) ---" in line or "# --- Rutas para SEO (Indexacin) ---" in line:
        start_frontend = i
    if start_frontend != -1 and "# Endpoint de emergencia para recrear admin" in line:
        end_frontend = i
        break

if start_frontend != -1 and end_frontend != -1:
    frontend_lines = lines[start_frontend:end_frontend]
    
    bp_code = "from flask import Blueprint, render_template, request, send_from_directory\n"
    bp_code += "from utils.db import supabase\n"
    bp_code += "import json\n\n"
    bp_code += "frontend_bp = Blueprint('frontend', __name__)\n\n"
    
    # We need to handle app.static_folder for send_from_directory.
    # In blueprint, we can use current_app.static_folder
    bp_code += "from flask import current_app\n\n"
    
    for line in frontend_lines:
        line = line.replace("@app.route", "@frontend_bp.route")
        line = line.replace("app.static_folder", "current_app.static_folder")
        bp_code += line
        
    with open(r'c:\SIAC\routes\frontend.py', 'w', encoding='utf-8') as f:
        f.write(bp_code)
        
    new_app = "".join(lines[:start_frontend]) + "".join(lines[end_frontend:])
    
    with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
        f.write(new_app)
        
    print(f"Extracted {end_frontend - start_frontend} lines for frontend blueprint.")
else:
    print("Could not find frontend section.")
