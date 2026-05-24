/**
 * downloader.js — Utilidad de descarga directa de archivos de Supabase Storage.
 *
 * Estrategia:
 * 1. Extraer el nombre real del archivo desde la URL de Supabase (incluye la extensión).
 * 2. Fetch directo a Supabase (permitido por CORS en buckets públicos y por CSP connect-src).
 * 3. Convertir a Blob URL (mismo-origen) → el atributo `download` del anchor ES respetado.
 * 4. Fallback: si el fetch falla, redirigir al proxy Flask /api/download.
 *
 * Esto evita completamente los límites de Vercel serverless (timeout 10s, 4.5MB body).
 */

/**
 * Extrae el nombre del archivo con extensión desde la URL de Supabase Storage.
 * La URL tiene la forma: .../storage/v1/object/public/bucket/path/filename.ext
 * @param {string} url
 * @returns {string|null}
 */
function getFilenameFromStorageUrl(url) {
    try {
        // Usar sólo el pathname (sin query string) para extraer el nombre
        const pathname = new URL(url).pathname;
        const segments = pathname.split('/');
        // El último segmento es el nombre del archivo
        const raw = segments[segments.length - 1];
        const decoded = decodeURIComponent(raw);
        // Sólo es válido si tiene extensión (punto en posición no inicial)
        if (decoded && decoded.lastIndexOf('.') > 0) {
            return decoded;
        }
    } catch (e) { /* URL inválida */ }
    return null;
}

/**
 * Descarga un archivo desde una URL de Supabase con el nombre correcto y extensión.
 * @param {string} fileUrl  - URL pública de Supabase Storage
 * @param {string} fileName - Nombre sugerido (puede ser genérico; se corrige automáticamente)
 */
async function forceDownload(fileUrl, fileName) {
    // Limpiar espacios del nombre
    fileName = (fileName || '').trim();

    // Si el nombre es genérico o no tiene extensión, extraerlo de la URL
    const genericNames = ['evidencia', 'archivo', 'file', 'download', ''];
    if (!fileName || !fileName.includes('.') || genericNames.includes(fileName.toLowerCase())) {
        fileName = getFilenameFromStorageUrl(fileUrl) || fileName || 'archivo';
    } else {
        // El nombre tiene extensión — verificar que sea la misma que la URL
        const urlName = getFilenameFromStorageUrl(fileUrl);
        if (urlName) {
            const urlExt  = urlName.split('.').pop().toLowerCase();
            const nameExt = fileName.split('.').pop().toLowerCase();
            if (urlExt && urlExt !== nameExt) {
                // Reemplazar extensión incorrecta por la de la URL
                fileName = fileName.substring(0, fileName.lastIndexOf('.') + 1) + urlExt;
            }
        }
    }

    // Sanitizar: quitar espacios al inicio/final definitivamente
    fileName = fileName.trim();

    /* ── Intento 1: Fetch directo a Supabase ── */
    try {
        const resp = await fetch(fileUrl, { mode: 'cors' });
        if (!resp.ok) throw new Error('HTTP ' + resp.status);

        const blob = await resp.blob();
        const blobUrl = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = blobUrl;
        a.download = fileName; // Mismo-origen → browser SIEMPRE respeta download attr
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        // Liberar memoria después de un momento
        setTimeout(() => URL.revokeObjectURL(blobUrl), 1500);
        return; // Éxito
    } catch (directErr) {
        console.warn('[downloader] Fetch directo falló, usando proxy:', directErr);
    }

    /* ── Intento 2: Proxy Flask /api/download ── */
    try {
        const proxyUrl = '/api/download?url=' + encodeURIComponent(fileUrl)
                       + '&name=' + encodeURIComponent(fileName);
        const resp = await fetch(proxyUrl);
        if (!resp.ok) throw new Error('Proxy HTTP ' + resp.status);

        const blob = await resp.blob();
        const blobUrl = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = blobUrl;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        setTimeout(() => URL.revokeObjectURL(blobUrl), 1500);
    } catch (proxyErr) {
        console.error('[downloader] Proxy también falló:', proxyErr);
        // Último recurso: navegar directamente
        window.open(fileUrl, '_blank');
    }
}
