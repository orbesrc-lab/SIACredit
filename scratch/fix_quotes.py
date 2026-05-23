import re

with open('templates/evidencias.html', 'r', encoding='utf-8') as f:
    text = f.read()

def replace_quotes(match):
    prefix = match.group(1)
    inner_html_content = match.group(2)
    suffix = match.group(3)
    
    # Escape quotes inside the innerHTML string
    fixed_inner = inner_html_content.replace('"', '&quot;')
    return prefix + fixed_inner + suffix

pattern = r'(onclick="this\.closest\(\'tr\'\)\.dataset\.adjunto=\'\'; this\.parentElement\.innerHTML=\')(.*?)(\'">)'
text = re.sub(pattern, replace_quotes, text, flags=re.DOTALL)

with open('templates/evidencias.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed quotes in evidencias.html")
