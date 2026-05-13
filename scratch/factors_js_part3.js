// ==========================================
// FACTOR 8: INVESTIGACIÓN, INNOVACIÓN Y CREACIÓN
// ==========================================
async function loadFactor8DataGrid(factorId) {
    document.querySelectorAll('.char-item').forEach(el => el.classList.remove('active'));
    const tab = document.getElementById(`char_tab_data_8_${factorId}`);
    if (tab) tab.classList.add('active');

    const container = document.getElementById('aspectsContainer');
    let html = `
        <div class="aspect-detail fade-in">
            <h2>Cuadros Dinámicos - Factor 8: Investigación</h2>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <p>Gestión de grupos, proyectos, publicaciones y semilleros de investigación.</p>
                <button class="btn-primary" onclick="saveFactor8Data()">💾 Guardar Todos los Cuadros</button>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 1: Proyectos de Investigación</h3>
                <table class="data-grid-table" id="tablaProyectos">
                    <thead>
                        <tr>
                            <th>Período</th>
                            <th>Proyecto</th>
                            <th>Investigador Principal</th>
                            <th>Línea</th>
                            <th>Financiación</th>
                            <th>Estado</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowProyecto()">+ Agregar Proyecto</button>
                <div class="chart-container" style="height:300px; margin-top:20px;">
                    <canvas id="chartFactor8"></canvas>
                </div>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 2: Grupos de Investigación</h3>
                <table class="data-grid-table" id="tablaGrupos">
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Líneas</th>
                            <th>Categoría (Minciencias)</th>
                            <th>Integrantes</th>
                            <th>Estado</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowGrupo()">+ Agregar Grupo</button>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 3: Publicaciones y Productos</h3>
                <table class="data-grid-table" id="tablaPublicaciones">
                    <thead>
                        <tr>
                            <th>Período</th>
                            <th>Título</th>
                            <th>Tipo</th>
                            <th>Autores</th>
                            <th>Revista / Indexación</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowPublicacion()">+ Agregar Publicación</button>
            </div>

            <div class="data-grid-container fade-in">
                <h3>Cuadro 4: Semilleros de Investigación</h3>
                <table class="data-grid-table" id="tablaSemilleros">
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Tutor</th>
                            <th>Estudiantes</th>
                            <th>Proyectos Activos</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <button class="btn-ghost" style="margin-top:10px; border:1px dashed var(--primary-color); color:var(--primary-color);" onclick="addRowSemillero()">+ Agregar Semillero</button>
            </div>
        </div>
    `;
    container.innerHTML = html;
    await fetchFactor8Data();
}

function addRowProyecto(data = {periodo:'', proyecto:'', ip:'', linea:'', financiacion:'', estado:'Aprobado'}) {
    const tbody = document.querySelector('#tablaProyectos tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.periodo}" placeholder="Ej. 2023-1"></td>
        <td><input type="text" value="${data.proyecto}" placeholder="Nombre Proyecto"></td>
        <td><input type="text" value="${data.ip}" placeholder="Investigador P."></td>
        <td><input type="text" value="${data.linea}" placeholder="Línea"></td>
        <td><input type="text" value="${data.financiacion}" placeholder="Interna/Externa"></td>
        <td>
            <select onchange="updateFactor8Charts()">
                <option value="Aprobado" ${data.estado==='Aprobado'?'selected':''}>Aprobado</option>
                <option value="En Ejecución" ${data.estado==='En Ejecución'?'selected':''}>En Ejecución</option>
                <option value="Finalizado" ${data.estado==='Finalizado'?'selected':''}>Finalizado</option>
            </select>
        </td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove(); updateFactor8Charts();">X</button></td>
    `;
    tbody.appendChild(tr);
    updateFactor8Charts();
}

function addRowGrupo(data = {nombre:'', lineas:'', categoria:'A', integrantes:0, estado:'Reconocido'}) {
    const tbody = document.querySelector('#tablaGrupos tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.nombre}" placeholder="Nombre Grupo"></td>
        <td><input type="text" value="${data.lineas}" placeholder="Líneas"></td>
        <td>
            <select>
                <option value="A1" ${data.categoria==='A1'?'selected':''}>A1</option>
                <option value="A" ${data.categoria==='A'?'selected':''}>A</option>
                <option value="B" ${data.categoria==='B'?'selected':''}>B</option>
                <option value="C" ${data.categoria==='C'?'selected':''}>C</option>
                <option value="Reconocido" ${data.categoria==='Reconocido'?'selected':''}>Reconocido</option>
                <option value="Registrado" ${data.categoria==='Registrado'?'selected':''}>Registrado</option>
            </select>
        </td>
        <td><input type="number" value="${data.integrantes}"></td>
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

function addRowPublicacion(data = {periodo:'', titulo:'', tipo:'Artículo', autores:'', indexacion:''}) {
    const tbody = document.querySelector('#tablaPublicaciones tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.periodo}" placeholder="Ej. 2023-1"></td>
        <td><input type="text" value="${data.titulo}" placeholder="Título del trabajo"></td>
        <td>
            <select>
                <option value="Artículo" ${data.tipo==='Artículo'?'selected':''}>Artículo</option>
                <option value="Libro" ${data.tipo==='Libro'?'selected':''}>Libro</option>
                <option value="Capítulo de Libro" ${data.tipo==='Capítulo de Libro'?'selected':''}>Capítulo de Libro</option>
                <option value="Software" ${data.tipo==='Software'?'selected':''}>Software</option>
                <option value="Patente" ${data.tipo==='Patente'?'selected':''}>Patente</option>
            </select>
        </td>
        <td><input type="text" value="${data.autores}" placeholder="Autores"></td>
        <td><input type="text" value="${data.indexacion}" placeholder="Ej. Scopus Q1"></td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove();">X</button></td>
    `;
    tbody.appendChild(tr);
}

function addRowSemillero(data = {nombre:'', tutor:'', estudiantes:0, proyectos:0}) {
    const tbody = document.querySelector('#tablaSemilleros tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" value="${data.nombre}" placeholder="Nombre Semillero"></td>
        <td><input type="text" value="${data.tutor}" placeholder="Tutor encargado"></td>
        <td><input type="number" value="${data.estudiantes}"></td>
        <td><input type="number" value="${data.proyectos}"></td>
        <td style="text-align:center;"><button class="btn-ghost" style="color:red;" onclick="this.closest('tr').remove();">X</button></td>
    `;
    tbody.appendChild(tr);
}

function extractFactor8Data() {
    const proyectos = []; document.querySelectorAll('#tablaProyectos tbody tr').forEach(tr => { const i = tr.querySelectorAll('input, select'); proyectos.push({ periodo: i[0].value, proyecto: i[1].value, ip: i[2].value, linea: i[3].value, financiacion: i[4].value, estado: i[5].value }); });
    const grupos = []; document.querySelectorAll('#tablaGrupos tbody tr').forEach(tr => { const i = tr.querySelectorAll('input, select'); grupos.push({ nombre: i[0].value, lineas: i[1].value, categoria: i[2].value, integrantes: i[3].value, estado: i[4].value }); });
    const publicaciones = []; document.querySelectorAll('#tablaPublicaciones tbody tr').forEach(tr => { const i = tr.querySelectorAll('input, select'); publicaciones.push({ periodo: i[0].value, titulo: i[1].value, tipo: i[2].value, autores: i[3].value, indexacion: i[4].value }); });
    const semilleros = []; document.querySelectorAll('#tablaSemilleros tbody tr').forEach(tr => { const i = tr.querySelectorAll('input'); semilleros.push({ nombre: i[0].value, tutor: i[1].value, estudiantes: i[2].value, proyectos: i[3].value }); });
    return { proyectos, grupos, publicaciones, semilleros };
}

async function saveFactor8Data() {
    const payload = { table_id: 'factor8_investigacion', data: extractFactor8Data(), inst_id: getInstId(), program_id: getProgramId() };
    const btn = document.querySelector('button[onclick="saveFactor8Data()"]');
    btn.textContent = 'Guardando...';
    try {
        const res = await fetch('/api/estadisticas', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if(res.ok) alert('Datos guardados correctamente.'); else alert('Error al guardar datos.');
    } catch (err) { alert('Error de conexión.'); }
    btn.textContent = '💾 Guardar Todos los Cuadros';
}

async function fetchFactor8Data() {
    try {
        const res = await fetch(`/api/estadisticas?table_id=factor8_investigacion&inst_id=${getInstId()}&program_id=${getProgramId()}`);
        if (res.ok) {
            const json = await res.json();
            if (json && json.data) {
                const data = typeof json.data === 'string' ? JSON.parse(json.data) : json.data;
                if (data.proyectos && data.proyectos.length > 0) data.proyectos.forEach(p => addRowProyecto(p)); else addRowProyecto();
                if (data.grupos && data.grupos.length > 0) data.grupos.forEach(g => addRowGrupo(g)); else addRowGrupo();
                if (data.publicaciones && data.publicaciones.length > 0) data.publicaciones.forEach(p => addRowPublicacion(p)); else addRowPublicacion();
                if (data.semilleros && data.semilleros.length > 0) data.semilleros.forEach(s => addRowSemillero(s)); else addRowSemillero();
                return;
            }
        }
    } catch(e) {}
    addRowProyecto(); addRowGrupo(); addRowPublicacion(); addRowSemillero();
}

function updateFactor8Charts() {
    const data = extractFactor8Data();
    let ctx = document.getElementById('chartFactor8');
    if (!ctx) return;
    let estados = { 'Aprobado': 0, 'En Ejecución': 0, 'Finalizado': 0 };
    data.proyectos.forEach(p => {
        if(estados[p.estado] !== undefined) estados[p.estado]++;
    });
    
    if (window.chartF8) window.chartF8.destroy();
    window.chartF8 = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(estados),
            datasets: [{
                label: 'Cantidad de Proyectos',
                data: Object.values(estados),
                backgroundColor: ['#3b82f6', '#10b981', '#64748b']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { title: { display: true, text: 'Estado Actual de los Proyectos de Investigación' } } }
    });
}
