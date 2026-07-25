import re

filepath = 'c:/SIAC/templates/evidencias.html'
with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Precise pattern that only matches the invalid adjunto inside the fetch options object
pattern = r'body:\s*JSON\.stringify\(payload\),\s*adjunto:\s*tr\.dataset\.adjunto\s*\|\|\s*\'\''

matches = list(re.finditer(pattern, content))
print(f"Found {len(matches)} matches in evidencias.html")

new_content = re.sub(pattern, 'body: JSON.stringify(payload)', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replacement complete.")
