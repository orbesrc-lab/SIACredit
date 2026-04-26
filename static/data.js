let localModelCache = [];
let localEvidencesCache = {};
let localEvaluationsCache = {};
let localReportsCache = {};
let localStatsCache = {};

// Cargar todos los datos desde la API del backend
async function loadDataFromAPI() {
    try {
        const resM = await fetch('/api/model');
        localModelCache = await resM.json();

        const resEv = await fetch('/api/evidences');
        localEvidencesCache = await resEv.json();

        const resEval = await fetch('/api/evaluations');
        localEvaluationsCache = await resEval.json();

        const resRep = await fetch('/api/reports');
        localReportsCache = await resRep.json();

        const resStat = await fetch('/api/estadisticas');
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
    fetch('/api/model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

function getEvidences() {
    return localEvidencesCache;
}

function saveEvidences(data) {
    localEvidencesCache = data;
    fetch('/api/evidences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

function getEvaluations() {
    return localEvaluationsCache;
}

function saveEvaluations(data) {
    localEvaluationsCache = data;
    fetch('/api/evaluations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

function getExternalReports() {
    return localReportsCache;
}

function saveExternalReports(data) {
    localReportsCache = data;
    fetch('/api/reports', {
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
    fetch('/api/estadisticas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

function generateId() {
    return Math.random().toString(36).substr(2, 9);
}
