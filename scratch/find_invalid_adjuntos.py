with open('c:/SIAC/templates/evidencias.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'adjunto: tr.dataset.adjunto' in line:
        # Check context
        context = []
        for j in range(max(0, i-5), min(len(lines), i+6)):
            context.append(f"{j+1}: {lines[j].strip().encode('ascii', 'ignore').decode('ascii')}")
        print(f"--- Context for line {i+1} ---")
        print("\n".join(context))
        print()
