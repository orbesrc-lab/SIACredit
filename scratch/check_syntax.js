const fs = require('fs');
const html = fs.readFileSync('c:/SIAC/templates/empresa_informe_gerencial.html', 'utf8');
const scriptMatch = html.match(/<script>(.*?)<\/script>/s);
if (scriptMatch) {
    try {
        new Function(scriptMatch[1]);
        console.log("Syntax OK");
    } catch (e) {
        console.error("Syntax Error:", e);
    }
} else {
    console.log("No script tag found.");
}
