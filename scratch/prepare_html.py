import re
import os

with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    informes_content = f.read()

with open(r'c:\SIAC\templates\planificacion.html', 'r', encoding='utf-8') as f:
    planificacion_content = f.read()
    
with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'r', encoding='utf-8') as f:
    gerencial_content = f.read()

# 1. We need to add Frappe Gantt JS/CSS to empresa_informe_gerencial.html
gantt_includes = """    <!-- Frappe Gantt -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/frappe-gantt/0.6.1/frappe-gantt.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/frappe-gantt/0.6.1/frappe-gantt.min.js"></script>
    <!-- End Frappe Gantt -->"""

if "frappe-gantt" not in gerencial_content:
    gerencial_content = gerencial_content.replace('</head>', f'{gantt_includes}\n</head>')

# 2. Add the CSS from informes.html and planificacion.html that we need
css_to_add = """
    <style>
        .grade-4-5 { background: #dcfce7; color: #166534; }
        .grade-4-0 { background: #dbeafe; color: #1e40af; }
        .grade-3-0 { background: #fef9c3; color: #854d0e; }
        .grade-low { background: #fee2e2; color: #991b1b; }
        .grade-badge { padding: 4px 8px; border-radius: 12px; font-weight: bold; }
        
        .factor-section { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        .factor-title { font-size: 1.2rem; color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
        .evidence-list { list-style: none; padding-left: 0; }
        .evidence-list li { margin-bottom: 8px; background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0; font-size: 0.9rem; }
        
        /* Node Tree */
        .node-card { background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; margin-bottom: 15px; position: relative; display: flex; gap: 15px; align-items: flex-start; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
        .node-card.level-1 { border-left: 5px solid #2563eb; margin-left: 0; }
        .node-card.level-2 { border-left: 5px solid #10b981; margin-left: 40px; background: #f8fafc; }
        .node-card.level-3 { border-left: 5px solid #f59e0b; margin-left: 80px; background: #fefce8; padding: 12px 15px; }
        .node-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: white; flex-shrink: 0; }
        .level-1 .node-icon { background: linear-gradient(135deg, #3b82f6, #2563eb); }
        .level-2 .node-icon { background: linear-gradient(135deg, #34d399, #10b981); }
        .level-3 .node-icon { background: linear-gradient(135deg, #fbbf24, #f59e0b); }
        
        /* Gantt override */
        .gantt .bar-label { fill: #fff; font-weight: bold; font-size: 12px; }
    </style>
"""
if "grade-4-5" not in gerencial_content:
    gerencial_content = gerencial_content.replace('</style>', f'</style>\n{css_to_add}')


# 3. Modify HTML of Chapter I to hold the full factor detail
html_cap1 = """
                        <div id="detalleFactoresCompleto" style="margin-top: 30px;">
                            <!-- Aquí se inyectarán todos los factores, encuestas, características, cuadros e IA -->
                        </div>
                        
                        <div id="texto_informe_dinamico" style="display:none;"></div>
"""
if "detalleFactoresCompleto" not in gerencial_content:
    gerencial_content = gerencial_content.replace('<!-- NEW CNA RESUMEN -->', f'<!-- NEW CNA RESUMEN -->\n{html_cap1}')


# 4. Modify HTML of Chapter II to be nicer
html_cap2_old = """                        <div id="texto_mefi_mefe" class="editable-content" contenteditable="true">
                            Cargando análisis MEFI/MEFE...
                        </div>
                        <h3 class="section-title">Fuerzas de Porter</h3>
                        <div id="texto_porter" class="editable-content" contenteditable="true">
                            Cargando fuerzas de Porter...
                        </div>
                        <h3 class="section-title">Gestión de Riesgos</h3>
                        <div id="texto_riesgos" class="editable-content" contenteditable="true">
                            Cargando matriz de riesgos...
                        </div>
                        <h3 class="section-title">Mapeo de Stakeholders</h3>
                        <div id="texto_stakeholders" class="editable-content" contenteditable="true">
                            Cargando stakeholders...
                        </div>
                        <h3 class="section-title">Matriz de Comunicación</h3>
                        <div id="texto_comunicacion" class="editable-content" contenteditable="true">
                            Cargando planes de comunicación...
                        </div>"""

html_cap2_new = """                        
                        <!-- Contenedores para visualizaciones de B2B -->
                        <div id="b2b_matrices_container" style="display: flex; flex-direction: column; gap: 20px;">
                            <div id="texto_mefi_mefe" class="editable-content">Cargando análisis MEFI/MEFE...</div>
                            <div id="texto_porter" class="editable-content">Cargando fuerzas de Porter...</div>
                            <div id="texto_riesgos" class="editable-content">Cargando matriz de riesgos...</div>
                            <div id="texto_stakeholders" class="editable-content">Cargando stakeholders...</div>
                            <div id="texto_comunicacion" class="editable-content">Cargando planes de comunicación...</div>
                        </div>
"""
gerencial_content = gerencial_content.replace(html_cap2_old, html_cap2_new)

# 5. Modify HTML of Chapter III to include the Tree and Gantt
html_cap3_old = """                        <div id="texto_planificacion" class="editable-content" contenteditable="true">
                            Cargando planificación...
                        </div>
                        <h3 class="section-title">Informe Financiero Básico</h3>
                        <div id="texto_financiero" class="editable-content" contenteditable="true">
                            Cargando financiero...
                        </div>"""
html_cap3_new = """                        
                        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
                            <h4 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px;">Árbol Estratégico</h4>
                            <div id="planningTree">Cargando árbol de planificación...</div>
                        </div>

                        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
                            <h4 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px;">Cronograma Global (Gantt)</h4>
                            <div style="overflow-x: auto; padding-bottom: 20px;">
                                <svg id="ganttGlobal"></svg>
                            </div>
                        </div>

                        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px;">
                            <h4 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px;">Informe Financiero Básico</h4>
                            <div id="texto_financiero">Cargando financiero...</div>
                        </div>
"""
gerencial_content = gerencial_content.replace(html_cap3_old, html_cap3_new)

with open(r'c:\SIAC\templates\empresa_informe_gerencial.html', 'w', encoding='utf-8') as f:
    f.write(gerencial_content)

print("HTML DOM structures prepared successfully.")
