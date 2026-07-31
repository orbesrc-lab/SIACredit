import re

with open(r'c:\SIAC\templates\formacion.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'// Verificar rol de usuario\s*if\s*\(user\s*&&\s*user\.role\s*===\s*\'estudiante\'\)\s*\{[\s\S]*?document\.head\.appendChild\(scrollFix\);\s*\}'

match = re.search(pattern, content)
if match:
    print('Found the block!')
    new_content = content.replace(match.group(0), '''// Adaptar interfaz para estudiante/profesor
    if (user && (user.role === 'estudiante' || user.role === 'profesor')) {
        // Renombrar "Capacitación" a "Mis Cursos" en el menú
        document.querySelectorAll('.sidebar-item').forEach(item => {
            if (item.textContent.toLowerCase().includes('capacitaci')) {
                item.innerHTML = '🎓 Mis Cursos';
            }
        });
    }''')
    
    with open(r'c:\SIAC\templates\formacion.html', 'w', encoding='utf-8') as out:
        out.write(new_content)
else:
    print('Block not found!')
