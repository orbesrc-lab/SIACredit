/**
 * SKEL Permissions Enforcer (Safe & Fast)
 * Garantiza navegación fluida entre módulos sin interrupciones ni bloqueos de red.
 */

(function() {
    function enforceAccess() {
        const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
        if (!user || !user.role) return;

        const role = (user.role || '').toLowerCase();
        const isSuperAdmin = ['admin', 'superadmin', 'super_admin', 'super-admin'].includes(role);
        const isInstAdmin = isSuperAdmin || role === 'inst_admin';

        // Módulo exclusivo de Registro Calificado
        const currentPage = window.location.pathname.split('/').pop() || '';
        if (currentPage.includes('registro_calificado') && !isSuperAdmin) {
            alert('Acceso Exclusivo: El módulo de Registro Calificado está reservado para el Superadministrador.');
            window.location.href = '/dashboard.html';
            return;
        }

        // Si es administrador o superadmin, tiene acceso completo inmediato
        if (isInstAdmin) return;

        // Si es estudiante o profesor, restringir al módulo de formación
        if (role === 'estudiante' || role === 'profesor') {
            if (!currentPage.includes('formacion') && !currentPage.includes('login') && !currentPage.includes('index') && currentPage !== '') {
                window.location.href = '/formacion.html';
                return;
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', enforceAccess);
    } else {
        enforceAccess();
    }
})();


