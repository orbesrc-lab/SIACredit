with open(r'c:\SIAC\templates\formacion.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = """            // Verificar rol de usuario
            if (user && user.role === 'estudiante') {
                // Ocultar la barra lateral por completo para no ver el resto de la aplicación
                const sidebarEl = document.querySelector('.sidebar');
                if (sidebarEl) sidebarEl.style.display = 'none';
                
                // Forzar scroll global de la página para que el contenido NUNCA se corte
                const scrollFix = document.createElement('style');
                scrollFix.innerHTML = `
                    html, body { 
                        display: block !important; 
                        height: auto !important; 
                        min-height: 100vh !important; 
                        overflow: auto !important; 
                        position: static !important;
                    }
                    .main-content { 
                        display: block !important; 
                        height: auto !important; 
                        overflow: visible !important; 
                        padding-bottom: 80px !important;
                    }
                    .content-area { 
                        display: block !important; 
                        height: auto !important; 
                        overflow: visible !important; 
                        max-width: 1000px !important; 
                        margin: 0 auto !important;
                    }
                    /* Ocultar posibles modales buggeados que bloquean clicks */
                    .modal-backdrop { display: none !important; }
                `;
                document.head.appendChild(scrollFix);
            }"""

replacement = """            // Adaptar interfaz para estudiante/profesor
            if (user && (user.role === 'estudiante' || user.role === 'profesor')) {
                // Renombrar "Capacitación" a "Mis Cursos" en el menú
                document.querySelectorAll('.sidebar-item').forEach(item => {
                    if (item.textContent.toLowerCase().includes('capacitaci')) {
                        item.innerHTML = '🎓 Mis Cursos';
                    }
                });
            }"""

if target in content:
    print("Found exact block, replacing...")
    new_content = content.replace(target, replacement)
    with open(r'c:\SIAC\templates\formacion.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
else:
    print("Exact block NOT FOUND. Trying with regex or normalized whitespace...")
    import re
    # Remove all whitespace for comparison
    def norm(s): return re.sub(r'\s+', '', s)
    norm_target = norm(target)
    
    # Simple search
    # Find start and end indices of the block
    # Actually, let's just find the start of the block
    start_str = "// Verificar rol de usuario"
    if start_str in content:
        start_idx = content.find(start_str)
        end_str = "document.head.appendChild(scrollFix);\n            }"
        if end_str in content[start_idx:]:
            end_idx = content.find(end_str, start_idx) + len(end_str)
            print("Found block via boundaries!")
            new_content = content[:start_idx] + replacement + content[end_idx:]
            with open(r'c:\SIAC\templates\formacion.html', 'w', encoding='utf-8') as f:
                f.write(new_content)
        else:
            print("End string not found!")
    else:
        print("Start string not found!")

