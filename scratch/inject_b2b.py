import re

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'r', encoding='utf-8') as f:
    gerencial_content = f.read()

carg_b2b_patch = """        async function cargarB2B() {
            try {
                // MEFI / MEFE
                const mefiRes = await fetch(`/api/business/matrix/MEFI?inst_id=${getInstId()}`);
                const mefeRes = await fetch(`/api/business/matrix/MEFE?inst_id=${getInstId()}`);
                let mefiData = await mefiRes.json();
                let mefeData = await mefeRes.json();
                
                let mmHtml = `
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:25px; margin-bottom:25px;">
                        <h4 style="color:#1e3a8a; border-bottom:2px solid #e2e8f0; padding-bottom:10px; margin-bottom:20px;">Análisis MEFI / MEFE</h4>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
                            <div>
                                <h5 style="color:#0f172a; margin-bottom:15px;">Matriz MEFI (Factores Internos)</h5>
                                <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                                    <tr style="background:#f1f5f9; color:#475569;"><th style="padding:8px;text-align:left;">Factor</th><th style="padding:8px;text-align:left;">Tipo</th><th style="padding:8px;text-align:center;">Peso</th></tr>
                `;
                
                let hasMefi = false;
                if(mefiData.data && mefiData.data.factors && mefiData.data.factors.length > 0) {
                    hasMefi = true;
                    mefiData.data.factors.forEach(f => { 
                        const tipoColor = String(f.type).toLowerCase().includes('fortaleza') ? '#16a34a' : '#dc2626';
                        mmHtml += `<tr style="border-bottom:1px solid #e2e8f0;">
                            <td style="padding:8px;">${f.factor}</td>
                            <td style="padding:8px; color:${tipoColor}; font-weight:bold;">${(f.type||'').toUpperCase()}</td>
                            <td style="padding:8px; text-align:center;">${f.weight}</td>
                        </tr>`; 
                    });
                } else { mmHtml += `<tr><td colspan="3" style="padding:8px; text-align:center; color:#64748b;">No hay factores internos.</td></tr>`; }
                
                mmHtml += `</table></div><div>
                                <h5 style="color:#0f172a; margin-bottom:15px;">Matriz MEFE (Factores Externos)</h5>
                                <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                                    <tr style="background:#f1f5f9; color:#475569;"><th style="padding:8px;text-align:left;">Factor</th><th style="padding:8px;text-align:left;">Tipo</th><th style="padding:8px;text-align:center;">Peso</th></tr>
                `;
                
                let hasMefe = false;
                if(mefeData.data && mefeData.data.factors && mefeData.data.factors.length > 0) {
                    hasMefe = true;
                    mefeData.data.factors.forEach(f => { 
                        const tipoColor = String(f.type).toLowerCase().includes('oportunidad') ? '#2563eb' : '#d97706';
                        mmHtml += `<tr style="border-bottom:1px solid #e2e8f0;">
                            <td style="padding:8px;">${f.factor}</td>
                            <td style="padding:8px; color:${tipoColor}; font-weight:bold;">${(f.type||'').toUpperCase()}</td>
                            <td style="padding:8px; text-align:center;">${f.weight}</td>
                        </tr>`; 
                    });
                } else { mmHtml += `<tr><td colspan="3" style="padding:8px; text-align:center; color:#64748b;">No hay factores externos.</td></tr>`; }
                
                mmHtml += `</table></div></div></div>`;
                document.getElementById('texto_mefi_mefe').innerHTML = mmHtml;

                // PORTER
                const porterRes = await fetch(`/api/business/matrix/PORTER?inst_id=${getInstId()}`);
                let porterData = await porterRes.json();
                let pHtml = `
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:25px; margin-bottom:25px;">
                        <h4 style="color:#1e3a8a; border-bottom:2px solid #e2e8f0; padding-bottom:10px; margin-bottom:20px;">5 Fuerzas de Porter</h4>
                        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                            <tr style="background:#f1f5f9; color:#475569;"><th style="padding:8px;text-align:left;">Fuerza</th><th style="padding:8px;text-align:left;">Descripción del Factor</th><th style="padding:8px;text-align:center;">Nivel Impacto</th></tr>
                `;
                if(porterData.data && porterData.data.factors && porterData.data.factors.length > 0) {
                    porterData.data.factors.forEach(f => { 
                        let impactoColor = '#94a3b8';
                        const lvl = String(f.level||'').toLowerCase();
                        if(lvl.includes('alto')) impactoColor = '#dc2626';
                        else if(lvl.includes('medio')) impactoColor = '#f59e0b';
                        else if(lvl.includes('bajo')) impactoColor = '#10b981';
                        
                        pHtml += `<tr style="border-bottom:1px solid #e2e8f0;">
                            <td style="padding:8px; font-weight:600;">${(f.type||'').toUpperCase()}</td>
                            <td style="padding:8px;">${f.factor}</td>
                            <td style="padding:8px; text-align:center;"><span style="background:${impactoColor}20; color:${impactoColor}; padding:2px 8px; border-radius:8px; font-weight:bold;">${f.level||'N/A'}</span></td>
                        </tr>`; 
                    });
                } else { pHtml += `<tr><td colspan="3" style="padding:8px; text-align:center; color:#64748b;">No hay fuerzas registradas.</td></tr>`; }
                pHtml += `</table></div>`;
                document.getElementById('texto_porter').innerHTML = pHtml;

                // RIESGOS
                const riesgosRes = await fetch(`/api/business/matrix/RIESGOS?inst_id=${getInstId()}`);
                let riesgosData = await riesgosRes.json();
                let rHtml = `
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:25px; margin-bottom:25px;">
                        <h4 style="color:#1e3a8a; border-bottom:2px solid #e2e8f0; padding-bottom:10px; margin-bottom:20px;">Gestión de Riesgos</h4>
                        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                            <tr style="background:#f1f5f9; color:#475569;"><th style="padding:8px;text-align:left;">Riesgo</th><th style="padding:8px;text-align:center;">Probabilidad</th><th style="padding:8px;text-align:center;">Impacto</th><th style="padding:8px;text-align:center;">Mitigación</th></tr>
                `;
                if(riesgosData.data && riesgosData.data.factors && riesgosData.data.factors.length > 0) {
                    riesgosData.data.factors.forEach(f => { 
                        rHtml += `<tr style="border-bottom:1px solid #e2e8f0;">
                            <td style="padding:8px; font-weight:500;">${f.factor}</td>
                            <td style="padding:8px; text-align:center;">${f.prob||'N/A'}</td>
                            <td style="padding:8px; text-align:center;">${f.impact||'N/A'}</td>
                            <td style="padding:8px; text-align:center; font-style:italic;">${f.mitigation||'No definida'}</td>
                        </tr>`; 
                    });
                } else { rHtml += `<tr><td colspan="4" style="padding:8px; text-align:center; color:#64748b;">No hay riesgos registrados.</td></tr>`; }
                rHtml += `</table></div>`;
                document.getElementById('texto_riesgos').innerHTML = rHtml;

                // STAKEHOLDERS
                const stRes = await fetch(`/api/business/matrix/STAKEHOLDERS?inst_id=${getInstId()}`);
                let stData = await stRes.json();
                let sHtml = `
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:25px; margin-bottom:25px;">
                        <h4 style="color:#1e3a8a; border-bottom:2px solid #e2e8f0; padding-bottom:10px; margin-bottom:20px;">Mapeo de Stakeholders</h4>
                        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                            <tr style="background:#f1f5f9; color:#475569;"><th style="padding:8px;text-align:left;">Stakeholder</th><th style="padding:8px;text-align:center;">Interés</th><th style="padding:8px;text-align:center;">Poder</th><th style="padding:8px;text-align:left;">Estrategia</th></tr>
                `;
                if(stData.data && stData.data.factors && stData.data.factors.length > 0) {
                    stData.data.factors.forEach(f => { 
                        sHtml += `<tr style="border-bottom:1px solid #e2e8f0;">
                            <td style="padding:8px; font-weight:500;">${f.factor}</td>
                            <td style="padding:8px; text-align:center;">${f.interest||'N/A'}</td>
                            <td style="padding:8px; text-align:center;">${f.power||'N/A'}</td>
                            <td style="padding:8px;">${f.strategy||'No definida'}</td>
                        </tr>`; 
                    });
                } else { sHtml += `<tr><td colspan="4" style="padding:8px; text-align:center; color:#64748b;">No hay stakeholders registrados.</td></tr>`; }
                sHtml += `</table></div>`;
                document.getElementById('texto_stakeholders').innerHTML = sHtml;

                // COMUNICACION
                const comRes = await fetch(`/api/business/matrix/COMUNICACION?inst_id=${getInstId()}`);
                let comData = await comRes.json();
                let cHtml = `
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:25px; margin-bottom:25px;">
                        <h4 style="color:#1e3a8a; border-bottom:2px solid #e2e8f0; padding-bottom:10px; margin-bottom:20px;">Matriz de Comunicación</h4>
                        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                            <tr style="background:#f1f5f9; color:#475569;"><th style="padding:8px;text-align:left;">Asunto / Tarea</th><th style="padding:8px;text-align:left;">Audiencia</th><th style="padding:8px;text-align:left;">Canal</th><th style="padding:8px;text-align:left;">Frecuencia</th></tr>
                `;
                if(comData.data && comData.data.factors && comData.data.factors.length > 0) {
                    comData.data.factors.forEach(f => { 
                        cHtml += `<tr style="border-bottom:1px solid #e2e8f0;">
                            <td style="padding:8px; font-weight:500;">${f.factor}</td>
                            <td style="padding:8px;">${f.audience||'N/A'}</td>
                            <td style="padding:8px;">${f.channel||'N/A'}</td>
                            <td style="padding:8px;">${f.frequency||'N/A'}</td>
                        </tr>`; 
                    });
                } else { cHtml += `<tr><td colspan="4" style="padding:8px; text-align:center; color:#64748b;">No hay planes de comunicación registrados.</td></tr>`; }
                cHtml += `</table></div>`;
                document.getElementById('texto_comunicacion').innerHTML = cHtml;

            } catch(e) {
                console.error("Error loading B2B data:", e);
            }
        }"""

gerencial_content = re.sub(
    r'async function cargarB2B\(\) \{.*?\}(?=\s*async function cargarISO)',
    carg_b2b_patch,
    gerencial_content,
    flags=re.DOTALL
)

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'w', encoding='utf-8') as f:
    f.write(gerencial_content)

print("B2B logic injected successfully.")
