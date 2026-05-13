// ==========================================
// FACTOR 5: ASPECTOS ACADEMICOS Y EVALUACION
// ==========================================
async function loadFactor5DataGrid(factorId) {
    document.querySelectorAll('.char-item').forEach(el => el.classList.remove('active'));
    const tab = document.getElementById(`char_tab_data_5_${factorId}`);
    if (tab) tab.classList.add('active');

    const container = document.getElementById('aspectsContainer');
    let html = `
        <div class="aspect-detail fade-in">
            <h2>Cuadros Dinámicos - Factor 5: Aspectos Académicos y Evaluación</h2>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <p>Gestión de mallas curriculares, competencias e histórico de revisiones.</p>
                <button class="btn-primary" onclick="saveFactor5Data()">💾 Guardar Todos los Cuadros</button>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 1: Asignaturas Vigentes (Malla Curricular)</h3>
                <table class="data-grid-table" id="tablaAsignaturas">
                    <thead>
                        <tr>
                            <th>Código</th>
                            <th>Asignatura</th>
                            <th>Créditos</th>
                            <th>Semestre</th>
                            <th>Horas Sem.</th>
                            <th>Núcleo Formación</th>
                            <th>Estado</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowAsignatura()">+ Agregar Asignatura</button>
                <div class="chart-container" style="height:300px; margin-top:20px;">
                    <canvas id="chartFactor5"></canvas>
                </div>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 2: Perfil y Competencias</h3>
                <table class="data-grid-table" id="tablaCompetencias">
                    <thead>
                        <tr>
                            <th>Competencia</th>
                            <th>Descripción</th>
                            <th>Tipo (Genérica/Específica)</th>
                            <th>Asignaturas Asociadas</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowCompetencia()">+ Agregar Competencia</button>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 3: Histórico de Revisiones Curriculares</h3>
                <table class="data-grid-table" id="tablaRevisiones">
                    <thead>
                        <tr>
                            <th>Fecha</th>
                            <th>Tipo de Revisión</th>
                            <th>Aspectos Modificados</th>
                            <th>Aprobación (Acta)</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowRevision()">+ Agregar Revisión</button>
            </div>
        </div>
    `;
    container.innerHTML = html;
    await fetchFactor5Data();
}

function addRowAsignatura(data = {codigo:'', nombre:'', creditos:0, semestre:1, horas:0, nucleo:'Básico', estado:'Activa'}) {
    const tbody = document.querySelector('#tablaAsignaturas tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.codigo}" placeholder="Ej. MAT101"></td>
        <td><input type="text" value="${data.nombre}" placeholder="Nombre Asignatura"></td>
        <td><input type="number" value="${data.creditos}" onchange="updateFactor5Charts()"></td>
        <td><input type="number" value="${data.semestre}"></td>
        <td><input type="number" value="${data.horas}"></td>
        <td>
            <select onchange="updateFactor5Charts()">
                <option value="Básico" ${data.nucleo==='Básico'?'selected':''}>Básico</option>
                <option value="Profesional" ${data.nucleo==='Profesional'?'selected':''}>Profesional</option>
                <option value="Electivo" ${data.nucleo==='Electivo'?'selected':''}>Electivo</option>
                <option value="Investigación" ${data.nucleo==='Investigación'?'selected':''}>Investigación</option>
            </select>
        </td>
        <td>
            <select>
                <option value="Activa" ${data.estado==='Activa'?'selected':''}>Activa</option>
                <option value="Inactiva" ${data.estado==='Inactiva'?'selected':''}>Inactiva</option>
            </select>
        </td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove(); updateFactor5Charts();">X</button></td>
    `;
    tbody.appendChild(tr);
    updateFactor5Charts();
}

function addRowCompetencia(data = {competencia:'', descripcion:'', tipo:'Genérica', asignaturas:''}) {
    const tbody = document.querySelector('#tablaCompetencias tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.competencia}" placeholder="Nombre competencia"></td>
        <td><input type="text" value="${data.descripcion}" placeholder="Descripción"></td>
        <td>
            <select>
                <option value="Genérica" ${data.tipo==='Genérica'?'selected':''}>Genérica</option>
                <option value="Específica" ${data.tipo==='Específica'?'selected':''}>Específica</option>
            </select>
        </td>
        <td><input type="text" value="${data.asignaturas}" placeholder="Ej. MAT101, FIS202"></td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove();">X</button></td>
    `;
    tbody.appendChild(tr);
}

function addRowRevision(data = {fecha:'', tipo:'', modificaciones:'', aprobacion:''}) {
    const tbody = document.querySelector('#tablaRevisiones tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="date" value="${data.fecha}"></td>
        <td><input type="text" value="${data.tipo}" placeholder="Ej. Actualización Plan"></td>
        <td><input type="text" value="${data.modificaciones}" placeholder="Breve resumen"></td>
        <td><input type="text" value="${data.aprobacion}" placeholder="Acta 01-2024"></td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove();">X</button></td>
    `;
    tbody.appendChild(tr);
}

function extractFactor5Data() {
    const asignaturas = [];
    document.querySelectorAll('#tablaAsignaturas tbody tr').forEach(tr => {
        const inputs = tr.querySelectorAll('input, select');
        asignaturas.push({
            codigo: inputs[0].value, nombre: inputs[1].value, creditos: inputs[2].value,
            semestre: inputs[3].value, horas: inputs[4].value, nucleo: inputs[5].value, estado: inputs[6].value
        });
    });
    const competencias = [];
    document.querySelectorAll('#tablaCompetencias tbody tr').forEach(tr => {
        const inputs = tr.querySelectorAll('input, select');
        competencias.push({
            competencia: inputs[0].value, descripcion: inputs[1].value, tipo: inputs[2].value, asignaturas: inputs[3].value
        });
    });
    const revisiones = [];
    document.querySelectorAll('#tablaRevisiones tbody tr').forEach(tr => {
        const inputs = tr.querySelectorAll('input');
        revisiones.push({
            fecha: inputs[0].value, tipo: inputs[1].value, modificaciones: inputs[2].value, aprobacion: inputs[3].value
        });
    });
    return { asignaturas, competencias, revisiones };
}

async function saveFactor5Data() {
    const payload = { table_id: 'factor5_curricular', data: extractFactor5Data(), inst_id: getInstId(), program_id: getProgramId() };
    const btn = document.querySelector('button[onclick="saveFactor5Data()"]');
    btn.textContent = 'Guardando...';
    try {
        const res = await fetch('/api/estadisticas', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if(res.ok) alert('Datos guardados correctamente.'); else alert('Error al guardar datos.');
    } catch (err) { alert('Error de conexión.'); }
    btn.textContent = '💾 Guardar Todos los Cuadros';
}

async function fetchFactor5Data() {
    try {
        const res = await fetch(`/api/estadisticas?table_id=factor5_curricular&inst_id=${getInstId()}&program_id=${getProgramId()}`);
        if (res.ok) {
            const json = await res.json();
            if (json && json.data) {
                const data = typeof json.data === 'string' ? JSON.parse(json.data) : json.data;
                if (data.asignaturas && data.asignaturas.length > 0) data.asignaturas.forEach(a => addRowAsignatura(a)); else addRowAsignatura();
                if (data.competencias && data.competencias.length > 0) data.competencias.forEach(c => addRowCompetencia(c)); else addRowCompetencia();
                if (data.revisiones && data.revisiones.length > 0) data.revisiones.forEach(r => addRowRevision(r)); else addRowRevision();
                return;
            }
        }
    } catch(e) {}
    addRowAsignatura(); addRowCompetencia(); addRowRevision();
}

function updateFactor5Charts() {
    const data = extractFactor5Data();
    let ctx = document.getElementById('chartFactor5');
    if (!ctx) return;
    let nucleos = { 'Básico': 0, 'Profesional': 0, 'Electivo': 0, 'Investigación': 0 };
    data.asignaturas.forEach(a => {
        if(nucleos[a.nucleo] !== undefined) nucleos[a.nucleo] += parseFloat(a.creditos || 0);
    });
    if (window.chartF5) window.chartF5.destroy();
    window.chartF5 = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(nucleos),
            datasets: [{
                data: Object.values(nucleos),
                backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { title: { display: true, text: 'Distribución de Créditos por Núcleo de Formación' } } }
    });
}
