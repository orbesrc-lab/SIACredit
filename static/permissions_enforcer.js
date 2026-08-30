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

        // SuperAdmin tiene bypass total
        if (isSuperAdmin) return;

        const currentPage = (window.location.pathname.split('/').pop() || '').toLowerCase();

        // 1. Módulo exclusivo de Registro Calificado
        if (currentPage.includes('registro_calificado') && !isSuperAdmin) {
            alert('Acceso Exclusivo: El módulo de Registro Calificado está reservado para el Superadministrador.');
            window.location.href = '/dashboard.html';
            return;
        }

        // 2. Si es estudiante o profesor, restringir al módulo de formación
        if (role === 'estudiante' || role === 'profesor') {
            if (!currentPage.includes('formacion') && !currentPage.includes('login') && !currentPage.includes('index') && currentPage !== '') {
                window.location.href = '/formacion.html';
                return;
            }
        }

        // 3. Validación por matriz FORM_PERMISSIONS
        let permissions = {};
        try {
            const cached = localStorage.getItem('siac_role_permissions');
            if (cached) permissions = JSON.parse(cached);
        } catch(e) {}

        if (permissions && Object.keys(permissions).length > 0) {
            // Mapear rutas a claves de módulos
            let requiredModule = null;
            if (currentPage.includes('skel360') || currentPage.includes('skel_')) requiredModule = 'skel_hc360';
            else if (currentPage.includes('empresa_')) requiredModule = 'hub_estrategico';
            else if (currentPage.includes('planificacion')) requiredModule = 'planificacion';
            else if (currentPage.includes('informes') || currentPage.includes('dofa')) requiredModule = 'informes';
            else if (currentPage.includes('formacion') || currentPage.includes('curso_')) requiredModule = 'capacitacion';
            else if (currentPage.includes('biblioteca') || currentPage.includes('crm') || currentPage.includes('backup')) requiredModule = 'herramientas';

            if (requiredModule && permissions[requiredModule]) {
                const allowedRoles = permissions[requiredModule];
                if (Array.isArray(allowedRoles) && !allowedRoles.includes(role)) {
                    alert(`Acceso Restringido: Tu rol (${role}) no tiene permisos para acceder a esta sección.`);
                    window.location.href = '/dashboard.html';
                    return;
                }
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', enforceAccess);
    } else {
        enforceAccess();
    }
})();


