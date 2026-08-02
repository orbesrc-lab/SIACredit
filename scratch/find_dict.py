import docx

doc = docx.Document('c:/SIAC/SKEL Human Capital 360.docx')
found = False
count = 0
for p in doc.paragraphs:
    text = p.text.strip()
    if 'diccionario' in text.lower():
        found = True
    
    if found and text:
        print(text)
        count += 1
        if count > 30:
            break
