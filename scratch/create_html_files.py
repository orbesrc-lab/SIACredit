import os
import re

source = "c:/SIAC/templates/dofa.html"
with open(source, "r", encoding="utf-8") as f:
    content = f.read()

# Split the content at the content-area
parts = content.split('<div class="content-area">')
header = parts[0] + '<div class="content-area">\n'

footer_start = content.rfind('</main>')
footer = '\n' + content[footer_start:]

# 1. empresa_dashboard.html
dash_content = """
    <div class="dofa-header">
        <h1>📊 Hub Estratégico Empresarial</h1>
        <p>Bienvenido al módulo de Diagnóstico B2B. Selecciona una herramienta para comenzar el análisis.</p>
    </div>
    <div class="factor-grid">
        <div class="factor-box" style="text-align:center; padding: 30px;">
            <h3 style="font-size: 1.5rem;">🛠️ Matrices (MEFI/MEFE)</h3>
            <p>Evalúa factores internos y externos ponderados.</p>
            <br>
            <a href="empresa_matrices.html" class="btn-primary" style="text-decoration:none;">Ir a Matrices</a>
        </div>
        <div class="factor-box" style="text-align:center; padding: 30px;">
            <h3 style="font-size: 1.5rem;">📈 5 Fuerzas de Porter</h3>
            <p>Analiza la competitividad y atractivo de la industria.</p>
            <br>
            <a href="empresa_porter.html" class="btn-primary" style="text-decoration:none;">Ir a Porter</a>
        </div>
    </div>
"""
with open("c:/SIAC/templates/empresa_dashboard.html", "w", encoding="utf-8") as f:
    f.write(header + dash_content + footer)

# 2. empresa_matrices.html
mat_content = """
    <div class="dofa-header">
        <h1>🛠️ Matrices MEFI y MEFE</h1>
        <p>Evaluación cuantitativa de Factores Internos (MEFI) y Externos (MEFE).</p>
    </div>
    <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
        <h3>En construcción (Fase 3)</h3>
        <p>Aquí se integrarán las tablas dinámicas para asignar ponderación y calificación a los factores de la empresa.</p>
    </div>
"""
with open("c:/SIAC/templates/empresa_matrices.html", "w", encoding="utf-8") as f:
    f.write(header + mat_content + footer)

# 3. empresa_porter.html
port_content = """
    <div class="dofa-header">
        <h1>📈 5 Fuerzas de Porter</h1>
        <p>Análisis del entorno competitivo de la empresa.</p>
    </div>
    <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
        <h3>En construcción (Fase 5)</h3>
        <p>Aquí se integrará la inteligencia artificial para calificar la rivalidad, proveedores, clientes, sustitutos y nuevos entrantes.</p>
    </div>
"""
with open("c:/SIAC/templates/empresa_porter.html", "w", encoding="utf-8") as f:
    f.write(header + port_content + footer)

print("Files created successfully.")
