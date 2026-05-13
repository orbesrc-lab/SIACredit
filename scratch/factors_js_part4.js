// ==========================================
// FACTOR 10: RECURSOS Y AMBIENTES (INFRAESTRUCTURA Y MEDIOS)
// ==========================================
async function loadFactor10DataGrid(factorId) {
    document.querySelectorAll('.char-item').forEach(el => el.classList.remove('active'));
    const tab = document.getElementById(`char_tab_data_10_${factorId}`);
    if (tab) tab.classList.add('active');

    const container = document.getElementById('aspectsContainer');
    let html = `
        <div class="aspect-detail fade-in">
            <h2>Cuadros Dinámicos - Factor 10: Recursos y Ambientes</h2>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <p>Gestión de infraestructura física y medios educativos (biblioteca, laboratorios).</p>
                <button class="btn-primary" onclick="saveFactor10Data()">💾 Guardar Todos los Cuadros</button>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 1: Aulas y Laboratorios</h3>
                <table class="data-grid-table" id="tablaAulas">
                    <thead>
                        <tr>
                            <th>Espacio</th>
                            <th>Cantidad</th>
                            <th>Capacidad</th>
                            <th>Ocupación %</th>
                            <th>Estado</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowAula()">+ Agregar Espacio</button>
                <div class="chart-container" style="height:300px; margin-top:20px;">
                    <canvas id="chartFactor10"></canvas>
                </div>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 2: Oficinas y Bienestar</h3>
                <table class="data-grid-table" id="tablaOficinas">
                    <thead>
                        <tr>
                            <th>Área / Espacio</th>
                            <th>Cantidad</th>
                            <th>Área m²</th>
                            <th>Dotación/Servicios</th>
                            <th>Estado</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowOficina()">+ Agregar Área</button>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 3: Recursos Bibliográficos</h3>
                <table class="data-grid-table" id="tablaBiblioteca">
                    <thead>
                        <tr>
                            <th>Período</th>
                            <th>Libros Físicos</th>
                            <th>E-Books</th>
                            <th>Bases de Datos</th>
                            <th>Usuarios Activos</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowBiblioteca()">+ Agregar Período</button>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 4: Recursos Tecnológicos</h3>
                <table class="data-grid-table" id="tablaTecnologico">
                    <thead>
                        <tr>
                            <th>Período</th>
                            <th>Labs Cómputo</th>
                            <th>Computadores</th>
                            <th>Software Específico</th>
                            <th>Licencias</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowTecnologico()">+ Agregar Período</button>
            </div>
        </div>
    `;
    container.innerHTML = html;
    await fetchFactor10Data();
}

function addRowAula(data = {espacio:'', cantidad:0, capacidad:0, ocupacion:0, estado:'Bueno'}) {
    const tbody = document.querySelector('#tablaAulas tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.espacio}" placeholder="Ej. Aula Múltiple"></td>
        <td><input type="number" value="${data.cantidad}"></td>
        <td><input type="number" value="${data.capacidad}"></td>
        <td><input type="number" value="${data.ocupacion}"></td>
        <td>
            <select onchange="updateFactor10Charts()">
                <option value="Excelente" ${data.estado==='Excelente'?'selected':''}>Excelente</option>
                <option value="Bueno" ${data.estado==='Bueno'?'selected':''}>Bueno</option>
                <option value="Regular" ${data.estado==='Regular'?'selected':''}>Regular</option>
                <option value="Malo" ${data.estado==='Malo'?'selected':''}>Malo</option>
            </select>
        </td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove(); updateFactor10Charts();">X</button></td>
    `;
    tbody.appendChild(tr);
    updateFactor10Charts();
}

function addRowOficina(data = {area:'', cantidad:0, m2:0, dotacion:'', estado:'Bueno'}) {
    const tbody = document.querySelector('#tablaOficinas tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.area}" placeholder="Ej. Sala Profesores"></td>
        <td><input type="number" value="${data.cantidad}"></td>
        <td><input type="number" value="${data.m2}"></td>
        <td><input type="text" value="${data.dotacion}" placeholder="Sillas, mesas, wifi"></td>
        <td>
            <select>
                <option value="Excelente" ${data.estado==='Excelente'?'selected':''}>Excelente</option>
                <option value="Bueno" ${data.estado==='Bueno'?'selected':''}>Bueno</option>
                <option value="Regular" ${data.estado==='Regular'?'selected':''}>Regular</option>
            </select>
        </td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove();">X</button></td>
    `;
    tbody.appendChild(tr);
}

function addRowBiblioteca(data = {periodo:'', fisicos:0, ebooks:0, bd:0, usuarios:0}) {
    const tbody = document.querySelector('#tablaBiblioteca tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.periodo}" placeholder="Ej. 2023-1"></td>
        <td><input type="number" value="${data.fisicos}"></td>
        <td><input type="number" value="${data.ebooks}"></td>
        <td><input type="number" value="${data.bd}"></td>
        <td><input type="number" value="${data.usuarios}"></td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove();">X</button></td>
    `;
    tbody.appendChild(tr);
}

function addRowTecnologico(data = {periodo:'', labs:0, pc:0, software:'', licencias:0}) {
    const tbody = document.querySelector('#tablaTecnologico tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.periodo}" placeholder="Ej. 2023-1"></td>
        <td><input type="number" value="${data.labs}"></td>
        <td><input type="number" value="${data.pc}"></td>
        <td><input type="text" value="${data.software}" placeholder="Ej. SPSS, AutoCAD"></td>
        <td><input type="number" value="${data.licencias}"></td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove();">X</button></td>
    `;
    tbody.appendChild(tr);
}

function extractFactor10Data() {
    const aulas = []; document.querySelectorAll('#tablaAulas tbody tr').forEach(tr => { const i = tr.querySelectorAll('input, select'); aulas.push({ espacio: i[0].value, cantidad: i[1].value, capacidad: i[2].value, ocupacion: i[3].value, estado: i[4].value }); });
    const oficinas = []; document.querySelectorAll('#tablaOficinas tbody tr').forEach(tr => { const i = tr.querySelectorAll('input, select'); oficinas.push({ area: i[0].value, cantidad: i[1].value, m2: i[2].value, dotacion: i[3].value, estado: i[4].value }); });
    const biblioteca = []; document.querySelectorAll('#tablaBiblioteca tbody tr').forEach(tr => { const i = tr.querySelectorAll('input'); biblioteca.push({ periodo: i[0].value, fisicos: i[1].value, ebooks: i[2].value, bd: i[3].value, usuarios: i[4].value }); });
    const tecnologico = []; document.querySelectorAll('#tablaTecnologico tbody tr').forEach(tr => { const i = tr.querySelectorAll('input'); tecnologico.push({ periodo: i[0].value, labs: i[1].value, pc: i[2].value, software: i[3].value, licencias: i[4].value }); });
    return { aulas, oficinas, biblioteca, tecnologico };
}

async function saveFactor10Data() {
    const payload = { table_id: 'factor10_recursos', data: extractFactor10Data(), inst_id: getInstId(), program_id: getProgramId() };
    const btn = document.querySelector('button[onclick="saveFactor10Data()"]');
    btn.textContent = 'Guardando...';
    try {
        const res = await fetch('/api/estadisticas', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if(res.ok) alert('Datos guardados correctamente.'); else alert('Error al guardar datos.');
    } catch (err) { alert('Error de conexión.'); }
    btn.textContent = '💾 Guardar Todos los Cuadros';
}

async function fetchFactor10Data() {
    try {
        const res = await fetch(`/api/estadisticas?table_id=factor10_recursos&inst_id=${getInstId()}&program_id=${getProgramId()}`);
        if (res.ok) {
            const json = await res.json();
            if (json && json.data) {
                const data = typeof json.data === 'string' ? JSON.parse(json.data) : json.data;
                if (data.aulas && data.aulas.length > 0) data.aulas.forEach(a => addRowAula(a)); else addRowAula();
                if (data.oficinas && data.oficinas.length > 0) data.oficinas.forEach(o => addRowOficina(o)); else addRowOficina();
                if (data.biblioteca && data.biblioteca.length > 0) data.biblioteca.forEach(b => addRowBiblioteca(b)); else addRowBiblioteca();
                if (data.tecnologico && data.tecnologico.length > 0) data.tecnologico.forEach(t => addRowTecnologico(t)); else addRowTecnologico();
                return;
            }
        }
    } catch(e) {}
    addRowAula(); addRowOficina(); addRowBiblioteca(); addRowTecnologico();
}

function updateFactor10Charts() {
    const data = extractFactor10Data();
    let ctx = document.getElementById('chartFactor10');
    if (!ctx) return;
    let estados = { 'Excelente': 0, 'Bueno': 0, 'Regular': 0, 'Malo': 0 };
    data.aulas.forEach(a => {
        if(estados[a.estado] !== undefined) estados[a.estado] += parseInt(a.cantidad || 0);
    });
    
    if (window.chartF10) window.chartF10.destroy();
    window.chartF10 = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(estados),
            datasets: [{
                data: Object.values(estados),
                backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { title: { display: true, text: 'Estado Físico de Aulas y Laboratorios' } } }
    });
}
