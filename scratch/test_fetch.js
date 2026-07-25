async function test() {
    try {
        const resp = await fetch('https://siacmen.vercel.app/api/courses/c_943c97c20?inst_id=1&program_id=47');
        const text = await resp.text();
        console.log("Status:", resp.status);
        console.log("Body:", text.substring(0, 500));
    } catch(e) {
        console.log("Error:", e.message);
    }
}
test();
