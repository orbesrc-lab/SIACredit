/**
 * SKEL Permissions Enforcer (Ultra-fast con caché en sessionStorage)
 * Valida permisos por rol inmediatamente sin retardos de red ni parpadeos.
 */

(function() {
    function applyPermissionsNow() {
        const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
        if (!user || !user.role) return;

        const role = (user.role || '').toLowerCase();
        const isSuperAdmin = ['admin', 'superadmin', 'super_admin', 'super-admin'].includes(role);
        const isInstAdmin = isSuperAdmin || role === 'inst_admin';

        // 1. Mostrar de inmediato enlaces exclusivos de SuperAdmin / Admin
        const rcLinks = document.querySelectorAll('.superadmin-rc-link, #menuRegistroCalificado');
        rcLinks.forEach(el => {
            el.style.display = isSuperAdmin ? (el.tagName === 'A' ? 'flex' : 'block') : 'none';
        });

        const crmLinks = document.querySelectorAll('#menuCrm');
        crmLinks.forEach(el => {
            el.style.display = isInstAdmin ? (el.tagName === 'A' ? 'flex' : 'block') : 'none';
        });

        const backupLinks = document.querySelectorAll('#menuBackup');
        backupLinks.forEach(el => {
            el.style.display = isInstAdmin ? (el.tagName === 'A' ? 'flex' : 'block') : 'none';
        });

        // 2. Mapeo de páginas a módulos
        const pageToModuleMap = {
            'dashboard.html': 'autoevaluacion',
            'autoevaluacion.html': 'autoevaluacion',
            'evidencias.html': 'autoevaluacion',
            'evidencias_mod.html': 'autoevaluacion',
            'encuestas.html': 'autoevaluacion',
            'estadisticas.html': 'autoevaluacion',
            'informes.html': 'informes',
            'dofa.html': 'informes',
            'planificacion.html': 'planificacion',
            'empresa_dashboard.html': 'hub_estrategico',
            'empresa_informe_gerencial.html': 'hub_estrategico',
            'empresa_matrices.html': 'hub_estrategico',
            'empresa_porter.html': 'hub_estrategico',
            'empresa_riesgos.html': 'hub_estrategico',
            'empresa_stakeholders.html': 'hub_estrategico',
            'empresa_comunicacion.html': 'hub_estrategico',
            'empresa_dofa.html': 'hub_estrategico',
            'empresa_bcg.html': 'hub_estrategico',
            'empresa_iso.html': 'iso9001',
            'formacion.html': 'capacitacion',
            'curso_reporte.html': 'capacitacion',
            'biblioteca.html': 'herramientas',
            'crm.html': 'herramientas',
            'backup.html': 'herramientas',
            'skel360.html': 'skel_hc360',
            'skel_empresa_dashboard.html': 'skel_hc360',
            'skel_diccionario.html': 'skel_hc360',
            'skel_evaluar.html': 'skel_hc360',
            'skel_empresa_plan_formacion.html': 'skel_hc360',
            'skel_empresa_resultados.html': 'skel_hc360',
            'reporte_individual_360.html': 'skel_hc360',
            'skel360_portal.html': 'skel_hc360',
            'configuracion.html': 'configuracion',
            'normatividad.html': 'autoevaluacion',
            'registro_calificado.html': 'registro_calificado'
        };

        let currentPage = window.location.pathname.split('/').pop();
        if (!currentPage || currentPage === '') currentPage = 'dashboard.html';

        // Protección específica para Registro Calificado
        if (currentPage === 'registro_calificado.html' && !isSuperAdmin) {
            alert('Acceso Exclusivo: El módulo de Registro Calificado está reservado exclusivamente para el Superadministrador.');
            window.location.href = '/dashboard.html';
            return;
        }

        if (isInstAdmin) return; // Administradores y Superadmins tienen acceso completo sin restricciones ni bloqueos

        // 3. Aplicar permisos desde caché local en memoria/sessionStorage
        const cacheKey = `siac_perms_${user.inst_id || 1}_${user.program_id || 0}`;
        const cached = sessionStorage.getItem(cacheKey);
        
        function enforcePerms(perms) {
            if (!perms) return;
            const requiredModule = pageToModuleMap[currentPage];

            if (requiredModule && !['configuracion', 'herramientas'].includes(requiredModule) && perms[requiredModule]) {
                if (!perms[requiredModule].includes(role)) {
                    if (currentPage !== 'dashboard.html') {
                        alert('Acceso Denegado: Tu rol no tiene permisos para acceder a este módulo.');
                        window.location.href = '/dashboard.html';
                        return;
                    }
                }
            }

            // Ocultar enlaces no permitidos
            const sidebarLinks = document.querySelectorAll('.sidebar-menu a, .sidebar-item');
            sidebarLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href) {
                    const linkPage = href.split('/').pop();
                    const linkModule = pageToModuleMap[linkPage];
                    if (linkModule && perms[linkModule] && !perms[linkModule].includes(role)) {
                        link.style.display = 'none';
                        link.classList.add('permission-hidden');
                    }
                }
            });

            // Limpiar grupos vacíos
            document.querySelectorAll('.sidebar-group').forEach(group => {
                const visibleLinks = group.querySelectorAll('.sidebar-submenu a:not(.permission-hidden)');
                if (group.querySelector('.sidebar-submenu') && visibleLinks.length === 0) {
                    group.style.display = 'none';
                }
            });
        }

        if (cached) {
            try {
                enforcePerms(JSON.parse(cached));
            } catch(e) {}
        }

        // Actualizar caché en segundo plano sin bloquear la interfaz
        const lastFetch = sessionStorage.getItem(cacheKey + '_time');
        const now = Date.now();
        if (!cached || !lastFetch || (now - parseInt(lastFetch)) > 300000) { // 5 min
            fetch(`/api/permissions/form?inst_id=${user.inst_id || 1}&program_id=${user.program_id || 0}`)
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success' && data.permissions) {
                        sessionStorage.setItem(cacheKey, JSON.stringify(data.permissions));
                        sessionStorage.setItem(cacheKey + '_time', String(now));
                        enforcePerms(data.permissions);
                    }
                })
                .catch(() => {});
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyPermissionsNow);
    } else {
        applyPermissionsNow();
    }
})();

