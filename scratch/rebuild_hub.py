import os

source_file = r'c:\SIAC\templates\dofa.html'
target_file = r'c:\SIAC\templates\empresa_dashboard.html'

with open(source_file, 'r', encoding='utf-8') as f:
    content = f.read()

parts = content.split('<div class="content-area">')
header = parts[0] + '<div class="content-area">\n'
footer_parts = parts[1].split('</main>')
footer = '\n</main>\n' + footer_parts[1]

dash_content = """
    <div class="tool-header" style="margin-bottom: 25px;">
        <h1 style="font-size: 1.8rem; margin-bottom: 8px; color: #2563eb;">📊 Hub Estratégico Empresarial</h1>
        <p style="color: #64748b; font-size: 0.95rem;">Bienvenido al módulo de Diagnóstico B2B. Selecciona una herramienta para comenzar o continuar tu análisis.</p>
    </div>
    
    <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 12px; padding: 30px; color: white; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 40px;">
        <div style="max-width: 600px;">
            <h2 style="font-size: 1.5rem; margin-top: 0; margin-bottom: 10px; display: flex; align-items: center; gap: 10px;">
                <span>📑</span> Informe Gerencial de Evaluación Organizacional
            </h2>
            <p style="color: #cbd5e1; font-size: 0.95rem; margin: 0; line-height: 1.5;">
                Consolida todos los análisis generados (MEFI/MEFE, Porter, Riesgos, etc.) en un único reporte estratégico inteligente.
            </p>
        </div>
        <a href="empresa_informe_gerencial.html" style="padding: 12px 25px; background: #3b82f6; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.05rem; box-shadow: 0 4px 6px rgba(59,130,246,0.3); transition: transform 0.2s;">
            Generar Informe Integral ➔
        </a>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px;">
        <!-- Core Tools -->
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h3 style="font-size: 1.25rem; margin-top: 0; color: #0f172a; margin-bottom: 10px;">🛠️ Matrices (MEFI/MEFE)</h3>
                <p style="font-size: 0.9rem; color: #475569; margin-bottom: 20px;">Evaluación cuantitativa de Fortalezas, Debilidades, Oportunidades y Amenazas extraídas de la Autoevaluación.</p>
            </div>
            <a href="empresa_matrices.html" style="display: block; width: 100%; padding: 10px; background: #f8fafc; color: #3b82f6; text-align: center; border: 1px solid #cbd5e1; border-radius: 6px; font-weight: 600; text-decoration: none;">Abrir Herramienta</a>
        </div>
        
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h3 style="font-size: 1.25rem; margin-top: 0; color: #0f172a; margin-bottom: 10px;">📈 5 Fuerzas de Porter</h3>
                <p style="font-size: 0.9rem; color: #475569; margin-bottom: 20px;">Análisis con Inteligencia Artificial sobre la rivalidad competitiva y atractivo de la industria.</p>
            </div>
            <a href="empresa_porter.html" style="display: block; width: 100%; padding: 10px; background: #f8fafc; color: #3b82f6; text-align: center; border: 1px solid #cbd5e1; border-radius: 6px; font-weight: 600; text-decoration: none;">Abrir Herramienta</a>
        </div>
        
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h3 style="font-size: 1.25rem; margin-top: 0; color: #0f172a; margin-bottom: 10px;">🛡️ Gestión de Riesgos</h3>
                <p style="font-size: 0.9rem; color: #475569; margin-bottom: 20px;">Identifica y evalúa riesgos estratégicos y operativos para el negocio con IA.</p>
            </div>
            <a href="empresa_riesgos.html" style="display: block; width: 100%; padding: 10px; background: #f8fafc; color: #3b82f6; text-align: center; border: 1px solid #cbd5e1; border-radius: 6px; font-weight: 600; text-decoration: none;">Abrir Herramienta</a>
        </div>
        
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h3 style="font-size: 1.25rem; margin-top: 0; color: #0f172a; margin-bottom: 10px;">🤝 Mapeo de Stakeholders</h3>
                <p style="font-size: 0.9rem; color: #475569; margin-bottom: 20px;">Clasifica y crea estrategias para gestionar a los grupos de interés clave.</p>
            </div>
            <a href="empresa_stakeholders.html" style="display: block; width: 100%; padding: 10px; background: #f8fafc; color: #3b82f6; text-align: center; border: 1px solid #cbd5e1; border-radius: 6px; font-weight: 600; text-decoration: none;">Abrir Herramienta</a>
        </div>

        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h3 style="font-size: 1.25rem; margin-top: 0; color: #0f172a; margin-bottom: 10px;">🏢 Alineación ISO 9001</h3>
                <p style="font-size: 0.9rem; color: #475569; margin-bottom: 20px;">Autodiagnóstico del nivel de cumplimiento del Sistema de Gestión de Calidad.</p>
            </div>
            <a href="empresa_iso.html" style="display: block; width: 100%; padding: 10px; background: #f8fafc; color: #3b82f6; text-align: center; border: 1px solid #cbd5e1; border-radius: 6px; font-weight: 600; text-decoration: none;">Abrir Herramienta</a>
        </div>

        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h3 style="font-size: 1.25rem; margin-top: 0; color: #0f172a; margin-bottom: 10px;">📢 Matriz de Comunicación</h3>
                <p style="font-size: 0.9rem; color: #475569; margin-bottom: 20px;">Planificación de canales, audiencias y frecuencia de comunicación corporativa.</p>
            </div>
            <a href="empresa_comunicacion.html" style="display: block; width: 100%; padding: 10px; background: #f8fafc; color: #3b82f6; text-align: center; border: 1px solid #cbd5e1; border-radius: 6px; font-weight: 600; text-decoration: none;">Abrir Herramienta</a>
        </div>
    </div>
"""

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(header + dash_content + footer)

print("Hub Estrategico (empresa_dashboard.html) rebuilt.")
