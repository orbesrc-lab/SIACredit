import codecs
import re

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

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

content = re.sub(r'(</script>\s*<!-- MODAL: VISOR DE PDF -->)', js_code + r'\n    \1', content)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)

print("JS injected!")
