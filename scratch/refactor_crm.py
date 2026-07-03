import re

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start and end of the CRM routes
start_crm = -1
end_crm = -1

for i, line in enumerate(lines):
    if "# --- RUTAS DE PARTNERS ---" in line:
        start_crm = i
    if start_crm != -1 and "# Ruta de depuración para arreglar la base de datos" in line:
        end_crm = i
        break

if start_crm != -1 and end_crm != -1:
    crm_lines = lines[start_crm:end_crm]
    
    # We will create blueprints/crm.py
    crm_code = "from flask import Blueprint, jsonify, request\n"
    crm_code += "from utils.db import supabase\n\n"
    crm_code += "crm_bp = Blueprint('crm', __name__)\n\n"
    
    # Replace @app.route with @crm_bp.route
    for line in crm_lines:
        crm_code += line.replace("@app.route", "@crm_bp.route")
        
    with open(r'c:\SIAC\routes\crm.py', 'w', encoding='utf-8') as f:
        f.write(crm_code)
        
    # Remove from app.py
    new_app = "".join(lines[:start_crm]) + "".join(lines[end_crm:])
    
    with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
        f.write(new_app)
        
    print(f"Extracted {end_crm - start_crm} lines for CRM blueprint.")
else:
    print("Could not find CRM section.")
