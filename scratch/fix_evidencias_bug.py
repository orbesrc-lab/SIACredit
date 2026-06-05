import re

filepath = 'c:/SIAC/templates/evidencias.html'
with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Pattern to match the comma, spacing, and the invalid adjunto expression
# e.g., ", adjunto: tr.dataset.adjunto || ''" or ",\n                    adjunto: tr.dataset.adjunto || ''"
pattern = r',\s*adjunto:\s*tr\.dataset\.adjunto\s*\|\|\s*\'\''

# Let's find matches first
matches = list(re.finditer(pattern, content))
print(f"Found {len(matches)} matches in evidencias.html")

new_content = re.sub(pattern, '', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replacement complete.")
