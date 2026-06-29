import codecs
import re

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

# 1. Remove subTabLibrary and button if they somehow still exist in the middle
content = re.sub(r'\s*<button class="sub-tab-btn" id="subTabBtnLibrary".*?</button>', '', content)

# 2. Insert Sub-Tab Content before TAB: TEACHERS
pattern_tab_end = r'(</div>\s*</div>\s*<!-- TAB: TEACHERS \(Admin\) -->)'
replacement_tab_end = r"""                    <!-- SECCIÓN: BIBLIOTECA ABIERTA (FINAL DEL EDITOR) -->
                    <div id="librarySectionBottom" style="margin-top: 40px; border-top: 2px dashed #e2e8f0; padding-top: 30px;">
                        <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(16, 185, 129, 0.05)); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 16px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); backdrop-filter: blur(10px);">
                            <h3 style="margin-top: 0; color: #1e293b; display: flex; justify-content: space-between; align-items: center; font-size: 1.15rem;">
                                <span><i class="fas fa-search" style="color: #6366f1; margin-right: 8px;"></i> Repositorio Libre OpenAlex (APA 7)</span>
                                <button class="btn-ghost" onclick="toggleSavedResources()" style="color: #6366f1; border: 1px solid #c7d2fe; padding: 6px 12px; border-radius: 8px; background: white; transition: all 0.3s; box-shadow: 0 2px 4px rgba(0,0,0,0.02); font-weight: 600;">⭐ Mis Favoritos</button>
                            </h3>
                            <p style="font-size: 0.9rem; color: #475569; margin-bottom: 15px;">Encuentra y guarda referencias de acceso abierto para tus cursos. Generamos la cita APA automáticamente.</p>
                            <div style="display: flex; gap: 10px;">
                                <input type="text" id="openLibrarySearchQuery" placeholder="Ej: Calidad Educativa, Machine Learning, etc." style="flex: 1; padding: 12px 18px; border-radius: 12px; border: 1px solid #cbd5e1; font-size: 0.95rem; outline: none; transition: border-color 0.3s;" onfocus="this.style.borderColor='#6366f1'" onblur="this.style.borderColor='#cbd5e1'" onkeydown="if(event.key==='Enter') searchOpenLibrary()">
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
\1"""
content = re.sub(pattern_tab_end, replacement_tab_end, content)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)
print("Added bottom container!")
