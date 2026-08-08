let localModelCache = [];
let localEvidencesCache = {};
let localEvaluationsCache = {};
let localReportsCache = {};
let localStatsCache = {};

function getInstId() {
    try {
        const user = JSON.parse(localStorage.getItem('siac_user'));
        return user ? (user.inst_id || 1) : 1;
    } catch (e) {
        console.error("Error parsing siac_user in getInstId:", e);
        return 1;
    }
}

function getProgramId() {
    try {
        const user = JSON.parse(localStorage.getItem('siac_user'));
        return user ? (user.program_id || 0) : 0;
    } catch (e) {
        console.error("Error parsing siac_user in getProgramId:", e);
        return 0;
    }
}

// Helper interno para fetch autenticado
function _doFetch(url, options) {
    if (typeof authFetch === 'function') {
        return authFetch(url, options);
    }
    const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
    const method = (options?.method || 'GET').toUpperCase();
    const headers = {
        ...(method !== 'GET' ? {'Content-Type': 'application/json'} : {}),
        ...(options?.headers || {}),
    };
    if (user && user.id) {
        headers['X-User-Id'] = user.id;
    }
    return fetch(url, { ...options, headers });
}

// Cargar todos los datos desde la API del backend
async function loadDataFromAPI() {
    const instId = getInstId();
    const progId = getProgramId();
    
    if (!progId || progId == 0) {
        localModelCache = [];
        localEvidencesCache = {};
        localEvaluationsCache = {};
        localStatsCache = {};
        return;
    }

    try {
        const timestamp = Date.now();
        const [resM, resEv, resEval, resStat] = await Promise.all([
            _doFetch(`/api/model?inst_id=${instId}&program_id=${progId}&t=${timestamp}`),
            _doFetch(`/api/evidences?inst_id=${instId}&program_id=${progId}&t=${timestamp}`),
            _doFetch(`/api/evaluations?inst_id=${instId}&program_id=${progId}&t=${timestamp}`),
            _doFetch(`/api/estadisticas?inst_id=${instId}&program_id=${progId}&t=${timestamp}`)
        ]);

        const [dataM, dataEv, dataEval, dataStat] = await Promise.all([
            resM.json(),
            resEv.json(),
            resEval.json(),
            resStat.json()
        ]);

        localModelCache = Array.isArray(dataM) ? dataM : [];
        localEvidencesCache = (dataEv && typeof dataEv === 'object' && !dataEv.status) ? dataEv : {};
        localEvaluationsCache = (dataEval && typeof dataEval === 'object' && !dataEval.status) ? dataEval : {};
        localStatsCache = (dataStat && typeof dataStat === 'object' && !dataStat.status) ? dataStat : {};
    } catch (err) {
        console.error("Error cargando datos del servidor:", err);
    }
}

// Helpers para obtener/guardar datos (síncronos en memoria, asíncronos hacia la BD)
function getDataModel() {
    return localModelCache;
}

function saveDataModel(data) {
    const progId = getProgramId();
    // TRAZABILIDAD: No guardar si no hay programa activo
    if (!progId || progId == 0) {
        alert("⚠️ No puedes guardar el Modelo sin un Programa Académico activo.\n\nVe a 'Gestión de Programas Académicos', selecciona o crea un programa y haz clic en 'Cambiar / Cargar'.");
        return;
    }
    localModelCache = data;
    _doFetch(`/api/model?inst_id=${getInstId()}&program_id=${progId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

function getEvidences() {
    return localEvidencesCache;
}

function getEvaluations() {
    return localEvaluationsCache;
}

function saveEvaluations(data) {
    localEvaluationsCache = data;
    _doFetch(`/api/evaluations?inst_id=${getInstId()}&program_id=${getProgramId()}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

function getStatistics() {
    return localStatsCache;
}

function saveStatistics(data) {
    localStatsCache = data;
    return _doFetch(`/api/estadisticas?inst_id=${getInstId()}&program_id=${getProgramId()}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

function generateId() {
    return Math.random().toString(36).substr(2, 9);
}

