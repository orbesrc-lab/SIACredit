import re

with open('c:/SIAC/templates/formacion.html', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('id="unitEvaluationModal"')
start = content.rfind('<div', 0, start)
end = content.find('</div>\n    </div>', start) + 16

print(content[start:end])
