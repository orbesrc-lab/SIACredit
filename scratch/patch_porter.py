import os
import re

file_path = r'c:\SIAC\templates\empresa_porter.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Date field and Manual Save Button
target_ui = r'<div class="context-panel">'
replacement_ui = r'''<div class="context-panel">
            <div style="margin-bottom: 15px;">
                <label style="font-weight: bold; font-size: 0.9rem; color: #475569;">📅 Fecha de Levantamiento de Información:</label>
                <input type="date" id="eval_date" style="margin-top: 5px; width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #cbd5e1;">
            </div>'''
if "Fecha de Levantamiento" not in content:
    content = re.sub(target_ui, replacement_ui, content, count=1)

# Add Manual Save Button
target_btn = r'<button class="btn-primary" onclick="analyzePorter()"'
replacement_btn = r'''<button class="btn-primary" onclick="saveMatrixData(false)" style="width:100%; margin-bottom:10px; padding:12px; border-radius:6px; border:none; background:#10b981; color:white; font-weight:bold; font-size:1rem; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px;">
                <i class="fas fa-save"></i> Guardar Manualmente
            </button>
            <button class="btn-primary" onclick="analyzePorter()"'''
if "Guardar Manualmente" not in content:
    content = re.sub(target_btn, replacement_btn, content, count=1)

# 2. Modify saveMatrixData
target_save = r'inputs \}'
replacement_save = r'inputs, eval_date: document.getElementById("eval_date").value }'
if 'eval_date: document' not in content:
    content = content.replace(target_save, replacement_save)

# 3. Modify loadMatriz
target_load = r'const dbData = data.data;'
replacement_load = r'''const dbData = data.data;
                    if(dbData.eval_date) document.getElementById('eval_date').value = dbData.eval_date;'''
if "if(dbData.eval_date)" not in content:
    content = content.replace(target_load, replacement_load)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("empresa_porter.html patched with date and save button")
