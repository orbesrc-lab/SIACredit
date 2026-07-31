import re

with open(r'c:\SIAC\templates\configuracion.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add postMessage to saveGlobalSettings
if "window.parent.postMessage" not in content:
    content = content.replace('await loadAllInstitutions();', 
        '''await loadAllInstitutions();
            // Notify parent to reload so theme changes apply globally
            if (window.parent && window.parent !== window) {
                window.parent.postMessage({ type: 'settings_updated' }, '*');
            }''')

with open(r'c:\SIAC\templates\configuracion.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Now add listener to app.js
with open(r'c:\SIAC\static\app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

if "type === 'settings_updated'" not in app_js:
    app_js += '''\n
window.addEventListener('message', (e) => {
    if (e.data && e.data.type === 'settings_updated') {
        window.location.reload();
    }
});
'''
with open(r'c:\SIAC\static\app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print('Settings updated logic injected.')
