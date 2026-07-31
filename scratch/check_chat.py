with open(r'c:\SIAC\scratch\script0.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'sendChatMessage' in line:
        print(f'Line {i+1}: {line.strip()}')
