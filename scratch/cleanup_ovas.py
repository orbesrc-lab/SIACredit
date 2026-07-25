import codecs
import re

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

# We need to replace everything from the first <!-- CONTENEDOR OVAS --> up to <!-- Favoritos Guardados -->
# To be safe, I'll extract it, fix it, and put it back.
start_marker = "<!-- CONTENEDOR OVAS -->"
end_marker = "<!-- Favoritos Guardados -->"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    correct_html = """<!-- CONTENEDOR OVAS -->
                        <div id="containerOvas" style="display: none;">

                            <!-- BUSCADOR UNIVERSAL EXTERNO -->
                            <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(147, 51, 234, 0.05)); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 16px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); backdrop-filter: blur(10px);">
                                <h3 style="margin-top: 0; color: #1e293b; display: flex; justify-content: space-between; align-items: center; font-size: 1.15rem;">
                                    <span><i class="fas fa-globe" style="color: #3b82f6; margin-right: 8px;"></i> Metabuscador de Multimedias y Juegos (Todas las áreas)</span>
                                </h3>
                                <p style="font-size: 0.9rem; color: #475569; margin-bottom: 15px;">¿Buscas temas como <b>Contabilidad</b>, <b>Historia</b>, <b>Derecho</b> o <b>Lenguaje</b>? Escribe el tema y encuéntralo en las mejores plataformas de aprendizaje interactivo.</p>
                                <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                                    <input type="text" id="universalSearchQuery" placeholder="Ej: Contabilidad Básica, Revolución Francesa, Sinónimos..." style="flex: 1; padding: 12px 18px; border-radius: 12px; border: 1px solid #cbd5e1; font-size: 0.95rem; outline: none; transition: border-color 0.3s;" onfocus="this.style.borderColor='#3b82f6'" onblur="this.style.borderColor='#cbd5e1'">
                                </div>
                                
                                <div id="universalLinks" style="display: flex; gap: 10px; flex-wrap: wrap;">
                                    <button class="btn-primary" onclick="openUniversal('educaplay')" style="flex:1; min-width: 200px; padding: 12px; border-radius: 12px; font-size: 0.95rem; background: white; color: #1e293b; border: 1px solid #cbd5e1; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px;" onmouseover="this.style.borderColor='#10b981'; this.style.color='#10b981'" onmouseout="this.style.borderColor='#cbd5e1'; this.style.color='#1e293b'"><img src="https://www.educaplay.com/favicon.ico" onerror="this.style.display='none'" style="width:16px; height:16px; border-radius:4px;"> Educaplay</button>
                                    
                                    <button class="btn-primary" onclick="openUniversal('wordwall')" style="flex:1; min-width: 200px; padding: 12px; border-radius: 12px; font-size: 0.95rem; background: white; color: #1e293b; border: 1px solid #cbd5e1; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px;" onmouseover="this.style.borderColor='#3b82f6'; this.style.color='#3b82f6'" onmouseout="this.style.borderColor='#cbd5e1'; this.style.color='#1e293b'"><img src="https://wordwall.net/favicon.ico" onerror="this.style.display='none'" style="width:16px; height:16px; border-radius:4px;"> Wordwall</button>
                                    
                                    <button class="btn-primary" onclick="openUniversal('khan')" style="flex:1; min-width: 200px; padding: 12px; border-radius: 12px; font-size: 0.95rem; background: white; color: #1e293b; border: 1px solid #cbd5e1; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px;" onmouseover="this.style.borderColor='#14b8a6'; this.style.color='#14b8a6'" onmouseout="this.style.borderColor='#cbd5e1'; this.style.color='#1e293b'"><img src="https://es.khanacademy.org/favicon.ico" onerror="this.style.display='none'" style="width:16px; height:16px; border-radius:4px;"> Khan Academy</button>
                                    
                                    <button class="btn-primary" onclick="openUniversal('youtube')" style="flex:1; min-width: 200px; padding: 12px; border-radius: 12px; font-size: 0.95rem; background: white; color: #1e293b; border: 1px solid #cbd5e1; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px;" onmouseover="this.style.borderColor='#ef4444'; this.style.color='#ef4444'" onmouseout="this.style.borderColor='#cbd5e1'; this.style.color='#1e293b'"><i class="fab fa-youtube" style="color: #ef4444;"></i> YouTube Edu</button>
                                </div>
                            </div>

                            <div style="background: linear-gradient(135deg, rgba(236, 72, 153, 0.05), rgba(245, 158, 11, 0.05)); border: 1px solid rgba(236, 72, 153, 0.2); border-radius: 16px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); backdrop-filter: blur(10px);">
                                <h3 style="margin-top: 0; color: #1e293b; display: flex; justify-content: space-between; align-items: center; font-size: 1.15rem;">
                                    <span><i class="fas fa-flask" style="color: #ec4899; margin-right: 8px;"></i> Catálogo PhET (Ciencias Exactas)</span>
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
    content = content[:start_idx] + correct_html + content[end_idx:]
    
    # Also fix JS
    content = content.replace("if(platform === 'quizizz') url = `https://quizizz.com/admin/search/${enc}`;", "if(platform === 'khan') url = `https://es.khanacademy.org/search?page_search_query=${enc}`;")
    
    # To prevent any issues with previous duplicate divs, there was a missing </div> closing librarySectionBottom before 'Favoritos Guardados'.
    # In my correct_html I included `</div>\n\n                        ` at the end to close `librarySectionBottom`.
    
    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(content)
    
    print("Cleanup successful")
else:
    print("Markers not found!")
