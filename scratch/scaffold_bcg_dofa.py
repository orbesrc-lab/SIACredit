import os

source = "c:/SIAC/templates/dofa.html"
with open(source, "r", encoding="utf-8") as f:
    content = f.read()

parts = content.split('<div class="content-area">')
header = parts[0] + '<div class="content-area">\n'
footer_start = content.rfind('</main>')
footer = '\n' + content[footer_start:]

# BCG Matrix
bcg_content = """
    <div class="dofa-header">
        <h1>📈 Matriz BCG (Boston Consulting Group)</h1>
        <p>Analiza tu cartera de productos o servicios según su crecimiento en el mercado y participación relativa.</p>
    </div>
    
    <div style="display: flex; gap: 20px; flex-wrap: wrap;">
        <!-- Panel Izquierdo: Tabla de Productos -->
        <div class="dofa-panel active" style="flex: 1; min-width: 500px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
                <h3>Lista de Productos / Unidades de Negocio</h3>
                <button class="btn-primary" onclick="saveBCG()">💾 Guardar BCG</button>
            </div>
            <table class="matrix-table" id="bcgTable" style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th style="padding: 8px; border: 1px solid #ccc;">Producto / Servicio</th>
                        <th style="padding: 8px; border: 1px solid #ccc;" title="Relativa a tu competidor principal (Ej: 1.5 es líder, 0.5 es seguidor)">Participación de Mercado Relativa (X)</th>
                        <th style="padding: 8px; border: 1px solid #ccc;" title="Crecimiento anual de la industria en %">Tasa de Crecimiento % (Y)</th>
                        <th style="padding: 8px; border: 1px solid #ccc;" title="Volumen de ventas (para el tamaño de la burbuja)">Ventas (Opcional)</th>
                        <th style="padding: 8px; border: 1px solid #ccc;">Acción</th>
                    </tr>
                </thead>
                <tbody id="bcgBody">
                </tbody>
            </table>
            <div style="margin-top: 15px;">
                <button class="btn-secondary" onclick="addBcgRow()">➕ Añadir Producto</button>
                <button class="btn-secondary" onclick="renderBCGChart()">🔄 Actualizar Gráfico</button>
            </div>
        </div>
        
        <!-- Panel Derecho: Gráfico -->
        <div class="dofa-panel active" style="flex: 1; min-width: 400px; display: flex; flex-direction: column; align-items: center;">
            <h3>Gráfico Matriz BCG</h3>
            <div style="position: relative; width: 100%; max-width: 500px; height: 400px; margin-top: 20px;">
                <canvas id="bcgChart"></canvas>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="{{ url_for('static', filename='data.js') }}"></script>
    <script>
        const user = JSON.parse(localStorage.getItem('siac_user')) || {};
        const role = user.role || '';
        document.getElementById('userInfo').textContent = user.email || '';
        let bcgChartInstance = null;

        function logout() { localStorage.removeItem('siac_user'); window.top.location.href = 'login.html'; }

        async function initPage() {
            const resp = await fetch(`/api/institution?inst_id=${getInstId()}`);
            const data = await resp.json();
            document.getElementById('inst_name_display').textContent = data.name || 'Empresa';
            if (data.logo_url) {
                const img = document.getElementById('inst_logo_img');
                img.src = data.logo_url; img.style.display = 'block';
            }
            await loadBCG();
        }

        function addBcgRow(pName = '', pShare = 1.0, pGrowth = 10, pSales = 1000) {
            const tbody = document.getElementById('bcgBody');
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><input type="text" class="bcg-name" value="${pName}" style="width:100%; padding:5px;"></td>
                <td><input type="number" step="0.1" class="bcg-share" value="${pShare}" style="width:100%; padding:5px;"></td>
                <td><input type="number" step="1" class="bcg-growth" value="${pGrowth}" style="width:100%; padding:5px;"></td>
                <td><input type="number" step="1" class="bcg-sales" value="${pSales}" style="width:100%; padding:5px;"></td>
                <td style="text-align:center;"><button class="btn-secondary" style="padding:4px 8px; color:red;" onclick="this.closest('tr').remove()">X</button></td>
            `;
            tbody.appendChild(tr);
        }

        function renderBCGChart() {
            const tbody = document.getElementById('bcgBody');
            const dataPoints = [];
            
            tbody.querySelectorAll('tr').forEach(tr => {
                const name = tr.querySelector('.bcg-name').value;
                if (name.trim() !== '') {
                    dataPoints.push({
                        label: name,
                        x: parseFloat(tr.querySelector('.bcg-share').value) || 0,
                        y: parseFloat(tr.querySelector('.bcg-growth').value) || 0,
                        r: Math.sqrt(parseFloat(tr.querySelector('.bcg-sales').value) || 100) // Bubble radius
                    });
                }
            });

            if (bcgChartInstance) bcgChartInstance.destroy();
            
            const ctx = document.getElementById('bcgChart').getContext('2d');
            bcgChartInstance = new Chart(ctx, {
                type: 'bubble',
                data: {
                    datasets: [{
                        label: 'Productos',
                        data: dataPoints,
                        backgroundColor: 'rgba(99, 102, 241, 0.6)',
                        borderColor: 'rgba(99, 102, 241, 1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.raw.label + ': Share ' + context.raw.x + ', Growth ' + context.raw.y + '%';
                                }
                            }
                        },
                        annotation: { /* Could add quadrant lines here if chartjs-plugin-annotation is used */ }
                    },
                    scales: {
                        x: {
                            title: { display: true, text: 'Participación Relativa de Mercado' },
                            reverse: true, // BCG X-axis usually goes from high to low
                            min: 0,
                            max: 2
                        },
                        y: {
                            title: { display: true, text: 'Tasa de Crecimiento (%)' },
                            min: -10,
                            max: 30
                        }
                    }
                }
            });
        }

        async function loadBCG() {
            try {
                const resp = await fetch(`/api/business/matrix/bcg?inst_id=${getInstId()}`);
                if(resp.ok) {
                    const res = await resp.json();
                    if(res.data && res.data.products && res.data.products.length > 0) {
                        res.data.products.forEach(p => addBcgRow(p.name, p.share, p.growth, p.sales));
                    } else {
                        addBcgRow(); // empty row
                    }
                    setTimeout(renderBCGChart, 100);
                }
            } catch (e) {
                console.error("Error loading BCG:", e);
                addBcgRow();
            }
        }

        async function saveBCG() {
            const tbody = document.getElementById('bcgBody');
            const products = [];
            
            tbody.querySelectorAll('tr').forEach(tr => {
                const name = tr.querySelector('.bcg-name').value;
                if(name.trim() !== '') {
                    products.push({
                        name: name,
                        share: parseFloat(tr.querySelector('.bcg-share').value) || 0,
                        growth: parseFloat(tr.querySelector('.bcg-growth').value) || 0,
                        sales: parseFloat(tr.querySelector('.bcg-sales').value) || 0
                    });
                }
            });
            
            const payload = {
                inst_id: getInstId(),
                user_id: user.id,
                data: { products: products },
                results: {}
            };
            
            try {
                const resp = await fetch(`/api/business/matrix/bcg`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(resp.ok) alert('Matriz BCG guardada con éxito.');
                else alert('Error al guardar.');
            } catch(e) {
                alert('Error de conexión.');
            }
        }

        initPage();
    </script>
"""
with open("c:/SIAC/templates/empresa_bcg.html", "w", encoding="utf-8") as f:
    f.write(header + bcg_content + footer)

# Corporate DOFA (which pulls from MEFI/MEFE)
dofa_content = """
    <div class="dofa-header">
        <h1>⚔️ Matriz DOFA Corporativa Cruzada (TOWS)</h1>
        <p>Genera estrategias de cruce (FO, DO, FA, DA) a partir de los factores ingresados en tus Matrices MEFI y MEFE.</p>
    </div>

    <div class="dofa-panel active" style="margin-top: 20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px;">
            <h3>Generador de Estrategias AI</h3>
            <button class="btn-primary" onclick="generateDofaAi()">✨ Generar Estrategias con IA</button>
        </div>
        <p style="color:#64748b; font-size:0.9rem; margin-bottom: 20px;">
            Haz clic en el botón mágico para que la Inteligencia Artificial analice tus matrices MEFI y MEFE guardadas y proponga acciones estratégicas corporativas de alto impacto.
        </p>
        
        <div id="dofaResults" style="padding: 20px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; min-height: 200px;">
            <i>Las estrategias generadas aparecerán aquí...</i>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="{{ url_for('static', filename='data.js') }}"></script>
    <script>
        const user = JSON.parse(localStorage.getItem('siac_user')) || {};
        const role = user.role || '';
        document.getElementById('userInfo').textContent = user.email || '';

        function logout() { localStorage.removeItem('siac_user'); window.top.location.href = 'login.html'; }

        async function initPage() {
            const resp = await fetch(`/api/institution?inst_id=${getInstId()}`);
            const data = await resp.json();
            document.getElementById('inst_name_display').textContent = data.name || 'Empresa';
            if (data.logo_url) {
                const img = document.getElementById('inst_logo_img');
                img.src = data.logo_url; img.style.display = 'block';
            }
        }

        async function generateDofaAi() {
            const resDiv = document.getElementById('dofaResults');
            resDiv.innerHTML = '<div style="text-align:center;"><div style="width:40px;height:40px;border:4px solid #ccc;border-top:4px solid #6366f1;border-radius:50%;animation:spin 1s linear infinite;margin:0 auto;"></div><p style="margin-top:10px;">Analizando MEFI y MEFE... Generando estrategias...</p></div>';
            
            try {
                // Here we would call a backend AI endpoint for DOFA. 
                // For now, let's call our business endpoint.
                const resp = await fetch(`/api/business/ai_dofa`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ inst_id: getInstId() })
                });
                
                if (resp.ok) {
                    const data = await resp.json();
                    resDiv.innerHTML = marked.parse(data.analysis);
                } else {
                    resDiv.innerHTML = '<span style="color:red;">Error al generar las estrategias. Asegúrate de haber guardado las matrices MEFI y MEFE primero.</span>';
                }
            } catch(e) {
                resDiv.innerHTML = '<span style="color:red;">Error de red.</span>';
            }
        }

        initPage();
    </script>
"""
with open("c:/SIAC/templates/empresa_dofa.html", "w", encoding="utf-8") as f:
    f.write(header + dofa_content + footer)

print("Created empresa_bcg.html and empresa_dofa.html")
