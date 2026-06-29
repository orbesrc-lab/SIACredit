with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Check modal exists
if 'id="takeQuizModal"' in html:
    print('takeQuizModal exists')
else:
    print('MISSING: takeQuizModal')

# Check onclick usage
import re
matches = re.findall(r'onclick="takeQuiz\([^"]*\)"', html)
print(f'takeQuiz onclick count: {len(matches)}')
for m in matches:
    print(' ', m[:100])

# Check for any remaining presentQuiz references
pq = re.findall(r'onclick="presentQuiz\([^"]*\)"', html)
print(f'Remaining presentQuiz onclick: {len(pq)}')
for m in pq:
    print(' ', m[:100])
