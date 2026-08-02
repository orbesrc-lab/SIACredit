
        
        function abrirModalEmpresa() {
            document.getElementById('modal-nueva-empresa').style.display = 'flex';
        }
        function cerrarModalEmpresa() {
            document.getElementById('modal-nueva-empresa').style.display = 'none';
        }
        
        document.getElementById('form-empresa').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                nombre: document.getElementById('emp-nombre').value,
                nit: document.getElementById('emp-nit').value,
                sector: document.getElementById('emp-sector').value,
                ciudad: document.getElementById('emp-ciudad').value
            };
            
            try {
                const response = await fetch('/api/skel360/empresas', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                if(result.status === 'success') {
                    cerrarModalEmpresa();
                    document.getElementById('form-empresa').reset();
                    loadEmpresas();
                } else {
                    alert('Error: ' + result.message);
                }
            } catch(error) {
                console.error(error);
                alert('Error de conexión.');
            }
        });

        async function loadEmpresas() {
            try {
                const response = await fetch('/api/skel360/empresas');
                const result = await response.json();
                const tbody = document.getElementById('empresas-list');
                tbody.innerHTML = '';
                
                if (result.status === 'success' && result.data.length > 0) {
                    document.getElementById('count-empresas').innerText = result.data.length;
                    
                    result.data.forEach(emp => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td><strong>${emp.nombre}</strong></td>
                            <td>${emp.nit || '-'}</td>
                            <td>${emp.sector || '-'}</td>
                            <td>${emp.ciudad || '-'}</td>
                            <td><span style="background: #10b981; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8rem;">${emp.estado}</span></td>
                            <td>
                                <button onclick="configurarLogistica('${emp.id}')" style="background: #f59e0b; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; margin-right: 5px;">⚙️ Configurar Envío</button>
                                <button onclick="generarInformeIA('${emp.id}')" style="background: #8b5cf6; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">✨ Generar Informe IA</button>
                            </td>
                        `;
                        tbody.appendChild(tr);
                    });
                } else {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No hay empresas registradas. Ejecuta el SQL inicial en Supabase.</td></tr>';
                }
            } catch (error) {
                console.error('Error fetching empresas:', error);
                document.getElementById('empresas-list').innerHTML = '<tr><td colspan="6" style="text-align: center; color: red;">Error al cargar datos.</td></tr>';
            }
        }
        
        document.addEventListener('DOMContentLoaded', () => {
            loadEmpresas();
        });

        async function generarInformeIA(empresaId) {
            alert('Calculando Índice de Prioridad de Formación y conectando con Inteligencia Artificial. Esto tomará unos segundos...');
            try {
                const response = await fetch(`/api/skel360/evaluaciones/empresa/${empresaId}/informe-ia`);
                const result = await response.json();
                
                if (result.status === 'success') {
                    // Mostrar informe en un modal o ventana (simplificado con alert o consola por ahora)
                    console.log("Top Brechas:", result.data.top_brechas);
                    
                    // Crear un simple modal para mostrar el reporte
                    const modalHtml = `
                        <div id="ia-modal" style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); display:flex; justify-content:center; align-items:center; z-index:9999;">
                            <div style="background:white; padding:30px; border-radius:12px; width:80%; max-width:800px; max-height:80vh; overflow-y:auto; box-shadow:0 10px 25px rgba(0,0,0,0.2);">
                                <h2>✨ Informe Gerencial Estratégico (SKEL AI)</h2>
                                <div style="margin-top:20px; font-size:1rem; line-height:1.6; color:#333;">
                                    ${result.data.informe_ia.replace(/\n/g, '<br>')}
                                </div>
                                <div style="margin-top:20px; text-align:right;">
                                    <button onclick="document.getElementById('ia-modal').remove()" class="btn-primary">Cerrar</button>
                                </div>
                            </div>
                        </div>
                    `;
                    document.body.insertAdjacentHTML('beforeend', modalHtml);

                } else {
                    alert('Aún no hay datos de evaluaciones (Matriz) para esta empresa. Ingresa datos primero.');
                }
            } catch (error) {
                console.error('Error al generar informe:', error);
                alert('Error al conectar con el motor de IA.');
            }
        }

        function configurarLogistica(empresaId) {
            const modalHtml = `
                <div id="logistica-modal" style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); display:flex; justify-content:center; align-items:center; z-index:9999;">
                    <div style="background:white; padding:30px; border-radius:12px; width:90%; max-width:500px; box-shadow:0 10px 25px rgba(0,0,0,0.2);">
                        <h2>⚙️ Configuración Logística (Empresa)</h2>
                        <p style="color:#666; margin-bottom:20px;">Habilita o deshabilita los métodos por los cuales los colaboradores podrán acceder a las evaluaciones.</p>
                        
                        <div style="margin-bottom:15px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #eee; padding-bottom:10px;">
                            <div>
                                <strong>📧 Magic Links (Email)</strong>
                                <div style="font-size:0.85rem; color:#888;">Acceso directo con un clic al correo. Ideal para administrativos.</div>
                            </div>
                            <input type="checkbox" checked style="transform: scale(1.5);">
                        </div>
                        
                        <div style="margin-bottom:15px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #eee; padding-bottom:10px;">
                            <div>
                                <strong>📱 Kiosco / Código QR</strong>
                                <div style="font-size:0.85rem; color:#888;">Acceso genérico digitando solo la cédula. Ideal para operarios.</div>
                            </div>
                            <input type="checkbox" checked style="transform: scale(1.5);">
                        </div>

                        <div style="margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #eee; padding-bottom:10px;">
                            <div>
                                <strong>💻 Portal del Colaborador</strong>
                                <div style="font-size:0.85rem; color:#888;">Acceso mediante usuario y contraseña tradicionales.</div>
                            </div>
                            <input type="checkbox" style="transform: scale(1.5);">
                        </div>
                        
                        <div style="margin-bottom:20px;">
                            <button onclick="lanzarEncuestas('${empresaId}')" class="btn-primary" style="width:100%; background:#10b981; margin-bottom:10px;">🚀 Lanzar Encuestas Ahora (Crear Tokens)</button>
                            <div style="font-size:0.8rem; color:#666; text-align:center;">Esto generará links seguros y enviará correos (si aplica).</div>
                        </div>

                        <div style="text-align:right;">
                            <button onclick="document.getElementById('logistica-modal').remove()" style="background:#ef4444; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer;">Guardar y Cerrar</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }

        async function lanzarEncuestas(empresaId) {
            // Simulamos el endpoint de lanzamiento
            alert('Generando Tokens Únicos (Magic Links) para todos los colaboradores de la empresa...');
            try {
                // En la vida real, enviamos evaluacion_id
                const response = await fetch(\`/api/skel360/empresa/\${empresaId}/evaluacion/UUID_MOCK/lanzar\`, {method: 'POST'});
                const result = await response.json();
                if(result.status === 'success') {
                    alert(result.message);
                } else {
                    alert('Operación simulada (Falta UUID de evaluación real). ' + result.message);
                }
            } catch(e) {
                console.log(e);
                alert('Tokens generados (simulación).');
            }
        }
    