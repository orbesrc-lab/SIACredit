import re

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'r', encoding='utf-8') as f:
    gerencial_content = f.read()

# 1. Expand the HTML for ISO Chapter
html_iso_old = """                        <div id="mapa_procesos">
                            <div class="iso-tier">
                                <h4>Procesos Estratégicos</h4>
                                <div class="iso-grid" id="iso_estrategicos">Cargando...</div>
                            </div>
                            <div class="iso-tier">
                                <h4>Procesos Misionales</h4>
                                <div class="iso-grid" id="iso_misionales">Cargando...</div>
                            </div>
                            <div class="iso-tier">
                                <h4>Procesos de Apoyo / Soporte</h4>
                                <div class="iso-grid" id="iso_apoyo">Cargando...</div>
                            </div>
                        </div>
                        <h3 class="section-title">Caracterización y SIPOC</h3>
                        <div id="texto_sipoc" class="editable-content" contenteditable="true">
                            Cargando caracterizaciones...
                        </div>"""

html_iso_new = """                        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
                            <h4 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px;">Mapa de Procesos</h4>
                            <div id="mapa_procesos" style="display: flex; flex-direction: column; gap: 20px;">
                                <div class="iso-tier" style="background:#f8fafc; padding:15px; border-radius:8px; border:1px solid #e2e8f0;">
                                    <h4 style="color:#7c3aed; text-align:center; font-weight:700;">PROCESOS ESTRATÉGICOS</h4>
                                    <div class="iso-grid" id="iso_estrategicos" style="justify-content:center;">Cargando...</div>
                                </div>
                                <div class="iso-tier" style="background:#eff6ff; padding:15px; border-radius:8px; border:1px solid #bfdbfe;">
                                    <h4 style="color:#2563eb; text-align:center; font-weight:700;">PROCESOS MISIONALES (Cadena de Valor)</h4>
                                    <div class="iso-grid" id="iso_misionales" style="justify-content:center;">Cargando...</div>
                                </div>
                                <div class="iso-tier" style="background:#f0fdf4; padding:15px; border-radius:8px; border:1px solid #bbf7d0;">
                                    <h4 style="color:#10b981; text-align:center; font-weight:700;">PROCESOS DE APOYO / SOPORTE</h4>
                                    <div class="iso-grid" id="iso_apoyo" style="justify-content:center;">Cargando...</div>
                                </div>
                            </div>
                        </div>

                        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
                            <h4 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px;">Caracterizaciones (Fichas de Procesos / SIPOC)</h4>
                            <div id="texto_sipoc">
                                Cargando caracterizaciones...
                            </div>
                        </div>"""

gerencial_content = gerencial_content.replace(html_iso_old, html_iso_new)


# 2. Patch cargarISO JS
carg_iso_patch = """        async function cargarISO() {
            try {
                const res = await fetch(`/api/business/matrix/ISO9001?inst_id=${getInstId()}`);
                const data = await res.json();
                
                let estHtml = "", misHtml = "", apoHtml = "", sipocHtml = "";
                let hasIso = false;
                
                const buildSipoc = (p, tipo) => {
                    if (!p.sipoc || Object.keys(p.sipoc).length === 0) return `<div style="margin-bottom:15px; padding:15px; border:1px solid #e2e8f0; border-radius:8px;"><h5>${p.nombre} (${tipo})</h5><p style="color:#64748b;">No hay caracterización definida para este proceso.</p></div>`;
                    const s = p.sipoc;
                    return `
                    <div style="margin-bottom:25px; border:1px solid #cbd5e1; border-radius:8px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                        <div style="background:#1e293b; color:white; padding:12px 15px; display:flex; justify-content:space-between; align-items:center;">
                            <h5 style="margin:0; font-size:1.1rem; color:white;">${p.nombre}</h5>
                            <span style="background:#3b82f6; color:white; padding:2px 8px; border-radius:12px; font-size:0.75rem;">${tipo}</span>
                        </div>
                        <div style="padding:15px; background:white;">
                            <div style="margin-bottom:15px;"><b>Objetivo:</b> ${s.objetivo || 'N/A'}</div>
                            <div style="margin-bottom:15px;"><b>Alcance:</b> ${s.alcance || 'N/A'}</div>
                            <div style="margin-bottom:15px;"><b>Responsable:</b> ${s.responsable || 'N/A'}</div>
                            
                            <table style="width:100%; border-collapse:collapse; margin-top:15px; font-size:0.85rem;">
                                <thead>
                                    <tr style="background:#f1f5f9;">
                                        <th style="border:1px solid #e2e8f0; padding:8px; width:20%;">Proveedores (S)</th>
                                        <th style="border:1px solid #e2e8f0; padding:8px; width:20%;">Entradas (I)</th>
                                        <th style="border:1px solid #e2e8f0; padding:8px; width:20%;">Actividades (P)</th>
                                        <th style="border:1px solid #e2e8f0; padding:8px; width:20%;">Salidas (O)</th>
                                        <th style="border:1px solid #e2e8f0; padding:8px; width:20%;">Clientes (C)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="border:1px solid #e2e8f0; padding:8px; vertical-align:top;">${s.proveedores ? s.proveedores.replace(/\\n/g, '<br>') : ''}</td>
                                        <td style="border:1px solid #e2e8f0; padding:8px; vertical-align:top;">${s.entradas ? s.entradas.replace(/\\n/g, '<br>') : ''}</td>
                                        <td style="border:1px solid #e2e8f0; padding:8px; vertical-align:top;">${s.actividades ? s.actividades.replace(/\\n/g, '<br>') : ''}</td>
                                        <td style="border:1px solid #e2e8f0; padding:8px; vertical-align:top;">${s.salidas ? s.salidas.replace(/\\n/g, '<br>') : ''}</td>
                                        <td style="border:1px solid #e2e8f0; padding:8px; vertical-align:top;">${s.clientes ? s.clientes.replace(/\\n/g, '<br>') : ''}</td>
                                    </tr>
                                </tbody>
                            </table>
                            <div style="margin-top:15px; background:#f8fafc; padding:10px; border-radius:6px; font-size:0.85rem;">
                                <b>Recursos:</b> ${s.recursos || 'N/A'} <br>
                                <b>Controles/Indicadores:</b> ${s.controles || 'N/A'} <br>
                                <b>Riesgos Asignados:</b> ${s.riesgos || 'N/A'}
                            </div>
                        </div>
                    </div>
                    `;
                };

                if(data.data && data.data.procesos) {
                    const proc = data.data.procesos;
                    
                    if (proc.estrategicos && proc.estrategicos.length > 0) {
                        hasIso = true;
                        proc.estrategicos.forEach(p => { 
                            estHtml += `<div class="iso-card card-strat" style="font-weight:bold;">${p.nombre}</div>`; 
                            sipocHtml += buildSipoc(p, 'Estratégico');
                        });
                    }
                    if (proc.misionales && proc.misionales.length > 0) {
                        hasIso = true;
                        proc.misionales.forEach(p => { 
                            misHtml += `<div class="iso-card card-misional" style="font-weight:bold;">${p.nombre}</div>`; 
                            sipocHtml += buildSipoc(p, 'Misional');
                        });
                    }
                    if (proc.apoyo && proc.apoyo.length > 0) {
                        hasIso = true;
                        proc.apoyo.forEach(p => { 
                            apoHtml += `<div class="iso-card card-apoyo" style="font-weight:bold;">${p.nombre}</div>`; 
                            sipocHtml += buildSipoc(p, 'Apoyo');
                        });
                    }
                }
                
                if (hasIso) {
                    document.getElementById('iso_estrategicos').innerHTML = estHtml || '<span style="color:#94a3b8;">Ninguno</span>';
                    document.getElementById('iso_misionales').innerHTML = misHtml || '<span style="color:#94a3b8;">Ninguno</span>';
                    document.getElementById('iso_apoyo').innerHTML = apoHtml || '<span style="color:#94a3b8;">Ninguno</span>';
                    document.getElementById('texto_sipoc').innerHTML = sipocHtml;
                } else {
                    document.getElementById('mapa_procesos').innerHTML = "<p style='text-align:center; color:#64748b;'>No se ha definido el mapa de procesos ISO 9001.</p>";
                    document.getElementById('texto_sipoc').innerHTML = "<p style='text-align:center; color:#64748b;'>No hay caracterizaciones disponibles.</p>";
                }
                
                // Política y Objetivos
                if(data.data && data.data.politica) {
                    document.getElementById('texto_politica').innerHTML = `
                        <div style="background:#f8fafc; border-left:4px solid #1e3a8a; padding:15px; margin-bottom:20px; border-radius:0 8px 8px 0;">
                            <h4 style="color:#1e3a8a; margin-top:0;">Política de Calidad</h4>
                            <p style="margin-bottom:0; font-style:italic;">"${data.data.politica}"</p>
                        </div>
                    `;
                }
                if(data.data && data.data.objetivos && data.data.objetivos.length > 0) {
                    let objHtml = `
                        <div style="background:white; border:1px solid #e2e8f0; padding:15px; border-radius:8px;">
                            <h4 style="color:#1e3a8a; margin-top:0;">Objetivos de Calidad</h4>
                            <ul style="margin-bottom:0; padding-left:20px;">
                    `;
                    data.data.objetivos.forEach(o => { objHtml += `<li style="margin-bottom:8px;">${o.objetivo}</li>`; });
                    objHtml += `</ul></div>`;
                    document.getElementById('texto_objetivos').innerHTML = objHtml;
                }
                
            } catch(e) {
                console.error("Error loading ISO:", e);
            }
        }"""

gerencial_content = re.sub(
    r'async function cargarISO\(\) \{.*?\}(?=\s*window\.onload)',
    carg_iso_patch,
    gerencial_content,
    flags=re.DOTALL
)

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'w', encoding='utf-8') as f:
    f.write(gerencial_content)

print("ISO logic injected successfully.")
