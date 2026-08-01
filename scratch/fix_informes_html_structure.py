import os

file_path = r'c:\SIAC\templates\informes.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove premature </body>\n</html>\n            `);\n            win.document.close();\n        }
bad_closing = """</body>
</html>
            `);
            win.document.close();
        }"""

content = content.replace(bad_closing, "")

# 2. Also remove any extra </body> or </html> inside script blocks
content = content.replace("</body>\n</html>\n            `);", "")

# 3. Ensure topbar header initializes properly
header_script = """
        document.addEventListener('DOMContentLoaded', async () => {
            if (typeof initHeader === 'function') await initHeader();
            else {
                try {
                    const resp = await fetch(`/api/institution?inst_id=${getInstId()}`);
                    if (resp.ok) {
                        const data = await resp.json();
                        document.getElementById('inst_name_display').textContent = data.name || 'INSTITUCIÓN EDUCATIVA';
                        if (data.logo_url) {
                            const img = document.getElementById('inst_logo_img');
                            img.src = data.logo_url; img.style.display = 'block';
                        }
                    }
                } catch(e){}
            }
        });
"""

if "initHeader()" not in content:
    content = content.replace("function imprimirInformeCompleto() {", header_script + "\n    function imprimirInformeCompleto() {")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("informes.html HTML structure completely cleaned up and fixed!")
