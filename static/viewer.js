/**
 * SKEL SIAC — Visor Universal de Archivos
 * PDF.js powered viewer — funciona en tablets, iOS Safari, Android Chrome
 * Expone: abrirVisor(url, nombre)
 */
(function () {
    'use strict';

    // ── Inyectar CSS del visor ──────────────────────────────────────────────
    const css = `
    #siac-viewer-overlay {
        display: none;
        position: fixed; inset: 0; z-index: 9000;
        background: rgba(0,0,0,0.82);
        backdrop-filter: blur(6px);
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
    }
    #siac-viewer-overlay.open { display: flex; }

    #siac-viewer-bar {
        width: 100%; background: #1e293b;
        display: flex; align-items: center; gap: 10px;
        padding: 10px 18px; flex-shrink: 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.5);
        flex-wrap: wrap;
    }
    #siac-viewer-filename {
        flex: 1; color: #e2e8f0; font-size: 0.88rem;
        font-weight: 600; white-space: nowrap;
        overflow: hidden; text-overflow: ellipsis;
        min-width: 0;
    }
    .siac-vbtn {
        background: #334155; color: #e2e8f0;
        border: none; padding: 8px 14px; border-radius: 8px;
        cursor: pointer; font-size: 0.85rem; font-weight: 600;
        transition: background 0.15s; white-space: nowrap;
        display: flex; align-items: center; gap: 5px;
    }
    .siac-vbtn:hover { background: #475569; }
    .siac-vbtn.accent { background: #2563eb; }
    .siac-vbtn.accent:hover { background: #1d4ed8; }
    .siac-vbtn.danger { background: #7f1d1d; }
    .siac-vbtn.danger:hover { background: #991b1b; }

    #siac-viewer-page-info {
        color: #94a3b8; font-size: 0.82rem; white-space: nowrap;
    }
    #siac-viewer-zoom-info {
        color: #94a3b8; font-size: 0.82rem; min-width: 45px; text-align: center;
    }

    #siac-viewer-body {
        flex: 1; width: 100%; overflow: auto;
        display: flex; align-items: flex-start; justify-content: center;
        padding: 20px; background: #0f172a;
    }

    /* Contenedor PDF */
    #siac-pdf-container {
        display: flex; flex-direction: column;
        align-items: center; gap: 10px;
    }
    #siac-pdf-container canvas {
        border-radius: 4px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.7);
        max-width: 100%;
        display: block;
    }

    /* Imagen */
    #siac-img-viewer {
        max-width: 95vw; max-height: 85vh;
        object-fit: contain; border-radius: 8px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.7);
    }

    /* Otros archivos */
    #siac-other-viewer {
        color: #94a3b8; text-align: center; padding: 60px 20px;
        font-size: 1rem;
    }
    #siac-other-viewer .siac-big-icon { font-size: 4rem; margin-bottom: 16px; }

    /* Loading */
    #siac-viewer-loading {
        position: absolute; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        display: flex; flex-direction: column;
        align-items: center; gap: 14px; display: none;
    }
    #siac-viewer-loading.show { display: flex; }
    .siac-loader-ring {
        width: 48px; height: 48px;
        border: 5px solid #334155;
        border-top-color: #2563eb;
        border-radius: 50%;
        animation: siac-spin 0.85s linear infinite;
    }
    @keyframes siac-spin { to { transform: rotate(360deg); } }
    #siac-viewer-loading p { color: #94a3b8; font-size: 0.9rem; }

    /* Error */
    #siac-viewer-error {
        display: none; color: #fca5a5;
        text-align: center; padding: 40px 20px; font-size: 0.95rem;
    }
    #siac-viewer-error.show { display: block; }

    @media (max-width: 600px) {
        #siac-viewer-bar { gap: 6px; padding: 8px 10px; }
        .siac-vbtn { padding: 7px 10px; font-size: 0.78rem; }
        #siac-viewer-body { padding: 10px; }
    }
    `;

    const styleEl = document.createElement('style');
    styleEl.textContent = css;
    document.head.appendChild(styleEl);

    // ── Inyectar HTML del visor ─────────────────────────────────────────────
    const html = `
    <div id="siac-viewer-overlay">
        <div id="siac-viewer-bar">
            <span id="siac-viewer-filename">Cargando...</span>
            <button class="siac-vbtn" id="siac-btn-prev" onclick="SIAC_Viewer.prevPage()" title="Página anterior">◀</button>
            <span id="siac-viewer-page-info"></span>
            <button class="siac-vbtn" id="siac-btn-next" onclick="SIAC_Viewer.nextPage()" title="Página siguiente">▶</button>
            <button class="siac-vbtn" onclick="SIAC_Viewer.zoomOut()" title="Reducir">🔍−</button>
            <span id="siac-viewer-zoom-info">100%</span>
            <button class="siac-vbtn" onclick="SIAC_Viewer.zoomIn()" title="Ampliar">🔍+</button>
            <button class="siac-vbtn" onclick="SIAC_Viewer.zoomReset()" title="Ajustar">⊡</button>
            <button class="siac-vbtn accent" id="siac-btn-download" onclick="SIAC_Viewer.download()" title="Descargar">⬇️ Descargar</button>
            <button class="siac-vbtn danger" onclick="SIAC_Viewer.cerrar()" title="Cerrar">✕ Cerrar</button>
        </div>
        <div id="siac-viewer-body">
            <div id="siac-viewer-loading">
                <div class="siac-loader-ring"></div>
                <p>Cargando documento...</p>
            </div>
            <div id="siac-viewer-error"></div>
            <div id="siac-pdf-container"></div>
            <img id="siac-img-viewer" src="" alt="" style="display:none;">
            <div id="siac-other-viewer" style="display:none;"></div>
        </div>
    </div>
    `;

    document.addEventListener('DOMContentLoaded', () => {
        document.body.insertAdjacentHTML('beforeend', html);

        // ── Cerrar con Escape ───────────────────────────────────────────────────
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') SIAC_Viewer.cerrar();
            if (e.key === 'ArrowRight') SIAC_Viewer.nextPage();
            if (e.key === 'ArrowLeft')  SIAC_Viewer.prevPage();
        });

        // Cerrar al clic en el fondo
        document.getElementById('siac-viewer-overlay').addEventListener('click', e => {
            if (e.target === document.getElementById('siac-viewer-overlay')) SIAC_Viewer.cerrar();
        });
    });

    // ── Estado interno ──────────────────────────────────────────────────────
    let _curUrl   = '';
    let _curName  = '';

    // ── API pública ─────────────────────────────────────────────────────────
    window.SIAC_Viewer = {

        abrir(url, nombre) {
            _curUrl  = url || '';
            _curName = nombre || url.split('/').pop() || 'archivo';

            const overlay = document.getElementById('siac-viewer-overlay');
            overlay.classList.add('open');
            document.body.style.overflow = 'hidden';

            document.getElementById('siac-viewer-filename').textContent = _curName;
            document.getElementById('siac-viewer-page-info').textContent = '';
            document.getElementById('siac-viewer-zoom-info').textContent = '';
            
            // Hide PDF controls since we use iframe
            document.getElementById('siac-btn-prev').style.display = 'none';
            document.getElementById('siac-btn-next').style.display = 'none';

            this._resetPanels();
            this._showLoading(true);

            const ext = _curUrl.split('?')[0].split('.').pop().toLowerCase();

            if (['jpg','jpeg','png','gif','webp','svg','bmp'].includes(ext)) {
                this._abrirImagen(_curUrl);
            } else if (ext === 'pdf' || _curUrl.includes('/api/download') || _curUrl.includes('supabase')) {
                this._abrirPDF(_curUrl);
            } else {
                this._abrirOtro(_curUrl, _curName, ext);
            }
        },

        cerrar() {
            document.getElementById('siac-viewer-overlay').classList.remove('open');
            document.body.style.overflow = '';
            document.getElementById('siac-pdf-container').innerHTML = ''; // clear iframe
        },

        download() {
            if (!_curUrl) return;
            if (typeof forceDownload === 'function') {
                forceDownload(_curUrl, _curName);
            } else {
                const a = document.createElement('a');
                a.href = _curUrl;
                a.download = _curName;
                a.target = '_blank';
                a.click();
            }
        },

        prevPage() {},
        nextPage() {},
        zoomIn() {},
        zoomOut() {},
        zoomReset() {},

        _resetPanels() {
            document.getElementById('siac-pdf-container').innerHTML = '';
            document.getElementById('siac-img-viewer').style.display = 'none';
            document.getElementById('siac-img-viewer').src = '';
            document.getElementById('siac-other-viewer').style.display = 'none';
            document.getElementById('siac-viewer-error').classList.remove('show');
            document.getElementById('siac-viewer-page-info').textContent = '';
        },

        _showLoading(show) {
            const el = document.getElementById('siac-viewer-loading');
            el.classList.toggle('show', show);
        },

        _showError(msg) {
            this._showLoading(false);
            const el = document.getElementById('siac-viewer-error');
            el.innerHTML = `<p style="font-size:2rem;">⚠️</p><p>${msg}</p>
                <button class="siac-vbtn" style="margin:16px auto 0;" onclick="SIAC_Viewer.download()">⬇️ Descargar archivo</button>`;
            el.classList.add('show');
        },

        _abrirImagen(url) {
            const img = document.getElementById('siac-img-viewer');
            img.onload = () => this._showLoading(false);
            img.onerror = () => this._showError('No se pudo cargar la imagen.');
            img.src = url;
            img.style.display = 'block';
        },

        _abrirOtro(url, nombre, ext) {
            this._showLoading(false);
            const el = document.getElementById('siac-other-viewer');
            const icons = { doc:'📝', docx:'📝', xls:'📊', xlsx:'📊', ppt:'📋', pptx:'📋', zip:'📦', rar:'📦', txt:'📄' };
            const icon = icons[ext] || '📁';
            el.innerHTML = `
                <div class="siac-big-icon">${icon}</div>
                <p style="color:#e2e8f0;font-size:1.1rem;font-weight:700;margin-bottom:8px;">${nombre}</p>
                <p style="margin-bottom:24px;">Este tipo de archivo (${ext.toUpperCase()}) no puede previsualizarse en el navegador.</p>
                <button class="siac-vbtn accent" onclick="SIAC_Viewer.download()">⬇️ Descargar para abrir</button>
            `;
            el.style.display = 'block';
        },

        _abrirPDF(url) {
            // Eliminar dependencias de pdf.js y usar un iframe nativo robusto.
            // Para resolver el problema de tablets, usamos Google Docs Viewer en móviles.
            const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
            
            let iframeUrl = url;
            // Si es móvil y es una URL pública (supabase o http), usar Google Docs Viewer para forzar renderizado en canvas web nativo
            if (isMobile && (url.includes('supabase') || url.startsWith('http'))) {
                iframeUrl = `https://docs.google.com/viewer?url=${encodeURIComponent(url)}&embedded=true`;
            } else if (!url.startsWith('http') && !url.includes('supabase')) {
                // Archivo local, usar proxy_download
                iframeUrl = `/api/download?url=${encodeURIComponent(url)}`;
            }

            const container = document.getElementById('siac-pdf-container');
            container.innerHTML = `<iframe src="${iframeUrl}" style="width:100%; height:85vh; border:none; border-radius:8px; background:#fff;" onload="document.getElementById('siac-viewer-loading').classList.remove('show');" onerror="SIAC_Viewer._showError('No se pudo cargar el documento en el marco.');"></iframe>`;
            container.style.width = '100%';
        }
    };

    // ── Función global de acceso rápido ─────────────────────────────────────
    window.abrirVisor = (url, nombre) => SIAC_Viewer.abrir(url, nombre);

})();
