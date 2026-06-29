import codecs

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

# 1. Insert Sub-Tab Button
target_btn = r'<button class="sub-tab-btn" id="subTabBtnGradebook" onclick="switchSubTab(\'gradebook\')">💯 Libro de Calificaciones</button>'
replacement_btn = target_btn + '\n                        <button class="sub-tab-btn" id="subTabBtnLibrary" onclick="switchSubTab(\'library\')">🌍 Biblioteca Libre (APA 7)</button>'
content = content.replace(target_btn, replacement_btn)

# 2. Insert Sub-Tab Content after subTabGradebook
target_content_end = r"""                            </table>
                        </div>
                    </div>"""
replacement_content_end = target_content_end + """
                    <!-- SUB-TAB: BIBLIOTECA ABIERTA -->
                    <div id="subTabLibrary" class="sub-tab-content" style="display: none;">
                        <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(16, 185, 129, 0.05)); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 16px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); backdrop-filter: blur(10px);">
                            <h3 style="margin-top: 0; color: #1e293b; display: flex; justify-content: space-between; align-items: center; font-size: 1.15rem;">
                                <span><i class="fas fa-search" style="color: #6366f1; margin-right: 8px;"></i> Repositorio Libre OpenAlex</span>
                                <button class="btn-ghost" onclick="toggleSavedResources()" style="color: #6366f1; border: 1px solid #c7d2fe; padding: 6px 12px; border-radius: 8px; background: white; transition: all 0.3s; box-shadow: 0 2px 4px rgba(0,0,0,0.02); font-weight: 600;">⭐ Mis Favoritos</button>
                            </h3>
                            <p style="font-size: 0.9rem; color: #475569; margin-bottom: 15px;">Encuentra y guarda referencias de acceso abierto para tus cursos. Generamos la cita APA automáticamente.</p>
                            <div style="display: flex; gap: 10px;">
                                <input type="text" id="openLibrarySearchQuery" placeholder="Ej: Calidad Educativa, Machine Learning, etc." style="flex: 1; padding: 12px 18px; border-radius: 12px; border: 1px solid #cbd5e1; font-size: 0.95rem; outline: none; transition: border-color 0.3s;" onfocus="this.style.borderColor='#6366f1'" onblur="this.style.borderColor='#cbd5e1'">
                                <button class="btn-primary" onclick="searchOpenLibrary()" style="padding: 0 30px; border-radius: 12px; font-size: 1rem; background: linear-gradient(135deg, #6366f1, #4f46e5); border: none; box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3); transition: transform 0.2s;"><i class="fas fa-search"></i> Buscar</button>
                            </div>
                        </div>

                        <!-- Resultados de búsqueda -->
                        <div id="openLibraryResults" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;">
                            <!-- Se llenará vía JS -->
                        </div>

                        <!-- Favoritos Guardados -->
                        <div id="savedResourcesContainer" style="display: none;">
                            <h3 style="margin-top: 0; color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;"><i class="fas fa-star" style="color: #f59e0b; margin-right: 5px;"></i> Mis Recursos Guardados</h3>
                            <div id="savedResourcesGrid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; margin-top: 20px;">
                                <!-- Se llenará vía JS -->
                            </div>
                        </div>
                    </div>
"""
content = content.replace(target_content_end, replacement_content_end)

# 3. Add to switchSubTab
target_js_tab = r"""            } else if (subTabId === 'forum_teacher') {
                document.getElementById('subTabBtnForumTeacher').classList.add('active');
                document.getElementById('subTabForumTeacher').style.display = 'block';
            }"""
replacement_js_tab = target_js_tab + r""" else if (subTabId === 'library') {
                document.getElementById('subTabBtnLibrary').classList.add('active');
                document.getElementById('subTabLibrary').style.display = 'block';
            }"""
content = content.replace(target_js_tab, replacement_js_tab)

# 4. Insert JS functions before </body>
target_js_funcs = r"</body>"
replacement_js_funcs = """
    <script>
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
            resultsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;"><i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: #6366f1; margin-bottom: 15px;"></i><br>Buscando en OpenAlex...</div>';
            
            try {
                // Buscamos cualquier recurso Open Access
                const url = `https://api.openalex.org/works?search=${encodeURIComponent(query)}&filter=is_oa:true&per-page=20`;
                const response = await fetch(url);
                const data = await response.json();
                
                if(!data.results || data.results.length === 0) {
                    resultsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">No se encontraron resultados de acceso abierto. Intenta usar otros términos.</div>';
                    return;
                }
                
                resultsDiv.innerHTML = '';
                data.results.forEach(work => {
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
                    
                    // APA 7
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
                    card.style.cssText = 'background: white; border: 1px solid rgba(99,102,241,0.15); border-radius: 16px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s, box-shadow 0.2s;';
                    card.onmouseover = () => { card.style.transform = 'translateY(-4px)'; card.style.boxShadow = '0 10px 15px -3px rgba(0,0,0,0.1)'; };
                    card.onmouseout = () => { card.style.transform = 'translateY(0)'; card.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.05)'; };
                    
                    const safeTitle = title.replace(/`/g, "'").replace(/'/g, "\\\\'");
                    const safeAuthors = authorsStr.replace(/`/g, "'").replace(/'/g, "\\\\'");
                    const safeApa = apaCitation.replace(/`/g, "'").replace(/'/g, "\\\\'").replace(/<[^>]*>?/gm, '');

                    card.innerHTML = `
                        <div>
                            <span style="background: rgba(99,102,241,0.1); color: #4338ca; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-block; margin-bottom: 10px;">
                                ${work.type === 'article' ? '📄 Artículo' : (work.type === 'book' ? '📘 Libro' : '📝 Documento')}
                            </span>
                            <h4 style="margin: 0 0 10px 0; font-size: 1.05rem; color: #0f172a; line-height: 1.3;">${title}</h4>
                            <p style="margin: 0 0 5px 0; font-size: 0.85rem; color: #64748b;"><i class="fas fa-users" style="margin-right:4px;"></i> ${authorsStr}</p>
                            <p style="margin: 0 0 15px 0; font-size: 0.85rem; color: #64748b;"><i class="fas fa-book-open" style="margin-right:4px;"></i> ${source} (${year})</p>
                            <div style="background: rgba(241,245,249,0.5); border-left: 3px solid #6366f1; padding: 10px; border-radius: 4px; font-size: 0.8rem; color: #475569; margin-bottom: 15px; word-break: break-word;">
                                <strong>APA 7.0:</strong><br> ${apaCitation}
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            ${pdfUrl ? `<button class="btn-primary" onclick="window.open('${pdfUrl}', '_blank')" style="flex: 1; padding: 8px; font-size: 0.85rem; background: #10b981; border: none; box-shadow: 0 2px 4px rgba(16,185,129,0.3);"><i class="fas fa-external-link-alt"></i> Leer/PDF</button>` : `<button class="btn-primary" onclick="window.open('https://doi.org/${doi}', '_blank')" style="flex: 1; padding: 8px; font-size: 0.85rem; background: #64748b; border: none;"><i class="fas fa-link"></i> Ver Fuente</button>`}
                            <button class="btn-secondary" onclick="saveResource('${work.id}', '${safeTitle}', '${safeAuthors}', ${year}, '${pdfUrl || doi}', '${safeApa}')" style="flex: 1; padding: 8px; font-size: 0.85rem; border: 1px solid #cbd5e1; background: white;"><i class="far fa-star"></i> Guardar</button>
                        </div>
                    `;
                    resultsDiv.appendChild(card);
                });
            } catch (err) {
                console.error("OpenAlex Error:", err);
                resultsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ef4444;"><i class="fas fa-exclamation-triangle" style="font-size:2rem; margin-bottom:10px;"></i><br>Error al buscar recursos. Intente nuevamente.</div>';
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
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px;"><i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: #6366f1; margin-bottom: 15px;"></i><br>Cargando tus recursos...</div>';
            try {
                const res = await fetch(`/api/library/saved?email=${encodeURIComponent(user.email)}`);
                const data = await res.json();
                if(data.length === 0) {
                    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">No tienes recursos guardados aún.</div>';
                    return;
                }
                grid.innerHTML = '';
                data.forEach(item => {
                    const card = document.createElement('div');
                    card.style.cssText = 'background: white; border: 1px solid rgba(245,158,11,0.2); border-radius: 16px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: space-between;';
                    card.innerHTML = `
                        <div>
                            <h4 style="margin: 0 0 10px 0; font-size: 1.05rem; color: #0f172a;">${item.title}</h4>
                            <p style="margin: 0 0 5px 0; font-size: 0.85rem; color: #64748b;"><strong>Autores:</strong> ${item.authors}</p>
                            <p style="margin: 0 0 15px 0; font-size: 0.85rem; color: #64748b;"><strong>Año:</strong> ${item.year}</p>
                            <div style="background: rgba(241,245,249,0.5); border-left: 3px solid #f59e0b; padding: 10px; border-radius: 4px; font-size: 0.8rem; color: #475569; margin-bottom: 15px; word-break: break-word;">
                                <strong>APA 7.0:</strong><br> ${item.apa_citation}
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            ${item.url ? `<button class="btn-primary" onclick="window.open('${item.url}', '_blank')" style="flex: 1; padding: 8px; font-size: 0.85rem; background: #10b981; border: none; box-shadow: 0 2px 4px rgba(16,185,129,0.3);"><i class="fas fa-external-link-alt"></i> Ir al Enlace</button>` : ''}
                            <button class="btn-secondary" onclick="deleteSavedResource(${item.id})" style="flex: 0 0 auto; padding: 8px 12px; font-size: 0.85rem; background: #fee2e2; color: #ef4444; border: none; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'"><i class="fas fa-trash-alt"></i></button>
                        </div>
                    `;
                    grid.appendChild(card);
                });
            } catch(e) {
                grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ef4444;"><i class="fas fa-exclamation-triangle"></i> Error al cargar.</div>';
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
content = content.replace(target_js_funcs, replacement_js_funcs)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)
print("Updated subtabs and javascript for better aesthetics and correct search!")
