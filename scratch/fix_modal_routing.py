import os

app_js_path = r'c:\SIAC\static\app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the condition in sidebar link interception
old_cond = "if (href && href !== '#' && !href.startsWith('javascript:')) {"
new_cond = "if (href && href !== '#' && !href.startsWith('javascript:') && !href.includes('empresa_')) {"

if old_cond in content:
    content = content.replace(old_cond, new_cond)
    with open(app_js_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated app.js successfully.")
else:
    print("Condition not found. Check app.js logic.")
