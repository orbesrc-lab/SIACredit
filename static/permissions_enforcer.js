/**
 * SKEL Permissions Enforcer (Safe, Fast & Non-Blocking)
 * Control de acceso y redirección inteligente según la matriz de roles.
 * Minimiza el parpadeo y garantiza coherencia sin alertas bloqueantes.
 */

(function() {
    function enforceAccess() {
        const fullPath = (window.location.pathname || '').toLowerCase();
        // Páginas públicas que no requieren validación
        if (fullPath.includes('public') || fullPath.includes('report') || fullPath.includes('encuesta_publica') || fullPath.includes('evaluar') || fullPath.includes('login') || fullPath.includes('registro') || fullPath.endsWith('/')) return;

        let user = null;
        try {
            user = JSON.parse(localStorage.getItem('siac_user') || 'null');
        } catch(e) {}

        if (!user || !user.role) return;

        const role = (user.role || '').toLowerCase();
        const isSuperAdmin = ['admin', 'superadmin', 'super_admin', 'super-admin'].includes(role);

        // SuperAdmin tiene acceso total a todos los módulos
        if (isSuperAdmin) return;

        // 1. Módulo exclusivo de Registro Calificado (Solo Super Administrador)
        if (fullPath.includes('registro_calificado')) {
            window.location.href = '/dashboard.html';
            return;
        }

        // 2. Rol Estudiante: Su único entorno es Capacitación / Aula Virtual
        if (role === 'estudiante') {
            const isEstudiantePermitted = (fullPath.includes('formacion') || fullPath.includes('curso_')) &&
                                          !fullPath.includes('skel') &&
                                          !fullPath.includes('plan-formacion');
            if (isEstudiantePermitted) {
                // Permitido siempre en su entorno formativo
                return;
            }
            // Cualquier intento de acceder a otro módulo redirige limpiamente a formación
            window.location.href = '/formacion.html';
            return;
        }

        // 3. Módulo de Configuración: Exclusivo para SuperAdmin e Inst_Admin
        if (fullPath.includes('configuracion')) {
            if (role !== 'admin' && role !== 'inst_admin') {
                const redirectTarget = (role === 'profesor') ? '/formacion.html' : '/dashboard.html';
                window.location.href = redirectTarget;
                return;
            }
        }

        // 4. Validación por matriz FORM_PERMISSIONS
        let permissions = {};
        try {
            const cached = localStorage.getItem('siac_role_permissions');
            if (cached) permissions = JSON.parse(cached);
        } catch(e) {}

        // Mapear rutas de páginas a las claves oficiales de módulos (evaluando la ruta completa)
        let requiredModule = null;
        if (fullPath.includes('skel360') || fullPath.includes('skel_') || fullPath.includes('reporte_individual') || fullPath.includes('plan-formacion')) {
            requiredModule = 'skel_hc360';
        } else if (fullPath.includes('empresa_iso') || fullPath.includes('iso9001')) {
            requiredModule = 'iso9001';
        } else if (fullPath.includes('empresa_')) {
            requiredModule = 'hub_estrategico';
        } else if (fullPath.includes('planificacion')) {
            requiredModule = 'planificacion';
        } else if (fullPath.includes('informes') || fullPath.includes('dofa')) {
            requiredModule = 'informes';
        } else if (fullPath.includes('formacion') || fullPath.includes('curso_')) {
            requiredModule = 'capacitacion';
        } else if (fullPath.includes('biblioteca') || fullPath.includes('crm') || fullPath.includes('backup')) {
            requiredModule = 'herramientas';
        } else if (fullPath.includes('dashboard') || fullPath.includes('normatividad') || fullPath.includes('autoevaluacion') || fullPath.includes('evidencias') || fullPath.includes('encuestas') || fullPath.includes('estadisticas')) {
            requiredModule = 'autoevaluacion';
        }

        if (requiredModule && permissions && Object.keys(permissions).length > 0) {
            const allowedRoles = permissions[requiredModule];
            if (Array.isArray(allowedRoles) && !allowedRoles.includes(role)) {
                // Redirigir de forma silenciosa y limpia a la sección permitida
                const fallbackUrl = (role === 'profesor') ? '/formacion.html' : '/dashboard.html';
                if (window.location.pathname.toLowerCase() !== fallbackUrl.toLowerCase()) {
                    window.location.href = fallbackUrl;
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
