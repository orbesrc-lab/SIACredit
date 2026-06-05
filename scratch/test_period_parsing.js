// Simulación de la función getPeriodOptionsHtml con distintos valores de activeProgramPeriod
function getPeriodOptionsHtml(activeProgramPeriod) {
    let periodOptionsHtml = '';
    if (activeProgramPeriod) {
        const years = activeProgramPeriod.match(/\b\d{4}\b/g);
        if (years && years.length > 0) {
            let startYear, endYear;
            if (years.length >= 2) {
                startYear = Math.min(parseInt(years[0]), parseInt(years[1]));
                endYear = Math.max(parseInt(years[0]), parseInt(years[1]));
            } else {
                startYear = parseInt(years[0]);
                endYear = startYear;
            }
            for (let y = endYear; y >= startYear; y--) {
                periodOptionsHtml += `<option value="${y}-2">${y}-2</option>\n`;
                periodOptionsHtml += `<option value="${y}-1">${y}-1</option>\n`;
            }
        }
    }
    if (!periodOptionsHtml) {
        periodOptionsHtml = `
            <option value="2025-1">2025-1</option>
            <option value="2024-2">2024-2</option>
            <option value="2024-1">2024-1</option>
            <option value="2023-2">2023-2</option>
            <option value="2023-1">2023-1</option>
        `;
    }
    return periodOptionsHtml;
}

// Pruebas
const testCases = [
    "2019-2026",
    "2019 - 2026",
    "2019",
    "",
    null,
    "rango invalido sin numeros",
    "2026 a 2019"
];

testCases.forEach((tc, i) => {
    console.log(`--- Test Case ${i + 1}: "${tc}" ---`);
    console.log(getPeriodOptionsHtml(tc));
});
