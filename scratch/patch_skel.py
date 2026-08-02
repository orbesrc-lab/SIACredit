import re

def patch():
    # 1. Read global sidebar from dashboard.html
    with open(r'c:\SIAC\templates\dashboard.html', 'r', encoding='utf-8') as f:
        dashboard_html = f.read()

    sidebar_match = re.search(r'(<aside class="sidebar">.*?</aside>)', dashboard_html, re.DOTALL)
    if not sidebar_match:
        print('Failed to find sidebar in dashboard.html')
        return
    global_sidebar = sidebar_match.group(1)

    # 2. Read skel360.html
    with open(r'c:\SIAC\templates\skel360.html', 'r', encoding='utf-8') as f:
        skel_html = f.read()

    # 3. Replace sidebar
    skel_html = re.sub(r'<aside class="sidebar">.*?</aside>', global_sidebar, skel_html, flags=re.DOTALL)

    # 4. Add the Modal and logic
    modal_html = """
    <!-- MODAL NUEVA EMPRESA -->
    <div id="modal-nueva-empresa" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; justify-content:center; align-items:center;">
        <div style="background:white; padding:30px; border-radius:12px; width:90%; max-width:500px;">
            <h2 style="margin-bottom:20px;">Crear Nueva Empresa</h2>
            <form id="form-empresa">
                <div style="margin-bottom:15px;">
                    <label style="display:block; margin-bottom:5px;">Nombre de la Empresa</label>
                    <input type="text" id="emp-nombre" required style="width:100%; padding:10px; border:1px solid #ccc; border-radius:5px; box-sizing:border-box;">
                </div>
                <div style="margin-bottom:15px;">
                    <label style="display:block; margin-bottom:5px;">NIT</label>
                    <input type="text" id="emp-nit" required style="width:100%; padding:10px; border:1px solid #ccc; border-radius:5px; box-sizing:border-box;">
                </div>
                <div style="margin-bottom:15px;">
                    <label style="display:block; margin-bottom:5px;">Sector</label>
                    <input type="text" id="emp-sector" style="width:100%; padding:10px; border:1px solid #ccc; border-radius:5px; box-sizing:border-box;">
                </div>
                <div style="margin-bottom:25px;">
                    <label style="display:block; margin-bottom:5px;">Ciudad</label>
                    <input type="text" id="emp-ciudad" style="width:100%; padding:10px; border:1px solid #ccc; border-radius:5px; box-sizing:border-box;">
                </div>
                <div style="display:flex; justify-content:flex-end; gap:10px;">
                    <button type="button" onclick="cerrarModalEmpresa()" style="padding:10px 15px; background:#e5e7eb; border:none; border-radius:5px; cursor:pointer;">Cancelar</button>
                    <button type="submit" style="padding:10px 15px; background:#4338ca; color:white; border:none; border-radius:5px; cursor:pointer;">Guardar Empresa</button>
                </div>
            </form>
        </div>
    </div>
"""

    # insert modal before <script>
    skel_html = skel_html.replace('    <script>', modal_html + '\n    <script>')

    # change the button onclick from alert to open modal
    skel_html = skel_html.replace("alert('Funcionalidad para crear empresa en desarrollo.')", "abrirModalEmpresa()")

    # add JS logic
    js_logic = """
        function abrirModalEmpresa() {
            document.getElementById('modal-nueva-empresa').style.display = 'flex';
        }
        function cerrarModalEmpresa() {
            document.getElementById('modal-nueva-empresa').style.display = 'none';
        }
        
        document.getElementById('form-empresa').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                nombre: document.getElementById('emp-nombre').value,
                nit: document.getElementById('emp-nit').value,
                sector: document.getElementById('emp-sector').value,
                ciudad: document.getElementById('emp-ciudad').value
            };
            
            try {
                const response = await fetch('/api/skel360/empresas', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                if(result.status === 'success') {
                    cerrarModalEmpresa();
                    document.getElementById('form-empresa').reset();
                    loadEmpresas();
                } else {
                    alert('Error: ' + result.message);
                }
            } catch(error) {
                console.error(error);
                alert('Error de conexión.');
            }
        });
"""

    skel_html = skel_html.replace('async function loadEmpresas()', js_logic + '\n        async function loadEmpresas()')

    # write back
    with open(r'c:\SIAC\templates\skel360.html', 'w', encoding='utf-8') as f:
        f.write(skel_html)
    print('Updated skel360.html successfully!')

if __name__ == '__main__':
    patch()
