with open('c:/SIAC/templates/formacion.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'promptInsertPodcast' in l:
        print(i+1, repr(l.rstrip()))
