import os
import re

# 1. Patch planificacion.html
file_plan = r'c:\SIAC\templates\planificacion.html'
with open(file_plan, 'r', encoding='utf-8') as f:
    content_plan = f.read()

# Add ISO dropdown to editNode gen_obj
old_edit_gen = """            } else if(type === 'gen_obj') {
                body.innerHTML = `
                    <div class="form-group"><label>Descripción</label><textarea id="f_desc" rows="3">${escHtml(data.description || '')}</textarea></div>
                    <div class="form-group"><label>Alineación (PDI)</label><input type="text" id="f_align" value="${escHtml(data.alignment_pdi || '')}"></div>
                `;"""

new_edit_gen = """            } else if(type === 'gen_obj') {
                let alignVal = data.alignment_pdi || '';
                let isoProc = '';
                if(alignVal.startsWith('[ISO: ')) {
                    let endIdx = alignVal.indexOf(']');
                    if(endIdx !== -1) {
                        isoProc = alignVal.substring(6, endIdx);
                        alignVal = alignVal.substring(endIdx + 1).trim();
                    }
                }
                body.innerHTML = `
                    <div class="form-group"><label>Descripción del Objetivo General</label><textarea id="f_desc" rows="3">${escHtml(data.description || '')}</textarea></div>
                    <div class="form-group">
                        <label><i class="fas fa-sitemap" style="color:#2563eb;"></i> 📍 Articular a Proceso del Mapa ISO 9001</label>
                        <select id="f_iso_process" class="form-control" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;">
                            <option value="">-- Seleccionar Proceso ISO 9001 --</option>
                            <option value="Gestión de la Dirección" ${isoProc === 'Gestión de la Dirección' ? 'selected' : ''}>Gestión de la Dirección (Estratégico)</option>
                            <option value="Aseguramiento de Calidad y Riesgos" ${isoProc === 'Aseguramiento de Calidad y Riesgos' ? 'selected' : ''}>Aseguramiento de Calidad y Riesgos (Estratégico)</option>
                            <option value="Gestión Académica y Docencia" ${isoProc === 'Gestión Académica y Docencia' ? 'selected' : ''}>Gestión Académica y Docencia (Misional)</option>
                            <option value="Investigación e Innovación" ${isoProc === 'Investigación e Innovación' ? 'selected' : ''}>Investigación e Innovación (Misional)</option>
                            <option value="Proyección Social y Extensión" ${isoProc === 'Proyección Social y Extensión' ? 'selected' : ''}>Proyección Social y Extensión (Misional)</option>
                            <option value="Gestión del Talento Humano" ${isoProc === 'Gestión del Talento Humano' ? 'selected' : ''}>Gestión del Talento Humano (Apoyo)</option>
                            <option value="Tecnología y Sistemas (TI)" ${isoProc === 'Tecnología y Sistemas (TI)' ? 'selected' : ''}>Tecnología y Sistemas (TI) (Apoyo)</option>
                            <option value="Gestión Financiera" ${isoProc === 'Gestión Financiera' ? 'selected' : ''}>Gestión Financiera (Apoyo)</option>
                        </select>
                    </div>
                    <div class="form-group"><label>Alineación (PDI / Plan)</label><input type="text" id="f_align" value="${escHtml(alignVal)}"></div>
                `;"""

content_plan = content_plan.replace(old_edit_gen.replace('\r\n', '\n'), new_edit_gen.replace('\r\n', '\n'))
content_plan = content_plan.replace(old_edit_gen, new_edit_gen)

# Add ISO dropdown to addNode gen_obj
old_add_gen = """            } else if(type === 'gen_obj') {
                title.textContent = 'Nuevo Objetivo General';
                body.innerHTML = `
                    <div class="form-group"><label>Descripción</label><textarea id="f_desc" rows="3"></textarea></div>
                    <div class="form-group"><label>Alineación (PDI)</label><input type="text" id="f_align" placeholder="Opcional"></div>
                `;"""

new_add_gen = """            } else if(type === 'gen_obj') {
                title.textContent = 'Nuevo Objetivo General';
                body.innerHTML = `
                    <div class="form-group"><label>Descripción del Objetivo General</label><textarea id="f_desc" rows="3" placeholder="Ej: Fortalecer la calidad docente mediante..."></textarea></div>
                    <div class="form-group">
                        <label><i class="fas fa-sitemap" style="color:#2563eb;"></i> 📍 Articular a Proceso del Mapa ISO 9001</label>
                        <select id="f_iso_process" class="form-control" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;">
                            <option value="">-- Seleccionar Proceso ISO 9001 --</option>
                            <option value="Gestión de la Dirección">Gestión de la Dirección (Estratégico)</option>
                            <option value="Aseguramiento de Calidad y Riesgos">Aseguramiento de Calidad y Riesgos (Estratégico)</option>
                            <option value="Gestión Académica y Docencia">Gestión Académica y Docencia (Misional)</option>
                            <option value="Investigación e Innovación">Investigación e Innovación (Misional)</option>
                            <option value="Proyección Social y Extensión">Proyección Social y Extensión (Misional)</option>
                            <option value="Gestión del Talento Humano">Gestión del Talento Humano (Apoyo)</option>
                            <option value="Tecnología y Sistemas (TI)">Tecnología y Sistemas (TI) (Apoyo)</option>
                            <option value="Gestión Financiera">Gestión Financiera (Apoyo)</option>
                        </select>
                    </div>
                    <div class="form-group"><label>Alineación (PDI / Plan)</label><input type="text" id="f_align" placeholder="Opcional"></div>
                `;"""

content_plan = content_plan.replace(old_add_gen.replace('\r\n', '\n'), new_add_gen.replace('\r\n', '\n'))
content_plan = content_plan.replace(old_add_gen, new_add_gen)

# Save node formatting for gen_obj
old_save_gen = "payload.alignment_pdi = document.getElementById('f_align') ? document.getElementById('f_align').value || '' : '';"
new_save_gen = """let pdiVal = document.getElementById('f_align') ? document.getElementById('f_align').value || '' : '';
                let isoProcSelect = document.getElementById('f_iso_process') ? document.getElementById('f_iso_process').value : '';
                if(isoProcSelect) { pdiVal = `[ISO: ${isoProcSelect}] ` + pdiVal; }
                payload.alignment_pdi = pdiVal;"""

content_plan = content_plan.replace(old_save_gen, new_save_gen)

with open(file_plan, 'w', encoding='utf-8') as f:
    f.write(content_plan)

print("planificacion.html patched with ISO 9001 process articulation dropdown")
