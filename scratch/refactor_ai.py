import re

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if line.startswith("def call_ai("):
        start_idx = i
    if start_idx != -1 and ("# --- Rutas del M" in line and "Encuestas de Autoevaluaci" in line):
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    extract_lines = lines[start_idx:end_idx]
    
    bp_code = "from flask import Blueprint, jsonify, request, Response\n"
    bp_code += "from utils.db import supabase, get_active_inst_id\n"
    bp_code += "import json\n"
    bp_code += "import os\n"
    bp_code += "from openai import OpenAI\n"
    bp_code += "from urllib.parse import unquote\n"
    bp_code += "import re\n\n"
    
    bp_code += "ai_bp = Blueprint('ai', __name__)\n\n"
    
    for line in extract_lines:
        line = line.replace("@app.route", "@ai_bp.route")
        bp_code += line
        
    with open(r'c:\SIAC\routes\ai.py', 'w', encoding='utf-8') as f:
        f.write(bp_code)
        
    new_app = "".join(lines[:start_idx]) + "".join(lines[end_idx:])
    
    with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
        f.write(new_app)
        
    print(f"Extracted {end_idx - start_idx} lines for ai blueprint.")
else:
    print(f"Could not find section boundaries. Start: {start_idx}, End: {end_idx}")
