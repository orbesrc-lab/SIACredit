const fs = require('fs');
const content = fs.readFileSync('c:\\SIAC\\templates\\formacion.html', 'utf8');
const scriptMatch = content.match(/<script>([\s\S]*?)<\/script>/gi);
if (scriptMatch) {
    scriptMatch.forEach((s, idx) => {
        try {
            const js = s.replace(/<\/?script>/gi, '');
            new Function(js);
            console.log(`Script ${idx} is valid.`);
        } catch (e) {
            console.error(`Script ${idx} Error:`, e);
        }
    });
}
