import re

base_file = r'c:\SIAC\templates\dofa.html'
content = open(base_file, encoding='utf-8').read()

parts = content.split('<div class="content-area">')
top_html = parts[0] + '<div class="content-area">\n'
bottom_html = '\n</main>\n' + parts[1].split('</main>')[1]
clean_bottom = bottom_html.replace('initPage();', '')

# 4. ISO
iso_content = """
    <style>
        .tool-header { margin-bottom: 25px; }
        .tool-header h1 { font-size: 1.8rem; margin-bottom: 8px; color: var(--primary-color); }
        .tool-header p { color: var(--text-muted); font-size: 0.95rem; }
        
        .iso-panel {
            background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 30px;
        }
        
        .clause-group {
            margin-bottom: 20px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;
        }
        .clause-header {
            background: #f8fafc; padding: 15px; font-weight: bold; color: #1e293b; display: flex; justify-content: space-between; align-items: center; cursor: pointer;
        }
        .clause-header:hover { background: #f1f5f9; }
        .clause-body {
            padding: 15px; border-top: 1px solid #e2e8f0; display: none;
        }
        .clause-group.active .clause-body { display: block; }
        .clause-group.active .clause-header { background: #eff6ff; color: #1d4ed8; border-bottom: 1px solid #bfdbfe; }
        
        .question-item {
            display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px dashed #e2e8f0;
        }
        .question-item:last-child { border-bottom: none; }
        .q-text { flex: 1; padding-right: 20px; font-size: 0.9rem; color: #334155; }
        
        .q-score select {
            padding: 8px; border-radius: 6px; border: 1px solid #cbd5e1; outline: none; background: white;
        }
        
        .score-box {
            display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 25px;
        }
        .score-card {
            background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center;
        }
        .score-value {
            font-size: 2.5rem; font-weight: 800; margin: 10px 0; color: #2563eb;
        }
    </style>
    
    <div class="tool-header">
        <h1>🏆 Gap Analysis Normativo (ISO 9001 / 14001)</h1>
        <p>Evaluación de madurez frente a los requisitos de los Sistemas de Gestión de Calidad y Medio Ambiente (Estructura de Alto Nivel HLS).</p>
    </div>

    <div class="score-box">
        <div class="score-card">
            <h3 style="margin:0; color:#64748b; font-size:1rem;">Madurez Global (Gap)</h3>
            <div class="score-value" id="globalScore">0%</div>
            <div style="font-size:0.85rem; color:#94a3b8;">100% = Certificable</div>
        </div>
        <div class="score-card">
            <h3 style="margin:0; color:#64748b; font-size:1rem;">Acción Recomendada</h3>
            <div class="score-value" id="actionText" style="font-size:1.5rem; color:#ef4444;">Fase Inicial</div>
            <button onclick="saveMatrixData()" style="margin-top:10px; padding:8px 15px; border-radius:6px; border:none; background:#10b981; color:white; font-weight:600; cursor:pointer;">
                💾 Guardar Evaluación
            </button>
        </div>
    </div>

    <div class="iso-panel" id="isoContainer">
        <!-- JS Injected -->
    </div>

    <script>
        const isoChecklist = [
            { id: 4, title: "Cláusula 4: Contexto de la Organización", items: [
                { id: "4.1", text: "Comprensión de la organización y su contexto (Factores Internos/Externos)." },
                { id: "4.2", text: "Comprensión de las necesidades y expectativas de las partes interesadas." },
                { id: "4.3", text: "Determinación del alcance del sistema de gestión." }
            ]},
            { id: 5, title: "Cláusula 5: Liderazgo", items: [
                { id: "5.1", text: "Liderazgo y compromiso de la alta dirección." },
                { id: "5.2", text: "Política (Calidad / Ambiental) establecida y comunicada." },
                { id: "5.3", text: "Roles, responsabilidades y autoridades definidas." }
            ]},
            { id: 6, title: "Cláusula 6: Planificación", items: [
                { id: "6.1", text: "Acciones para abordar riesgos y oportunidades." },
                { id: "6.2", text: "Objetivos (Calidad / Ambientales) y planificación para lograrlos." }
            ]},
            { id: 7, title: "Cláusula 7: Apoyo / Soporte", items: [
                { id: "7.1", text: "Recursos provistos (personas, infraestructura, ambiente)." },
                { id: "7.2", text: "Competencia y toma de conciencia del personal." },
                { id: "7.4", text: "Comunicación (interna y externa) planificada." },
                { id: "7.5", text: "Información documentada controlada." }
            ]},
            { id: 8, title: "Cláusula 8: Operación", items: [
                { id: "8.1", text: "Planificación y control operacional." },
                { id: "8.2", text: "Requisitos para productos y servicios." },
                { id: "8.4", text: "Control de procesos, productos y servicios suministrados externamente." }
            ]},
            { id: 9, title: "Cláusula 9: Evaluación del Desempeño", items: [
                { id: "9.1", text: "Seguimiento, medición, análisis y evaluación." },
                { id: "9.2", text: "Auditoría interna ejecutada de manera planificada." },
                { id: "9.3", text: "Revisión por la dirección." }
            ]},
            { id: 10, title: "Cláusula 10: Mejora", items: [
                { id: "10.1", text: "Oportunidades de mejora y cumplimiento." },
                { id: "10.2", text: "Gestión de No Conformidades y Acciones Correctivas." }
            ]}
        ];

        let evaluations = {};
        
        function loadMatriz() {}
        function loadInternos() {}
        function loadExternos() {}

        async function initPageISO() {
            try {
                const resp = await fetch(`/api/business/matrix/ISO?inst_id=${getInstId()}`);
                if(resp.ok) {
                    const res = await resp.json();
                    if(res.data && res.data.evaluations) {
                        evaluations = res.data.evaluations;
                    }
                }
            } catch(e) { console.error("Error cargando iso", e); }
            
            renderChecklist();
            calculateScore();
        }

        function toggleClause(id) {
            document.getElementById(`clause_${id}`).classList.toggle('active');
        }

        function renderChecklist() {
            const container = document.getElementById('isoContainer');
            container.innerHTML = '';
            
            isoChecklist.forEach(clause => {
                let itemsHtml = '';
                clause.items.forEach(item => {
                    const val = evaluations[item.id] || 0;
                    itemsHtml += `
                        <div class="question-item">
                            <div class="q-text"><strong>${item.id}</strong> - ${item.text}</div>
                            <div class="q-score">
                                <select onchange="updateScore('${item.id}', this.value)">
                                    <option value="0" ${val==0?'selected':''}>0 - No iniciado</option>
                                    <option value="1" ${val==1?'selected':''}>1 - Planificado</option>
                                    <option value="2" ${val==2?'selected':''}>2 - En desarrollo</option>
                                    <option value="3" ${val==3?'selected':''}>3 - Implementado (No documentado)</option>
                                    <option value="4" ${val==4?'selected':''}>4 - Implementado y Documentado</option>
                                    <option value="5" ${val==5?'selected':''}>5 - Totalmente (Auditado/Certificable)</option>
                                </select>
                            </div>
                        </div>
                    `;
                });
                
                container.innerHTML += `
                    <div class="clause-group" id="clause_${clause.id}">
                        <div class="clause-header" onclick="toggleClause(${clause.id})">
                            <span>${clause.title}</span>
                            <span>▼</span>
                        </div>
                        <div class="clause-body">
                            ${itemsHtml}
                        </div>
                    </div>
                `;
            });
        }

        function updateScore(id, val) {
            evaluations[id] = parseInt(val);
            calculateScore();
        }

        function calculateScore() {
            let totalMax = 0;
            let current = 0;
            
            isoChecklist.forEach(clause => {
                clause.items.forEach(item => {
                    totalMax += 5;
                    current += evaluations[item.id] || 0;
                });
            });
            
            const pct = totalMax === 0 ? 0 : Math.round((current / totalMax) * 100);
            const scoreEl = document.getElementById('globalScore');
            const actionEl = document.getElementById('actionText');
            
            scoreEl.textContent = `${pct}%`;
            
            if(pct >= 90) {
                scoreEl.style.color = '#16a34a';
                actionEl.textContent = 'Listo para Certificación';
                actionEl.style.color = '#16a34a';
            } else if(pct >= 60) {
                scoreEl.style.color = '#ca8a04';
                actionEl.textContent = 'Requiere Auditoría Interna';
                actionEl.style.color = '#ca8a04';
            } else {
                scoreEl.style.color = '#dc2626';
                actionEl.textContent = 'Fase Inicial / Planificación';
                actionEl.style.color = '#dc2626';
            }
        }

        async function saveMatrixData() {
            const payload = {
                inst_id: getInstId(),
                user_id: user.id,
                data: { evaluations: evaluations },
                results: {}
            };
            
            try {
                const resp = await fetch('/api/business/matrix/ISO', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(resp.ok) {
                    alert("✅ Evaluación ISO guardada con éxito.");
                } else {
                    alert("Error al guardar.");
                }
            } catch(e) {
                alert("Error de red.");
            }
        }
        
        setTimeout(() => { initPageISO(); }, 500);
    </script>
"""

with open(r'c:\SIAC\templates\empresa_iso.html', 'w', encoding='utf-8') as f:
    f.write(top_html + iso_content + clean_bottom)

print("Generated empresa_iso.html successfully.")
