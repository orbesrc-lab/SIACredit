// ==========================================
// FACTOR 7: SECTOR EXTERNO Y PROYECCION
// ==========================================
async function loadFactor7DataGrid(factorId) {
    document.querySelectorAll('.char-item').forEach(el => el.classList.remove('active'));
    const tab = document.getElementById(`char_tab_data_7_${factorId}`);
    if (tab) tab.classList.add('active');

    const container = document.getElementById('aspectsContainer');
    let html = `
        <div class="aspect-detail fade-in">
            <h2>Cuadros Dinámicos - Factor 7: Sector Externo</h2>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <p>Gestión de convenios, prácticas, extensión e impacto en egresados.</p>
                <button class="btn-primary" onclick="saveFactor7Data()">💾 Guardar Todos los Cuadros</button>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 1: Impacto en Egresados</h3>
                <table class="data-grid-table" id="tablaEgresados">
                    <thead>
                        <tr>
                            <th>Período</th>
                            <th>Total Egresados</th>
                            <th>Ubicados Laboralmente</th>
                            <th>Sector Principal</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowEgresado()">+ Agregar Período</button>
                <div class="chart-container" style="height:300px; margin-top:20px;">
                    <canvas id="chartFactor7"></canvas>
                </div>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 2: Convenios Vigentes</h3>
                <table class="data-grid-table" id="tablaConvenios">
                    <thead>
                        <tr>
                            <th>Entidad</th>
                            <th>Sector</th>
                            <th>Vigencia</th>
                            <th>Estado</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowConvenio()">+ Agregar Convenio</button>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 3: Prácticas Empresariales</h3>
                <table class="data-grid-table" id="tablaPracticas">
                    <thead>
                        <tr>
                            <th>Período</th>
                            <th>Empresa</th>
                            <th>Tipo Vinculación</th>
                            <th>Estudiantes</th>
                            <th>Estado</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowPractica()">+ Agregar Práctica</button>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 4: Proyectos de Extensión</h3>
                <table class="data-grid-table" id="tablaExtension">
                    <thead>
                        <tr>
                            <th>Período</th>
                            <th>Proyecto</th>
                            <th>Población Beneficiada</th>
                            <th>Estado</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowExtension()">+ Agregar Proyecto</button>
            </div>
        </div>
    `;
    container.innerHTML = html;
    await fetchFactor7Data();
}

function addRowEgresado(data = {periodo:'', egresados:0, ubicados:0, sector:''}) {
    const tbody = document.querySelector('#tablaEgresados tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.periodo}" placeholder="Ej. 2023-1" onchange="updateFactor7Charts()"></td>
        <td><input type="number" value="${data.egresados}" onchange="updateFactor7Charts()"></td>
        <td><input type="number" value="${data.ubicados}" onchange="updateFactor7Charts()"></td>
        <td><input type="text" value="${data.sector}" placeholder="Ej. Financiero"></td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove(); updateFactor7Charts();">X</button></td>
    `;
    tbody.appendChild(tr);
    updateFactor7Charts();
}

function addRowConvenio(data = {entidad:'', sector:'Público', vigencia:'', estado:'Activo'}) {
    const tbody = document.querySelector('#tablaConvenios tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.entidad}" placeholder="Nombre Entidad"></td>
        <td>
            <select>
                <option value="Público" ${data.sector==='Público'?'selected':''}>Público</option>
                <option value="Privado" ${data.sector==='Privado'?'selected':''}>Privado</option>
                <option value="Mixto" ${data.sector==='Mixto'?'selected':''}>Mixto</option>
            </select>
        </td>
        <td><input type="text" value="${data.vigencia}" placeholder="Ej. 2 años"></td>
        <td>
            <select>
                <option value="Activo" ${data.estado==='Activo'?'selected':''}>Activo</option>
                <option value="Inactivo" ${data.estado==='Inactivo'?'selected':''}>Inactivo</option>
            </select>
        </td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove();">X</button></td>
    `;
    tbody.appendChild(tr);
}

function addRowPractica(data = {periodo:'', empresa:'', tipo:'', estudiantes:0, estado:'Finalizada'}) {
    const tbody = document.querySelector('#tablaPracticas tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.periodo}" placeholder="Ej. 2023-1"></td>
        <td><input type="text" value="${data.empresa}" placeholder="Nombre Empresa"></td>
        <td><input type="text" value="${data.tipo}" placeholder="Contrato/Convenio"></td>
        <td><input type="number" value="${data.estudiantes}"></td>
        <td>
            <select>
                <option value="En curso" ${data.estado==='En curso'?'selected':''}>En curso</option>
                <option value="Finalizada" ${data.estado==='Finalizada'?'selected':''}>Finalizada</option>
            </select>
        </td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove();">X</button></td>
    `;
    tbody.appendChild(tr);
}

function addRowExtension(data = {periodo:'', proyecto:'', poblacion:'', estado:'Activo'}) {
    const tbody = document.querySelector('#tablaExtension tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.periodo}" placeholder="Ej. 2023-1"></td>
        <td><input type="text" value="${data.proyecto}" placeholder="Nombre Proyecto"></td>
        <td><input type="text" value="${data.poblacion}" placeholder="Ej. 50 emprendedores"></td>
        <td>
            <select>
                <option value="Activo" ${data.estado==='Activo'?'selected':''}>Activo</option>
                <option value="Finalizado" ${data.estado==='Finalizado'?'selected':''}>Finalizado</option>
            </select>
        </td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove();">X</button></td>
    `;
    tbody.appendChild(tr);
}

function extractFactor7Data() {
    const egresados = []; document.querySelectorAll('#tablaEgresados tbody tr').forEach(tr => { const i = tr.querySelectorAll('input'); egresados.push({ periodo: i[0].value, egresados: i[1].value, ubicados: i[2].value, sector: i[3].value }); });
    const convenios = []; document.querySelectorAll('#tablaConvenios tbody tr').forEach(tr => { const i = tr.querySelectorAll('input, select'); convenios.push({ entidad: i[0].value, sector: i[1].value, vigencia: i[2].value, estado: i[3].value }); });
    const practicas = []; document.querySelectorAll('#tablaPracticas tbody tr').forEach(tr => { const i = tr.querySelectorAll('input, select'); practicas.push({ periodo: i[0].value, empresa: i[1].value, tipo: i[2].value, estudiantes: i[3].value, estado: i[4].value }); });
    const extension = []; document.querySelectorAll('#tablaExtension tbody tr').forEach(tr => { const i = tr.querySelectorAll('input, select'); extension.push({ periodo: i[0].value, proyecto: i[1].value, poblacion: i[2].value, estado: i[3].value }); });
    return { egresados, convenios, practicas, extension };
}

async function saveFactor7Data() {
    const payload = { table_id: 'factor7_extension', data: extractFactor7Data(), inst_id: getInstId(), program_id: getProgramId() };
    const btn = document.querySelector('button[onclick="saveFactor7Data()"]');
    btn.textContent = 'Guardando...';
    try {
        const res = await fetch('/api/estadisticas', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if(res.ok) alert('Datos guardados correctamente.'); else alert('Error al guardar datos.');
    } catch (err) { alert('Error de conexión.'); }
    btn.textContent = '💾 Guardar Todos los Cuadros';
}

async function fetchFactor7Data() {
    try {
        const res = await fetch(`/api/estadisticas?table_id=factor7_extension&inst_id=${getInstId()}&program_id=${getProgramId()}`);
        if (res.ok) {
            const json = await res.json();
            if (json && json.data) {
                const data = typeof json.data === 'string' ? JSON.parse(json.data) : json.data;
                if (data.egresados && data.egresados.length > 0) data.egresados.forEach(e => addRowEgresado(e)); else addRowEgresado();
                if (data.convenios && data.convenios.length > 0) data.convenios.forEach(c => addRowConvenio(c)); else addRowConvenio();
                if (data.practicas && data.practicas.length > 0) data.practicas.forEach(p => addRowPractica(p)); else addRowPractica();
                if (data.extension && data.extension.length > 0) data.extension.forEach(e => addRowExtension(e)); else addRowExtension();
                return;
            }
        }
    } catch(e) {}
    addRowEgresado(); addRowConvenio(); addRowPractica(); addRowExtension();
}

function updateFactor7Charts() {
    const data = extractFactor7Data();
    let ctx = document.getElementById('chartFactor7');
    if (!ctx) return;
    let periodos = data.egresados.map(e => e.periodo);
    let totales = data.egresados.map(e => parseInt(e.egresados || 0));
    let ubicados = data.egresados.map(e => parseInt(e.ubicados || 0));
    
    if (window.chartF7) window.chartF7.destroy();
    window.chartF7 = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: periodos,
            datasets: [
                { label: 'Total Egresados', data: totales, backgroundColor: '#cbd5e1' },
                { label: 'Ubicados Laboralmente', data: ubicados, backgroundColor: '#10b981' }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { title: { display: true, text: 'Ubicación Laboral de Egresados por Período' } } }
    });
}
