import os

# 1. RIESGOS
riesgos_path = r'c:\SIAC\templates\empresa_riesgos.html'
with open(riesgos_path, 'r', encoding='utf-8') as f:
    content = f.read()

edit_risk_func = """
        function editRisk(idx) {
            const r = risks[idx];
            document.getElementById('r_desc').value = r.desc;
            document.getElementById('r_prob').value = r.prob;
            document.getElementById('r_impact').value = r.impact;
            document.getElementById('r_plan').value = r.plan || '';
            removeRisk(idx);
            document.getElementById('r_desc').focus();
        }
"""

if 'function editRisk' not in content:
    content = content.replace('function removeRisk(idx)', edit_risk_func + '\n        function removeRisk(idx)')

# Replace the action column in renderRisks
old_action_r = '<button onclick="removeRisk(${r.originalIdx})" style="background:none; border:none; color:#ef4444; cursor:pointer;"><i class="fas fa-trash"></i></button>'
new_action_r = '<button onclick="editRisk(${r.originalIdx})" style="background:none; border:none; color:#3b82f6; cursor:pointer; margin-right:15px; font-size:1.1rem;"><i class="fas fa-edit"></i></button><button onclick="removeRisk(${r.originalIdx})" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:1.1rem;"><i class="fas fa-trash"></i></button>'

content = content.replace(old_action_r, new_action_r)

with open(riesgos_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. STAKEHOLDERS
stake_path = r'c:\SIAC\templates\empresa_stakeholders.html'
with open(stake_path, 'r', encoding='utf-8') as f:
    content = f.read()

edit_stake_func = """
        function editStakeholder(idx) {
            const s = stakeholders[idx];
            document.getElementById('sh_name').value = s.name;
            document.getElementById('sh_power').value = s.power;
            document.getElementById('sh_interest').value = s.interest;
            document.getElementById('sh_strategy').value = s.strategy || '';
            removeStakeholder(idx);
            document.getElementById('sh_name').focus();
        }
"""

if 'function editStakeholder' not in content:
    content = content.replace('function removeStakeholder(idx)', edit_stake_func + '\n        function removeStakeholder(idx)')

old_action_s = '<button onclick="removeStakeholder(${s.originalIdx})" style="background:none; border:none; color:#ef4444; cursor:pointer;"><i class="fas fa-trash"></i></button>'
new_action_s = '<button onclick="editStakeholder(${s.originalIdx})" style="background:none; border:none; color:#3b82f6; cursor:pointer; margin-right:15px; font-size:1.1rem;"><i class="fas fa-edit"></i></button><button onclick="removeStakeholder(${s.originalIdx})" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:1.1rem;"><i class="fas fa-trash"></i></button>'

content = content.replace(old_action_s, new_action_s)

with open(stake_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Edit buttons added.")
