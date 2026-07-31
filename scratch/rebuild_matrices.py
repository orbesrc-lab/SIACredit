import re

# 1. Read the standard base (dofa.html)
with open(r'c:\SIAC\templates\dofa.html', 'r', encoding='utf-8') as f:
    base_content = f.read()

parts = base_content.split('<div class="content-area">')
top_html = parts[0] + '<div class="content-area">\n'
bottom_html = '\n</main>\n' + parts[1].split('</main>')[1]
clean_bottom = bottom_html.replace('initPage();', '')

# 2. Read current empresa_matrices.html
with open(r'c:\SIAC\templates\empresa_matrices.html', 'r', encoding='utf-8') as f:
    mat_content = f.read()

# Extract styles
styles_match = re.search(r'<style>(.*?)</style>', mat_content, re.DOTALL)
styles = f"<style>\n{styles_match.group(1)}\n</style>" if styles_match else ""

# Extract the main content (matrices-container)
main_match = re.search(r'(<div class="matrices-container">.*?)(?:<script>|</body>)', mat_content, re.DOTALL)
main_html = main_match.group(1) if main_match else ""

# Extract the script
script_match = re.search(r'<script>(.*?)</script>', mat_content, re.DOTALL)
script_js = f"<script>\n{script_match.group(1)}\n</script>" if script_match else ""

# Combine
new_content = top_html + styles + "\n" + main_html + "\n" + script_js + "\n" + clean_bottom

# Add the "Volver al Hub" button right after <div class="matrices-header">
volver_btn = """
    <div style="margin-bottom: 20px;">
        <a href="empresa_dashboard.html" style="display: inline-block; padding: 10px 20px; background: #e2e8f0; color: #334155; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 0.95rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: background 0.2s;">
            ⬅️ Volver al Hub Estratégico
        </a>
    </div>
"""
new_content = re.sub(r'(<div class="matrices-header">.*?</div>)', r'\1\n' + volver_btn, new_content, count=1, flags=re.DOTALL)

# Fix the user_id in JS
new_content = new_content.replace('user_id: user.id', "user_id: (JSON.parse(localStorage.getItem('siac_user') || '{}')).id || 1")

with open(r'c:\SIAC\templates\empresa_matrices.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("empresa_matrices.html rebuilt successfully!")
