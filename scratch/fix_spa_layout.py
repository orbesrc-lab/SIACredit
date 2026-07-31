import re

with open(r'c:\SIAC\static\styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Update CSS
# Find #skel-module-modal { ... } and replace position/inset
css = re.sub(r'#skel-module-modal \{.*?\}', '''#skel-module-modal {
    display: none;
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    background: rgba(15, 23, 42, 0.5); /* Lighter overlay since it's just main-content */
    backdrop-filter: blur(8px);
    z-index: 10000;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}''', css, flags=re.DOTALL)

# Find .skel-module-modal-content { ... } and adjust width/height
css = re.sub(r'\.skel-module-modal-content \{.*?\}', '''.skel-module-modal-content {
    background: var(--secondary-bg, #f8fafc);
    width: 98%;
    height: 98%;
    max-width: none;
    border-radius: 16px;
    border: 1px solid var(--border-color);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transform: translateY(10px);
    animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}''', css, flags=re.DOTALL)

with open(r'c:\SIAC\static\styles.css', 'w', encoding='utf-8') as f:
    f.write(css)

# 2. Update app.js
with open(r'c:\SIAC\static\app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

app_js = app_js.replace("document.body.insertAdjacentHTML('beforeend', modalHTML);", 
'''const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.style.position = 'relative'; // Ensure positioning context
            mainContent.insertAdjacentHTML('beforeend', modalHTML);
        } else {
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }''')

with open(r'c:\SIAC\static\app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print('SPA layout updated. Sidebar will now remain visible.')
