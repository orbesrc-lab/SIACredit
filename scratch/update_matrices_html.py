import os

content = """
    <style>
        .matrix-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .matrix-table th, .matrix-table td { border: 1px solid #e2e8f0; padding: 10px; text-align: left; }
        .matrix-table th { background: #f8fafc; font-weight: 600; color: #475569; }
        .matrix-input { width: 100%; padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px; }
        .score-cell { font-weight: 600; text-align: center; }
        .total-row { font-weight: bold; background: #f1f5f9; }
    </style>
    <div class="dofa-header">
        <h1>🛠️ Matrices MEFI y MEFE</h1>
        <p>Evaluación cuantitativa de Factores Internos (MEFI) y Externos (MEFE).</p>
    </div>

    <div class="dofa-tabs">
        <button class="dofa-tab active" onclick="switchMatrixTab('mefi')">1. MEFI (Internos)</button>
        <button class="dofa-tab" onclick="switchMatrixTab('mefe')">2. MEFE (Externos)</button>
    </div>

    <!-- MEFI PANEL -->
    <div id="tabMefi" class="dofa-panel active">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
            <h3>Matriz de Evaluación de Factores Internos</h3>
            <button class="btn-primary" onclick="saveMatrix('mefi')">💾 Guardar MEFI</button>
        </div>
        <table class="matrix-table" id="mefiTable">
            <thead>
                <tr>
                    <th style="width: 45%;">Factor Interno Clave</th>
                    <th style="width: 15%;">Tipo</th>
                    <th style="width: 10%;">Peso</th>
                    <th style="width: 10%;">Calificación</th>
                    <th style="width: 10%;">Puntuación</th>
                    <th style="width: 10%;">Acción</th>
                </tr>
            </thead>
            <tbody id="mefiBody">
                <!-- Rows will be added here -->
            </tbody>
            <tfoot>
                <tr class="total-row">
                    <td colspan="2" style="text-align:right;">Totales:</td>
                    <td id="mefiTotalWeight" style="text-align:center;">0.00</td>
                    <td></td>
                    <td id="mefiTotalScore" class="score-cell">0.00</td>
                    <td></td>
                </tr>
            </tfoot>
        </table>
        <div style="margin-top: 15px;">
            <button class="btn-secondary" onclick="addMatrixRow('mefi')">➕ Añadir Factor Interno</button>
        </div>
    </div>

    <!-- MEFE PANEL -->
    <div id="tabMefe" class="dofa-panel">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
            <h3>Matriz de Evaluación de Factores Externos</h3>
            <button class="btn-primary" onclick="saveMatrix('mefe')">💾 Guardar MEFE</button>
        </div>
        <table class="matrix-table" id="mefeTable">
            <thead>
                <tr>
                    <th style="width: 45%;">Factor Externo Clave</th>
                    <th style="width: 15%;">Tipo</th>
                    <th style="width: 10%;">Peso</th>
                    <th style="width: 10%;">Calificación</th>
                    <th style="width: 10%;">Puntuación</th>
                    <th style="width: 10%;">Acción</th>
                </tr>
            </thead>
            <tbody id="mefeBody">
                <!-- Rows will be added here -->
            </tbody>
            <tfoot>
                <tr class="total-row">
                    <td colspan="2" style="text-align:right;">Totales:</td>
                    <td id="mefeTotalWeight" style="text-align:center;">0.00</td>
                    <td></td>
                    <td id="mefeTotalScore" class="score-cell">0.00</td>
                    <td></td>
                </tr>
            </tfoot>
        </table>
        <div style="margin-top: 15px;">
            <button class="btn-secondary" onclick="addMatrixRow('mefe')">➕ Añadir Factor Externo</button>
        </div>
    </div>

</main>
</div>

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
            
            // Load existing data
            await loadMatrix('mefi');
            await loadMatrix('mefe');
        }

        function switchMatrixTab(tabName) {
            document.querySelectorAll('.dofa-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.dofa-panel').forEach(p => p.classList.remove('active'));
            
            if (tabName === 'mefi') {
                document.querySelectorAll('.dofa-tab')[0].classList.add('active');
                document.getElementById('tabMefi').classList.add('active');
            } else {
                document.querySelectorAll('.dofa-tab')[1].classList.add('active');
                document.getElementById('tabMefe').classList.add('active');
            }
        }

        function addMatrixRow(type, factorData = null) {
            const tbody = document.getElementById(`${type}Body`);
            const tr = document.createElement('tr');
            
            const isMefi = (type === 'mefi');
            const typeOptions = isMefi ? 
                `<option value="fortaleza">Fortaleza</option><option value="debilidad">Debilidad</option>` :
                `<option value="oportunidad">Oportunidad</option><option value="amenaza">Amenaza</option>`;
                
            const factorVal = factorData ? factorData.factor : '';
            const tTypeVal = factorData ? factorData.type : (isMefi ? 'fortaleza' : 'oportunidad');
            const weightVal = factorData ? factorData.weight : 0;
            const ratingVal = factorData ? factorData.rating : 1;
            
            tr.innerHTML = `
                <td><input type="text" class="matrix-input f-name" value="${factorVal}" placeholder="Descripción del factor..."></td>
                <td><select class="matrix-input f-type">${typeOptions}</select></td>
                <td><input type="number" class="matrix-input f-weight" step="0.01" min="0" max="1" value="${weightVal}" onchange="calcTotals('${type}')"></td>
                <td>
                    <select class="matrix-input f-rating" onchange="calcTotals('${type}')">
                        <option value="1">1 (Menor)</option>
                        <option value="2">2 (Promedio)</option>
                        <option value="3">3 (Alto)</option>
                        <option value="4">4 (Mayor)</option>
                    </select>
                </td>
                <td class="score-cell f-score">0.00</td>
                <td style="text-align:center;"><button class="btn-secondary" style="padding:4px 8px; color:red;" onclick="this.closest('tr').remove(); calcTotals('${type}')">X</button></td>
            `;
            tbody.appendChild(tr);
            
            // Set selects
            tr.querySelector('.f-type').value = tTypeVal;
            tr.querySelector('.f-rating').value = ratingVal;
            
            calcTotals(type);
        }

        function calcTotals(type) {
            const tbody = document.getElementById(`${type}Body`);
            let totalWeight = 0;
            let totalScore = 0;
            
            tbody.querySelectorAll('tr').forEach(tr => {
                const w = parseFloat(tr.querySelector('.f-weight').value) || 0;
                const r = parseInt(tr.querySelector('.f-rating').value) || 0;
                const score = w * r;
                tr.querySelector('.f-score').textContent = score.toFixed(2);
                
                totalWeight += w;
                totalScore += score;
            });
            
            document.getElementById(`${type}TotalWeight`).textContent = totalWeight.toFixed(2);
            document.getElementById(`${type}TotalWeight`).style.color = Math.abs(totalWeight - 1.0) > 0.01 ? 'red' : 'green';
            document.getElementById(`${type}TotalScore`).textContent = totalScore.toFixed(2);
        }

        async function loadMatrix(type) {
            try {
                const resp = await fetch(`/api/business/matrix/${type}?inst_id=${getInstId()}`);
                if(resp.ok) {
                    const res = await resp.json();
                    if(res.data && res.data.factors) {
                        res.data.factors.forEach(f => addMatrixRow(type, f));
                    }
                }
            } catch (e) {
                console.error("Error loading matrix:", e);
            }
        }

        async function saveMatrix(type) {
            const tbody = document.getElementById(`${type}Body`);
            const factors = [];
            
            tbody.querySelectorAll('tr').forEach(tr => {
                const name = tr.querySelector('.f-name').value;
                if(name.trim() !== '') {
                    factors.push({
                        factor: name,
                        type: tr.querySelector('.f-type').value,
                        weight: parseFloat(tr.querySelector('.f-weight').value) || 0,
                        rating: parseInt(tr.querySelector('.f-rating').value) || 0
                    });
                }
            });
            
            const totalWeight = document.getElementById(`${type}TotalWeight`).textContent;
            const totalScore = document.getElementById(`${type}TotalScore`).textContent;
            
            if(Math.abs(parseFloat(totalWeight) - 1.0) > 0.01) {
                alert(`Error: La suma de los pesos debe ser 1.00 (Actual: ${totalWeight}). Por favor ajusta los valores antes de guardar.`);
                return;
            }
            
            const payload = {
                inst_id: getInstId(),
                user_id: user.id,
                data: { factors: factors },
                results: { totalScore: parseFloat(totalScore) }
            };
            
            try {
                const resp = await fetch(`/api/business/matrix/${type}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if(resp.ok) {
                    alert('Matriz guardada con éxito.');
                } else {
                    alert('Error al guardar la matriz.');
                }
            } catch(e) {
                alert('Error de conexión.');
            }
        }

        initPage();
    </script>
</body>
</html>
"""

filepath = "c:/SIAC/templates/empresa_matrices.html"
with open(filepath, "r", encoding="utf-8") as f:
    original = f.read()

parts = original.split('<div class="content-area">')
header = parts[0] + '<div class="content-area">\n'

with open(filepath, "w", encoding="utf-8") as f:
    f.write(header + content)

print("Updated empresa_matrices.html")
