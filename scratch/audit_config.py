with open(r'c:\SIAC\templates\configuracion.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all places that mention aiApiKeyInput and functions that use it
idx = content.find('aiApiKeyInput')
while idx != -1:
    print(f"Position {idx}:", content[idx:idx+100])
    idx = content.find('aiApiKeyInput', idx+1)

# Find save functions
for keyword in ['guardarConfigGlobal', 'saveGlobal', 'guardarConfig', 'global-settings', '/api/global']:
    idx = content.find(keyword)
    if idx != -1:
        print(f"\n--- Found '{keyword}' at {idx} ---")
        print(content[idx:idx+400])
