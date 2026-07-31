import os
import re

tools_info = [
    {
        'file': 'empresa_riesgos.html',
        'type': 'RIESGOS',
        'title': 'Registro de Riesgos',
        'save_func': 'saveRisksData',
        'load_func': 'loadRisksData',
        'pdf_rows': """(risksData || []).map(r => `
            <tr>
                <td style="padding:8px; border:1px solid #cbd5e1;">${r.risk || r.riesgo || ''}</td>
                <td style="padding:8px; border:1px solid #cbd5e1; text-align:center;">${r.impact || r.impacto || ''}</td>
                <td style="padding:8px; border:1px solid #cbd5e1; text-align:center;">${r.probability || r.probabilidad || ''}</td>
                <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; font-weight:bold;">${r.level || r.nivel || ''}</td>
                <td style="padding:8px; border:1px solid #cbd5e1;">${r.strategy || r.estrategia || ''}</td>
            </tr>
        `).join('')""",
        'pdf_headers': "<th>Riesgo Identificado</th><th>Impacto</th><th>Probabilidad</th><th>Nivel de Riesgo</th><th>Estrategia / Control</th>"
    },
    {
        'file': 'empresa_stakeholders.html',
        'type': 'STAKEHOLDERS',
        'title': 'Matriz de Stakeholders',
        'save_func': 'saveStakeholdersData',
        'load_func': 'loadStakeholdersData',
        'pdf_rows': """(stakeholdersData || []).map(s => `
            <tr>
                <td style="padding:8px; border:1px solid #cbd5e1;">${s.group || s.grupo || ''}</td>
                <td style="padding:8px; border:1px solid #cbd5e1;">${s.expectations || s.expectativas || ''}</td>
                <td style="padding:8px; border:1px solid #cbd5e1; text-align:center;">${s.power || s.poder || ''}</td>
                <td style="padding:8px; border:1px solid #cbd5e1; text-align:center;">${s.interest || s.interes || ''}</td>
                <td style="padding:8px; border:1px solid #cbd5e1;">${s.strategy || s.estrategia || ''}</td>
            </tr>
        `).join('')""",
        'pdf_headers': "<th>Grupo de Interés</th><th>Expectativas / Necesidades</th><th>Poder (1-5)</th><th>Interés (1-5)</th><th>Estrategia de Relacionamiento</th>"
    },
    {
        'file': 'empresa_comunicacion.html',
        'type': 'COMUNICACION',
        'title': 'Matriz de Comunicación',
        'save_func': 'saveCommsData',
        'load_func': 'loadCommsData',
        'pdf_rows': """(commsData || []).map(c => `
            <tr>
                <td style="padding:8px; border:1px solid #cbd5e1;">${c.what || c.que || ''}</td>
                <td style="padding:8px; border:1px solid #cbd5e1;">${c.target || c.a_quien || ''}</td>
                <td style="padding:8px; border:1px solid #cbd5e1;">${c.channel || c.como || ''}</td>
                <td style="padding:8px; border:1px solid #cbd5e1; text-align:center;">${c.frequency || c.frecuencia || ''}</td>
                <td style="padding:8px; border:1px solid #cbd5e1;">${c.owner || c.responsable || ''}</td>
            </tr>
        `).join('')""",
        'pdf_headers': "<th>¿Qué comunicar?</th><th>¿A quién?</th><th>Canal / Medio</th><th>Frecuencia</th><th>Responsable</th>"
    }
]

for item in tools_info:
    file_path = os.path.join(r'c:\SIAC\templates', item['file'])
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Remove leftover DOFA functions at the end of the script
    if 'async function loadInternos' in content:
        idx = content.find('async function loadInternos')
        # Find where script closes
        end_script = content.rfind('</script>')
        if idx != -1 and end_script > idx:
            content = content[:idx] + content[end_script:]
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Cleaned leftover DOFA functions in {item['file']}")
