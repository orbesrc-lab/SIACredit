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
            }

            // Rediseñar Topbar de forma premium para el estudiante con su información y botón de cerrar sesión
            const topbarEl = document.querySelector('.topbar');
            if (topbarEl) {
                topbarEl.style.background = 'var(--white)';
                topbarEl.style.borderBottom = '1px solid var(--border-color)';
                topbarEl.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <img src="/static/logo_skel.png" alt="SKEL" style="height: 40px; max-width: 120px; object-fit: contain;">
                        <div style="height: 24px; width: 1px; background: var(--border-color);"></div>
                        <h2 style="font-size: 1.15rem; font-weight: 700; color: var(--primary-color); margin: 0; display: flex; align-items: center; gap: 8px;">
                            🎓 Aula Virtual de Aprendizaje
                        </h2>
                    </div>
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <div style="display: flex; flex-direction: column; align-items: flex-end; line-height: 1.3;">
                            <span style="font-weight: 700; font-size: 0.95rem; color: var(--text-main);" id="studentHeaderName">Cargando...</span>
                            <span style="font-size: 0.78rem; color: var(--text-muted);">${escapeHtml(user.email)}</span>
                        </div>
                        <div style="height: 24px; width: 1px; background: var(--border-color);"></div>
                        <button onclick="logout()" class="btn-secondary" style="padding: 8px 16px; font-size: 0.85rem; font-weight: 600; border: 1.5px solid #ef4444; color: #ef4444; background: transparent; display: flex; align-items: center; gap: 6px; border-radius: var(--radius-md); cursor: pointer; transition: all 0.2s;">
                            🚪 Cerrar Sesión
                        </button>
                    </div>
                `;
            }"""

replacement = """            // Verificar rol de usuario
            if (user && (user.role === 'estudiante' || user.role === 'profesor')) {
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
                    .dashboard-container {
                        overflow: auto !important;
                        height: auto !important;
                        display: block !important;
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

                // Insertar Topbar de forma premium para el estudiante ya que no hay sidebar
                const mainContentEl = document.querySelector('.main-content');
                if (mainContentEl) {
                    const topbarDiv = document.createElement('div');
                    topbarDiv.style.background = 'var(--white)';
                    topbarDiv.style.borderBottom = '1px solid var(--border-color)';
                    topbarDiv.style.padding = '15px 35px';
                    topbarDiv.style.display = 'flex';
                    topbarDiv.style.justifyContent = 'space-between';
                    topbarDiv.style.alignItems = 'center';
                    topbarDiv.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <img src="/static/logo_skel.png" alt="SKEL" style="height: 40px; max-width: 120px; object-fit: contain;">
                            <div style="height: 24px; width: 1px; background: var(--border-color);"></div>
                            <h2 style="font-size: 1.15rem; font-weight: 700; color: var(--primary-color); margin: 0; display: flex; align-items: center; gap: 8px;">
                                🎓 Aula Virtual de Aprendizaje
                            </h2>
                        </div>
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <div style="display: flex; flex-direction: column; align-items: flex-end; line-height: 1.3;">
                                <span style="font-weight: 700; font-size: 0.95rem; color: var(--text-main);" id="studentHeaderName">Estudiante/Profesor</span>
                                <span style="font-size: 0.78rem; color: var(--text-muted);">${escapeHtml(user.email)}</span>
                            </div>
                            <div style="height: 24px; width: 1px; background: var(--border-color);"></div>
                            <button onclick="logout()" class="btn-secondary" style="padding: 8px 16px; font-size: 0.85rem; font-weight: 600; border: 1.5px solid #ef4444; color: #ef4444; background: transparent; display: flex; align-items: center; gap: 6px; border-radius: 12px; cursor: pointer; transition: all 0.2s;">
                                🚪 Cerrar Sesión
                            </button>
                        </div>
                    `;
                    mainContentEl.insertBefore(topbarDiv, mainContentEl.firstChild);
                }
            }"""

if target in content:
    print("Found block!")
    new_content = content.replace(target, replacement)
    with open(r'c:\SIAC\templates\formacion.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
else:
    print("Block not found!")
