import re

base_file = r'c:\SIAC\templates\empresa_dashboard.html'
content = open(base_file, encoding='utf-8').read()

# Split into top and bottom parts using content-area
parts = content.split('<div class="content-area">')
if len(parts) != 2:
    print("Could not split content-area")
    exit(1)

top_html = parts[0] + '<div class="content-area">\n'
bottom_html = '\n</main>\n' + parts[1].split('</main>')[1]

# Now let's define the content for each tool

# 1. Stakeholders
stakeholders_content = """
    <style>
        .tool-header { margin-bottom: 25px; }
        .tool-header h1 { font-size: 1.8rem; margin-bottom: 8px; color: var(--primary-color); }
        .tool-header p { color: var(--text-muted); font-size: 0.95rem; }
        
        .matrix-grid {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        @media (max-width: 1000px) {
            .matrix-grid { grid-template-columns: 1fr; }
        }
        
        .input-panel {
            background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;
        }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 5px; }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9rem;
        }
        
        .chart-panel {
            background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;
            display: flex; flex-direction: column; position: relative;
        }
        
        .stakeholder-table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .stakeholder-table th, .stakeholder-table td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; }
        .stakeholder-table th { background-color: #f8fafc; font-weight: 600; color: #475569; }
        
        .badge { padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
        .b-manage { background: #fef2f2; color: #991b1b; } /* Gestionar de Cerca */
        .b-satisfy { background: #fffbeb; color: #b45309; } /* Mantener Satisfechos */
        .b-inform { background: #eff6ff; color: #1e3a8a; } /* Mantener Informados */
        .b-monitor { background: #f0fdf4; color: #166534; } /* Monitorear */
    </style>
    
    <div class="tool-header">
        <h1>👥 Matriz de Stakeholders (Poder/Interés)</h1>
        <p>Identifique y clasifique a las partes interesadas de su organización para definir estrategias de gestión y comunicación efectivas.</p>
    </div>

    <div class="matrix-grid">
        <div class="input-panel">
            <h3 style="margin-top:0; font-size:1.1rem; border-bottom:1px solid #e2e8f0; padding-bottom:10px;">Nuevo Stakeholder</h3>
            <div class="form-group">
                <label>Nombre / Grupo de Interés</label>
                <input type="text" id="sh_name" placeholder="Ej. Inversores, Proveedores Locales">
            </div>
            <div class="form-group">
                <label>Poder / Influencia (1 - 10)</label>
                <input type="number" id="sh_power" min="1" max="10" value="5">
            </div>
            <div class="form-group">
                <label>Nivel de Interés (1 - 10)</label>
                <input type="number" id="sh_interest" min="1" max="10" value="5">
            </div>
            <div class="form-group">
                <label>Estrategia / Expectativa</label>
                <textarea id="sh_strategy" rows="3" placeholder="Qué esperan de nosotros o cómo planeamos interactuar"></textarea>
            </div>
            <button class="btn-primary" onclick="addStakeholder()" style="width:100%; padding:10px; border-radius:6px; border:none; background:#2563eb; color:white; font-weight:600; cursor:pointer;">
                + Añadir Stakeholder
            </button>
            <button onclick="saveMatrixData()" style="width:100%; margin-top:10px; padding:10px; border-radius:6px; border:1px solid #10b981; background:#f0fdf4; color:#10b981; font-weight:600; cursor:pointer;">
                💾 Guardar Matriz
            </button>
        </div>
        
        <div class="chart-panel">
            <h3 style="margin-top:0; font-size:1.1rem;">Mapa de Posicionamiento</h3>
            <div style="position:relative; flex:1; min-height:400px; width:100%;">
                <canvas id="stakeholderChart"></canvas>
            </div>
            <div style="display:flex; justify-content:center; gap:15px; margin-top:15px; flex-wrap:wrap;">
                <span class="badge b-manage">Poder Alto, Interés Alto (Gestionar de Cerca)</span>
                <span class="badge b-satisfy">Poder Alto, Interés Bajo (Mantener Satisfechos)</span>
                <span class="badge b-inform">Poder Bajo, Interés Alto (Mantener Informados)</span>
                <span class="badge b-monitor">Poder Bajo, Interés Bajo (Monitorear)</span>
            </div>
        </div>
    </div>

    <div>
        <h3 style="margin-bottom:15px; font-size:1.2rem; color:var(--primary-color);">Registro de Partes Interesadas</h3>
        <table class="stakeholder-table">
            <thead>
                <tr>
                    <th>Stakeholder</th>
                    <th>Poder</th>
                    <th>Interés</th>
                    <th>Clasificación</th>
                    <th>Estrategia Sugerida</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody id="stakeholderList">
                <!-- Data injected by JS -->
            </tbody>
        </table>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        let stakeholders = [];
        let chartInstance = null;
        
        // Disable bottom script from dash
        function loadMatriz() {}
        function loadInternos() {}
        function loadExternos() {}

        async function initPageStakeholders() {
            try {
                const resp = await fetch(`/api/business/matrix/STAKEHOLDERS?inst_id=${getInstId()}`);
                if(resp.ok) {
                    const res = await resp.json();
                    if(res.data && res.data.stakeholders) {
                        stakeholders = res.data.stakeholders;
                    }
                }
            } catch(e) { console.error("Error cargando stakeholders", e); }
            
            initChart();
            renderStakeholders();
        }

        function getClassification(power, interest) {
            if(power > 5 && interest > 5) return { label: 'Gestionar de Cerca', class: 'b-manage' };
            if(power > 5 && interest <= 5) return { label: 'Mantener Satisfechos', class: 'b-satisfy' };
            if(power <= 5 && interest > 5) return { label: 'Mantener Informados', class: 'b-inform' };
            return { label: 'Monitorear', class: 'b-monitor' };
        }

        function initChart() {
            const ctx = document.getElementById('stakeholderChart').getContext('2d');
            
            chartInstance = new Chart(ctx, {
                type: 'scatter',
                data: { datasets: [] },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(ctx) {
                                    return ctx.raw.label + ' (Poder: ' + ctx.raw.x + ', Interés: ' + ctx.raw.y + ')';
                                }
                            }
                        }
                    },
                    scales: {
                        x: { 
                            title: { display: true, text: 'Poder / Influencia', font:{weight:'bold'} },
                            min: 0, max: 10,
                            grid: { color: (ctx) => ctx.tick.value === 5 ? 'rgba(0,0,0,0.5)' : 'rgba(0,0,0,0.1)', lineWidth: (ctx) => ctx.tick.value === 5 ? 2 : 1 }
                        },
                        y: { 
                            title: { display: true, text: 'Nivel de Interés', font:{weight:'bold'} },
                            min: 0, max: 10,
                            grid: { color: (ctx) => ctx.tick.value === 5 ? 'rgba(0,0,0,0.5)' : 'rgba(0,0,0,0.1)', lineWidth: (ctx) => ctx.tick.value === 5 ? 2 : 1 }
                        }
                    }
                }
            });
            updateChart();
        }

        function updateChart() {
            if(!chartInstance) return;
            const dataPoints = stakeholders.map((s, idx) => {
                let color = '#10b981'; // Monitor
                if(s.power > 5 && s.interest > 5) color = '#ef4444'; // Manage
                else if(s.power > 5 && s.interest <= 5) color = '#f59e0b'; // Satisfy
                else if(s.power <= 5 && s.interest > 5) color = '#3b82f6'; // Inform
                
                return {
                    x: s.power, y: s.interest, label: s.name, backgroundColor: color, pointRadius: 8, pointHoverRadius: 10
                };
            });
            
            chartInstance.data.datasets = [{
                label: 'Stakeholders',
                data: dataPoints,
                backgroundColor: dataPoints.map(d => d.backgroundColor),
            }];
            chartInstance.update();
        }

        function addStakeholder() {
            const name = document.getElementById('sh_name').value.trim();
            const power = parseInt(document.getElementById('sh_power').value);
            const interest = parseInt(document.getElementById('sh_interest').value);
            const strategy = document.getElementById('sh_strategy').value.trim();
            
            if(!name) return alert("Por favor ingresa un nombre para el stakeholder.");
            
            stakeholders.push({ id: Date.now(), name, power, interest, strategy });
            
            document.getElementById('sh_name').value = '';
            document.getElementById('sh_strategy').value = '';
            
            renderStakeholders();
        }

        function removeStakeholder(idx) {
            stakeholders.splice(idx, 1);
            renderStakeholders();
        }

        function renderStakeholders() {
            const tbody = document.getElementById('stakeholderList');
            tbody.innerHTML = '';
            
            if(stakeholders.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#94a3b8;">No hay stakeholders registrados.</td></tr>';
            } else {
                stakeholders.forEach((s, idx) => {
                    const cls = getClassification(s.power, s.interest);
                    tbody.innerHTML += `
                        <tr>
                            <td><strong>${s.name}</strong></td>
                            <td>${s.power}/10</td>
                            <td>${s.interest}/10</td>
                            <td><span class="badge ${cls.class}">${cls.label}</span></td>
                            <td>${s.strategy || '<span style="color:#cbd5e1;">-</span>'}</td>
                            <td>
                                <button onclick="removeStakeholder(${idx})" style="background:none; border:none; color:#ef4444; cursor:pointer;"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
                    `;
                });
            }
            updateChart();
        }

        async function saveMatrixData() {
            const payload = {
                inst_id: getInstId(),
                user_id: user.id,
                data: { stakeholders: stakeholders },
                results: {}
            };
            
            try {
                const resp = await fetch('/api/business/matrix/STAKEHOLDERS', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(resp.ok) {
                    alert("✅ Matriz de Stakeholders guardada con éxito.");
                } else {
                    alert("Error al guardar.");
                }
            } catch(e) {
                alert("Error de red.");
            }
        }
        
        // Hook to override initPage from dashboard
        setTimeout(() => {
            initPageStakeholders();
        }, 500);
    </script>
"""

# Replace in bottom_html the specific calls we don't need
clean_bottom = bottom_html.replace('initPage();', '')

with open(r'c:\SIAC\templates\empresa_stakeholders.html', 'w', encoding='utf-8') as f:
    f.write(top_html + stakeholders_content + clean_bottom)


print("Generated empresa_stakeholders.html successfully.")
