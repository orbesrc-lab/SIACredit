with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Find the function containing line 924 (const html = `)
# Look backwards from line 924 to find the function name
for i in range(923, max(0, 880), -1):
    if 'function ' in lines[i] or 'async function ' in lines[i]:
        print(f'Function at line {i+1}: {repr(lines[i][:100])}')
        break

# Show lines 924 to 940
print('\nLines 920-940:')
for i in range(919, 940):
    print(f'{i+1}: {repr(lines[i][:120])}')

print('\n--- imprimirPESTA context around line 1742 ---')
for i in range(1720, 1760):
    print(f'{i+1}: {repr(lines[i][:120])}')
