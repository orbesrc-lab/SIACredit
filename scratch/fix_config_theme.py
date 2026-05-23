import os

filepath = r"c:\SIAC\templates\configuracion.html"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Make it visible to admin
content = content.replace(
    "document.getElementById('instSelectorCard').style.display = 'block';",
    "document.getElementById('instSelectorCard').style.display = 'block';\n                if (document.getElementById('globalSettingsCard')) document.getElementById('globalSettingsCard').style.display = 'block';"
)

# Add saveGlobalTheme at the end before </body>
js_code = """
        async function saveGlobalTheme() {
            const theme = document.getElementById('globalThemeSelect').value;
            try {
                const res = await fetch('/api/global-settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ theme: theme })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    alert("✅ Tema global guardado correctamente.");
                } else {
                    alert("❌ Error: " + data.message);
                }
            } catch (e) {
                alert("❌ Error de conexión al guardar el tema global.");
            }
        }
"""
content = content.replace("</body>", js_code + "\n</body>")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated configuracion.html successfully")
