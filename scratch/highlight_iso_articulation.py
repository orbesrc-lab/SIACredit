import os

file_plan = r'c:\SIAC\templates\planificacion.html'
with open(file_plan, 'r', encoding='utf-8') as f:
    content = f.read()

old_align_render = "${g.alignment_pdi ? `<div style=\"font-size:0.72rem; color:#059669; margin-top:2px;\"><i class=\"fas fa-link\" style=\"margin-right:3px;\"></i>${escHtml(g.alignment_pdi)}</div>` : ''}"

new_align_render = """${(() => {
    let pdi = g.alignment_pdi || '';
    if (!pdi) return '';
    if (pdi.startsWith('[ISO: ')) {
        let endIdx = pdi.indexOf(']');
        let isoProc = endIdx !== -1 ? pdi.substring(6, endIdx) : '';
        let rest = endIdx !== -1 ? pdi.substring(endIdx + 1).trim() : pdi;
        return `<div style="margin-top:4px; display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            <span style="background:linear-gradient(135deg, #2563eb, #1d4ed8); color:white; font-size:0.78rem; font-weight:bold; padding:3px 10px; border-radius:12px; box-shadow:0 2px 4px rgba(37,99,235,0.2);"><i class="fas fa-sitemap"></i> Proceso ISO: ${escHtml(isoProc)}</span>
            ${rest ? `<span style="font-size:0.75rem; color:#64748b;"><i class="fas fa-link"></i> ${escHtml(rest)}</span>` : ''}
        </div>`;
    }
    return `<div style="font-size:0.75rem; color:#059669; margin-top:3px;"><i class="fas fa-link"></i> ${escHtml(pdi)}</div>`;
})()}"""

content = content.replace(old_align_render.replace('\r\n', '\n'), new_align_render.replace('\r\n', '\n'))
content = content.replace(old_align_render, new_align_render)

with open(file_plan, 'w', encoding='utf-8') as f:
    f.write(content)

print("planificacion.html upgraded with prominent ISO process badges!")
