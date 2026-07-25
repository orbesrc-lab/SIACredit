import re

file_path = r'c:\SIAC\templates\formacion.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('program_id=0${getProgramId()}', 'program_id=0')
content = content.replace('program_id=00', 'program_id=0')
content = content.replace('&program_id=0\' + getProgramId()', '&program_id=0\'')
content = content.replace('program_id=0\' + getProgramId()', 'program_id=0\'')
content = content.replace('&program_id=0\" + getProgramId()', '&program_id=0\"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fix completed.")
