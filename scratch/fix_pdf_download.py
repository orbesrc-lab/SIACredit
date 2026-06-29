import codecs
import re

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

# Modify the Modal HTML to include the Toggle button
new_modal_html = """
    <!-- MODAL: VISOR DE PDF -->
    <div id="pdfViewerModal" style="display:none; position:fixed; inset:0; background:rgba(15, 23, 42, 0.85); backdrop-filter: blur(5px); z-index:9999; align-items:center; justify-content:center; flex-direction:column;">
        <div style="width:95%; max-width:1200px; height:90vh; background:white; border-radius:12px; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 25px 50px -12px rgba(0,0,0,0.5);">
            <div style="background:var(--primary-color, #6366f1); color:white; padding:15px 25px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <h3 style="margin:0; font-size:1.2rem; display:flex; align-items:center;"><i class="fas fa-file-pdf" style="margin-right:10px;"></i> Visor de Documentos Integrado</h3>
                <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                    <button onclick="toggleViewerType()" class="btn-ghost" style="color:white; border:1px solid rgba(255,255,255,0.3); padding:6px 12px; border-radius:8px; background:rgba(255,255,255,0.1); cursor:pointer;"><i class="fas fa-sync-alt"></i> Cambiar Motor de Visor</button>
                    <button id="pdfViewerExternalBtn" class="btn-ghost" style="color:white; border:1px solid rgba(255,255,255,0.3); padding:6px 12px; border-radius:8px; background:rgba(255,255,255,0.1); cursor:pointer;"><i class="fas fa-external-link-alt"></i> Abrir Original</button>
                    <button onclick="closePdfViewer()" style="background:transparent; border:none; color:white; font-size:1.8rem; cursor:pointer; line-height:1; opacity:0.8; transition:opacity 0.2s; margin-left:10px;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">&times;</button>
                </div>
            </div>
            <div style="flex:1; background:#f1f5f9; position:relative; display:flex; justify-content:center; align-items:center;">
                <div id="pdfViewerLoading" style="position:absolute; color:#64748b; text-align:center; display:none;">
                    <i class="fas fa-spinner fa-spin" style="font-size:2.5rem; color:#6366f1; margin-bottom:15px;"></i><br><span id="pdfViewerLoadingText">Cargando documento...</span><br><small style="opacity:0.7;">(Si se queda en blanco, haz clic en "Cambiar Motor de Visor")</small>
                </div>
                <iframe id="pdfViewerIframe" src="" style="width:100%; height:100%; border:none; position:relative; z-index:1;" onload="document.getElementById('pdfViewerLoading').style.display='none'"></iframe>
            </div>
        </div>
    </div>
"""

# Replace the old modal with the new one
content = re.sub(r'<!-- MODAL: VISOR DE PDF -->.*?</div>\s*</div>\s*</div>', new_modal_html.strip(), content, flags=re.DOTALL)

# Modify the JS functions
new_js_code = """
        let currentPdfUrl = '';
        let useGoogleViewer = true;
        
        function openPdfViewer(url) {
            currentPdfUrl = url;
            useGoogleViewer = true; // Por defecto intentamos Google Viewer para forzar la visualización en lugar de descarga
            document.getElementById('pdfViewerExternalBtn').onclick = () => window.open(url, '_blank');
            document.getElementById('pdfViewerModal').style.display = 'flex';
            renderPdfIframe();
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
            }
            document.getElementById('pdfViewerIframe').src = viewerUrl;
        }

        function closePdfViewer() {
            document.getElementById('pdfViewerModal').style.display = 'none';
            document.getElementById('pdfViewerIframe').src = '';
        }
"""

content = re.sub(r'function openPdfViewer\(url\).*?function closePdfViewer\(\)\s*\{.*?\}', new_js_code.strip(), content, flags=re.DOTALL)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)

print("Toggle viewer script injected!")
