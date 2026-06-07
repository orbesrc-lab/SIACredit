with open('c:/SIAC/templates/formacion.html', 'r', encoding='utf-8') as f:
    content = f.read()

start1 = content.find('id="unitEvaluationModal"')
if start1 != -1:
    print("unitEvaluationModal context:")
    print(content[start1+1700:start1+2200])

print("-" * 40)
start2 = content.find('id="quizModal"')
if start2 != -1:
    print("quizModal context:")
    print(content[start2+1500:start2+2000])
