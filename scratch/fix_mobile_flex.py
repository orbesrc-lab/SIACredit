import os

file_path = r"c:\SIAC\templates\formacion.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. unit-header
content = content.replace(
    'class="unit-header" style="background: #e2e8f0; color: #64748b; border-color: #cbd5e1; display:flex; justify-content:space-between; align-items:center;"',
    'class="unit-header" style="background: #e2e8f0; color: #64748b; border-color: #cbd5e1; display:flex; justify-content:space-between; align-items:center; flex-wrap: wrap; gap: 8px;"'
)

# 2. toggleTopicAccordion(topic)
content = content.replace(
    'align-items: center; background: rgba(99,102,241,0.04); color: var(--text-main); transition: background 0.2s;"',
    'align-items: center; background: rgba(99,102,241,0.04); color: var(--text-main); transition: background 0.2s; flex-wrap: wrap; gap: 8px;"'
)

# 3. toggleTopicAccordion(resource)
content = content.replace(
    'align-items: center; background: #f8fafc; color: var(--text-main); transition: background 0.2s;"',
    'align-items: center; background: #f8fafc; color: var(--text-main); transition: background 0.2s; flex-wrap: wrap; gap: 8px;"'
)

# 4. resources inner flex
content = content.replace(
    '<div style="display:flex; gap:10px; align-items:center;">',
    '<div style="display:flex; gap:10px; align-items:center; flex-wrap: wrap;">'
)

# 5. activity-item inner flex
content = content.replace(
    '<div style="display:flex; justify-content:space-between; align-items:center; width:100%;">',
    '<div style="display:flex; justify-content:space-between; align-items:center; width:100%; flex-wrap: wrap; gap: 10px;">'
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Flex wrap fixes applied.")
