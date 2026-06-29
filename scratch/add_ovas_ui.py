import codecs
import re

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

# REPLACEMENT FOR THE UI HTML
new_html = """
                    <div id="librarySectionBottom" style="margin-top: 40px; border-top: 2px dashed #e2e8f0; padding-top: 30px;">
                        
                        <!-- Pestañas del Repositorio -->
                        <div style="display:flex; justify-content:center; margin-bottom: 25px; gap: 10px;">
                            <button id="tabOpenAlex" onclick="switchLibraryTab('openalex')" class="btn-primary" style="border-radius: 20px; padding: 10px 25px; box-shadow: 0 4px 10px rgba(99,102,241,0.2); background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; border: none;"><i class="fas fa-book-open"></i> Documentos Académicos</button>
                            <button id="tabOvas" onclick="switchLibraryTab('ovas')" class="btn-ghost" style="border-radius: 20px; padding: 10px 25px; border: 1px solid #cbd5e1; background: white; color: #475569;"><i class="fas fa-flask"></i> Simuladores OVAs</button>
                        </div>

                        <!-- CONTENEDOR OPENALEX -->
                        <div id="containerOpenAlex">
                            <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(16, 185, 129, 0.05)); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 16px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); backdrop-filter: blur(10px);">
                                <h3 style="margin-top: 0; color: #1e293b; display: flex; justify-content: space-between; align-items: center; font-size: 1.15rem;">
                                    <span><i class="fas fa-search" style="color: #6366f1; margin-right: 8px;"></i> Repositorio SKEL</span>
                                    <button class="btn-ghost" onclick="toggleSavedResources()" style="color: #6366f1; border: 1px solid #c7d2fe; padding: 6px 12px; border-radius: 8px; background: white; transition: all 0.3s; box-shadow: 0 2px 4px rgba(0,0,0,0.02); font-weight: 600;">⭐ Mis Favoritos</button>
                                </h3>
                                <p style="font-size: 0.9rem; color: #475569; margin-bottom: 15px;">Encuentra y guarda referencias de acceso abierto para tus cursos. Generamos la cita APA automáticamente.</p>
                                <div style="display: flex; gap: 10px;">
                                    <input type="text" id="openLibrarySearchQuery" placeholder="Ej: Calidad Educativa, Machine Learning, etc." style="flex: 1; padding: 12px 18px; border-radius: 12px; border: 1px solid #cbd5e1; font-size: 0.95rem; outline: none; transition: border-color 0.3s;" onfocus="this.style.borderColor='#6366f1'" onblur="this.style.borderColor='#cbd5e1'" onkeydown="if(event.key==='Enter') searchOpenLibrary()">
                                    <button class="btn-primary" onclick="searchOpenLibrary()" style="padding: 0 30px; border-radius: 12px; font-size: 1rem; background: linear-gradient(135deg, #6366f1, #4f46e5); border: none; box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3); transition: transform 0.2s;"><i class="fas fa-search"></i> Buscar</button>
                                </div>
                            </div>
                            <div id="openLibraryResults" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;">
                                <!-- Se llenará vía JS -->
                            </div>
                        </div>

                        <!-- CONTENEDOR OVAS -->
                        <div id="containerOvas" style="display: none;">
                            <div style="background: linear-gradient(135deg, rgba(236, 72, 153, 0.05), rgba(245, 158, 11, 0.05)); border: 1px solid rgba(236, 72, 153, 0.2); border-radius: 16px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); backdrop-filter: blur(10px);">
                                <h3 style="margin-top: 0; color: #1e293b; display: flex; justify-content: space-between; align-items: center; font-size: 1.15rem;">
                                    <span><i class="fas fa-flask" style="color: #ec4899; margin-right: 8px;"></i> Catálogo Interactivo de OVAs</span>
                                </h3>
                                <p style="font-size: 0.9rem; color: #475569; margin-bottom: 15px;">Explora simuladores interactivos de PhET para todas las áreas (Ciencias, Matemáticas, etc).</p>
                                <div style="display: flex; gap: 10px;">
                                    <input type="text" id="ovasSearchQuery" placeholder="Filtrar simulador por nombre... (ej. Fracciones, Fuerza, Balance)" style="flex: 1; padding: 12px 18px; border-radius: 12px; border: 1px solid #cbd5e1; font-size: 0.95rem; outline: none; transition: border-color 0.3s;" onfocus="this.style.borderColor='#ec4899'" onblur="this.style.borderColor='#cbd5e1'" onkeyup="filterOvas()">
                                    <button class="btn-primary" onclick="loadOvas()" style="padding: 0 20px; border-radius: 12px; font-size: 1rem; background: linear-gradient(135deg, #ec4899, #f43f5e); border: none; box-shadow: 0 4px 10px rgba(236, 72, 153, 0.3); transition: transform 0.2s;"><i class="fas fa-sync-alt"></i> Recargar</button>
                                </div>
                            </div>
                            <div id="ovasLoadingIndicator" style="text-align: center; padding: 40px; color: #64748b; display: none;">
                                <i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: #ec4899; margin-bottom: 15px;"></i><br>Cargando catálogo de OVAs...
                            </div>
                            <div id="ovasResults" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px;">
                                <!-- Se llenará vía JS -->
                            </div>
                        </div>

                    </div>
"""
# Replace from librarySectionBottom to openLibraryResults
content = re.sub(r'<div id="librarySectionBottom" .*?<!-- Se llenará vía JS -->\s*</div>', new_html.strip()[:-6], content, flags=re.DOTALL) # -6 removes the last </div> from new_html because the regex captures up to the inner div closing, wait actually regex is tricky.

# safer way:
# We know the block starts with <div id="librarySectionBottom" and ends with </div> right after openLibraryResults
# Let's read the lines to make it safer.
"""
                    <div id="librarySectionBottom" style="margin-top: 40px; border-top: 2px dashed #e2e8f0; padding-top: 30px;">
...
                        <div id="openLibraryResults" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;">
                            <!-- Se llenará vía JS -->
                        </div>
                    </div>
"""
pattern_html = re.compile(r'<div id="librarySectionBottom".*?<div id="openLibraryResults".*?</div>\s*</div>', re.DOTALL)
content = pattern_html.sub(new_html, content)


js_code = """
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
"""
content = re.sub(r'(</script>\s*<!-- MODAL: VISOR DE PDF -->)', js_code + r'\n    \1', content)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)

print("UI HTML and JS updated!")
