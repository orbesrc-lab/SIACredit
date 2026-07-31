import re

base_file = r'c:\SIAC\templates\dofa.html'
content = open(base_file, encoding='utf-8').read()

parts = content.split('<div class="content-area">')
top_html = parts[0] + '<div class="content-area">\n'
bottom_html = '\n</main>\n' + parts[1].split('</main>')[1]
clean_bottom = bottom_html.replace('initPage();', '')

porter_content = """
    <style>
        .tool-header { margin-bottom: 25px; }
        .tool-header h1 { font-size: 1.8rem; margin-bottom: 8px; color: var(--primary-color); }
        .tool-header p { color: var(--text-muted); font-size: 0.95rem; }
        
        .porter-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        @media (max-width: 900px) { .porter-grid { grid-template-columns: 1fr; } }
        
        .input-panel {
            background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;
        }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 5px; }
        .form-group textarea {
            width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9rem; resize: vertical; min-height: 60px;
        }
        
        .chart-panel {
            background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;
            display: flex; flex-direction: column; align-items: center; position: relative;
        }
        
        .results-panel {
            background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px;
            margin-top: 20px; display: none;
        }
        
        .force-card {
            background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 15px;
            position: relative;
        }
        .force-card h4 { margin: 0 0 10px; color: #1e293b; font-size: 1.1rem; display: flex; justify-content: space-between; }
        .force-score { background: #3b82f6; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.85rem; }
        
        .spinner-overlay {
            position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255,255,255,0.8);
            display: flex; justify-content: center; align-items: center; flex-direction: column;
            border-radius: 12px; z-index: 10; display: none;
        }
        .spinner {
            border: 4px solid rgba(0,0,0,0.1); width: 40px; height: 40px; border-radius: 50%;
            border-left-color: #2563eb; animation: spin 1s linear infinite; margin-bottom: 10px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
    
    <div class="tool-header">
        <h1>📈 5 Fuerzas de Porter + IA</h1>
        <p>Analice el entorno competitivo de su industria y descubra qué fuerzas presionan su rentabilidad.</p>
    </div>

    <div class="porter-grid">
        <div class="input-panel">
            <h3 style="margin-top:0; font-size:1.1rem; border-bottom:1px solid #e2e8f0; padding-bottom:10px; margin-bottom:15px;">Contexto de la Industria</h3>
            <p style="font-size:0.85rem; color:#64748b; margin-bottom:15px;">Describe brevemente la situación de tu empresa frente a cada fuerza. Si lo dejas en blanco, la IA asumirá un escenario estándar basado en tu sector general.</p>
            
            <div class="form-group">
                <label>1. Rivalidad entre competidores existentes</label>
                <textarea id="p_rivalidad" placeholder="Ej. Hay muchos competidores que ofrecen precios bajos..."></textarea>
            </div>
            <div class="form-group">
                <label>2. Poder de negociación de proveedores</label>
                <textarea id="p_proveedores" placeholder="Ej. Dependemos de 2 grandes proveedores de materia prima..."></textarea>
            </div>
            <div class="form-group">
                <label>3. Poder de negociación de clientes</label>
                <textarea id="p_clientes" placeholder="Ej. Nuestros clientes son corporaciones grandes que exigen descuentos..."></textarea>
            </div>
            <div class="form-group">
                <label>4. Amenaza de nuevos entrantes</label>
                <textarea id="p_entrantes" placeholder="Ej. Es muy caro abrir una fábrica como la nuestra (barreras altas)..."></textarea>
            </div>
            <div class="form-group">
                <label>5. Amenaza de productos sustitutos</label>
                <textarea id="p_sustitutos" placeholder="Ej. Hay tecnologías nuevas que hacen casi lo mismo más barato..."></textarea>
            </div>
            
            <button class="btn-primary" onclick="analyzePorter()" style="width:100%; padding:12px; border-radius:6px; border:none; background:linear-gradient(135deg, #8b5cf6, #3b82f6); color:white; font-weight:bold; font-size:1rem; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px;">
                <i class="fas fa-robot"></i> Generar Análisis con IA
            </button>
        </div>
        
        <div class="chart-panel">
            <h3 style="margin-top:0; font-size:1.1rem; width:100%; text-align:center;">Mapa de Presión Competitiva</h3>
            <div style="position:relative; width:100%; max-width:400px; aspect-ratio:1; margin-top:20px;">
                <canvas id="porterChart"></canvas>
            </div>
            <p style="font-size:0.8rem; color:#64748b; text-align:center; margin-top:20px; padding:0 20px;">
                <strong>10 = Máxima Amenaza/Presión.</strong> Un área más grande en el gráfico significa que la industria es más hostil y menos rentable.
            </p>
            
            <div class="spinner-overlay" id="loadingOverlay">
                <div class="spinner"></div>
                <div style="font-weight:bold; color:#1e293b;">La IA está analizando tu industria...</div>
                <div style="font-size:0.8rem; color:#64748b;">(Esto puede tomar unos 10 segundos)</div>
            </div>
        </div>
    </div>

    <div class="results-panel" id="resultsPanel">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border-bottom:2px solid #e2e8f0; padding-bottom:10px;">
            <h2 style="margin:0; font-size:1.4rem; color:#1e293b;">Diagnóstico Estratégico Detallado</h2>
            <button onclick="saveMatrixData()" style="padding:8px 15px; border-radius:6px; border:none; background:#10b981; color:white; font-weight:600; cursor:pointer;">
                💾 Guardar Resultado
            </button>
        </div>
        
        <div style="background:#eff6ff; padding:15px; border-radius:8px; border-left:4px solid #3b82f6; margin-bottom:25px;">
            <strong style="color:#1e3a8a;">Conclusión Global:</strong>
            <p id="globalConclusion" style="margin:8px 0 0; color:#334155; font-size:0.95rem; line-height:1.5;"></p>
        </div>
        
        <div id="forcesList">
            <!-- JS Injected -->
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        let currentAnalysis = null;
        let chartInstance = null;
        
        function loadMatriz() {}
        function loadInternos() {}
        function loadExternos() {}

        async function initPagePorter() {
            try {
                const resp = await fetch(`/api/business/matrix/PORTER?inst_id=${getInstId()}`);
                if(resp.ok) {
                    const res = await resp.json();
                    if(res.data && res.data.analysis) {
                        currentAnalysis = res.data.analysis;
                        // Populate inputs if saved
                        if(res.data.inputs) {
                            document.getElementById('p_rivalidad').value = res.data.inputs.rivalidad || '';
                            document.getElementById('p_proveedores').value = res.data.inputs.proveedores || '';
                            document.getElementById('p_clientes').value = res.data.inputs.clientes || '';
                            document.getElementById('p_entrantes').value = res.data.inputs.entrantes || '';
                            document.getElementById('p_sustitutos').value = res.data.inputs.sustitutos || '';
                        }
                    }
                }
            } catch(e) { console.error("Error cargando Porter", e); }
            
            initChart();
            if(currentAnalysis) {
                renderResults();
            }
        }

        function initChart() {
            const ctx = document.getElementById('porterChart').getContext('2d');
            
            const dataScores = currentAnalysis ? [
                getScore('Rivalidad'), getScore('Proveedores'), getScore('Clientes'), getScore('Nuevos Entrantes'), getScore('Sustitutos')
            ] : [0,0,0,0,0];
            
            chartInstance = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['Rivalidad', 'Poder Proveedores', 'Poder Clientes', 'Nuevos Entrantes', 'Sustitutos'],
                    datasets: [{
                        label: 'Nivel de Presión (1-10)',
                        data: dataScores,
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        borderColor: '#3b82f6',
                        pointBackgroundColor: '#2563eb',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    scales: {
                        r: {
                            angleLines: { display: true },
                            suggestedMin: 0, suggestedMax: 10,
                            ticks: { stepSize: 2 }
                        }
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }
        
        function getScore(forceName) {
            if(!currentAnalysis || !currentAnalysis.scores) return 0;
            const f = currentAnalysis.scores.find(s => s.force.toLowerCase().includes(forceName.toLowerCase().split(' ')[0]));
            return f ? f.score : 0;
        }

        function updateChart() {
            if(!chartInstance || !currentAnalysis) return;
            chartInstance.data.datasets[0].data = [
                getScore('Rivalidad'), getScore('Proveedores'), getScore('Clientes'), getScore('Nuevos Entrantes'), getScore('Sustitutos')
            ];
            chartInstance.update();
        }

        async function analyzePorter() {
            const inputs = {
                rivalidad: document.getElementById('p_rivalidad').value.trim(),
                proveedores: document.getElementById('p_proveedores').value.trim(),
                clientes: document.getElementById('p_clientes').value.trim(),
                entrantes: document.getElementById('p_entrantes').value.trim(),
                sustitutos: document.getElementById('p_sustitutos').value.trim(),
            };
            
            document.getElementById('loadingOverlay').style.display = 'flex';
            
            try {
                const resp = await fetch('/api/business/ai_porter', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ inst_id: getInstId(), forces: inputs })
                });
                
                const data = await resp.json();
                
                if(data.status === 'success' && data.analysis) {
                    currentAnalysis = data.analysis;
                    currentAnalysis.inputs_used = inputs;
                    renderResults();
                    // Save automatically
                    saveMatrixData(true);
                } else {
                    alert("Error en el análisis de IA: " + (data.error || "Desconocido"));
                }
            } catch(e) {
                alert("Error de red contactando a la IA.");
            } finally {
                document.getElementById('loadingOverlay').style.display = 'none';
            }
        }

        function renderResults() {
            document.getElementById('resultsPanel').style.display = 'block';
            document.getElementById('globalConclusion').textContent = currentAnalysis.global_conclusion || "Sin conclusión.";
            
            const list = document.getElementById('forcesList');
            list.innerHTML = '';
            
            if(currentAnalysis.scores) {
                currentAnalysis.scores.forEach(s => {
                    let color = '#10b981'; // Green (Low pressure)
                    if(s.score >= 8) color = '#ef4444'; // Red (High)
                    else if(s.score >= 5) color = '#eab308'; // Yellow (Med)
                    
                    list.innerHTML += `
                        <div class="force-card">
                            <h4>
                                ${s.force} 
                                <span class="force-score" style="background:${color};">Presión: ${s.score}/10</span>
                            </h4>
                            <p style="font-size:0.9rem; color:#475569; margin:0 0 8px;"><strong>Análisis:</strong> ${s.description}</p>
                            <p style="font-size:0.9rem; color:#1e293b; margin:0;"><strong>Estrategia:</strong> ${s.strategy}</p>
                        </div>
                    `;
                });
            }
            updateChart();
            
            // Scroll to results
            document.getElementById('resultsPanel').scrollIntoView({behavior: 'smooth'});
        }

        async function saveMatrixData(silent = false) {
            if(!currentAnalysis) return;
            
            const payload = {
                inst_id: getInstId(),
                user_id: user.id,
                data: { analysis: currentAnalysis, inputs: currentAnalysis.inputs_used },
                results: {}
            };
            
            try {
                const resp = await fetch('/api/business/matrix/PORTER', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(resp.ok && !silent) {
                    alert("✅ Análisis de Porter guardado con éxito.");
                }
            } catch(e) {
                if(!silent) alert("Error de red al guardar.");
            }
        }
        
        setTimeout(() => { initPagePorter(); }, 500);
    </script>
"""

with open(r'c:\SIAC\templates\empresa_porter.html', 'w', encoding='utf-8') as f:
    f.write(top_html + porter_content + clean_bottom)

print("Generated empresa_porter.html successfully.")
