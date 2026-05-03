let localModelCache = [];
let localEvidencesCache = {};
let localEvaluationsCache = {};
let localReportsCache = {};
let localStatsCache = {};

function getInstId() {
    const user = JSON.parse(localStorage.getItem('siac_user'));
    return user ? (user.inst_id || 1) : 1;
}

function getProgramId() {
    const user = JSON.parse(localStorage.getItem('siac_user'));
    return user ? (user.program_id || 0) : 0;
}

// Cargar todos los datos desde la API del backend
async function loadDataFromAPI() {
    const instId = getInstId();
    const progId = getProgramId();
    try {
        const resM = await fetch(`/api/model?inst_id=${instId}&program_id=${progId}`);
        localModelCache = await resM.json();

        const resEv = await fetch(`/api/evidences?inst_id=${instId}&program_id=${progId}`);
        localEvidencesCache = await resEv.json();

        const resEval = await fetch(`/api/evaluations?inst_id=${instId}&program_id=${progId}`);
        localEvaluationsCache = await resEval.json();

        const resStat = await fetch(`/api/estadisticas?inst_id=${instId}&program_id=${progId}`);
        localStatsCache = await resStat.json();
    } catch (err) {
        console.error("Error cargando datos del servidor:", err);
    }
}

// Helpers para obtener/guardar datos (síncronos en memoria, asíncronos hacia la BD)
function getDataModel() {
    return localModelCache;
}

function saveDataModel(data) {
    localModelCache = data;
    fetch(`/api/model?inst_id=${getInstId()}&program_id=${getProgramId()}`, {
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
    fetch(`/api/evaluations?inst_id=${getInstId()}&program_id=${getProgramId()}`, {
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
    fetch(`/api/estadisticas?inst_id=${getInstId()}&program_id=${getProgramId()}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

function generateId() {
    return Math.random().toString(36).substr(2, 9);
}

