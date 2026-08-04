import os
import re

with open(r'c:\SIAC\templates\skel360.html', 'r', encoding='utf-8') as f:
    base = f.read()

# 1. Build Diccionario view
dicc_content = '''
        <div class="content-wrapper">
            <div class="card" style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h3>Gestor de Formularios y Competencias</h3>
                    <div>
                        <a href="/skel360.html" class="btn-primary" style="background: #64748b; margin-right: 10px; text-decoration: none;">⬅ Volver a Empresas</a>
                        <button class="btn-primary" onclick="alert('En desarrollo')">+ Nueva Competencia</button>
                    </div>
                </div>
                
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>Competencia</th>
                            <th>Tipo</th>
                            <th>Descripción</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody id="diccionario-list">
                        <tr><td colspan="4" style="text-align: center;">Cargando competencias...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
'''
new_dicc = re.sub(r'<div class="content-wrapper">.*?</main>', dicc_content + '\n    </main>', base, flags=re.DOTALL)
# Strip out the modal and javascript block from the base, and add a simple JS block for diccionario
new_dicc = re.sub(r'<!-- MODAL NUEVA EMPRESA -->.*?</script>', '<script>\n        console.log("Diccionario loaded");\n    </script>', new_dicc, flags=re.DOTALL)

with open(r'c:\SIAC\templates\skel_diccionario.html', 'w', encoding='utf-8') as f:
    f.write(new_dicc)

# 2. Build Empresa Dashboard view
empresa_content = '''
        <div class="content-wrapper" style="flex: 1; overflow-y: auto; padding: 20px;">
            <div class="card" style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h3>Gestión de Empresa: <span id="empresa-nombre">Cargando...</span></h3>
                    <a href="/skel360.html" class="btn-primary" style="background: #64748b; text-decoration: none;">⬅ Volver a Empresas</a>
                </div>
                
                <div class="grid-cards" style="margin-bottom: 20px;">
                    <div class="card" style="text-align: center;">
                        <h4 style="margin-bottom: 10px;">1. Carga de Empleados</h4>
                        <p style="font-size: 0.85rem; color: #666; margin-bottom: 15px;">Sube el Excel con la estructura organizacional de la empresa.</p>
                        <button class="btn-primary" style="background: #3b82f6; width: 100%;" onclick="alert('Carga masiva en desarrollo')">Subir Plantilla Excel</button>
                    </div>
                    <div class="card" style="text-align: center;">
                        <h4 style="margin-bottom: 10px;">2. Asignar Competencias</h4>
                        <p style="font-size: 0.85rem; color: #666; margin-bottom: 15px;">Vincula las competencias del Diccionario a cada Cargo.</p>
                        <button class="btn-primary" style="background: #8b5cf6; width: 100%;" onclick="alert('Asignación en desarrollo')">Gestionar Perfiles</button>
                    </div>
                    <div class="card" style="text-align: center;">
                        <h4 style="margin-bottom: 10px;">3. Logística de Envío</h4>
                        <p style="font-size: 0.85rem; color: #666; margin-bottom: 15px;">Genera los Magic Links y lanza la evaluación.</p>
                        <button class="btn-primary" style="background: #10b981; width: 100%;" onclick="alert('Logística en desarrollo')">Lanzar Encuestas</button>
                    </div>
                </div>

                <h3>Colaboradores Cargados</h3>
                <div style="max-height: 400px; overflow-y: auto; border: 1px solid #eee; border-radius: 8px;">
                    <table class="admin-table" style="margin-top: 0; border-top: none;">
                        <thead style="position: sticky; top: 0; background: #fff; z-index: 10; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                            <tr>
                                <th>Nombre</th>
                                <th>Cédula</th>
                                <th>Correo</th>
                                <th>Cargo</th>
                                <th>Área</th>
                            </tr>
                        </thead>
                        <tbody id="colaboradores-list">
                            <tr><td colspan="5" style="text-align: center;">No hay colaboradores cargados.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
'''
new_emp = re.sub(r'<div class="content-wrapper">.*?</main>', empresa_content + '\n    </main>', base, flags=re.DOTALL)
new_emp = re.sub(r'<!-- MODAL NUEVA EMPRESA -->.*?</script>', '<script>\n        console.log("Empresa Dashboard loaded");\n    </script>', new_emp, flags=re.DOTALL)

with open(r'c:\SIAC\templates\skel_empresa_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(new_emp)

print("Views generated successfully.")
