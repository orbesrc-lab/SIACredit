import codecs

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

# 1. Insert Global Nav and mainLmsContainer
target1 = r"<!-- Tab Navigation (Solo Admin) -->"
replacement1 = """
            <!-- GLOBAL TAB NAV FOR OPEN LIBRARY -->
            <div class="tab-nav" id="globalTabNav" style="background: rgba(16, 185, 129, 0.08); border-color: rgba(16, 185, 129, 0.2); display: flex; gap: 10px; margin-bottom: 20px;">
                <button class="tab-btn active" id="tabGlobalMain" onclick="switchGlobalTab('main')">🏫 Aula de Formación</button>
                <button class="tab-btn" id="tabGlobalLib" onclick="switchGlobalTab('lib')">🌍 Biblioteca Abierta y APA 7</button>
            </div>

            <div id="mainLmsContainer" style="display: flex; flex-direction: column; flex: 1; min-height: 0; overflow-y: auto;">
            <!-- Tab Navigation (Solo Admin) -->
"""
content = content.replace(target1, replacement1)

# 2. Close mainLmsContainer and add openLibraryContainer before END settings-card
target2 = r"</div> <!-- END settings-card -->"
replacement2 = """
            </div> <!-- END mainLmsContainer -->

            <!-- OPEN LIBRARY CONTAINER -->
            <div id="openLibraryContainer" style="display: none; flex: 1; flex-direction: column; overflow-y: auto;">
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 25px; margin-bottom: 25px; flex-shrink: 0;">
                    <h3 style="margin-top: 0; color: #334155; display: flex; justify-content: space-between; align-items: center;">
                        <span>🔍 Búsqueda en Repositorios Libres (OpenAlex)</span>
                        <button class="btn-ghost" onclick="toggleSavedResources()" style="color: #6366f1; border: 1px solid #c7d2fe; padding: 6px 12px; border-radius: 8px;">⭐ Mis Favoritos</button>
                    </h3>
                    <div style="display: flex; gap: 10px;">
                        <input type="text" id="openLibrarySearchQuery" placeholder="Ej: 'Machine Learning Education' o 'Física Cuántica'" style="flex: 1; padding: 12px 18px; border-radius: 12px; border: 1px solid #cbd5e1; font-size: 1rem;">
                        <button class="btn-primary" onclick="searchOpenLibrary()" style="padding: 0 30px; border-radius: 12px; font-size: 1.05rem;">Buscar</button>
                    </div>
                </div>

                <!-- Resultados de búsqueda -->
                <div id="openLibraryResults" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px;">
                    <!-- Se llenará vía JS -->
                </div>

                <!-- Favoritos Guardados -->
                <div id="savedResourcesContainer" style="display: none;">
                    <h3 style="margin-top: 0; color: #334155; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">⭐ Mis Recursos Guardados</h3>
                    <div id="savedResourcesGrid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; margin-top: 20px;">
                        <!-- Se llenará vía JS -->
                    </div>
                </div>
            </div>

            </div> <!-- END settings-card -->
"""
content = content.replace(target2, replacement2)

# 3. Add Script for OpenAlex and APA before </body>
target3 = r"</body>"
replacement3 = """
    <script>
        function switchGlobalTab(tab) {
            document.getElementById('tabGlobalMain').classList.remove('active');
            document.getElementById('tabGlobalLib').classList.remove('active');
            
            if(tab === 'main') {
                document.getElementById('tabGlobalMain').classList.add('active');
                document.getElementById('mainLmsContainer').style.display = 'flex';
                document.getElementById('openLibraryContainer').style.display = 'none';
            } else {
                document.getElementById('tabGlobalLib').classList.add('active');
                document.getElementById('mainLmsContainer').style.display = 'none';
                document.getElementById('openLibraryContainer').style.display = 'flex';
                document.getElementById('openLibraryResults').style.display = 'grid';
                document.getElementById('savedResourcesContainer').style.display = 'none';
            }
        }

        function toggleSavedResources() {
            const resultsDiv = document.getElementById('openLibraryResults');
            const savedDiv = document.getElementById('savedResourcesContainer');
            if(savedDiv.style.display === 'none') {
                resultsDiv.style.display = 'none';
                savedDiv.style.display = 'block';
                loadSavedResources();
            } else {
                resultsDiv.style.display = 'grid';
                savedDiv.style.display = 'none';
            }
        }

        async function searchOpenLibrary() {
            const query = document.getElementById('openLibrarySearchQuery').value.trim();
            if(!query) return;
            
            const resultsDiv = document.getElementById('openLibraryResults');
            resultsDiv.style.display = 'grid';
            document.getElementById('savedResourcesContainer').style.display = 'none';
            resultsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">⏳ Buscando en millones de artículos (OpenAlex)...</div>';
            
            try {
                // OpenAlex API: Has OA Hosted URL (to ensure PDF is available)
                const url = `https://api.openalex.org/works?search=${encodeURIComponent(query)}&filter=has_oa_hosted_url:true&per-page=20`;
                const response = await fetch(url);
                const data = await response.json();
                
                if(!data.results || data.results.length === 0) {
                    resultsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">No se encontraron resultados de acceso abierto.</div>';
                    return;
                }
                
                resultsDiv.innerHTML = '';
                data.results.forEach(work => {
                    // Extract data
                    const title = work.title || 'Sin título';
                    const year = work.publication_year || 'S.F.';
                    let authorsStr = '';
                    if(work.authorships && work.authorships.length > 0) {
                        authorsStr = work.authorships.map(a => a.author.display_name).slice(0, 3).join(', ');
                        if(work.authorships.length > 3) authorsStr += ' et al.';
                    } else {
                        authorsStr = 'Autor desconocido';
                    }
                    
                    const source = (work.primary_location && work.primary_location.source && work.primary_location.source.display_name) ? work.primary_location.source.display_name : 'Publicación Independiente';
                    const doi = work.doi || '';
                    const pdfUrl = (work.open_access && work.open_access.oa_url) ? work.open_access.oa_url : '';
                    
                    // APA 7 Citation Generator
                    let apaCitation = '';
                    if(work.authorships && work.authorships.length > 0) {
                        const firstAuthor = work.authorships[0].author.display_name.split(' ');
                        const lastName = firstAuthor[firstAuthor.length-1];
                        const initials = firstAuthor.slice(0, firstAuthor.length-1).map(n => n.charAt(0)+'.').join(' ');
                        apaCitation = `${lastName}, ${initials} (${year}). <i>${title}</i>. ${source}. ${doi}`;
                    } else {
                        apaCitation = `${title}. (${year}). ${source}. ${doi}`;
                    }

                    const card = document.createElement('div');
                    card.style.cssText = 'background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s;';
                    card.onmouseover = () => card.style.transform = 'translateY(-4px)';
                    card.onmouseout = () => card.style.transform = 'translateY(0)';
                    
                    card.innerHTML = `
                        <div>
                            <span style="background: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-block; margin-bottom: 10px;">${work.type === 'article' ? '📄 Artículo' : (work.type === 'book' ? '📘 Libro' : '📝 Documento')}</span>
                            <h4 style="margin: 0 0 10px 0; font-size: 1.1rem; color: #0f172a; line-height: 1.3;">${title}</h4>
                            <p style="margin: 0 0 5px 0; font-size: 0.85rem; color: #64748b;"><strong>Autores:</strong> ${authorsStr}</p>
                            <p style="margin: 0 0 15px 0; font-size: 0.85rem; color: #64748b;"><strong>Publicación:</strong> ${source} (${year})</p>
                            <div style="background: #f8fafc; border-left: 3px solid #6366f1; padding: 10px; border-radius: 4px; font-size: 0.8rem; color: #475569; margin-bottom: 15px; word-break: break-word;">
                                <strong>APA 7.0:</strong><br> ${apaCitation}
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            ${pdfUrl ? `<button class="btn-primary" onclick="window.open('${pdfUrl}', '_blank')" style="flex: 1; padding: 8px; font-size: 0.85rem; background: #10b981; border: none;">⬇️ Leer/PDF</button>` : ''}
                            <button class="btn-secondary" onclick="saveResource('${work.id}', \`${title.replace(/`/g, "'")}\`, \`${authorsStr.replace(/`/g, "'")}\`, ${year}, '${pdfUrl || doi}', \`${apaCitation.replace(/`/g, "'").replace(/<[^>]*>?/gm, '')}\`)" style="flex: 1; padding: 8px; font-size: 0.85rem;">⭐ Guardar</button>
                        </div>
                    `;
                    resultsDiv.appendChild(card);
                });
            } catch (err) {
                console.error("OpenAlex Error:", err);
                resultsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ef4444;">Error al buscar recursos. Intente nuevamente.</div>';
            }
        }

        async function saveResource(resource_id, title, authors, year, url, apa_citation) {
            const user_email = user.email;
            if(!user_email) {
                alert("Debes iniciar sesión para guardar recursos.");
                return;
            }
            try {
                const res = await fetch('/api/library/saved', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        email: user_email,
                        resource_id: resource_id,
                        title: title,
                        authors: authors,
                        year: year,
                        url: url,
                        apa_citation: apa_citation
                    })
                });
                const data = await res.json();
                if(data.status === 'success') {
                    alert('✅ Recurso guardado en tus favoritos!');
                } else {
                    alert('Error al guardar: ' + data.message);
                }
            } catch(e) {
                alert('Error de conexión.');
            }
        }

        async function loadSavedResources() {
            const grid = document.getElementById('savedResourcesGrid');
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 20px;">Cargando tus recursos...</div>';
            try {
                const res = await fetch(`/api/library/saved?email=${encodeURIComponent(user.email)}`);
                const data = await res.json();
                if(data.length === 0) {
                    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 20px; color: #64748b;">No tienes recursos guardados aún.</div>';
                    return;
                }
                grid.innerHTML = '';
                data.forEach(item => {
                    const card = document.createElement('div');
                    card.style.cssText = 'background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: space-between;';
                    card.innerHTML = `
                        <div>
                            <h4 style="margin: 0 0 10px 0; font-size: 1.1rem; color: #0f172a;">${item.title}</h4>
                            <p style="margin: 0 0 5px 0; font-size: 0.85rem; color: #64748b;"><strong>Autores:</strong> ${item.authors}</p>
                            <p style="margin: 0 0 15px 0; font-size: 0.85rem; color: #64748b;"><strong>Año:</strong> ${item.year}</p>
                            <div style="background: #f8fafc; border-left: 3px solid #6366f1; padding: 10px; border-radius: 4px; font-size: 0.8rem; color: #475569; margin-bottom: 15px; word-break: break-word;">
                                <strong>APA 7.0:</strong><br> ${item.apa_citation}
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            ${item.url ? `<button class="btn-primary" onclick="window.open('${item.url}', '_blank')" style="flex: 1; padding: 8px; font-size: 0.85rem; background: #10b981; border: none;">Ir al Enlace</button>` : ''}
                            <button class="btn-secondary" onclick="deleteSavedResource(${item.id})" style="flex: 0 0 auto; padding: 8px 12px; font-size: 0.85rem; background: #fee2e2; color: #ef4444; border: none;">🗑️</button>
                        </div>
                    `;
                    grid.appendChild(card);
                });
            } catch(e) {
                grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 20px; color: #ef4444;">Error al cargar.</div>';
            }
        }

        async function deleteSavedResource(id) {
            if(!confirm("¿Seguro que deseas eliminar este recurso de tus favoritos?")) return;
            try {
                const res = await fetch(`/api/library/saved/${id}`, { method: 'DELETE' });
                const data = await res.json();
                if(data.status === 'success') {
                    loadSavedResources();
                } else {
                    alert('Error: ' + data.message);
                }
            } catch(e) {
                alert('Error de red');
            }
        }
    </script>
</body>
"""
content = content.replace(target3, replacement3)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)
print("formacion.html updated successfully!")
