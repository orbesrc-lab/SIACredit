import re

base_file = r'c:\SIAC\templates\empresa_dashboard.html'
content = open(base_file, encoding='utf-8').read()

parts = content.split('<div class="content-area">')
top_html = parts[0] + '<div class="content-area">\n'
bottom_html = '\n</main>\n' + parts[1].split('</main>')[1]
clean_bottom = bottom_html.replace('initPage();', '')

# 2. Riesgos
riesgos_content = """
    <style>
        .tool-header { margin-bottom: 25px; }
        .tool-header h1 { font-size: 1.8rem; margin-bottom: 8px; color: var(--primary-color); }
        .tool-header p { color: var(--text-muted); font-size: 0.95rem; }
        
        .matrix-grid {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        @media (max-width: 1000px) { .matrix-grid { grid-template-columns: 1fr; } }
        
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
            display: flex; flex-direction: column; align-items: center;
        }
        
        .heatmap-container {
            display: grid;
            grid-template-columns: 30px repeat(5, 1fr);
            grid-template-rows: repeat(5, 1fr) 30px;
            width: 100%; max-width: 500px; aspect-ratio: 1;
            gap: 2px; position: relative;
        }
        .hm-cell {
            display: flex; align-items: center; justify-content: center;
            font-weight: bold; color: white; text-shadow: 0 1px 2px rgba(0,0,0,0.4);
            border-radius: 4px; font-size: 1.2rem; transition: transform 0.2s;
            cursor: pointer; position: relative;
        }
        .hm-cell:hover { transform: scale(1.05); z-index: 10; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        
        .hm-low { background-color: #22c55e; } /* Green */
        .hm-med { background-color: #eab308; } /* Yellow */
        .hm-high { background-color: #ef4444; } /* Red */
        
        .hm-axis-y { grid-column: 1; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; color: #64748b; transform: rotate(-90deg); white-space: nowrap; }
        .hm-axis-x { grid-column: 2 / -1; grid-row: 6; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; color: #64748b; }
        
        .stakeholder-table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .stakeholder-table th, .stakeholder-table td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; }
        .stakeholder-table th { background-color: #f8fafc; font-weight: 600; color: #475569; }
        
        .badge { padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; color: white; }
        .risk-count { position: absolute; top: 4px; right: 4px; background: white; color: #1e293b; border-radius: 50%; width: 20px; height: 20px; font-size: 0.7rem; display: flex; align-items: center; justify-content: center; text-shadow: none; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
    </style>
    
    <div class="tool-header">
        <h1>⚠️ Matriz de Riesgos (Probabilidad × Impacto)</h1>
        <p>Valore los riesgos corporativos para definir planes de contingencia y mitigación según su severidad.</p>
    </div>

    <div class="matrix-grid">
        <div class="input-panel">
            <h3 style="margin-top:0; font-size:1.1rem; border-bottom:1px solid #e2e8f0; padding-bottom:10px;">Nuevo Riesgo</h3>
            <div class="form-group">
                <label>Descripción del Riesgo</label>
                <input type="text" id="r_desc" placeholder="Ej. Fuga de talentos clave">
            </div>
            <div class="form-group">
                <label>Probabilidad (1 - Raro a 5 - Casi Certeza)</label>
                <select id="r_prob">
                    <option value="1">1 - Raro</option>
                    <option value="2">2 - Improbable</option>
                    <option value="3">3 - Posible</option>
                    <option value="4">4 - Probable</option>
                    <option value="5">5 - Casi Certeza</option>
                </select>
            </div>
            <div class="form-group">
                <label>Impacto (1 - Insignificante a 5 - Catastrófico)</label>
                <select id="r_impact">
                    <option value="1">1 - Insignificante</option>
                    <option value="2">2 - Menor</option>
                    <option value="3">3 - Moderado</option>
                    <option value="4">4 - Mayor</option>
                    <option value="5">5 - Catastrófico</option>
                </select>
            </div>
            <div class="form-group">
                <label>Plan de Mitigación / Controles</label>
                <textarea id="r_plan" rows="3" placeholder="Acciones para reducir la probabilidad o impacto"></textarea>
            </div>
            <button class="btn-primary" onclick="addRisk()" style="width:100%; padding:10px; border-radius:6px; border:none; background:#ef4444; color:white; font-weight:600; cursor:pointer;">
                + Añadir Riesgo
            </button>
            <button onclick="saveMatrixData()" style="width:100%; margin-top:10px; padding:10px; border-radius:6px; border:1px solid #10b981; background:#f0fdf4; color:#10b981; font-weight:600; cursor:pointer;">
                💾 Guardar Matriz
            </button>
        </div>
        
        <div class="chart-panel">
            <h3 style="margin-top:0; font-size:1.1rem; width: 100%;">Mapa de Calor de Riesgos</h3>
            <div style="display:flex; width: 100%; height: 100%; align-items:center; justify-content:center; padding: 20px;">
                <div class="heatmap-container" id="heatmapGrid">
                    <!-- JS Grid Injected -->
                </div>
            </div>
            <div style="display:flex; justify-content:center; gap:15px; margin-top:15px; width: 100%;">
                <span style="font-size: 0.8rem;"><span style="display:inline-block; width:12px; height:12px; background:#22c55e; border-radius:2px;"></span> Riesgo Bajo (1-6)</span>
                <span style="font-size: 0.8rem;"><span style="display:inline-block; width:12px; height:12px; background:#eab308; border-radius:2px;"></span> Riesgo Medio (8-12)</span>
                <span style="font-size: 0.8rem;"><span style="display:inline-block; width:12px; height:12px; background:#ef4444; border-radius:2px;"></span> Riesgo Alto (15-25)</span>
            </div>
        </div>
    </div>

    <div>
        <h3 style="margin-bottom:15px; font-size:1.2rem; color:var(--primary-color);">Registro de Riesgos</h3>
        <table class="stakeholder-table">
            <thead>
                <tr>
                    <th>Riesgo</th>
                    <th>Probabilidad</th>
                    <th>Impacto</th>
                    <th>Nivel (PxI)</th>
                    <th>Plan de Mitigación</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody id="riskList">
                <!-- Data injected by JS -->
            </tbody>
        </table>
    </div>

    <script>
        let risks = [];
        
        function loadMatriz() {}
        function loadInternos() {}
        function loadExternos() {}

        async function initPageRisks() {
            try {
                const resp = await fetch(`/api/business/matrix/RIESGOS?inst_id=${getInstId()}`);
                if(resp.ok) {
                    const res = await resp.json();
                    if(res.data && res.data.risks) {
                        risks = res.data.risks;
                    }
                }
            } catch(e) { console.error("Error cargando riesgos", e); }
            
            renderHeatmap();
            renderRisks();
        }

        function getRiskLevel(score) {
            if(score >= 15) return { label: 'Alto', class: 'hm-high' };
            if(score >= 8) return { label: 'Medio', class: 'hm-med' };
            return { label: 'Bajo', class: 'hm-low' };
        }

        function renderHeatmap() {
            const grid = document.getElementById('heatmapGrid');
            grid.innerHTML = '<div class="hm-axis-y">Probabilidad</div><div class="hm-axis-x">Impacto</div>';
            
            // 5x5 grid (row 1 is probability 5, col 1 is impact 1)
            for(let p = 5; p >= 1; p--) {
                for(let i = 1; i <= 5; i++) {
                    const score = p * i;
                    const level = getRiskLevel(score);
                    
                    // Count risks in this cell
                    const count = risks.filter(r => r.prob === p && r.impact === i).length;
                    const badge = count > 0 ? `<div class="risk-count">${count}</div>` : '';
                    
                    grid.innerHTML += `
                        <div class="hm-cell ${level.class}" style="grid-row:${6-p}; grid-column:${i+1};" title="Prob:${p} x Imp:${i} = ${score}">
                            ${score}
                            ${badge}
                        </div>
                    `;
                }
            }
        }

        function addRisk() {
            const desc = document.getElementById('r_desc').value.trim();
            const prob = parseInt(document.getElementById('r_prob').value);
            const impact = parseInt(document.getElementById('r_impact').value);
            const plan = document.getElementById('r_plan').value.trim();
            
            if(!desc) return alert("Por favor ingresa la descripción del riesgo.");
            
            risks.push({ id: Date.now(), desc, prob, impact, plan });
            
            document.getElementById('r_desc').value = '';
            document.getElementById('r_plan').value = '';
            
            renderRisks();
            renderHeatmap();
        }

        function removeRisk(idx) {
            risks.splice(idx, 1);
            renderRisks();
            renderHeatmap();
        }

        function renderRisks() {
            const tbody = document.getElementById('riskList');
            tbody.innerHTML = '';
            
            if(risks.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#94a3b8;">No hay riesgos registrados.</td></tr>';
            } else {
                // Sort by score descending
                const sortedRisks = [...risks].map((r, i) => ({...r, originalIdx: i, score: r.prob * r.impact}))
                                            .sort((a,b) => b.score - a.score);
                                            
                sortedRisks.forEach((r) => {
                    const level = getRiskLevel(r.score);
                    tbody.innerHTML += `
                        <tr>
                            <td><strong>${r.desc}</strong></td>
                            <td>${r.prob}</td>
                            <td>${r.impact}</td>
                            <td><span class="badge ${level.class}">${r.score} - ${level.label}</span></td>
                            <td>${r.plan || '<span style="color:#cbd5e1;">-</span>'}</td>
                            <td>
                                <button onclick="removeRisk(${r.originalIdx})" style="background:none; border:none; color:#ef4444; cursor:pointer;"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
                    `;
                });
            }
        }

        async function saveMatrixData() {
            const payload = {
                inst_id: getInstId(),
                user_id: user.id,
                data: { risks: risks },
                results: {}
            };
            
            try {
                const resp = await fetch('/api/business/matrix/RIESGOS', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(resp.ok) {
                    alert("✅ Matriz de Riesgos guardada con éxito.");
                } else {
                    alert("Error al guardar.");
                }
            } catch(e) {
                alert("Error de red.");
            }
        }
        
        setTimeout(() => { initPageRisks(); }, 500);
    </script>
"""

with open(r'c:\SIAC\templates\empresa_riesgos.html', 'w', encoding='utf-8') as f:
    f.write(top_html + riesgos_content + clean_bottom)

print("Generated empresa_riesgos.html successfully.")
