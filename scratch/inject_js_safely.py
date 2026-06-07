import os
import ast

with open('c:/SIAC/templates/formacion.html', 'r', encoding='utf-8') as f:
    content = f.read()

with open('c:/SIAC/scratch/apply_quizzes.py', 'r', encoding='utf-8') as f:
    apply_code = f.read()

module = ast.parse(apply_code)
js_injection = ""
for node in module.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if getattr(target, 'id', None) == 'js_injection':
                js_injection = node.value.value

if not js_injection:
    print("Could not find js_injection in apply_quizzes.py")
    exit(1)

if 'window.presentQuiz =' in content:
    print("JS already injected!")
    exit(0)

parts = content.rsplit('</script>', 1)
if len(parts) == 2:
    new_content = parts[0] + "\n" + js_injection + "\n</script>" + parts[1]
    with open('c:/SIAC/templates/formacion.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully injected JS before </script>")
else:
    print("Could not find </script>")
