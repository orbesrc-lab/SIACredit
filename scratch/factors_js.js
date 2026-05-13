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
