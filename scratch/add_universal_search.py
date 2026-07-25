import codecs
import re

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

universal_search_html = """
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
                                    
                                    <button class="btn-primary" onclick="openUniversal('quizizz')" style="flex:1; min-width: 200px; padding: 12px; border-radius: 12px; font-size: 0.95rem; background: white; color: #1e293b; border: 1px solid #cbd5e1; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px;" onmouseover="this.style.borderColor='#8b5cf6'; this.style.color='#8b5cf6'" onmouseout="this.style.borderColor='#cbd5e1'; this.style.color='#1e293b'"><img src="https://quizizz.com/favicon.ico" onerror="this.style.display='none'" style="width:16px; height:16px; border-radius:4px;"> Quizizz</button>
                                    
                                    <button class="btn-primary" onclick="openUniversal('youtube')" style="flex:1; min-width: 200px; padding: 12px; border-radius: 12px; font-size: 0.95rem; background: white; color: #1e293b; border: 1px solid #cbd5e1; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px;" onmouseover="this.style.borderColor='#ef4444'; this.style.color='#ef4444'" onmouseout="this.style.borderColor='#cbd5e1'; this.style.color='#1e293b'"><i class="fab fa-youtube" style="color: #ef4444;"></i> YouTube Edu</button>
                                </div>
                            </div>
"""

content = content.replace('<div id="containerOvas" style="display: none;">', '<div id="containerOvas" style="display: none;">\n' + universal_search_html)

content = content.replace('<i class="fas fa-flask"></i> Simuladores OVAs</button>', '<i class="fas fa-photo-video"></i> Multimedias y OVAs</button>')
content = content.replace('<span><i class="fas fa-flask" style="color: #ec4899; margin-right: 8px;"></i> Catálogo Interactivo de OVAs</span>', '<span><i class="fas fa-flask" style="color: #ec4899; margin-right: 8px;"></i> Catálogo PhET (Ciencias Exactas)</span>')

js_logic = """
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
            if(platform === 'quizizz') url = `https://quizizz.com/admin/search/${enc}`;
            if(platform === 'youtube') url = `https://www.youtube.com/results?search_query=${enc}+educativo`;
            
            window.open(url, '_blank');
        }
"""

content = content.replace("async function loadOvas()", js_logic + "\n        async function loadOvas()")

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)

print("Universal search injected!")
