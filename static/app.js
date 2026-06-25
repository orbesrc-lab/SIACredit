// Funciones Globales de Identificación
function getInstId() {
    const user = JSON.parse(localStorage.getItem('siac_user'));
    return user ? (user.inst_id || 1) : 1;
}

function getProgramId() {
    const user = JSON.parse(localStorage.getItem('siac_user'));
    return user ? (user.program_id || 0) : 0;
}

// Redirección de Estudiantes para evitar que accedan a páginas administrativas
(function() {
    try {
        const user = JSON.parse(localStorage.getItem('siac_user'));
        if (user && (user.role === 'estudiante' || user.role === 'profesor')) {
            const path = window.location.pathname.toLowerCase();
            if (!path.includes('formacion.html') && !path.includes('login') && !path.includes('registro') && path !== '/' && !path.includes('index.html')) {
                window.location.href = 'formacion.html';
            }
        }
    } catch (e) {
        console.error("Error in student check:", e);
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
            if (role !== 'admin' && role !== 'profesor' && role !== 'estudiante') {
                if (text.includes('formacion') || text.includes('formación')) {
                    item.style.display = 'none';
                }
            }
            
            // Ocultar Informes y DOFA para cualquier rol que no sea admin
            if (role !== 'admin' && role !== 'super-admin' && role !== 'superadmin') {
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
