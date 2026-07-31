JS_CODE = """
// ==========================================
// SPA MODULE MODAL SYSTEM (IFRAMES)
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Detect if we are inside an iframe (Module Modal)
    const isModal = window.self !== window.top;
    
    if (isModal) {
        // We are a module loaded inside the giant modal!
        // Hide the sidebar
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) sidebar.style.display = 'none';
        
        // Remove dashboard container constraints so we use 100% of iframe
        const dashContainer = document.querySelector('.dashboard-container');
        if (dashContainer) {
            dashContainer.style.maxWidth = 'none';
            dashContainer.style.borderRadius = '0';
            dashContainer.style.boxShadow = 'none';
            dashContainer.style.background = 'transparent';
            dashContainer.style.height = '100vh';
        }
        
        // Let the parent modal know the title of this module
        const topbarTitle = document.querySelector('.topbar h2');
        if (topbarTitle && window.parent && window.parent.setModuleModalTitle) {
            window.parent.setModuleModalTitle(topbarTitle.textContent);
        }
    } else {
        // We are the HOST (Dashboard or main window)
        // Inject the Modal HTML if it doesn't exist
        if (!document.getElementById('skel-module-modal')) {
            const modalHTML = `
            <div id="skel-module-modal">
                <div class="skel-module-modal-content">
                    <div class="skel-module-modal-header">
                        <h2 id="skel-module-modal-title">Cargando Módulo...</h2>
                        <button class="skel-module-modal-close" onclick="closeModuleModal()">✕</button>
                    </div>
                    <div class="skel-module-modal-body">
                        <iframe id="skel-module-iframe"></iframe>
                    </div>
                </div>
            </div>`;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }
        
        // Intercept sidebar links
        const sidebarLinks = document.querySelectorAll('.sidebar-item');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                // Don't intercept logout or hash links
                if (href && href !== '#' && !href.startsWith('javascript:')) {
                    e.preventDefault();
                    // Keep the emoji out of the title guess if possible, or just pass the text
                    openModuleModal(href, link.textContent.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ0-9 ]/g, '').trim()); 
                }
            });
        });
    }
});

// Global functions for the Host
window.openModuleModal = function(url, titleGuess) {
    const modal = document.getElementById('skel-module-modal');
    const iframe = document.getElementById('skel-module-iframe');
    const title = document.getElementById('skel-module-modal-title');
    
    if (modal && iframe) {
        title.textContent = titleGuess ? titleGuess : 'Cargando Módulo...';
        iframe.src = url;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
};

window.closeModuleModal = function() {
    const modal = document.getElementById('skel-module-modal');
    const iframe = document.getElementById('skel-module-iframe');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        setTimeout(() => { if(iframe) iframe.src = ''; }, 300); // Clear memory after animation
    }
};

window.setModuleModalTitle = function(newTitle) {
    const title = document.getElementById('skel-module-modal-title');
    if (title) {
        title.textContent = newTitle;
    }
};
"""

with open(r'c:\SIAC\static\app.js', 'a', encoding='utf-8') as f:
    f.write(JS_CODE)
