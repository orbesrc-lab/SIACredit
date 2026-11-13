/**
 * SKEL 360 / SIAC - Módulo Global de Perfil Ejecutivo Institucional
 * Incluye:
 * - Constructor interactivo de Avatar Ejecutivo con Camibuso Oficial y Logo de INTENALCO
 * - Galería de Presets Ejecutivos y Soporte de Foto Personal
 * - Edición de Datos Personales, Cargo, Teléfono y Biografía
 * - Cambio Seguro de Contraseña
 * - Perspectiva y Articulación Integral de Procesos (Autoevaluación, Cambio de Carácter, etc.)
 */

// ── 1. Generador de Avatar Vectorial SVG con Camibuso Oficial ──

function generateCamibusoAvatarSVG(cfg) {
    cfg = cfg || {};
    var skin = cfg.skin || '#d99b70';
    var hair = cfg.hair || 'sidepart';
    var hairColor = cfg.hairColor || '#1c1917';
    var poloColor = cfg.poloColor || '#1e3a8a'; // Azul Marino INTENALCO por defecto
    var collarColor = cfg.collarColor || (poloColor === '#ffffff' ? '#0f172a' : '#172554');
    var glasses = cfg.glasses || 'none';
    var lanyard = cfg.lanyard !== false;
    var logoUrl = cfg.logoUrl || 'https://www.intenalco.edu.co/INTENALCOLOGO.png';
    var photoUrl = cfg.photoUrl || null;

    // Si tiene foto personalizada, renderizar dentro de marco institucional ejecutivo
    if (photoUrl) {
        return `
        <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" class="executive-avatar-svg" style="width:100%; height:100%; border-radius:50%; background:#0f172a;">
            <defs>
                <clipPath id="execPhotoClip">
                    <circle cx="100" cy="100" r="92" />
                </clipPath>
                <linearGradient id="goldBorder" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#fbbf24"/>
                    <stop offset="50%" stop-color="#d97706"/>
                    <stop offset="100%" stop-color="#b45309"/>
                </linearGradient>
            </defs>
            <circle cx="100" cy="100" r="96" fill="url(#goldBorder)" />
            <circle cx="100" cy="100" r="92" fill="#ffffff" />
            <image href="${photoUrl}" x="8" y="8" width="184" height="184" preserveAspectRatio="xMidYMid slice" clip-path="url(#execPhotoClip)" />
            <!-- Insignia Institucional Inferior -->
            <rect x="50" y="166" width="100" height="24" rx="12" fill="#1e3a8a" stroke="#fbbf24" stroke-width="2" />
            <text x="100" y="182" font-size="10" font-weight="900" fill="#ffffff" text-anchor="middle" font-family="'Segoe UI', Roboto, sans-serif" letter-spacing="1">INTENALCO</text>
        </svg>`;
    }

    // Cabello detrás (para moño o melenas largas)
    var backHairSVG = '';
    if (hair === 'bun') {
        backHairSVG = `
            <!-- Moño alto trasero institucional con sujeción dorada -->
            <circle cx="100" cy="12" r="22" fill="${hairColor}" />
            <ellipse cx="100" cy="14" rx="18" ry="7" fill="rgba(255,255,255,0.18)" />
            <rect x="87" y="16" width="26" height="5" rx="2.5" fill="#f59e0b" stroke="#d97706" stroke-width="0.8" />
        `;
    } else if (hair === 'wavy' || hair === 'bob') {
        backHairSVG = `
            <path d="M 44 80 Q 32 140 66 162 L 74 142 Q 54 110 62 80 Z" fill="${hairColor}" />
            <path d="M 156 80 Q 168 140 134 162 L 126 142 Q 146 110 138 80 Z" fill="${hairColor}" />
        `;
    }

    // Cabello frontal según estilo con coronilla elevada, volumen natural y forma de cabeza anatómica (elimina efecto balaca)
    var frontHairSVG = '';
    if (hair === 'sidepart') {
        frontHairSVG = `
            <!-- Peinado Ejecutivo Clásico con Volumen Alto, Raya al Costado y Caída Natural -->
            <path d="M 56 78 C 50 52 50 28 72 14 C 90 2 122 4 142 18 C 152 26 150 52 144 78 C 138 66 132 54 118 48 C 98 40 88 54 74 58 C 64 62 60 72 56 78 Z" fill="${hairColor}" />
            <!-- Raya ejecutiva definida -->
            <path d="M 74 58 C 78 38 82 22 88 14" stroke="rgba(0,0,0,0.35)" stroke-width="2" stroke-linecap="round" fill="none" />
            <!-- Brillo y textura de peinado institucional -->
            <path d="M 94 12 Q 118 14 136 24" stroke="rgba(255,255,255,0.3)" stroke-width="3" stroke-linecap="round" fill="none" />
            <path d="M 98 22 Q 118 24 132 34" stroke="rgba(255,255,255,0.16)" stroke-width="2" stroke-linecap="round" fill="none" />
            <!-- Patilla izquierda sutil -->
            <path d="M 56 78 L 57 84 L 60 80 Z" fill="${hairColor}" />
            <!-- Patilla derecha sutil -->
            <path d="M 144 78 L 143 84 L 140 80 Z" fill="${hairColor}" />
        `;
    } else if (hair === 'short') {
        frontHairSVG = `
            <!-- Corto Moderno con Tupé Elevado y Volumen Superior -->
            <path d="M 56 76 C 50 48 52 24 74 12 C 92 2 118 2 136 14 C 150 24 150 50 144 76 C 138 64 128 50 112 48 C 98 46 92 42 84 46 C 74 50 66 64 56 76 Z" fill="${hairColor}" />
            <!-- Textura de tupé elevado y volumen -->
            <path d="M 88 12 Q 92 26 88 42" stroke="rgba(255,255,255,0.28)" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M 104 10 Q 106 24 102 40" stroke="rgba(255,255,255,0.28)" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M 120 14 Q 120 26 116 40" stroke="rgba(255,255,255,0.2)" stroke-width="2" stroke-linecap="round" fill="none" />
        `;
    } else if (hair === 'curly') {
        frontHairSVG = `
            <!-- Cabello Rizado / Ondulado con Copete Abundante y Corona Alta -->
            <path d="M 54 78 C 46 44 48 20 74 10 C 92 2 120 4 140 14 C 154 24 152 50 146 78 Z" fill="${hairColor}" />
            <!-- Rizos de coronilla con relieve natural -->
            <circle cx="62" cy="24" r="14" fill="${hairColor}" />
            <circle cx="80" cy="12" r="16" fill="${hairColor}" />
            <circle cx="104" cy="9" r="17" fill="${hairColor}" />
            <circle cx="128" cy="14" r="16" fill="${hairColor}" />
            <circle cx="146" cy="30" r="14" fill="${hairColor}" />
            <circle cx="52" cy="42" r="13" fill="${hairColor}" />
            <!-- Rizos frontales naturales -->
            <circle cx="76" cy="46" r="9" fill="${hairColor}" />
            <circle cx="100" cy="44" r="9.5" fill="${hairColor}" />
            <circle cx="124" cy="46" r="9" fill="${hairColor}" />
        `;
    } else if (hair === 'bun') {
        frontHairSVG = `
            <!-- Moño / Recogido Formal con Copete Elevado y Frente Despejada -->
            <path d="M 56 78 C 50 48 52 24 76 16 C 92 8 114 8 130 16 C 148 24 150 48 144 78 C 138 62 126 48 100 48 C 74 48 62 62 56 78 Z" fill="${hairColor}" />
            <path d="M 76 24 Q 100 16 124 24" stroke="rgba(255,255,255,0.28)" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M 80 36 Q 100 28 120 36" stroke="rgba(255,255,255,0.16)" stroke-width="2" stroke-linecap="round" fill="none" />
        `;
    } else if (hair === 'bob') {
        frontHairSVG = `
            <!-- Melena Lisa Bob con Volumen de Coronilla Elevada y Caída Elegante -->
            <path d="M 54 82 C 48 44 52 20 76 12 C 94 4 118 4 136 14 C 152 24 154 48 148 82 C 152 116 144 142 136 148 L 126 144 C 132 118 132 74 100 74 C 68 74 68 118 74 144 L 64 148 C 56 142 48 116 54 82 Z" fill="${hairColor}" />
            <path d="M 74 22 Q 100 14 126 22" stroke="rgba(255,255,255,0.24)" stroke-width="2.5" stroke-linecap="round" fill="none" />
        `;
    } else if (hair === 'bald') {
        frontHairSVG = `
            <!-- Corte Rapado Ejecutivo Sutil y Gradual -->
            <path d="M 58 76 C 54 44 70 24 100 24 C 130 24 146 44 142 76 C 138 66 126 54 100 54 C 74 54 62 66 58 76 Z" fill="${hairColor}" opacity="0.32" />
        `;
    } else if (hair === 'wavy') {
        frontHairSVG = `
            <!-- Ondas Largas con Copete Elevado y Caída Fluyente -->
            <path d="M 54 80 C 48 44 52 18 76 10 C 94 2 120 2 138 12 C 152 22 154 46 148 80 C 138 62 126 46 100 46 C 74 46 62 62 54 80 Z" fill="${hairColor}" />
            <path d="M 54 85 Q 44 125 60 156 L 70 152 Q 60 125 66 85 Z" fill="${hairColor}" />
            <path d="M 146 85 Q 156 125 140 156 L 130 152 Q 140 125 134 85 Z" fill="${hairColor}" />
            <path d="M 76 20 Q 100 12 124 20" stroke="rgba(255,255,255,0.26)" stroke-width="2.5" stroke-linecap="round" fill="none" />
        `;
    }

    // Gafas ejecutivas
    var glassesSVG = '';
    if (glasses === 'rect') {
        glassesSVG = `
            <g stroke="#18181b" stroke-width="2.2" fill="rgba(255,255,255,0.25)">
                <rect x="70" y="68" width="24" height="15" rx="3" />
                <rect x="106" y="68" width="24" height="15" rx="3" />
                <line x1="94" y1="74" x2="106" y2="74" />
                <line x1="60" y1="74" x2="70" y2="74" />
                <line x1="130" y1="74" x2="140" y2="74" />
            </g>
        `;
    } else if (glasses === 'round') {
        glassesSVG = `
            <g stroke="#d97706" stroke-width="2" fill="rgba(255,255,255,0.2)">
                <circle cx="82" cy="76" r="11" />
                <circle cx="118" cy="76" r="11" />
                <line x1="93" y1="75" x2="107" y2="75" />
                <line x1="61" y1="75" x2="71" y2="75" />
                <line x1="129" y1="75" x2="139" y2="75" />
            </g>
        `;
    } else if (glasses === 'wire') {
        glassesSVG = `
            <g stroke="#64748b" stroke-width="1.6" fill="rgba(255,255,255,0.2)">
                <rect x="71" y="69" width="23" height="13" rx="2" />
                <rect x="106" y="69" width="23" height="13" rx="2" />
                <line x1="94" y1="74" x2="106" y2="74" />
            </g>
        `;
    }

    // Carnet institucional (Lanyard)
    var lanyardSVG = '';
    if (lanyard) {
        lanyardSVG = `
            <!-- Cinta de carnet institucional azul INTENALCO con texto -->
            <path d="M 88 136 L 96 178" stroke="#1d4ed8" stroke-width="4.5" stroke-linecap="round" />
            <path d="M 112 136 L 104 178" stroke="#1d4ed8" stroke-width="4.5" stroke-linecap="round" />
            <!-- Hebilla / mosquetón metálico -->
            <rect x="96" y="176" width="8" height="5" rx="1.5" fill="#94a3b8" stroke="#475569" stroke-width="0.8" />
            <!-- Credencial de acreditación institucional -->
            <rect x="88" y="181" width="24" height="19" rx="3" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" />
            <rect x="90" y="183" width="20" height="5" fill="#1e3a8a" />
            <circle cx="94" cy="192" r="3" fill="#cbd5e1" />
            <line x1="99" y1="190" x2="106" y2="190" stroke="#334155" stroke-width="1.2" />
            <line x1="99" y1="194" x2="105" y2="194" stroke="#64748b" stroke-width="1" />
        `;
    }

    // Botones del camibuso
    var buttonColor = (poloColor === '#ffffff' ? '#1e293b' : '#f8fafc');

    return `
    <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" class="executive-avatar-svg" style="width:100%; height:100%; border-radius:50%; background:linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);">
        <defs>
            <clipPath id="avatarCircle">
                <circle cx="100" cy="100" r="100" />
            </clipPath>
            <filter id="execShadow" x="-10%" y="-10%" width="120%" height="120%">
                <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.18"/>
            </filter>
        </defs>

        <g clip-path="url(#avatarCircle)">
            <!-- Cabello detrás -->
            ${backHairSVG}

            <!-- Cuello -->
            <path d="M 86 98 L 86 132 C 86 138 114 138 114 132 L 114 98 Z" fill="${skin}" />
            <ellipse cx="100" cy="112" rx="15" ry="6" fill="rgba(0,0,0,0.14)" />

            <!-- Cabeza / Rostro -->
            <ellipse cx="100" cy="74" rx="35" ry="41" fill="${skin}" filter="url(#execShadow)" />

            <!-- Orejas -->
            <circle cx="64" cy="76" r="8" fill="${skin}" />
            <circle cx="64" cy="76" r="5" fill="rgba(0,0,0,0.08)" />
            <circle cx="136" cy="76" r="8" fill="${skin}" />
            <circle cx="136" cy="76" r="5" fill="rgba(0,0,0,0.08)" />

            <!-- Ojos ejecutivos -->
            <ellipse cx="84" cy="75" rx="3.5" ry="4" fill="#1c1917" />
            <circle cx="85.5" cy="73.5" r="1.2" fill="#ffffff" />
            <ellipse cx="116" cy="75" rx="3.5" ry="4" fill="#1c1917" />
            <circle cx="117.5" cy="73.5" r="1.2" fill="#ffffff" />

            <!-- Cejas -->
            <path d="M 77 68 Q 84 65 91 67" stroke="${hairColor}" stroke-width="2.2" stroke-linecap="round" fill="none" />
            <path d="M 109 67 Q 116 65 123 68" stroke="${hairColor}" stroke-width="2.2" stroke-linecap="round" fill="none" />

            <!-- Nariz ejecutiva -->
            <path d="M 100 74 L 99 82 L 103 82" stroke="rgba(0,0,0,0.22)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none" />

            <!-- Sonrisa profesional -->
            <path d="M 91 90 Q 100 96 109 90" stroke="#991b1b" stroke-width="2" stroke-linecap="round" fill="none" />

            <!-- Cabello frontal -->
            ${frontHairSVG}

            <!-- Gafas si aplica -->
            ${glassesSVG}

            <!-- ── CUERPO: CAMIBUSO INSTITUCIONAL OFICIAL ── -->
            <!-- Torso / Hombros del Camibuso -->
            <path d="M 22 205 L 22 165 C 22 142 56 128 72 125 L 86 126 C 92 138 108 138 114 126 L 128 125 C 144 128 178 142 178 165 L 178 205 Z" fill="${poloColor}" />

            <!-- Costuras y textura de hombro del camibuso -->
            <path d="M 28 168 C 45 150 68 135 84 130" stroke="rgba(0,0,0,0.12)" stroke-width="1.5" fill="none" />
            <path d="M 172 168 C 155 150 132 135 116 130" stroke="rgba(0,0,0,0.12)" stroke-width="1.5" fill="none" />

            <!-- Pechera / Tapeta Central del Camibuso -->
            <rect x="94" y="138" width="12" height="46" rx="2" fill="${collarColor}" opacity="0.95" />
            <line x1="94" y1="138" x2="94" y2="184" stroke="rgba(0,0,0,0.2)" stroke-width="0.8" />
            <line x1="106" y1="138" x2="106" y2="184" stroke="rgba(255,255,255,0.25)" stroke-width="0.8" />

            <!-- Botones ejecutivos nacarados -->
            <circle cx="100" cy="150" r="2.8" fill="${buttonColor}" stroke="rgba(0,0,0,0.2)" stroke-width="0.8" />
            <circle cx="100" cy="150" r="1.2" fill="none" stroke="rgba(0,0,0,0.3)" stroke-width="0.6" />
            <circle cx="100" cy="166" r="2.8" fill="${buttonColor}" stroke="rgba(0,0,0,0.2)" stroke-width="0.8" />
            <circle cx="100" cy="166" r="1.2" fill="none" stroke="rgba(0,0,0,0.3)" stroke-width="0.6" />

            <!-- Solapas del Cuello Polo (Camibuso) -->
            <!-- Cuello Izquierdo -->
            <polygon points="72,124 100,143 83,153 66,134" fill="${collarColor}" stroke="rgba(0,0,0,0.18)" stroke-width="1" />
            <line x1="72" y1="124" x2="83" y2="153" stroke="rgba(255,255,255,0.25)" stroke-width="1" />

            <!-- Cuello Derecho -->
            <polygon points="128,124 100,143 117,153 134,134" fill="${collarColor}" stroke="rgba(0,0,0,0.18)" stroke-width="1" />
            <line x1="128" y1="124" x2="117" y2="153" stroke="rgba(255,255,255,0.25)" stroke-width="1" />

            <!-- ── ESCUDO / LOGO BORDADO INSTITUCIONAL EN EL PECHO (Pecho Izquierdo del Usuario) ── -->
            <!-- Ubicado en x=136, y=156 con bordado perimetral dorado -->
            <g transform="translate(126, 145)">
                <!-- Base del Escudo Bordado -->
                <rect x="0" y="0" width="22" height="23" rx="4" fill="#ffffff" stroke="#d97706" stroke-width="1.2" stroke-dasharray="2,1" filter="url(#execShadow)" />
                <!-- Fondo interior azul institucional -->
                <rect x="1.5" y="1.5" width="19" height="20" rx="3" fill="#f8fafc" />
                <!-- Imagen del Logo Institucional INTENALCO -->
                <image href="${logoUrl}" x="2" y="2" width="18" height="14" preserveAspectRatio="xMidYMid meet" />
                <!-- Siglas Institucionales Bordadas -->
                <rect x="2" y="16.5" width="18" height="4.5" rx="1.5" fill="#1e3a8a" />
                <text x="11" y="20" font-size="3.6" font-weight="900" fill="#ffffff" text-anchor="middle" font-family="'Segoe UI', Roboto, sans-serif" letter-spacing="0.4">INTENALCO</text>
            </g>

            <!-- Carnet de Identificación Colgado (Lanyard) si está activo -->
            ${lanyardSVG}
        </g>
    </svg>`;
}

// ── 2. Presets Ejecutivos Listos para Usar ──

function getExecutiveAvatarPresets() {
    return [
        {
            id: 'preset_rectoria',
            title: 'Directivo / Rectoría',
            desc: 'Polo Azul Institucional INTENALCO, Carnet al Cuello',
            config: { skin: '#d99b70', hair: 'sidepart', hairColor: '#1c1917', poloColor: '#1e3a8a', glasses: 'none', lanyard: true }
        },
        {
            id: 'preset_internacionalizacion',
            title: 'Líder de Internacionalización',
            desc: 'Polo Blanco Ejecutivo, Gafas Rectangulares',
            config: { skin: '#f5be98', hair: 'short', hairColor: '#451a03', poloColor: '#ffffff', collarColor: '#1e3a8a', glasses: 'rect', lanyard: true }
        },
        {
            id: 'preset_calidad',
            title: 'Líder de Calidad & Autoevaluación',
            desc: 'Polo Verde Esmeralda, Gafas Doradas',
            config: { skin: '#ffd1b3', hair: 'bun', hairColor: '#78350f', poloColor: '#065f46', collarColor: '#022c22', glasses: 'round', lanyard: true }
        },
        {
            id: 'preset_planeacion',
            title: 'Director(a) de Planeación',
            desc: 'Polo Vino Tinto Borgoña, Carnet Oficial',
            config: { skin: '#a56c45', hair: 'bob', hairColor: '#1c1917', poloColor: '#881337', collarColor: '#4c0519', glasses: 'wire', lanyard: true }
        },
        {
            id: 'preset_academico',
            title: 'Vicerrectoría Académica',
            desc: 'Polo Azul Rey, Peinado Ejecutivo',
            config: { skin: '#d99b70', hair: 'curly', hairColor: '#1c1917', poloColor: '#2563eb', collarColor: '#1e3a8a', glasses: 'none', lanyard: true }
        },
        {
            id: 'preset_investigacion',
            title: 'Docente Investigador(a)',
            desc: 'Polo Negro Ejecutivo, Gafas Intelectuales',
            config: { skin: '#5c3826', hair: 'short', hairColor: '#1c1917', poloColor: '#18181b', collarColor: '#09090b', glasses: 'rect', lanyard: true }
        },
        {
            id: 'preset_extension',
            title: 'Líder de Extensión y Entorno',
            desc: 'Polo Azul INTENALCO, Melena Ondulada',
            config: { skin: '#ffd1b3', hair: 'wavy', hairColor: '#ca8a04', poloColor: '#1e3a8a', collarColor: '#172554', glasses: 'none', lanyard: true }
        },
        {
            id: 'preset_coordinador',
            title: 'Coordinador Operativo',
            desc: 'Polo Blanco Clásico, Corte Rapado Moderno',
            config: { skin: '#f5be98', hair: 'bald', hairColor: '#64748b', poloColor: '#ffffff', collarColor: '#334155', glasses: 'wire', lanyard: true }
        }
    ];
}

// ── 3. Estado Activo del Editor de Perfil ──

window._currentProfileData = null;
window._activeAvatarConfig = {
    skin: '#d99b70',
    hair: 'sidepart',
    hairColor: '#1c1917',
    poloColor: '#1e3a8a',
    collarColor: '#172554',
    glasses: 'none',
    lanyard: true,
    photoUrl: null
};

// ── 4. Inyección del Modal de Perfil Ejecutivo Institucional ──

function ensureExecutiveProfileModalDOM() {
    if (document.getElementById('userProfileModal')) return;

    var modalHTML = `
    <div id="userProfileModal" style="display:none; position:fixed; inset:0; z-index:99999; background:rgba(15,23,42,0.75); backdrop-filter:blur(6px); align-items:center; justify-content:center; padding:16px;">
        <div style="background:#ffffff; width:100%; max-width:880px; max-height:92vh; border-radius:18px; box-shadow:0 25px 50px -12px rgba(0,0,0,0.35); display:flex; flex-direction:column; overflow:hidden; border:1px solid #cbd5e1; font-family:'Segoe UI', Roboto, sans-serif;">
            
            <!-- Cabecera Institucional -->
            <div style="background:linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #0369a1 100%); color:white; padding:18px 24px; display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <img id="modalInstLogo" src="https://www.intenalco.edu.co/INTENALCOLOGO.png" alt="Logo INTENALCO" style="width:42px; height:42px; object-fit:contain; background:white; padding:3px; border-radius:8px; border:1px solid rgba(255,255,255,0.4);" onerror="this.style.display='none'">
                    <div>
                        <div style="font-size:0.75rem; letter-spacing:1.5px; text-transform:uppercase; color:#93c5fd; font-weight:700;">INSTITUCIÓN UNIVERSITARIA INTENALCO</div>
                        <h2 style="margin:0; font-size:1.25rem; font-weight:800; color:#ffffff;">Perfil Ejecutivo & Articulación Institucional</h2>
                    </div>
                </div>
                <button onclick="closeExecutiveProfileModal()" style="background:rgba(255,255,255,0.15); border:none; color:white; width:34px; height:34px; border-radius:50%; cursor:pointer; font-size:1.1rem; display:flex; align-items:center; justify-content:center; transition:0.2s;" onmouseover="this.style.background='rgba(239,68,68,0.8)'" onmouseout="this.style.background='rgba(255,255,255,0.15)'">✕</button>
            </div>

            <!-- Barra de Pestañas Principales -->
            <div style="display:flex; border-bottom:1px solid #e2e8f0; background:#f8fafc; overflow-x:auto;">
                <button class="profile-tab-btn active" data-tab="tabAvatar" onclick="switchProfileTab('tabAvatar')" style="padding:12px 20px; font-weight:700; font-size:0.88rem; border:none; background:transparent; cursor:pointer; border-bottom:3px solid #2563eb; color:#1e3a8a; display:flex; align-items:center; gap:8px;">
                    👔 Avatar Institucional (Camibuso)
                </button>
                <button class="profile-tab-btn" data-tab="tabDatos" onclick="switchProfileTab('tabDatos')" style="padding:12px 20px; font-weight:600; font-size:0.88rem; border:none; background:transparent; cursor:pointer; border-bottom:3px solid transparent; color:#64748b; display:flex; align-items:center; gap:8px;">
                    👤 Datos & Cargo Institucional
                </button>
                <button class="profile-tab-btn" data-tab="tabProcesos" onclick="switchProfileTab('tabProcesos')" style="padding:12px 20px; font-weight:600; font-size:0.88rem; border:none; background:transparent; cursor:pointer; border-bottom:3px solid transparent; color:#64748b; display:flex; align-items:center; gap:8px;">
                    🎯 Articulación de Mis Procesos
                </button>
                <button class="profile-tab-btn" data-tab="tabSeguridad" onclick="switchProfileTab('tabSeguridad')" style="padding:12px 20px; font-weight:600; font-size:0.88rem; border:none; background:transparent; cursor:pointer; border-bottom:3px solid transparent; color:#64748b; display:flex; align-items:center; gap:8px;">
                    🔒 Seguridad & Contraseña
                </button>
            </div>

            <!-- Contenido Scrolleable del Modal -->
            <div style="flex:1; overflow-y:auto; padding:24px; background:#ffffff;">

                <!-- ── PESTAÑA 1: CONSTRUCTOR DE AVATAR CON CAMIBUSO ── -->
                <div id="tabAvatar" class="profile-tab-pane">
                    <div style="display:grid; grid-template-columns: 240px 1fr; gap:24px; align-items:start;">
                        <!-- Vista Previa del Avatar Oficial -->
                        <div style="text-align:center; background:#f8fafc; padding:20px; border-radius:14px; border:1px solid #e2e8f0;">
                            <div id="avatarLivePreview" style="width:160px; height:160px; margin:0 auto; box-shadow:0 10px 25px -5px rgba(30,58,138,0.25); border-radius:50%;">
                                <!-- El SVG se renderiza dinámicamente aquí -->
                            </div>
                            <div style="margin-top:12px; font-weight:700; color:#1e293b; font-size:0.92rem;" id="previewUserName">Usuario Activo</div>
                            <div style="font-size:0.75rem; color:#059669; font-weight:700; background:#ecfdf5; padding:3px 10px; border-radius:12px; display:inline-block; margin-top:4px;">
                                👕 Camibuso Oficial INTENALCO
                            </div>
                            <div style="font-size:0.75rem; color:#64748b; margin-top:6px;" id="previewUserCargo">Líder Institucional</div>

                            <button onclick="triggerPhotoUpload()" style="margin-top:16px; width:100%; font-size:0.8rem; padding:8px 12px; background:white; border:1px dashed #3b82f6; color:#2563eb; border-radius:8px; font-weight:600; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:6px;">
                                📷 Subir Foto Propia
                            </button>
                            <input type="file" id="userPhotoInput" accept="image/*" style="display:none;" onchange="handlePhotoUpload(this)">
                            <button id="btnRemovePhoto" onclick="removePhotoCustom()" style="display:none; margin-top:6px; width:100%; font-size:0.75rem; padding:6px 10px; background:#fee2e2; border:none; color:#dc2626; border-radius:6px; font-weight:600; cursor:pointer;">
                                ✕ Quitar Foto y Usar Camibuso
                            </button>
                        </div>

                        <!-- Controles del Constructor de Avatar -->
                        <div>
                            <!-- Selector de Modo: Presets o Personalizar -->
                            <div style="display:flex; gap:10px; margin-bottom:16px;">
                                <button type="button" id="btnModeCustomize" onclick="setAvatarSubMode('customize')" style="flex:1; padding:8px 12px; border-radius:8px; border:1px solid #2563eb; background:#eff6ff; color:#1e40af; font-weight:700; font-size:0.82rem; cursor:pointer;">
                                    🎨 Diseñar Mi Camibuso
                                </button>
                                <button type="button" id="btnModePresets" onclick="setAvatarSubMode('presets')" style="flex:1; padding:8px 12px; border-radius:8px; border:1px solid #cbd5e1; background:white; color:#475569; font-weight:600; font-size:0.82rem; cursor:pointer;">
                                    👔 Galería de 8 Presets
                                </button>
                            </div>

                            <!-- Panel Diseñar Personalizado -->
                            <div id="paneCustomize">
                                <!-- Color del Camibuso -->
                                <div style="margin-bottom:16px;">
                                    <label style="display:block; font-size:0.8rem; font-weight:700; color:#334155; margin-bottom:6px;">Color del Camibuso Institucional:</label>
                                    <div style="display:flex; gap:8px; flex-wrap:wrap;">
                                        <button type="button" onclick="setPoloColor('#1e3a8a', '#172554')" class="color-pill" style="background:#1e3a8a; width:34px; height:34px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 0 0 2px #cbd5e1; cursor:pointer;" title="Azul INTENALCO"></button>
                                        <button type="button" onclick="setPoloColor('#ffffff', '#0f172a')" class="color-pill" style="background:#ffffff; width:34px; height:34px; border-radius:50%; border:2px solid #e2e8f0; box-shadow:0 0 0 2px #cbd5e1; cursor:pointer;" title="Blanco Ejecutivo"></button>
                                        <button type="button" onclick="setPoloColor('#881337', '#4c0519')" class="color-pill" style="background:#881337; width:34px; height:34px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 0 0 2px #cbd5e1; cursor:pointer;" title="Vino Tinto"></button>
                                        <button type="button" onclick="setPoloColor('#065f46', '#022c22')" class="color-pill" style="background:#065f46; width:34px; height:34px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 0 0 2px #cbd5e1; cursor:pointer;" title="Verde Esmeralda"></button>
                                        <button type="button" onclick="setPoloColor('#2563eb', '#1e3a8a')" class="color-pill" style="background:#2563eb; width:34px; height:34px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 0 0 2px #cbd5e1; cursor:pointer;" title="Azul Rey"></button>
                                        <button type="button" onclick="setPoloColor('#18181b', '#09090b')" class="color-pill" style="background:#18181b; width:34px; height:34px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 0 0 2px #cbd5e1; cursor:pointer;" title="Negro Ejecutivo"></button>
                                    </div>
                                </div>

                                <!-- Tono de Piel -->
                                <div style="margin-bottom:16px;">
                                    <label style="display:block; font-size:0.8rem; font-weight:700; color:#334155; margin-bottom:6px;">Tono de Piel:</label>
                                    <div style="display:flex; gap:8px;">
                                        <button type="button" onclick="setSkinColor('#ffd1b3')" style="background:#ffd1b3; width:30px; height:30px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 0 2px #cbd5e1; cursor:pointer;" title="Claro"></button>
                                        <button type="button" onclick="setSkinColor('#f5be98')" style="background:#f5be98; width:30px; height:30px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 0 2px #cbd5e1; cursor:pointer;" title="Medio Claro"></button>
                                        <button type="button" onclick="setSkinColor('#d99b70')" style="background:#d99b70; width:30px; height:30px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 0 2px #cbd5e1; cursor:pointer;" title="Trigueño Cálido"></button>
                                        <button type="button" onclick="setSkinColor('#a56c45')" style="background:#a56c45; width:30px; height:30px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 0 2px #cbd5e1; cursor:pointer;" title="Moreno Canela"></button>
                                        <button type="button" onclick="setSkinColor('#5c3826')" style="background:#5c3826; width:30px; height:30px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 0 2px #cbd5e1; cursor:pointer;" title="Oscuro"></button>
                                    </div>
                                </div>

                                <!-- Estilo y Color de Cabello -->
                                <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:16px;">
                                    <div>
                                        <label style="display:block; font-size:0.8rem; font-weight:700; color:#334155; margin-bottom:6px;">Estilo de Cabello:</label>
                                        <select id="selHairStyle" onchange="setHairStyle(this.value)" style="width:100%; padding:8px 10px; border-radius:8px; border:1px solid #cbd5e1; font-size:0.85rem;">
                                            <option value="sidepart">Ejecutivo Clásico (Lado)</option>
                                            <option value="short">Corto Moderno</option>
                                            <option value="curly">Rizado / Ondulado</option>
                                            <option value="bun">Moño / Recogido Formal</option>
                                            <option value="bob">Melena Lisa / Bob</option>
                                            <option value="wavy">Ondas Largas</option>
                                            <option value="bald">Calvo / Rapado Ejecutivo</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label style="display:block; font-size:0.8rem; font-weight:700; color:#334155; margin-bottom:6px;">Color de Cabello:</label>
                                        <div style="display:flex; gap:6px; align-items:center; height:38px;">
                                            <button type="button" onclick="setHairColor('#1c1917')" style="background:#1c1917; width:26px; height:26px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 0 1.5px #cbd5e1; cursor:pointer;" title="Negro"></button>
                                            <button type="button" onclick="setHairColor('#451a03')" style="background:#451a03; width:26px; height:26px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 0 1.5px #cbd5e1; cursor:pointer;" title="Castaño Oscuro"></button>
                                            <button type="button" onclick="setHairColor('#78350f')" style="background:#78350f; width:26px; height:26px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 0 1.5px #cbd5e1; cursor:pointer;" title="Castaño"></button>
                                            <button type="button" onclick="setHairColor('#ca8a04')" style="background:#ca8a04; width:26px; height:26px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 0 1.5px #cbd5e1; cursor:pointer;" title="Rubio Miel"></button>
                                            <button type="button" onclick="setHairColor('#64748b')" style="background:#64748b; width:26px; height:26px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 0 1.5px #cbd5e1; cursor:pointer;" title="Canoso / Plata"></button>
                                        </div>
                                    </div>
                                </div>

                                <!-- Gafas y Carnet Institucional -->
                                <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px;">
                                    <div>
                                        <label style="display:block; font-size:0.8rem; font-weight:700; color:#334155; margin-bottom:6px;">Gafas Ejecutivas:</label>
                                        <select id="selGlasses" onchange="setGlasses(this.value)" style="width:100%; padding:8px 10px; border-radius:8px; border:1px solid #cbd5e1; font-size:0.85rem;">
                                            <option value="none">Sin Gafas</option>
                                            <option value="rect">Rectangulares Negras</option>
                                            <option value="round">Redondas Intelectuales (Doradas)</option>
                                            <option value="wire">Montura Metálica Fina</option>
                                        </select>
                                    </div>
                                    <div style="display:flex; align-items:center; gap:10px; padding-top:22px;">
                                        <input type="checkbox" id="chkLanyard" onchange="setLanyard(this.checked)" checked style="width:18px; height:18px; cursor:pointer;">
                                        <label for="chkLanyard" style="font-size:0.82rem; font-weight:700; color:#1e293b; cursor:pointer;">
                                            Carnet Institucional al Cuello (Lanyard INTENALCO)
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <!-- Panel de Galería de 8 Presets -->
                            <div id="panePresets" style="display:none; max-height:280px; overflow-y:auto; padding-right:6px;">
                                <div id="presetsGrid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(130px, 1fr)); gap:12px;">
                                    <!-- Los 8 presets se inyectan dinámicamente -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ── PESTAÑA 2: DATOS PERSONALES Y CARGO ── -->
                <div id="tabDatos" class="profile-tab-pane" style="display:none;">
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:18px;">
                        <div>
                            <label style="display:block; font-size:0.82rem; font-weight:700; color:#334155; margin-bottom:6px;">Nombre Completo:</label>
                            <input type="text" id="profName" style="width:100%; padding:10px 12px; border-radius:8px; border:1px solid #cbd5e1; font-size:0.9rem;" placeholder="Ej: John Cortés">
                        </div>
                        <div>
                            <label style="display:block; font-size:0.82rem; font-weight:700; color:#334155; margin-bottom:6px;">Correo Institucional (Acceso):</label>
                            <input type="email" id="profEmail" readonly style="width:100%; padding:10px 12px; border-radius:8px; border:1px solid #e2e8f0; background:#f8fafc; color:#64748b; font-size:0.9rem;">
                        </div>
                        <div>
                            <label style="display:block; font-size:0.82rem; font-weight:700; color:#334155; margin-bottom:6px;">Cargo / Dependencia Institucional:</label>
                            <input type="text" id="profCargo" style="width:100%; padding:10px 12px; border-radius:8px; border:1px solid #cbd5e1; font-size:0.9rem;" placeholder="Ej: Líder de Internacionalización y Cooperación">
                        </div>
                        <div>
                            <label style="display:block; font-size:0.82rem; font-weight:700; color:#334155; margin-bottom:6px;">Teléfono / WhatsApp de Contacto:</label>
                            <input type="text" id="profPhone" style="width:100%; padding:10px 12px; border-radius:8px; border:1px solid #cbd5e1; font-size:0.9rem;" placeholder="Ej: 315 123 4567">
                        </div>
                        <div style="grid-column:1 / -1;">
                            <label style="display:block; font-size:0.82rem; font-weight:700; color:#334155; margin-bottom:6px;">Breve Perfil Profesional / Biografía:</label>
                            <textarea id="profBio" rows="3" style="width:100%; padding:10px 12px; border-radius:8px; border:1px solid #cbd5e1; font-size:0.9rem;" placeholder="Responsable de los convenios internacionales, movilidad académica y articulación con redes de educación superior..."></textarea>
                        </div>
                    </div>
                </div>

                <!-- ── PESTAÑA 3: ARTICULACIÓN DE MIS PROCESOS ── -->
                <div id="tabProcesos" class="profile-tab-pane" style="display:none;">
                    <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:14px 18px; margin-bottom:18px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:1.2rem;">🎯</span>
                            <div>
                                <div style="font-weight:700; color:#1e40af; font-size:0.92rem;">Perspectiva Integral de Procesos Institucionales</div>
                                <div style="font-size:0.8rem; color:#3b82f6;">Aquí puedes observar y seleccionar los módulos de SKEL 360 en los que estás involucrado como líder o evaluador:</div>
                            </div>
                        </div>
                    </div>

                    <!-- Módulos Institucionales -->
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:20px;">
                        
                        <!-- Autoevaluación Institucional -->
                        <div style="border:1px solid #cbd5e1; border-radius:10px; padding:14px; background:#fafafa;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <div style="font-weight:700; color:#1e293b; font-size:0.92rem;">📋 Autoevaluación Institucional</div>
                                <input type="checkbox" id="chkProcAutoeval" checked style="width:18px; height:18px;">
                            </div>
                            <div style="font-size:0.78rem; color:#64748b; margin-bottom:10px;">
                                Evaluación de los 12 factores institucionales y ponderación CNA.
                            </div>
                            <div id="userAssignedFactorsBadge" style="font-size:0.75rem; color:#1e40af; background:#dbeafe; padding:4px 8px; border-radius:6px; margin-bottom:8px;">
                                Cargando factores asignados...
                            </div>
                            <a href="autoevaluacion.html" style="font-size:0.78rem; color:#2563eb; font-weight:700; text-decoration:none;">
                                ➔ Ir a Mis Factores en Autoevaluación
                            </a>
                        </div>

                        <!-- Cambio de Carácter -->
                        <div style="border:1px solid #cbd5e1; border-radius:10px; padding:14px; background:#fafafa;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <div style="font-weight:700; color:#1e293b; font-size:0.92rem;">🏛️ Cambio de Carácter</div>
                                <input type="checkbox" id="chkProcCambioCaracter" checked style="width:18px; height:18px;">
                            </div>
                            <div style="font-size:0.78rem; color:#64748b; margin-bottom:10px;">
                                Plan Estratégico de Redefinición a Institución Universitaria (Ley 749/2002).
                            </div>
                            <div style="font-size:0.75rem; color:#047857; background:#d1fae5; padding:4px 8px; border-radius:6px; margin-bottom:8px;">
                                ✓ Frentes de trabajo y análisis de brechas habilitados
                            </div>
                            <a href="cambio_caracter.html" style="font-size:0.78rem; color:#059669; font-weight:700; text-decoration:none;">
                                ➔ Ir a Plan de Cambio de Carácter
                            </a>
                        </div>

                        <!-- Registro Calificado -->
                        <div style="border:1px solid #cbd5e1; border-radius:10px; padding:14px; background:#fafafa;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <div style="font-weight:700; color:#1e293b; font-size:0.92rem;">🎓 Registro Calificado</div>
                                <input type="checkbox" id="chkProcRC" style="width:18px; height:18px;">
                            </div>
                            <div style="font-size:0.78rem; color:#64748b; margin-bottom:10px;">
                                Condiciones de calidad de programa institucional (Decreto 1330).
                            </div>
                            <a href="registro_calificado.html" style="font-size:0.78rem; color:#2563eb; font-weight:700; text-decoration:none;">
                                ➔ Ir a Registro Calificado
                            </a>
                        </div>

                        <!-- Planificación y Planes de Mejora -->
                        <div style="border:1px solid #cbd5e1; border-radius:10px; padding:14px; background:#fafafa;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <div style="font-weight:700; color:#1e293b; font-size:0.92rem;">📊 Planificación y Mejora</div>
                                <input type="checkbox" id="chkProcPlan" checked style="width:18px; height:18px;">
                            </div>
                            <div style="font-size:0.78rem; color:#64748b; margin-bottom:10px;">
                                Planes de mejoramiento institucional, metas y seguimiento periódico.
                            </div>
                            <a href="plan_mejoramiento.html" style="font-size:0.78rem; color:#2563eb; font-weight:700; text-decoration:none;">
                                ➔ Ir a Planes de Mejoramiento
                            </a>
                        </div>
                    </div>
                </div>

                <!-- ── PESTAÑA 4: SEGURIDAD Y CAMBIO DE CONTRASEÑA ── -->
                <div id="tabSeguridad" class="profile-tab-pane" style="display:none;">
                    <div style="max-width:480px; margin:0 auto;">
                        <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:12px; margin-bottom:18px; font-size:0.82rem; color:#92400e;">
                            🔒 Puedes cambiar tu contraseña en cualquier momento. Debe tener al menos 6 caracteres.
                        </div>

                        <div style="margin-bottom:14px;">
                            <label style="display:block; font-size:0.82rem; font-weight:700; color:#334155; margin-bottom:6px;">Contraseña Actual:</label>
                            <input type="password" id="oldPasswordInput" style="width:100%; padding:10px 12px; border-radius:8px; border:1px solid #cbd5e1; font-size:0.9rem;" placeholder="Tu contraseña actual">
                        </div>
                        <div style="margin-bottom:14px;">
                            <label style="display:block; font-size:0.82rem; font-weight:700; color:#334155; margin-bottom:6px;">Nueva Contraseña:</label>
                            <input type="password" id="newPasswordInput" style="width:100%; padding:10px 12px; border-radius:8px; border:1px solid #cbd5e1; font-size:0.9rem;" placeholder="Mínimo 6 caracteres">
                        </div>
                        <div style="margin-bottom:18px;">
                            <label style="display:block; font-size:0.82rem; font-weight:700; color:#334155; margin-bottom:6px;">Confirmar Nueva Contraseña:</label>
                            <input type="password" id="confirmPasswordInput" style="width:100%; padding:10px 12px; border-radius:8px; border:1px solid #cbd5e1; font-size:0.9rem;" placeholder="Repite la nueva contraseña">
                        </div>
                    </div>
                </div>

            </div>

            <!-- Pie del Modal: Acciones -->
            <div style="background:#f8fafc; border-top:1px solid #e2e8f0; padding:14px 24px; display:flex; justify-content:space-between; align-items:center;">
                <span id="profileSaveStatus" style="font-size:0.85rem; font-weight:600; color:#059669;"></span>
                <div style="display:flex; gap:10px;">
                    <button type="button" onclick="closeExecutiveProfileModal()" style="padding:9px 18px; border-radius:8px; border:1px solid #cbd5e1; background:white; color:#475569; font-weight:600; font-size:0.85rem; cursor:pointer;">
                        Cancelar
                    </button>
                    <button type="button" id="btnSaveExecutiveProfile" onclick="saveExecutiveProfile()" style="padding:9px 22px; border-radius:8px; border:none; background:#2563eb; color:white; font-weight:700; font-size:0.85rem; cursor:pointer; display:flex; align-items:center; gap:6px;">
                        💾 Guardar Perfil Ejecutivo
                    </button>
                </div>
            </div>

        </div>
    </div>
    `;

    var div = document.createElement('div');
    div.innerHTML = modalHTML;
    document.body.appendChild(div.firstElementChild);

    // Inicializar presets en el DOM
    renderPresetsGrid();
}

// ── 5. Renderizado de Presets en el Grid ──

function renderPresetsGrid() {
    var grid = document.getElementById('presetsGrid');
    if (!grid) return;

    var presets = getExecutiveAvatarPresets();
    var html = '';
    presets.forEach(function(p) {
        var svgThumb = generateCamibusoAvatarSVG(p.config);
        html += `
        <div onclick="applyAvatarPreset('${p.id}')" style="cursor:pointer; border:1px solid #e2e8f0; background:white; padding:10px; border-radius:10px; text-align:center; transition:0.2s;" onmouseover="this.style.borderColor='#2563eb'; this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='#e2e8f0'; this.style.transform='none'">
            <div style="width:68px; height:68px; margin:0 auto 8px auto; border-radius:50%; overflow:hidden;">
                ${svgThumb}
            </div>
            <div style="font-size:0.75rem; font-weight:700; color:#1e293b; line-height:1.2;">${p.title}</div>
            <div style="font-size:0.68rem; color:#64748b; margin-top:2px;">${p.desc}</div>
        </div>`;
    });
    grid.innerHTML = html;
}

// ── 6. Control de Pestañas del Modal ──

function switchProfileTab(tabId) {
    document.querySelectorAll('.profile-tab-btn').forEach(function(btn) {
        var active = btn.getAttribute('data-tab') === tabId;
        btn.style.borderBottom = active ? '3px solid #2563eb' : '3px solid transparent';
        btn.style.color = active ? '#1e3a8a' : '#64748b';
        btn.style.fontWeight = active ? '700' : '600';
    });
    document.querySelectorAll('.profile-tab-pane').forEach(function(pane) {
        pane.style.display = (pane.id === tabId) ? 'block' : 'none';
    });
}

function setAvatarSubMode(mode) {
    var btnC = document.getElementById('btnModeCustomize');
    var btnP = document.getElementById('btnModePresets');
    var paneC = document.getElementById('paneCustomize');
    var paneP = document.getElementById('panePresets');

    if (mode === 'customize') {
        btnC.style.background = '#eff6ff'; btnC.style.borderColor = '#2563eb'; btnC.style.color = '#1e40af';
        btnP.style.background = 'white'; btnP.style.borderColor = '#cbd5e1'; btnP.style.color = '#475569';
        paneC.style.display = 'block';
        paneP.style.display = 'none';
    } else {
        btnP.style.background = '#eff6ff'; btnP.style.borderColor = '#2563eb'; btnP.style.color = '#1e40af';
        btnC.style.background = 'white'; btnC.style.borderColor = '#cbd5e1'; btnC.style.color = '#475569';
        paneP.style.display = 'block';
        paneC.style.display = 'none';
    }
}

// ── 7. Modificadores de la Configuración del Avatar ──

function updateAvatarLivePreview() {
    var preview = document.getElementById('avatarLivePreview');
    if (preview) {
        preview.innerHTML = generateCamibusoAvatarSVG(window._activeAvatarConfig);
    }
}

function setPoloColor(color, collar) {
    window._activeAvatarConfig.poloColor = color;
    window._activeAvatarConfig.collarColor = collar || color;
    window._activeAvatarConfig.photoUrl = null;
    updateAvatarLivePreview();
}

function setSkinColor(color) {
    window._activeAvatarConfig.skin = color;
    window._activeAvatarConfig.photoUrl = null;
    updateAvatarLivePreview();
}

function setHairStyle(style) {
    window._activeAvatarConfig.hair = style;
    window._activeAvatarConfig.photoUrl = null;
    updateAvatarLivePreview();
}

function setHairColor(color) {
    window._activeAvatarConfig.hairColor = color;
    window._activeAvatarConfig.photoUrl = null;
    updateAvatarLivePreview();
}

function setGlasses(glasses) {
    window._activeAvatarConfig.glasses = glasses;
    window._activeAvatarConfig.photoUrl = null;
    updateAvatarLivePreview();
}

function setLanyard(active) {
    window._activeAvatarConfig.lanyard = active;
    updateAvatarLivePreview();
}

function applyAvatarPreset(presetId) {
    var presets = getExecutiveAvatarPresets();
    var p = presets.find(function(x) { return x.id === presetId; });
    if (p) {
        window._activeAvatarConfig = Object.assign({}, p.config);
        window._activeAvatarConfig.photoUrl = null;
        updateAvatarLivePreview();
        setAvatarSubMode('customize');
        // Sincronizar selects
        if (document.getElementById('selHairStyle')) document.getElementById('selHairStyle').value = p.config.hair;
        if (document.getElementById('selGlasses')) document.getElementById('selGlasses').value = p.config.glasses;
        if (document.getElementById('chkLanyard')) document.getElementById('chkLanyard').checked = p.config.lanyard !== false;
    }
}

function triggerPhotoUpload() {
    var fileInp = document.getElementById('userPhotoInput');
    if (fileInp) fileInp.click();
}

function handlePhotoUpload(input) {
    if (input.files && input.files[0]) {
        var file = input.files[0];
        if (file.size > 2 * 1024 * 1024) {
            alert('Por favor selecciona una imagen menor a 2MB.');
            return;
        }
        var reader = new FileReader();
        reader.onload = function(e) {
            window._activeAvatarConfig.photoUrl = e.target.result;
            updateAvatarLivePreview();
            var btnRem = document.getElementById('btnRemovePhoto');
            if (btnRem) btnRem.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

function removePhotoCustom() {
    window._activeAvatarConfig.photoUrl = null;
    updateAvatarLivePreview();
    var btnRem = document.getElementById('btnRemovePhoto');
    if (btnRem) btnRem.style.display = 'none';
}

// ── 8. Apertura y Carga del Modal de Perfil ──

async function openExecutiveProfileModal() {
    ensureExecutiveProfileModalDOM();
    var modal = document.getElementById('userProfileModal');
    if (!modal) return;
    modal.style.display = 'flex';

    var localUser = JSON.parse(localStorage.getItem('siac_user') || '{}');

    // Cargar datos actuales en los campos
    document.getElementById('profName').value = (localUser.name || '').replace(/\[(?:PENDING|ASPIRANTE)[^\]]*\]\s*/g, '');
    document.getElementById('profEmail').value = localUser.email || '';
    document.getElementById('profCargo').value = localUser.cargo || '';
    document.getElementById('profPhone').value = localUser.phone || '';
    document.getElementById('profBio').value = localUser.bio || '';
    document.getElementById('previewUserName').textContent = localUser.name || localUser.email || 'Usuario';
    document.getElementById('previewUserCargo').textContent = localUser.cargo || (localUser.role ? localUser.role.toUpperCase() : 'Líder Institucional');

    // Configuración de Avatar
    if (localUser.avatar_config && typeof localUser.avatar_config === 'object') {
        window._activeAvatarConfig = Object.assign({}, window._activeAvatarConfig, localUser.avatar_config);
    }
    if (localUser.avatar_url) {
        window._activeAvatarConfig.photoUrl = localUser.avatar_url;
    }
    updateAvatarLivePreview();

    // Sincronizar controles
    if (document.getElementById('selHairStyle')) document.getElementById('selHairStyle').value = window._activeAvatarConfig.hair || 'sidepart';
    if (document.getElementById('selGlasses')) document.getElementById('selGlasses').value = window._activeAvatarConfig.glasses || 'none';
    if (document.getElementById('chkLanyard')) document.getElementById('chkLanyard').checked = window._activeAvatarConfig.lanyard !== false;

    // Obtener datos frescos desde la API
    try {
        var resp = await authFetch('/api/user/profile');
        if (resp.ok) {
            var data = await resp.json();
            if (data.status === 'success' && data.user) {
                var u = data.user;
                window._currentProfileData = data;
                document.getElementById('profName').value = u.name || '';
                document.getElementById('profCargo').value = u.cargo || '';
                document.getElementById('profPhone').value = u.phone || '';
                document.getElementById('profBio').value = u.bio || '';
                document.getElementById('previewUserName').textContent = u.name || u.email;
                document.getElementById('previewUserCargo').textContent = u.cargo || u.role;

                if (u.avatar_config && Object.keys(u.avatar_config).length > 0) {
                    window._activeAvatarConfig = Object.assign({}, window._activeAvatarConfig, u.avatar_config);
                }
                if (u.avatar_url) {
                    window._activeAvatarConfig.photoUrl = u.avatar_url;
                    var btnRem = document.getElementById('btnRemovePhoto');
                    if (btnRem) btnRem.style.display = 'block';
                }
                updateAvatarLivePreview();

                // Procesos
                var procs = u.processes || ['autoevaluacion', 'cambio_caracter'];
                if (document.getElementById('chkProcAutoeval')) document.getElementById('chkProcAutoeval').checked = procs.includes('autoevaluacion');
                if (document.getElementById('chkProcCambioCaracter')) document.getElementById('chkProcCambioCaracter').checked = procs.includes('cambio_caracter');
                if (document.getElementById('chkProcRC')) document.getElementById('chkProcRC').checked = procs.includes('registro_calificado');
                if (document.getElementById('chkProcPlan')) document.getElementById('chkProcPlan').checked = procs.includes('planificacion');

                // Factores asignados en Autoevaluación
                var afBadge = document.getElementById('userAssignedFactorsBadge');
                if (afBadge) {
                    var factors = data.factors || [];
                    if (factors.length > 0) {
                        var fList = factors.map(function(f) { return 'Factor ' + f.number + ': ' + f.name; }).join('<br>');
                        afBadge.innerHTML = '<strong>Tus Factores Asignados:</strong><br>' + fList;
                    } else if (u.assigned_factors && u.assigned_factors.length > 0) {
                        afBadge.innerHTML = '<strong>Factores Asignados:</strong> Factores ' + u.assigned_factors.join(', ');
                    } else {
                        afBadge.innerHTML = 'ℹ️ Sin factores exclusivos asignados aún (Acceso global habilitado)';
                    }
                }
            }
        }
    } catch(err) {
        console.warn('Carga de perfil desde API:', err);
    }
}

function closeExecutiveProfileModal() {
    var modal = document.getElementById('userProfileModal');
    if (modal) modal.style.display = 'none';
}

// ── 9. Guardar Perfil Ejecutivo y Contraseña ──

async function saveExecutiveProfile() {
    var btn = document.getElementById('btnSaveExecutiveProfile');
    var status = document.getElementById('profileSaveStatus');
    if (btn) btn.disabled = true;
    if (status) { status.style.color = '#2563eb'; status.textContent = 'Guardando cambios...'; }

    var name = document.getElementById('profName').value.trim();
    var cargo = document.getElementById('profCargo').value.trim();
    var phone = document.getElementById('profPhone').value.trim();
    var bio = document.getElementById('profBio').value.trim();

    var oldPass = document.getElementById('oldPasswordInput') ? document.getElementById('oldPasswordInput').value : '';
    var newPass = document.getElementById('newPasswordInput') ? document.getElementById('newPasswordInput').value : '';
    var confPass = document.getElementById('confirmPasswordInput') ? document.getElementById('confirmPasswordInput').value : '';

    if (newPass) {
        if (newPass.length < 6) {
            alert('La nueva contraseña debe tener al menos 6 caracteres.');
            if (btn) btn.disabled = false;
            if (status) status.textContent = '';
            return;
        }
        if (newPass !== confPass) {
            alert('La confirmación de la contraseña no coincide.');
            if (btn) btn.disabled = false;
            if (status) status.textContent = '';
            return;
        }
        if (!oldPass) {
            alert('Debes ingresar tu contraseña actual para cambiarla.');
            if (btn) btn.disabled = false;
            if (status) status.textContent = '';
            return;
        }
    }

    // Recolectar procesos seleccionados
    var processes = [];
    if (document.getElementById('chkProcAutoeval') && document.getElementById('chkProcAutoeval').checked) processes.push('autoevaluacion');
    if (document.getElementById('chkProcCambioCaracter') && document.getElementById('chkProcCambioCaracter').checked) processes.push('cambio_caracter');
    if (document.getElementById('chkProcRC') && document.getElementById('chkProcRC').checked) processes.push('registro_calificado');
    if (document.getElementById('chkProcPlan') && document.getElementById('chkProcPlan').checked) processes.push('planificacion');

    var payload = {
        name: name,
        cargo: cargo,
        phone: phone,
        bio: bio,
        avatar_config: window._activeAvatarConfig,
        avatar_url: window._activeAvatarConfig.photoUrl || null,
        processes: processes
    };

    if (newPass && oldPass) {
        payload.old_password = oldPass;
        payload.new_password = newPass;
    }

    try {
        var resp = await authFetch('/api/user/profile', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        var resData = await resp.json();

        if (resp.ok && resData.status === 'success') {
            if (status) {
                status.style.color = '#059669';
                status.textContent = '✅ Perfil actualizado exitosamente.';
            }

            // Actualizar localStorage
            var currentStorage = JSON.parse(localStorage.getItem('siac_user') || '{}');
            if (name) currentStorage.name = name;
            currentStorage.cargo = cargo;
            currentStorage.phone = phone;
            currentStorage.bio = bio;
            currentStorage.avatar_config = window._activeAvatarConfig;
            currentStorage.avatar_url = window._activeAvatarConfig.photoUrl || null;
            currentStorage.processes = processes;
            localStorage.setItem('siac_user', JSON.stringify(currentStorage));

            // Actualizar Topbar global inmediatamente
            initUserProfileTopbar();

            // Limpiar campos de contraseña
            if (document.getElementById('oldPasswordInput')) document.getElementById('oldPasswordInput').value = '';
            if (document.getElementById('newPasswordInput')) document.getElementById('newPasswordInput').value = '';
            if (document.getElementById('confirmPasswordInput')) document.getElementById('confirmPasswordInput').value = '';

            setTimeout(function() {
                closeExecutiveProfileModal();
                if (status) status.textContent = '';
            }, 1200);
        } else {
            alert('Error: ' + (resData.message || 'No se pudo actualizar el perfil'));
            if (status) status.textContent = '';
        }
    } catch(err) {
        alert('Error al comunicar con el servidor: ' + err.message);
        if (status) status.textContent = '';
    } finally {
        if (btn) btn.disabled = false;
    }
}

// ── 10. Inyección del Chip de Perfil Ejecutivo en la Topbar ──

function initUserProfileTopbar() {
    var userInfo = document.getElementById('userInfo');
    if (!userInfo) return;

    var user = JSON.parse(localStorage.getItem('siac_user') || '{}');
    var cleanName = (user.name || user.email || 'Usuario').replace(/\[(?:PENDING|ASPIRANTE)[^\]]*\]\s*/g, '');
    var roleLabel = (user.role || 'INVITADO').toUpperCase();
    var cargoLabel = user.cargo || (user.role === 'admin' ? 'Superadministrador' : (user.role === 'inst_admin' ? 'Administrador Institucional' : 'Líder Institucional'));

    // Generar thumbnail del Avatar en SVG
    var avatarCfg = user.avatar_config || {
        skin: '#d99b70',
        hair: 'sidepart',
        hairColor: '#1c1917',
        poloColor: '#1e3a8a',
        glasses: 'none',
        lanyard: true
    };
    if (user.avatar_url) avatarCfg.photoUrl = user.avatar_url;

    var avatarThumbSVG = generateCamibusoAvatarSVG(avatarCfg);

    // Contenedor ejecutivo estilizado
    userInfo.style.display = 'flex';
    userInfo.style.alignItems = 'center';
    userInfo.style.gap = '10px';
    userInfo.style.cursor = 'pointer';
    userInfo.setAttribute('title', 'Abrir Mi Perfil Ejecutivo Institucional');
    userInfo.onclick = function() {
        openExecutiveProfileModal();
    };

    userInfo.innerHTML = `
        <div style="width:38px; height:38px; border-radius:50%; box-shadow:0 2px 6px rgba(0,0,0,0.15); border:2px solid #2563eb; overflow:hidden; flex-shrink:0;">
            ${avatarThumbSVG}
        </div>
        <div style="display:flex; flex-direction:column; text-align:left; line-height:1.2;">
            <div style="font-weight:700; font-size:0.86rem; color:#1e293b; display:flex; align-items:center; gap:6px;">
                <span>${cleanName}</span>
                <span style="font-size:0.68rem; padding:1px 6px; border-radius:10px; background:#eff6ff; color:#1e40af; font-weight:800; border:1px solid #bfdbfe;">
                    ${roleLabel}
                </span>
            </div>
            <div style="font-size:0.74rem; color:#64748b; font-weight:500;">
                👔 ${cargoLabel}
            </div>
        </div>
        <button type="button" style="background:#f1f5f9; border:1px solid #cbd5e1; color:#334155; padding:4px 8px; border-radius:6px; font-size:0.74rem; font-weight:600; cursor:pointer; margin-left:4px;" title="Editar Perfil">
            ⚙️ Perfil
        </button>
    `;
}

// Iniciar al cargar el DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        initUserProfileTopbar();
    });
} else {
    initUserProfileTopbar();
}

