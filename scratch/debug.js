<script>
        const empresaId = "{{ empresa_id }}";
        
        async function loadEmpresa() {
            try {
                const response = await fetch('/api/skel360/empresas');
                const result = await response.json();
                if(result.status === 'success') {
                    const emp = result.data.find(e => e.id === empresaId);
                    if(emp) document.getElementById('empresa-nombre').innerText = emp.nombre;
                }
            } catch(e) { console.error(e); }
        }
        
        async function uploadExcelHandler(e) {
            const file = e.target.files[0];
            if(!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            
            document.getElementById('colaboradores-list').innerHTML = '<tr><td colspan="6" style="text-align: center;">Procesando archivo...</td></tr>';
            
            try {
                const response = await fetch(`/api/skel360/empresa/${empresaId}/carga-masiva`, {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if(result.status === 'success') {
                    alert(result.message);
                    loadColaboradores();
                } else {
                    alert('Error: ' + result.message);
                    loadColaboradores();
                }
            } catch(error) {
                console.error(error);
                alert('Error de conexión');
            }
        }
        
        async function abrirModalColaborador(id = '') {
            document.getElementById('modalColabTitle').innerText = id ? 'Editar Colaborador' : 'Crear Colaborador';
            document.getElementById('colab-id').value = id;
            if(id) {
                const colab = window.allColaboradores.find(c => c.id == id);
                document.getElementById('colab-nombres').value = colab.nombres;
                document.getElementById('colab-apellidos').value = colab.apellidos;
                document.getElementById('colab-documento').value = colab.documento;
                document.getElementById('colab-email').value = colab.email;
                document.getElementById('colab-cargo').value = colab.skel_cargos?.nombre || '';
                document.getElementById('colab-area').value = colab.skel_areas?.nombre || '';
            } else {
                document.getElementById('formColaborador').reset();
            }
            document.getElementById('modalColaborador').style.display = 'flex';
        }
        
        function cerrarModalColaborador() {
            document.getElementById('modalColaborador').style.display = 'none';
        }
        
        async function guardarColaborador(e) {
            e.preventDefault();
            const data = {
                id: document.getElementById('colab-id').value,
                nombres: document.getElementById('colab-nombres').value,
                apellidos: document.getElementById('colab-apellidos').value,
                documento: document.getElementById('colab-documento').value,
                email: document.getElementById('colab-email').value,
                cargo: document.getElementById('colab-cargo').value,
                area: document.getElementById('colab-area').value
            };
            
            const res = await fetch(`/api/skel360/empresa/${empresaId}/colaborador`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            if((await res.json()).status === 'success') {
                cerrarModalColaborador();
                loadColaboradores();
            }
        }
        
        async function eliminarColaborador(id) {
            if(!confirm('¿Eliminar este colaborador?')) return;
            await fetch(`/api/skel360/empresa/${empresaId}/colaborador/${id}`, {method: 'DELETE'});
            loadColaboradores();
        }

        let allCargos = [];
        let allCompetencias = [];
        
        async function abrirModalPerfiles() {
            document.getElementById('modalPerfiles').style.display = 'flex';
            
            const resDicc = await fetch('/api/skel360/diccionario');
            const dataDicc = await resDicc.json();
            allCompetencias = dataDicc.data || [];
            
            const resPerf = await fetch(`/api/skel360/empresa/${empresaId}/perfiles`);
            const dataPerf = await resPerf.json();
            allCargos = dataPerf.data || [];
            
            const sel = document.getElementById('select-cargo');
            sel.innerHTML = '<option value="">Seleccione un cargo...</option>';
            allCargos.forEach(c => {
                sel.innerHTML += `<option value="${c.id}">${c.nombre}</option>`;
            });
            
            document.getElementById('lista-competencias').innerHTML = 'Seleccione un cargo arriba.';
        }
        
        function cargarCompetenciasCargo() {
            const cargoId = document.getElementById('select-cargo').value;
            if(!cargoId) {
                document.getElementById('lista-competencias').innerHTML = 'Seleccione un cargo arriba.';
                return;
            }
            
            const cargo = allCargos.find(c => c.id === cargoId);
            const html = allCompetencias.map(comp => {
                const isChecked = cargo.competencias.includes(comp.id) ? 'checked' : '';
                return `<label style="display:block; margin-bottom:5px;"><input type="checkbox" class="comp-cb" value="${comp.id}" ${isChecked}> ${comp.nombre}</label>`;
            }).join('');
            
            document.getElementById('lista-competencias').innerHTML = html;
        }
        
        async function guardarPerfil() {
            const cargoId = document.getElementById('select-cargo').value;
            if(!cargoId) return alert('Seleccione un cargo');
            
            const checks = document.querySelectorAll('.comp-cb:checked');
            const compIds = Array.from(checks).map(c => c.value);
            
            try {
                const res = await fetch(`/api/skel360/empresa/${empresaId}/perfiles`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ cargo_id: cargoId, competencias: compIds })
                });
                const data = await res.json();
                if(data.status === 'success') {
                    alert('Asignación guardada con éxito.');
                    document.getElementById('modalPerfiles').style.display = 'none';
                }
            } catch(e) { console.error(e); }
        }
        
        async function lanzarEncuestas() {
            if(!confirm('¿Estás seguro de generar las evaluaciones para todos los colaboradores?')) return;
            
            try {
                const res = await fetch(`/api/skel360/empresa/${empresaId}/lanzar`, {method: 'POST'});
                const data = await res.json();
                if(data.status === 'success') {
                    alert(data.message);
                    const tbody = document.getElementById('links-tbody');
                    tbody.innerHTML = '';
                    data.links.forEach(l => {
                        tbody.innerHTML += `<tr><td>${l.nombre}</td><td>${l.correo}</td><td><a href="${l.link}" target="_blank" style="color:#3b82f6; font-size:0.85rem;">${l.link}</a></td></tr>`;
                    });
                    document.getElementById('modalLinks').style.display = 'flex';
                } else {
                    alert('Error: ' + data.message);
                }
            } catch(e) { console.error(e); }
        }
        
        async function loadColaboradores() {
            try {
                const response = await fetch(`/api/skel360/empresa/${empresaId}/colaboradores`);
                const result = await response.json();
                if(result.status === 'success') {
                    const tbody = document.getElementById('colaboradores-list');
                    tbody.innerHTML = '';
                    if(result.data.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No hay colaboradores cargados.</td></tr>';
                    }
                    window.allColaboradores = result.data;
                    result.data.forEach(c => {
                        tbody.innerHTML += `
                            <tr>
                                <td><strong>${c.nombres || ''} ${c.apellidos || ''}</strong></td>
                                <td>${c.documento || ''}</td>
                                <td>${c.email || ''}</td>
                                <td>${c.skel_cargos?.nombre || ''}</td>
                                <td>${c.skel_areas?.nombre || ''}</td>
                                <td>
                                    <button onclick="abrirModalColaborador('${c.id}')" style="background:#3b82f6; color:white; border:none; padding:5px 10px; border-radius:5px; cursor:pointer; margin-right:5px;">✏️</button>
                                    <button onclick="eliminarColaborador('${c.id}')" style="background:#ef4444; color:white; border:none; padding:5px 10px; border-radius:5px; cursor:pointer;">🗑️</button>
                                </td>
                            </tr>
                        `;
                    });
                }
            } catch(e) { console.error(e); }
        }
        
        loadEmpresa();
        loadColaboradores();

    </script>
</body>
</html>
