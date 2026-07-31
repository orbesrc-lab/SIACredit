import os

with open(r'c:\SIAC\static\app.js', 'r', encoding='utf-8') as f:
    content = f.read()

PATCH = '''
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.style.height = '100%';
            mainContent.style.overflowY = 'auto';
        }
        const contentArea = document.querySelector('.content-area');
        if (contentArea) {
            contentArea.style.height = 'auto';
            contentArea.style.overflowY = 'visible';
        }
        // Force body to scroll if needed
        document.body.style.display = 'block';
'''

if 'contentArea.style.overflowY' not in content:
    content = content.replace("dashContainer.style.height = '100vh';", "dashContainer.style.height = '100vh';" + PATCH)
    with open(r'c:\SIAC\static\app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print('app.js patched for modal scroll.')
else:
    print('Already patched.')
