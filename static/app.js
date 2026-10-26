// ── Soporte dinámico de tema (Claro por defecto / Oscuro configurable) ──
(function(){
    var savedTheme = localStorage.getItem('siac_theme') || 'default';
    document.documentElement.setAttribute('data-theme', savedTheme);
})();

// Global authentication check
(function() {
    const path = window.location.pathname.toLowerCase();
    const isPublic = path.includes('index.html') || path.includes('login.html') || path.includes('registro.html') || path.includes('public') || path.includes('report') || path.includes('encuesta_publica') || path.endsWith('/');
    const user = JSON.parse(localStorage.getItem('siac_user') || 'null');
    if (!user && !isPublic) {
        window.location.href = '/login.html';
    }
})();

// Funciones Globales de Identificación
function getInstId() {
    const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
    return user.inst_id || 7;
}

function getProgramId() {
    const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
    return user.program_id || 68;
}

/**
 * authFetch — Wrapper autenticado sobre fetch().
 */
function authFetch(url, options = {}) {
    const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
    const method = ((options && options.method) || 'GET').toUpperCase();
    const isFormData = options.body instanceof FormData;
    const headers = {
        ...(!isFormData && method !== 'GET' ? {'Content-Type': 'application/json'} : {}),
        ...((options && options.headers) || {}),
    };
    const userId = user.id || user.user_id || user.email || localStorage.getItem('user_id') || '1';
    if (userId) {
        headers['X-User-Id'] = String(userId);
    }
    return fetch(url, { ...options, headers });
}

// ── Prevención Inmediata de Parpadeo (Anti-Flicker CSS según Rol) ──
(function applyAntiFlickerStyle() {
    try {
        const user = JSON.parse(localStorage.getItem('siac_user') || 'null');
        if (!user || !user.role) return;
        const role = (user.role || '').toLowerCase();
        const isSuperAdmin = ['admin', 'superadmin', 'super_admin', 'super-admin'].includes(role);
        if (isSuperAdmin) return; // SuperAdmin tiene acceso total sin restricciones

        let css = '';
        // Registro Calificado siempre oculto para no superadmin
        css += '.superadmin-rc-link, #menuRegistroCalificado { display: none !important; }\n';

        // Configuración solo para superadmin e inst_admin
        if (role !== 'inst_admin') {
            css += 'a[href*="configuracion"], #menuConfiguracion { display: none !important; }\n';
        }

        if (role === 'estudiante') {
            // Estudiante: Ocultar todas las categorías administrativas del sidebar
            css += `
                .sidebar-group,
                #menuConsultoriaB2B,
                #menuConfiguracion,
                a[href*="configuracion"],
                .sidebar-item:not([href*="formacion"]):not([onclick*="logout"]):not(.logout-item) {
                    display: none !important;
                }
            `;
        } else {
            // Otros roles: Filtrar según permisos cacheados
            let perms = {};
            try { perms = JSON.parse(localStorage.getItem('siac_role_permissions') || '{}'); } catch(e) {}
            if (perms && Object.keys(perms).length > 0) {
                const isAllowed = (mod) => Array.isArray(perms[mod]) && perms[mod].includes(role);
                if (!isAllowed('autoevaluacion')) css += '.sidebar-group-autoeval { display: none !important; }\n';
                if (!isAllowed('informes')) css += '.sidebar-group-informes { display: none !important; }\n';
                if (!isAllowed('planificacion')) css += '.sidebar-group-planif { display: none !important; }\n';
                if (!isAllowed('hub_estrategico')) css += '#menuConsultoriaB2B, [data-module="hub_estrategico"] { display: none !important; }\n';
                if (!isAllowed('iso9001')) css += 'a[href*="empresa_iso"] { display: none !important; }\n';
                if (!isAllowed('capacitacion')) css += '#menuCapacitacion, a[href*="formacion.html"] { display: none !important; }\n';
                if (!isAllowed('herramientas')) css += '.sidebar-group-herramientas, #menuCrm, #menuBackup, a[href*="biblioteca"] { display: none !important; }\n';
                if (!isAllowed('skel_hc360')) css += '.sidebar-group-skel360 { display: none !important; }\n';
            }
        }

        if (css) {
            const style = document.createElement('style');
            style.id = 'siac-anti-flicker';
            style.textContent = css;
            (document.head || document.documentElement).appendChild(style);
        }
    } catch(e) {
        console.error("Error al aplicar anti-flicker:", e);
    }
})();

// Inicialización de Menú y Permisos Rápida y Reactiva
async function initFastSidebar() {
    const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
    if (!user || !user.role) return;

    const role = (user.role || '').toLowerCase();
    const isSuperAdmin = ['admin', 'superadmin', 'super_admin', 'super-admin'].includes(role);

    // 1. Registro Calificado (Exclusivo SuperAdmin)
    document.querySelectorAll('.superadmin-rc-link, #menuRegistroCalificado').forEach(el => {
        el.style.display = isSuperAdmin ? (el.tagName === 'A' ? 'flex' : 'block') : 'none';
        if (window.location.pathname.includes('registro_calificado')) el.classList.add('active');
    });

    // 2. Configuración del Sistema (Exclusivo SuperAdmin e Inst_Admin)
    const configLinks = document.querySelectorAll('a[href*="configuracion"], #menuConfiguracion');
    const canAccessConfig = isSuperAdmin || (role === 'inst_admin');
    configLinks.forEach(el => {
        el.style.display = canAccessConfig ? (el.tagName === 'A' ? 'flex' : 'block') : 'none';
    });

    // 3. Caso especial Estudiante: entorno exclusivo y limpio
    if (role === 'estudiante') {
        document.querySelectorAll('.sidebar-group, #menuConsultoriaB2B, #menuConfiguracion, a[href*="configuracion"]').forEach(el => {
            el.style.display = 'none';
        });
        document.querySelectorAll('.sidebar-item').forEach(item => {
            const href = (item.getAttribute('href') || '').toLowerCase();
            const text = item.textContent.toLowerCase();
            if (!href.includes('formacion') && !text.includes('formaci') && !text.includes('cerrar') && !text.includes('salir')) {
                item.style.display = 'none';
            } else {
                item.style.display = item.tagName === 'A' ? 'flex' : 'block';
            }
        });
        return; // Terminar ejecución temprana para estudiante
    }

    // 4. Obtener matriz de permisos activa
    let permissions = {};
    try {
        const cached = localStorage.getItem('siac_role_permissions');
        if (cached) permissions = JSON.parse(cached);
    } catch(e) {}

    const canAccess = (moduleKey) => {
        if (isSuperAdmin) return true;
        if (role === 'estudiante') return moduleKey === 'capacitacion';
        if (!permissions || Object.keys(permissions).length === 0) {
            if (moduleKey === 'skel_hc360') return false;
            if (moduleKey === 'hub_estrategico' || moduleKey === 'consultoria') return ['inst_admin', 'consultor'].includes(role);
            if (moduleKey === 'configuracion') return ['inst_admin'].includes(role);
            if (moduleKey === 'capacitacion') return ['inst_admin', 'lider', 'profesor', 'estudiante'].includes(role);
            return true;
        }
        const allowed = permissions[moduleKey];
        if (!allowed || !Array.isArray(allowed)) return false;
        return allowed.includes(role);
    };

    const applyVisibility = (elements, isVisible) => {
        elements.forEach(el => {
            if (!isVisible) {
                el.style.display = 'none';
            } else {
                el.style.display = el.tagName === 'A' ? 'flex' : 'block';
            }
        });
    };

    // Aplicar a cada módulo del Sidebar
    const autoevalGroups = Array.from(document.querySelectorAll('.sidebar-group')).filter(g => {
        const t = (g.querySelector('.sidebar-group-title') || {}).textContent || '';
        return t.toLowerCase().includes('autoevaluación') || t.toLowerCase().includes('autoevaluacion');
    });
    applyVisibility(autoevalGroups, canAccess('autoevaluacion'));

    const informesGroups = Array.from(document.querySelectorAll('.sidebar-group')).filter(g => {
        const t = (g.querySelector('.sidebar-group-title') || {}).textContent || '';
        return t.toLowerCase().includes('análisis') || t.toLowerCase().includes('analisis') || t.toLowerCase().includes('informes');
    });
    applyVisibility(informesGroups, canAccess('informes'));

    const planifGroups = Array.from(document.querySelectorAll('.sidebar-group')).filter(g => {
        const t = (g.querySelector('.sidebar-group-title') || {}).textContent || '';
        return t.toLowerCase().includes('autorregulación') || t.toLowerCase().includes('autorregulacion') || t.toLowerCase().includes('planificación') || t.toLowerCase().includes('planificacion');
    });
    applyVisibility(planifGroups, canAccess('planificacion'));

    // Hub Estratégico / Consultoría B2B
    const b2bGroups = document.querySelectorAll('#menuConsultoriaB2B, [data-module="hub_estrategico"]');
    applyVisibility(Array.from(b2bGroups), canAccess('hub_estrategico'));

    // ISO 9001
    const isoElements = document.querySelectorAll('a[href*="empresa_iso"]');
    applyVisibility(Array.from(isoElements), canAccess('iso9001'));

    // SKEL HC 360
    const skel360Groups = Array.from(document.querySelectorAll('.sidebar-group')).filter(g => {
        const t = (g.querySelector('.sidebar-group-title') || {}).textContent || '';
        return t.toLowerCase().includes('skel') || t.toLowerCase().includes('360');
    });
    applyVisibility(skel360Groups, canAccess('skel_hc360'));

    // Herramientas Gerenciales
    const herramGroups = Array.from(document.querySelectorAll('.sidebar-group')).filter(g => {
        const t = (g.querySelector('.sidebar-group-title') || {}).textContent || '';
        return t.toLowerCase().includes('herramientas gerenciales') || t.toLowerCase().includes('herramientas');
    });
    applyVisibility(herramGroups, canAccess('herramientas'));

    const crmElements = document.querySelectorAll('#menuCrm');
    applyVisibility(Array.from(crmElements), canAccess('herramientas'));
    const backupElements = document.querySelectorAll('#menuBackup');
    applyVisibility(Array.from(backupElements), canAccess('herramientas'));

    // Capacitación / Formación
    const capElements = document.querySelectorAll('#menuCapacitacion, a[href*="formacion.html"]');
    applyVisibility(Array.from(capElements), canAccess('capacitacion'));

    // Ocultar grupos del acordeón cuyos subelementos estén todos ocultos
    document.querySelectorAll('.sidebar-group').forEach(group => {
        const submenuItems = group.querySelectorAll('.sidebar-submenu a, .sidebar-submenu .sidebar-item');
        if (submenuItems.length > 0) {
            const hasVisibleChild = Array.from(submenuItems).some(a => a.style.display !== 'none' && window.getComputedStyle(a).display !== 'none');
            if (!hasVisibleChild) {
                group.style.display = 'none';
            }
        }
    });

    // Sincronizar en segundo plano de forma no bloqueante para aplicar cambios de permisos inmediatamente
    if (!window._syncingRolePermissions) {
        window._syncingRolePermissions = true;
        authFetch(`/api/permissions/form?inst_id=${typeof getInstId === 'function' ? getInstId() : 1}&program_id=0`)
            .then(res => res.json())
            .then(data => {
                if (data && data.status === 'success' && data.permissions) {
                    const currentStr = localStorage.getItem('siac_role_permissions');
                    const newStr = JSON.stringify(data.permissions);
                    if (currentStr !== newStr) {
                        localStorage.setItem('siac_role_permissions', newStr);
                        initFastSidebar(); // Reaplicar visibilidad del menú si la matriz cambió
                    }
                }
            })
            .catch(() => {})
            .finally(() => {
                window._syncingRolePermissions = false;
            });
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFastSidebar);
} else {
    initFastSidebar();
}

document.addEventListener('DOMContentLoaded', () => {
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
            const mainContent = document.querySelector('.main-content') || document.querySelector('.dashboard-container');
            if (mainContent) {
                mainContent.style.position = 'relative';
                mainContent.insertAdjacentHTML('beforeend', modalHTML);
            }
        }
    }
});

// Global functions for the Host
window.openModuleModal = function(url, titleGuess) {
    window.location.href = url;
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
        
        const chatWidget = document.querySelector('.ai-chat-widget');
        if (chatWidget) chatWidget.style.display = 'flex';
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

// Helpers globales para navegación lateral y cierre de sesión
window.toggleSidebarGroup = function(element) {
    if (!element) return;
    const group = element.parentElement;
    if (!group) return;
    const allGroups = document.querySelectorAll('.sidebar-group');
    allGroups.forEach(g => {
        if (g !== group) g.classList.remove('active');
    });
    group.classList.toggle('active');
};

window.logout = function() {
    localStorage.removeItem('siac_user');
    localStorage.removeItem('user_role');
    window.top.location.href = '/login.html';
};

// ==========================================
// Gestor Universal de Modales
// ==========================================
function closeAllModals() {
    try {
        const modals = document.querySelectorAll('.cc-modal-backdrop, .modal-backdrop, .modal-overlay, .rrc-overlay, [id$="Modal"], [id$="modal"], .modal');
        modals.forEach(m => {
            const tag = (m.tagName || '').toLowerCase();
            if (['input', 'select', 'textarea', 'button', 'label', 'option', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5'].includes(tag)) {
                return;
            }
            if (m.style && m.style.display !== 'none') {
                m.style.display = 'none';
            }
            if (m.classList && m.classList.contains('modal-backdrop')) {
                m.remove();
            }
        });
        document.body.style.overflow = '';
    } catch(err) {
        console.error("Error cerrando modales:", err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // 1. Cerrar modales al presionar la tecla Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });

    // 2. Cerrar modal al hacer clic en el fondo oscuro ("cortina") únicamente si se hace clic directo en el backdrop
    document.addEventListener('click', (e) => {
        if (!e.target) return;
        const tag = (e.target.tagName || '').toLowerCase();
        if (['select', 'input', 'textarea', 'button', 'option', 'label', 'a', 'i', 'svg', 'span', 'p', 'div'].includes(tag)) {
            // Si el elemento no es explícitamente un backdrop contenedor, nunca ocultarlo
            const isBackdrop = e.target.classList.contains('cc-modal-backdrop') || 
                               e.target.classList.contains('modal-backdrop') || 
                               e.target.classList.contains('modal-overlay') || 
                               e.target.classList.contains('rrc-overlay');
            if (isBackdrop) {
                e.target.style.display = 'none';
                document.body.style.overflow = '';
            }
            return;
        }
    });

    // 3. Cerrar modales activos al hacer clic en cualquier enlace del menú lateral
    const navLinks = document.querySelectorAll('.sidebar-menu a, .sidebar-item, a[href]');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            closeAllModals();
        });
    });

    // Persistencia del estado de los grupos desplegados en el Sidebar
    try {
        const groups = document.querySelectorAll('.sidebar-group');
        groups.forEach((group, idx) => {
            const title = group.querySelector('.sidebar-group-title');
            if (title) {
                // Si el grupo contiene el enlace activo actual, mantenerlo abierto
                const hasActive = group.querySelector('.sidebar-item.active, .sidebar-item[style*="font-weight: 600"]');
                if (hasActive) {
                    group.classList.add('active');
                }
            }
        });
    } catch(e) {}
});
