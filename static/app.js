
// Global authentication check
(function() {
    const path = window.location.pathname.toLowerCase();
    const isPublic = path.includes('index.html') || path.includes('login.html') || path.includes('registro.html') || path.endsWith('/');
    const user = JSON.parse(localStorage.getItem('siac_user'));
    if (!user && !isPublic) {
        window.location.href = 'login.html';
    }
})();

// Funciones Globales de Identificación
function getInstId() {
    const user = JSON.parse(localStorage.getItem('siac_user'));
    return user ? (user.inst_id || 1) : 1;
}

function getProgramId() {
    const user = JSON.parse(localStorage.getItem('siac_user'));
    return user ? (user.program_id || 0) : 0;
}

// Redirección de Accesos y Roles
(function() {
    try {
        const user = JSON.parse(localStorage.getItem('siac_user'));
        if (user) {
            const path = window.location.pathname.toLowerCase();
            const isAdmin = (user.role === 'admin' || user.role === 'superadmin' || user.role === 'inst_admin');

            // 1. Evitar que estudiantes y profesores accedan a páginas administrativas
            if (user.role === 'estudiante' || user.role === 'profesor') {
                if (!path.includes('formacion.html') && !path.includes('login') && !path.includes('registro') && path !== '/' && !path.includes('index.html')) {
                    window.location.href = 'formacion.html';
                    return;
                }
            }

            // 2. Proteger exclusivamente los módulos DOFA e INFORMES para administradores
            if (path.includes('dofa.html') || path.includes('informes.html')) {
                if (!isAdmin) {
                    alert('Acceso denegado. Este módulo es de uso exclusivo para Administradores de la plataforma.');
                    window.location.href = 'dashboard.html';
                    return;
                }
            }

            // 3. Ocultar del menú lateral si es un rol restringido
            document.addEventListener("DOMContentLoaded", () => {
                const restrictedRoles = ['estudiante', 'profesor', 'operativo', 'lider', 'coordinador'];
                if (restrictedRoles.includes((user.role || '').toLowerCase())) {
                    const menuInformes = document.querySelector('a[href="informes.html"]');
                    const menuDofa = document.querySelector('a[href="dofa.html"]');
                    if (menuInformes) menuInformes.style.display = 'none';
                    if (menuDofa) menuDofa.style.display = 'none';
                }
            });
        }
    } catch (e) {
        console.error("Error in role check:", e);
    }
})();

// Cargar tema al iniciar
(function() {
    const savedTheme = localStorage.getItem('siac_theme') || 'default';
    document.documentElement.setAttribute('data-theme', savedTheme);
})();

document.addEventListener('DOMContentLoaded', () => {
    // Theme Toggle Handler
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'default' : 'dark';
            document.documentElement.setAttribute('data-theme', currentTheme);
            localStorage.setItem('siac_theme', currentTheme);
        });
    }

    // Control de visibilidad por roles en el menú
    const user = JSON.parse(localStorage.getItem('siac_user'));

    if (user && user.role) {
        const role = user.role.toLowerCase();
        const menuItems = document.querySelectorAll('.sidebar-item');
        
        menuItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            
            // Ocultar Formación para cualquier rol excepto super-admin, profesor y estudiante
            if (role !== 'admin' && role !== 'profesor' && role !== 'estudiante' && role !== 'superadmin' && role !== 'super-admin') {
                if (text.includes('formacion') || text.includes('formación')) {
                    item.style.display = 'none';
                }
            }
            
            // Ocultar Informes y DOFA para cualquier rol que no sea admin
            if (role !== 'admin' && role !== 'super-admin' && role !== 'superadmin' && role !== 'inst_admin') {
                if (text.includes('informes') || text.includes('dofa')) {
                    item.style.display = 'none';
                }
            }
            
            if (role === 'operativo') {
                // El operativo solo ve Dashboard, Evidencias y Cerrar Sesión
                if (!text.includes('dashboard') && !text.includes('evidencias') && !text.includes('cerrar')) {
                    item.style.display = 'none';
                }
            } else if (role === 'estudiante' || role === 'profesor') {
                // El estudiante/profesor solo debe ver Formación y Cerrar Sesión en el menú
                if (!text.includes('cerrar') && !text.includes('formacion') && !text.includes('formación')) {
                    item.style.display = 'none';
                }
            } else if (role === 'lider') {
                // El líder ve todo menos Configuración
                if (text.includes('configuracion') || text.includes('configuración')) {
                    item.style.display = 'none';
                }
            }
        });

        // Ocultar los grupos del acordeón que se quedaron vacíos (sin items visibles)
        const groups = document.querySelectorAll('.sidebar-group');
        groups.forEach(group => {
            const visibleItems = Array.from(group.querySelectorAll('.sidebar-item')).filter(item => {
                return window.getComputedStyle(item).display !== 'none' && item.style.display !== 'none';
            });
            if (visibleItems.length === 0) {
                group.style.display = 'none';
            }
        });
    }

    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add intersection observer for reveal animations on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";
            }
        });
    }, observerOptions);

    // Apply animation initial state and observe
    const animatedElements = document.querySelectorAll('.feature-card, .step, .dash-card');
    animatedElements.forEach(el => {
        el.style.opacity = "0";
        el.style.transform = "translateY(20px)";
        el.style.transition = "opacity 0.6s ease-out, transform 0.6s ease-out";
        observer.observe(el);
    });
    
    // Simulate some real-time activity in the mockup
    const progressCircle = document.querySelector('.progress-circle');
    if(progressCircle) {
        let val = 0;
        const target = 72;
        const interval = setInterval(() => {
            if(val >= target) {
                clearInterval(interval);
            } else {
                val += 2;
                progressCircle.textContent = val + '%';
            }
        }, 30);
    }

    // Asegurar que siempre exista un botón de cerrar sesión en la barra superior para todos los perfiles
    const topbar = document.querySelector('.topbar');
    const userInfo = document.getElementById('userInfo');
    if (topbar && userInfo && !document.getElementById('globalLogoutBtn')) {
        // Envolver userInfo y el botón en un contenedor flex si userInfo no está ya en uno
        if (userInfo.parentElement === topbar) {
            const userContainer = document.createElement('div');
            userContainer.style.display = 'flex';
            userContainer.style.alignItems = 'center';
            userContainer.style.gap = '15px';
            topbar.insertBefore(userContainer, userInfo);
            userContainer.appendChild(userInfo);
            
            const logoutBtn = document.createElement('button');
            logoutBtn.id = 'globalLogoutBtn';
            logoutBtn.className = 'btn-ghost';
            logoutBtn.style.cssText = 'color: #ef4444; font-size: 0.85rem; font-weight: 600; display: flex; align-items: center; gap: 5px; cursor: pointer; border: 1px solid #fca5a5; padding: 6px 12px; border-radius: 8px; background: rgba(239, 68, 68, 0.05);';
            logoutBtn.innerHTML = '🚪 Cerrar Sesión';
            logoutBtn.onclick = function() {
                localStorage.removeItem('siac_user');
                window.location.href = 'index.html';
            };
            userContainer.appendChild(logoutBtn);
        }
    }
});

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
                    <iframe id="skel-module-iframe" src="about:blank"></iframe>
                </div>
            </div>`;
            const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.style.position = 'relative'; // Ensure positioning context
            mainContent.insertAdjacentHTML('beforeend', modalHTML);
        } else {
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }
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
});

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


window.addEventListener('message', (e) => {
    if (e.data && e.data.type === 'settings_updated') {
        window.location.reload();
    }
});
