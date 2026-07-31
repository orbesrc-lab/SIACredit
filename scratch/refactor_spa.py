import re

with open(r'c:\SIAC\static\styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Update CSS for seamless modal
# #skel-module-modal
css = re.sub(r'#skel-module-modal \{.*?\}', '''#skel-module-modal {
    display: none;
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    background: var(--bg-color);
    z-index: 10000;
}''', css, flags=re.DOTALL)

# #skel-module-modal.active
css = re.sub(r'#skel-module-modal\.active \{.*?\}', '''#skel-module-modal.active {
    display: block;
}''', css, flags=re.DOTALL)

# .skel-module-modal-content
css = re.sub(r'\.skel-module-modal-content \{.*?\}', '''.skel-module-modal-content {
    background: transparent;
    width: 100%;
    height: 100%;
    border: none;
    border-radius: 0;
    box-shadow: none;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}''', css, flags=re.DOTALL)

# #skel-module-iframe
css = re.sub(r'#skel-module-iframe \{.*?\}', '''#skel-module-iframe {
    width: 100%;
    height: 100%;
    border: none;
    display: block;
}''', css, flags=re.DOTALL)

# Remove the header classes if they exist, or just leave them (they won't be used)
with open(r'c:\SIAC\static\styles.css', 'w', encoding='utf-8') as f:
    f.write(css)


# 2. Update app.js
with open(r'c:\SIAC\static\app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Replace modalHTML
old_modal_html = re.search(r'const modalHTML = `.*?`;', app_js, re.DOTALL)
if old_modal_html:
    new_modal_html = '''const modalHTML = `
            <div id="skel-module-modal">
                <div class="skel-module-modal-content">
                    <iframe id="skel-module-iframe" src="about:blank"></iframe>
                </div>
            </div>`;'''
    app_js = app_js.replace(old_modal_html.group(0), new_modal_html)


# Update openModuleModal function
old_open_func = re.search(r'window\.openModuleModal = function\(url, titleGuess\) \{.*?\};', app_js, re.DOTALL)
if old_open_func:
    new_open_func = '''window.openModuleModal = function(url, titleGuess) {
    const modal = document.getElementById('skel-module-modal');
    const iframe = document.getElementById('skel-module-iframe');
    
    if (modal && iframe) {
        iframe.src = url;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Push state for SPA feel
        const targetUrl = url.startsWith('/') ? url : '/' + url;
        if (window.location.pathname !== targetUrl) {
            history.pushState(null, titleGuess, targetUrl);
        }
    } else {
        window.location.href = url;
    }
};

window.addEventListener('popstate', (e) => {
    // When user clicks browser back button, reload to sync state
    window.location.reload();
});'''
    app_js = app_js.replace(old_open_func.group(0), new_open_func)

with open(r'c:\SIAC\static\app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print('Seamless SPA layout implemented.')
