
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
            const limit = document.getElementById('openLibraryLimit').value;
            if(!query) return;
            
            const resultsDiv = document.getElementById('openLibraryResults');
            resultsDiv.style.display = 'grid';
            document.getElementById('savedResourcesContainer').style.display = 'none';
            resultsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;"><i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: #6366f1; margin-bottom: 15px;"></i><br>Buscando en la red académica global...</div>';
            
            try {
                const url = `/api/library/search?q=${encodeURIComponent(query)}&limit=${limit}`;
                const response = await fetch(url);
                const data = await response.json();
                if (data.error) throw new Error(data.error);
                
                if(!data.results || data.results.length === 0) {
                    resultsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">No se encontraron resultados de acceso abierto. Intenta usar otros términos.</div>';
                    return;
                }
                
                resultsDiv.innerHTML = '';
                data.results.forEach(work => {
                    const title = work.title || 'Sin título';
                    const year = work.publication_year || 'S.F.';
                    
                    let validAuthors = [];
                    if(work.authorships && work.authorships.length > 0) {
                        validAuthors = work.authorships.filter(a => a.author && a.author.display_name).map(a => a.author.display_name);
                    }
                    
                    let authorsStr = validAuthors.length > 0 ? validAuthors.slice(0, 3).join(', ') : 'Autor desconocido';
                    if(validAuthors.length > 3) authorsStr += ' et al.';
                    
                    const source = (work.primary_location && work.primary_location.source && work.primary_location.source.display_name) ? work.primary_location.source.display_name : 'Publicación Independiente';
                    const doi = work.doi || '';
                    const pdfUrl = (work.open_access && work.open_access.oa_url) ? work.open_access.oa_url : '';
                    
                    // APA 7
                    let apaCitation = '';
                    if(validAuthors.length > 0) {
                        const firstAuthorParts = validAuthors[0].split(' ');
                        const lastName = firstAuthorParts[firstAuthorParts.length-1];
                        const initials = firstAuthorParts.slice(0, firstAuthorParts.length-1).map(n => n.charAt(0)+'.').join(' ');
                        apaCitation = `${lastName}, ${initials} (${year}). <i>${title}</i>. ${source}. ${doi}`;
                    } else {
                        apaCitation = `${title}. (${year}). ${source}. ${doi}`;
                    }

                    const card = document.createElement('div');
                    card.style.cssText = 'background: white; border: 1px solid rgba(99,102,241,0.15); border-radius: 16px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s, box-shadow 0.2s;';
                    card.onmouseover = () => { card.style.transform = 'translateY(-4px)'; card.style.boxShadow = '0 10px 15px -3px rgba(0,0,0,0.1)'; };
                    card.onmouseout = () => { card.style.transform = 'translateY(0)'; card.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.05)'; };
                    
                    const safeTitle = title.replace(/'/g, "&#39;").replace(/"/g, "&quot;");
                    const safeAuthors = authorsStr.replace(/'/g, "&#39;").replace(/"/g, "&quot;");
                    const safeApa = apaCitation.replace(/'/g, "&#39;").replace(/"/g, "&quot;").replace(/<[^>]*>?/gm, '');

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
                            ${pdfUrl ? `<button class="btn-primary" onclick="openPdfViewer('${pdfUrl}', '${safeTitle}', true)" style="flex: 1; padding: 8px; font-size: 0.85rem; background: #10b981; border: none; box-shadow: 0 2px 4px rgba(16,185,129,0.3);"><i class="fas fa-external-link-alt"></i> Leer/PDF</button>` : `<button class="btn-primary" onclick="openPdfViewer('https://doi.org/${doi}', '${safeTitle}', false)" style="flex: 1; padding: 8px; font-size: 0.85rem; background: #64748b; border: none;"><i class="fas fa-link"></i> Ver Fuente</button>`}
                            <button class="btn-secondary" onclick="saveResource('${work.id}', '${safeTitle}', '${safeAuthors}', ${year}, '${pdfUrl || doi}', '${safeApa}')" style="flex: 1; padding: 8px; font-size: 0.85rem; border: 1px solid #cbd5e1; background: white;"><i class="far fa-star"></i> Guardar</button>
                        </div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; justify-content: flex-end;">
                            <button class="btn-ghost" onclick="translateCard(this, 'es')" style="font-size: 0.75rem; padding: 4px 8px; color: #64748b; border: 1px solid #e2e8f0; border-radius: 4px; background: white; transition: all 0.2s;"><i class="fas fa-language"></i> Traducir 🇪🇸</button>
                            <button class="btn-ghost" onclick="translateCard(this, 'en')" style="font-size: 0.75rem; padding: 4px 8px; color: #64748b; border: 1px solid #e2e8f0; border-radius: 4px; background: white; transition: all 0.2s;"><i class="fas fa-language"></i> Traducir 🇬🇧</button>
                        </div>
                    `;
                    resultsDiv.appendChild(card);
                });
            } catch (err) {
                console.error("OpenAlex Error:", err);
                resultsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ef4444;"><i class="fas fa-exclamation-triangle" style="font-size:2rem; margin-bottom:10px;"></i><br>Error al buscar recursos. ' + err.message + '</div>';
            }
        }

        function openExternalRepo(repo) {
            const query = document.getElementById('openLibrarySearchQuery').value.trim() || 'Educación';
            let url = '';
            switch(repo) {
                case 'scielo': url = `https://search.scielo.org/?q=${encodeURIComponent(query)}`; break;
                case 'redalyc': url = `https://www.redalyc.org/busquedaArticuloFiltros.oa?q=${encodeURIComponent(query)}`; break;
                case 'dialnet': url = `https://dialnet.unirioja.es/buscar/documentos?querysDismax.DOCUMENTAL_TODO=${encodeURIComponent(query)}`; break;
                case 'europepmc': url = `https://europepmc.org/search?query=${encodeURIComponent(query)}`; break;
                case 'doaj': url = `https://doaj.org/search/articles?source={"query":{"query_string":{"query":"${encodeURIComponent(query)}"}},"size":50}`; break;
            }
            if(url) openPdfViewer(url);
        }

        async function translateCard(btnElement, targetLang) {
            const cardDiv = btnElement.closest('div').previousElementSibling.previousElementSibling;
            const titleEl = cardDiv.querySelector('h4');
            const apaEl = cardDiv.querySelector('div'); 
            const originalText = titleEl.innerText + "\n\n" + apaEl.innerText;
            
            const originalBtnText = btnElement.innerHTML;
            btnElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i>...';
            btnElement.disabled = true;
            
            try {
                const res = await fetch('/api/library/translate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: originalText, target_lang: targetLang})
                });
                const data = await res.json();
                if(data.status === 'success') {
                    const parts = data.translated.split("\n\n");
                    titleEl.innerText = parts[0] || data.translated;
                    if(parts.length > 1) {
                        apaEl.innerHTML = `<strong>Traducción APA:</strong><br> ${parts.slice(1).join("<br>")}`;
                    }
                } else {
                    alert('Error en traducción: ' + data.message);
                }
            } catch(e) {
                alert('Error de conexión al traducir.');
            } finally {
                btnElement.innerHTML = originalBtnText;
                btnElement.disabled = false;
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
                            ${item.url ? `<button class="btn-primary" onclick="openPdfViewer('${item.url}', '${item.title.replace(/'/g, "&#39;").replace(/"/g, "&quot;")}', false)" style="flex: 1; padding: 8px; font-size: 0.85rem; background: #10b981; border: none; box-shadow: 0 2px 4px rgba(16,185,129,0.3);"><i class="fas fa-external-link-alt"></i> Ir al Enlace</button>` : ''}
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
    
        let currentPdfUrl = '';
        let currentIsPdf = false;
        let useGoogleViewer = false;
        
        function openPdfViewer(url, title = 'Documento de Consulta', isPdf = false) {
            currentPdfUrl = url;
            currentIsPdf = isPdf;
            useGoogleViewer = false; // Por defecto intentamos motor Nativo (Proxy) porque Google Docs bloquea el copiado de texto y rompe el traductor
            
            const definitelyPdf = isPdf || url.toLowerCase().includes('.pdf');
            const isProtected = url.includes('doi.org') || (!definitelyPdf && (url.includes('scielo.org') || url.includes('redalyc.org') || url.includes('dialnet') || url.includes('europepmc') || url.includes('doaj')));
            
            document.getElementById('pdfViewerExternalBtn').onclick = () => window.open(url, '_blank');
            document.getElementById('pdfViewerModal').style.display = 'flex';
            
            let fallbackDiv = document.getElementById('pdfViewerFallback');
            if(!fallbackDiv) {
                fallbackDiv = document.createElement('div');
                fallbackDiv.id = 'pdfViewerFallback';
                fallbackDiv.style.cssText = 'width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #f8fafc; color: #334155; padding: 40px; text-align: center; overflow-y: auto;';
                document.getElementById('pdfViewerIframe').parentNode.appendChild(fallbackDiv);
            }

            if (isProtected) {
                document.getElementById('pdfViewerIframe').style.display = 'none';
                fallbackDiv.style.display = 'flex';
                // Usamos textContent de un div temporal para escapar HTML si es necesario
                const safeTitle = document.createElement('div');
                safeTitle.textContent = title;
                fallbackDiv.innerHTML = `
                    <i class="fas fa-shield-alt" style="font-size: 4rem; color: #cbd5e1; margin-bottom: 20px;"></i>
                    <h2 style="margin-bottom: 15px; color: #0f172a;">Documento Protegido por el Publicador</h2>
                    <p style="margin-bottom: 25px; max-width: 600px; font-size: 1.1rem;">Por políticas de derechos de autor, este recurso bloquea la visualización embebida. Hemos generado esta ficha para tu consulta:</p>
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 30px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); width: 100%; max-width: 600px; text-align: left;">
                        <h3 style="margin-top: 0; color: #4338ca; border-bottom: 2px solid #e0e7ff; padding-bottom: 10px; margin-bottom: 20px;"><i class="fas fa-file-alt"></i> ${safeTitle.innerHTML}</h3>
                        <p><strong>Enlace Oficial:</strong></p>
                        <div style="background: #f1f5f9; padding: 10px; border-radius: 6px; word-break: break-all; margin-bottom: 20px; font-family: monospace;">
                            <a href="${url}" target="_blank" style="color: #2563eb; text-decoration: none;">${url}</a>
                        </div>
                        <p style="color: #64748b; font-size: 0.9rem;"><i class="fas fa-info-circle"></i> Haz clic en el enlace superior o en el botón "Abrir Original" para visualizar el documento en una pestaña segura.</p>
                    </div>
                `;
                document.getElementById('pdfViewerLoading').style.display = 'none';
            } else {
                document.getElementById('pdfViewerIframe').style.display = 'block';
                fallbackDiv.style.display = 'none';
                renderPdfIframe();
            }
        }
        
        function toggleViewerType() {
            useGoogleViewer = !useGoogleViewer;
            renderPdfIframe();
        }
        
        function renderPdfIframe() {
            document.getElementById('pdfViewerLoading').style.display = 'block';
            document.getElementById('pdfViewerLoadingText').textContent = useGoogleViewer ? "Cargando motor de Google Docs..." : "Cargando motor Nativo...";
            
            let viewerUrl = currentPdfUrl;
            if(useGoogleViewer) {
                viewerUrl = 'https://docs.google.com/gview?url=' + encodeURIComponent(currentPdfUrl) + '&embedded=true';
            } else {
                if(currentIsPdf || currentPdfUrl.toLowerCase().includes('.pdf')) {
                    viewerUrl = '/api/proxy/external_pdf?url=' + encodeURIComponent(currentPdfUrl);
                }
            }
            document.getElementById('pdfViewerIframe').src = viewerUrl;
        }

        function closePdfViewer() {
            document.getElementById('pdfViewerModal').style.display = 'none';
            document.getElementById('pdfViewerIframe').src = '';
        }

    
        // Funciones para OVAs
        let allOvas = [];
        
        function switchLibraryTab(tab) {
            const btnOpenAlex = document.getElementById('tabOpenAlex');
            const btnOvas = document.getElementById('tabOvas');
            const contOpenAlex = document.getElementById('containerOpenAlex');
            const contOvas = document.getElementById('containerOvas');
            
            if(tab === 'openalex') {
                btnOpenAlex.className = 'btn-primary';
                btnOpenAlex.style.background = 'linear-gradient(135deg, #6366f1, #4f46e5)';
                btnOpenAlex.style.color = 'white';
                btnOpenAlex.style.border = 'none';
                
                btnOvas.className = 'btn-ghost';
                btnOvas.style.background = 'white';
                btnOvas.style.color = '#475569';
                btnOvas.style.border = '1px solid #cbd5e1';
                
                contOpenAlex.style.display = 'block';
                contOvas.style.display = 'none';
            } else {
                btnOvas.className = 'btn-primary';
                btnOvas.style.background = 'linear-gradient(135deg, #ec4899, #f43f5e)';
                btnOvas.style.color = 'white';
                btnOvas.style.border = 'none';
                
                btnOpenAlex.className = 'btn-ghost';
                btnOpenAlex.style.background = 'white';
                btnOpenAlex.style.color = '#475569';
                btnOpenAlex.style.border = '1px solid #cbd5e1';
                
                contOpenAlex.style.display = 'none';
                contOvas.style.display = 'block';
                
                if(allOvas.length === 0) {
                    loadOvas();
                }
            }
        }
        
        
        function openUniversal(platform) {
            const query = document.getElementById('universalSearchQuery').value.trim();
            if(!query) {
                alert("Por favor, escribe un tema primero (ej. Contabilidad)");
                document.getElementById('universalSearchQuery').focus();
                return;
            }
            
            let url = '';
            const enc = encodeURIComponent(query);
            
            if(platform === 'educaplay') url = `https://es.educaplay.com/recursos-educativos/?q=${enc}`;
            if(platform === 'wordwall') url = `https://wordwall.net/es/community?query=${enc}`;
            if(platform === 'khan') url = `https://es.khanacademy.org/search?page_search_query=${enc}`;
            if(platform === 'youtube') url = `https://www.youtube.com/results?search_query=${enc}+educativo`;
            
            openNativeViewer(url);
        }

        async function loadOvas() {
            document.getElementById('ovasLoadingIndicator').style.display = 'block';
            document.getElementById('ovasResults').innerHTML = '';
            try {
                const res = await fetch('/api/library/ovas');
                const data = await res.json();
                if(data.status === 'success') {
                    allOvas = data.ovas;
                    renderOvas(allOvas);
                } else {
                    document.getElementById('ovasResults').innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #ef4444;">Error al cargar OVAs: ' + data.message + '</div>';
                }
            } catch(e) {
                document.getElementById('ovasResults').innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #ef4444;">Error de red al cargar OVAs.</div>';
            } finally {
                document.getElementById('ovasLoadingIndicator').style.display = 'none';
            }
        }
        
        function filterOvas() {
            const query = document.getElementById('ovasSearchQuery').value.toLowerCase();
            const filtered = allOvas.filter(ova => ova.title.toLowerCase().includes(query) || ova.description.toLowerCase().includes(query));
            renderOvas(filtered);
        }
        
        function renderOvas(ovasArray) {
            const container = document.getElementById('ovasResults');
            if(ovasArray.length === 0) {
                container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #64748b; padding: 20px;">No se encontraron simuladores con ese nombre.</div>';
                return;
            }
            
            let html = '';
            ovasArray.forEach(ova => {
                html += `
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 10px 15px rgba(0,0,0,0.05)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.02)'">
                        <div style="height: 160px; background: #f8fafc; position: relative; overflow: hidden; border-bottom: 1px solid #e2e8f0;">
                            <img src="${ova.thumbUrl}" onerror="this.src='https://via.placeholder.com/600x400?text=Simulador+PhET'" style="width: 100%; height: 100%; object-fit: cover;">
                            <div style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.6); color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold;">
                                HTML5
                            </div>
                        </div>
                        <div style="padding: 15px; flex: 1; display: flex; flex-direction: column;">
                            <h4 style="margin: 0 0 8px 0; color: #1e293b; font-size: 1rem; line-height: 1.3;">${ova.title}</h4>
                            <p style="margin: 0 0 15px 0; color: #64748b; font-size: 0.85rem; flex: 1; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">${ova.description}</p>
                            <button class="btn-primary" onclick="openNativeViewer('${ova.runUrl}')" style="width: 100%; padding: 8px; background: #ec4899; border: none; border-radius: 8px; box-shadow: 0 2px 4px rgba(236,72,153,0.3); font-size: 0.9rem;"><i class="fas fa-play"></i> Abrir Simulador</button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        // Helper to force native viewer for OVAs
        function openNativeViewer(url) {
            currentPdfUrl = url;
            useGoogleViewer = false; // Forzamos visor nativo porque los OVAs son HTML5 interactivos
            document.getElementById('pdfViewerExternalBtn').onclick = () => window.open(url, '_blank');
            document.getElementById('pdfViewerModal').style.display = 'flex';
            renderPdfIframe();
        }

        function openMiniTranslator() {
            document.getElementById('miniTranslatorModal').style.display = 'flex';
            
            // Ocultar el iframe para que no bloquee el foco ni los atajos de teclado (Ctrl+V)
            const iframe = document.getElementById('pdfViewerIframe');
            if(iframe) iframe.style.visibility = 'hidden';

            document.getElementById('miniTranslatorSource').value = '';
            document.getElementById('miniTranslatorResult').value = '';
            document.getElementById('miniTranslatorResult').style.display = 'none';
            
            setTimeout(() => {
                const ta = document.getElementById('miniTranslatorSource');
                ta.focus();
            }, 150);
        }

        function closeMiniTranslator() {
            document.getElementById('miniTranslatorModal').style.display = 'none';
            // Restaurar el iframe
            const iframe = document.getElementById('pdfViewerIframe');
            if(iframe) iframe.style.visibility = 'visible';
        }

        async function pasteToTranslator() {
            const ta = document.getElementById('miniTranslatorSource');
            ta.focus();
            try {
                if (!navigator.clipboard || !navigator.clipboard.readText) {
                    throw new Error("Clipboard API not available");
                }
                const text = await navigator.clipboard.readText();
                if (!text || text.trim() === '') {
                    alert("⚠️ El portapapeles está vacío o no contiene texto.\n\nAsegúrate de seleccionar el texto en el PDF y presionar 'Ctrl + C' (o clic derecho > Copiar) ANTES de usar este botón.");
                    return;
                }
                ta.value = text;
            } catch (err) {
                alert("⛔ Tu navegador requiere que pegues el texto manualmente (por seguridad en esta red).\n\nSOLUCIÓN:\n1. Haz clic dentro de la caja de texto blanca.\n2. Presiona las teclas 'Ctrl' y 'V' al mismo tiempo para pegar.\n(O haz clic derecho en la caja y selecciona 'Pegar').");
            }
        }

        function pasteAlternative() {
            const text = prompt("Pega aquí tu texto (Ctrl+V o Clic Derecho > Pegar) y presiona Aceptar:");
            if (text && text.trim() !== '') {
                document.getElementById('miniTranslatorSource').value = text;
            }
        }

        async function translateMiniText() {
            const text = document.getElementById('miniTranslatorSource').value.trim();
            if (!text) return;
            
            document.getElementById('miniTranslatorLoading').style.display = 'block';
            document.getElementById('miniTranslatorResult').style.display = 'none';
            
            try {
                const resp = await fetch('/api/library/translate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text, target_lang: 'es'})
                });
                const res = await resp.json();
                document.getElementById('miniTranslatorLoading').style.display = 'none';
                
                if (res.status === 'success') {
                    document.getElementById('miniTranslatorResult').value = res.translated;
                    document.getElementById('miniTranslatorResult').style.display = 'block';
                } else {
                    alert("Error: " + res.message);
                }
            } catch(e) {
                document.getElementById('miniTranslatorLoading').style.display = 'none';
                alert("Error de red al traducir.");
            }
        }
    