// Cargar tema al iniciar
(function() {
    const savedTheme = localStorage.getItem('siac_theme') || 'default';
    document.documentElement.setAttribute('data-theme', savedTheme);
})();

document.addEventListener('DOMContentLoaded', () => {
    // Control de visibilidad por roles en el menú
    const user = JSON.parse(localStorage.getItem('siac_user'));
    if (user && user.role) {
        const role = user.role.toLowerCase();
        const menuItems = document.querySelectorAll('.sidebar-item');
        
        menuItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            
            if (role === 'operativo') {
                // El operativo solo ve Dashboard y Evidencias
                if (!text.includes('dashboard') && !text.includes('evidencias')) {
                    item.style.display = 'none';
                }
            } else if (role === 'lider') {
                // El líder ve todo menos Configuración
                if (text.includes('configuracion') || text.includes('configuración')) {
                    item.style.display = 'none';
                }
            }
            // Admin ve todo, no ocultamos nada
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
});
