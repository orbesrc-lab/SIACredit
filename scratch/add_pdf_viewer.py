import codecs
import re

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

modal_code = """
    <!-- MODAL: VISOR DE PDF -->
    <div id="pdfViewerModal" style="display:none; position:fixed; inset:0; background:rgba(15, 23, 42, 0.85); backdrop-filter: blur(5px); z-index:9999; align-items:center; justify-content:center; flex-direction:column;">
        <div style="width:95%; max-width:1200px; height:90vh; background:white; border-radius:12px; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 25px 50px -12px rgba(0,0,0,0.5);">
            <div style="background:var(--primary-color, #6366f1); color:white; padding:15px 25px; display:flex; justify-content:space-between; align-items:center;">
                <h3 style="margin:0; font-size:1.2rem; display:flex; align-items:center;"><i class="fas fa-file-pdf" style="margin-right:10px;"></i> Visor de Documentos Integrado</h3>
                <div style="display:flex; gap:15px; align-items:center;">
                    <button id="pdfViewerExternalBtn" class="btn-ghost" style="color:white; border:1px solid rgba(255,255,255,0.3); padding:6px 12px; border-radius:8px; background:rgba(255,255,255,0.1); cursor:pointer;"><i class="fas fa-external-link-alt"></i> Abrir en otra pestaña</button>
                    <button onclick="closePdfViewer()" style="background:transparent; border:none; color:white; font-size:1.8rem; cursor:pointer; line-height:1; opacity:0.8; transition:opacity 0.2s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">&times;</button>
                </div>
            </div>
            <div style="flex:1; background:#f1f5f9; position:relative; display:flex; justify-content:center; align-items:center;">
                <div id="pdfViewerLoading" style="position:absolute; color:#64748b; text-align:center; display:none;">
                    <i class="fas fa-spinner fa-spin" style="font-size:2.5rem; color:#6366f1; margin-bottom:15px;"></i><br>Cargando documento...<br><small style="opacity:0.7;">(Si no carga o aparece bloqueado, usa "Abrir en otra pestaña")</small>
                </div>
                <iframe id="pdfViewerIframe" src="" style="width:100%; height:100%; border:none; position:relative; z-index:1;" onload="document.getElementById('pdfViewerLoading').style.display='none'"></iframe>
            </div>
        </div>
    </div>
"""
content = content.replace("</body>", modal_code + "\n</body>")

js_code = """
        function openPdfViewer(url) {
            document.getElementById('pdfViewerLoading').style.display = 'block';
            document.getElementById('pdfViewerIframe').src = url;
            document.getElementById('pdfViewerExternalBtn').onclick = () => window.open(url, '_blank');
            document.getElementById('pdfViewerModal').style.display = 'flex';
        }
        
        function closePdfViewer() {
            document.getElementById('pdfViewerModal').style.display = 'none';
            document.getElementById('pdfViewerIframe').src = '';
        }
"""
content = content.replace("</script>\n</body>", js_code + "\n</script>\n</body>")

content = content.replace(
    "onclick=\"window.open('${pdfUrl}', '_blank')\" style=\"flex: 1; padding: 8px; font-size: 0.85rem; background: #10b981;",
    "onclick=\"openPdfViewer('${pdfUrl}')\" style=\"flex: 1; padding: 8px; font-size: 0.85rem; background: #10b981;"
)

content = content.replace(
    "onclick=\"window.open('${item.url}', '_blank')\" style=\"flex: 1; padding: 8px; font-size: 0.85rem; background: #10b981;",
    "onclick=\"openPdfViewer('${item.url}')\" style=\"flex: 1; padding: 8px; font-size: 0.85rem; background: #10b981;"
)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)

print("PDF Viewer Injected!")
