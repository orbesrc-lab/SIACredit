/**
 * SKEL Permissions Enforcer
 * Este script se ejecuta en todas las páginas protegidas para validar permisos por rol.
 */

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Validar que el usuario esté logueado
    const user = JSON.parse(localStorage.getItem('siac_user'));
    if (!user || !user.role) {
        return; // Probablemente en login u otra página pública
    }

    let originalRole = user.role;
    
    // MAPEO DE ROLES REALES (DB) A COLUMNAS DE LA MATRIZ:
    // Ahora la matriz tiene columnas independientes para: super_admin, admin, lider, operativo, consultor, auditor, profesor, estudiante
    let mappedRole = originalRole;
    if (originalRole === 'inst_admin') {
        mappedRole = 'admin'; // Administrador Institucional usa la columna de Administrador
    }
    
    if (mappedRole === 'super_admin') return; // Bypass global

    // 2. Mapeo de páginas (URLs) a módulos de permisos
    const pageToModuleMap = {
        // Autoevaluación & Estadísticas Globales
        'dashboard.html': 'autoevaluacion',
        'autoevaluacion.html': 'autoevaluacion',
        'evidencias.html': 'autoevaluacion',
        'evidencias_mod.html': 'autoevaluacion',
        'encuestas.html': 'autoevaluacion',
        'estadisticas.html': 'autoevaluacion',
        
        // Informes Institucionales & PDF
        'informes.html': 'informes',
        'dofa.html': 'informes',
        
        // Planificación Estratégica & PDI
        'planificacion.html': 'planificacion',
        
        // Hub Estratégico B2B
        'empresa_dashboard.html': 'hub_estrategico',
        'empresa_informe_gerencial.html': 'hub_estrategico',
        'empresa_matrices.html': 'hub_estrategico',
        'empresa_porter.html': 'hub_estrategico',
        'empresa_riesgos.html': 'hub_estrategico',
        'empresa_stakeholders.html': 'hub_estrategico',
        'empresa_comunicacion.html': 'hub_estrategico',
        'empresa_dofa.html': 'hub_estrategico',
        'empresa_bcg.html': 'hub_estrategico',
        
        // Sistema ISO 9001
        'empresa_iso.html': 'iso9001',
        
        // Módulo de Capacitación & Cursos
        'formacion.html': 'capacitacion',
        'curso_reporte.html': 'capacitacion',
        
        // Herramientas Gerenciales
        'biblioteca.html': 'herramientas',
        'crm.html': 'herramientas',
        'backup.html': 'herramientas',
        
        // Configuración - Usualmente solo admin/superadmin, pero lo manejamos
        'configuracion.html': 'configuracion'
    };

    // 3. Obtener página actual
    let currentPage = window.location.pathname.split('/').pop();
    if (!currentPage || currentPage === '') currentPage = 'dashboard.html';

    try {
        const instId = user.inst_id || 1;
        const progId = user.program_id || 0;
        
        // Evitamos múltiples llamadas en cache si es posible (aunque fetch es rapido localmente)
        const res = await fetch(`/api/permissions/form?inst_id=${instId}&program_id=${progId}`);
        const data = await res.json();
        
        if (data.status === 'success' && data.permissions) {
            const perms = data.permissions;
            
            // 4. VERIFICAR ACCESO A LA PÁGINA ACTUAL
            const requiredModule = pageToModuleMap[currentPage];
            
            if (requiredModule && requiredModule !== 'configuracion' && perms[requiredModule]) {
                if (!perms[requiredModule].includes(mappedRole)) {
                    // BLOQUEADO - Redirigir al dashboard si no es dashboard, sino alertar.
                    if (currentPage !== 'dashboard.html') {
                        if (typeof Swal !== 'undefined') {
                            await Swal.fire({
                                icon: 'error',
                                title: 'Acceso Denegado',
                                text: 'Tu rol no tiene permisos para acceder a este módulo.',
                                confirmButtonColor: '#3b82f6'
                            });
                        } else {
                            alert('Acceso Denegado: Tu rol no tiene permisos para acceder a este módulo.');
                        }
                        window.location.href = 'dashboard.html';
                        return; // Detener ejecución
                    }
                }
            }
            
            // 5. OCULTAR ENLACES EN EL MENÚ LATERAL (SIDEBAR)
            // Recorrer todos los enlaces del sidebar
            const sidebarLinks = document.querySelectorAll('.sidebar-menu a');
            sidebarLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href) {
                    const linkPage = href.split('/').pop();
                    const linkModule = pageToModuleMap[linkPage];
                    
                    if (linkModule && perms[linkModule]) {
                        if (!perms[linkModule].includes(mappedRole)) {
                            // Ocultar el enlace (display: none)
                            link.style.display = 'none';
                            link.classList.add('permission-hidden');
                        }
                    }
                }
            });
            
            // 6. LIMPIAR SIDEBAR GROUPS VACÍOS
            const sidebarGroups = document.querySelectorAll('.sidebar-group');
            sidebarGroups.forEach(group => {
                const visibleLinks = group.querySelectorAll('.sidebar-submenu a:not(.permission-hidden)');
                if (group.querySelector('.sidebar-submenu') && visibleLinks.length === 0) {
                    group.style.display = 'none';
                }
            });
        }
    } catch (error) {
        console.error("Error validando permisos de acceso:", error);
    }
});
