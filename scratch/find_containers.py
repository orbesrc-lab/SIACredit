with open('c:/SIAC/scratch/containers_out.txt', 'w', encoding='utf-8') as out:
    with open('c:/SIAC/templates/formacion.html', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if 'id="' in line and ('view' in line.lower() or 'modal' in line.lower() or 'tab' in line.lower()):
                out.write(f"{i+1}: {line.strip()[:100]}\n")
