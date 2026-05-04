    
        const user = JSON.parse(localStorage.getItem('siac_user'));
        if (!user) { window.location.href = 'login.html'; }
        document.getElementById('userInfo').textContent = user ? user.email : '';

        function logout() {
            localStorage.removeItem('siac_user');
            window.location.href = 'index.html';
        }

        // --- LÃ³gica del Gestor de Modelo ---
        function renderModelEditor() {
            const container = document.getElementById('modelEditorContainer');
            const progId = getProgramId();

            // TRAZABILIDAD: Bloquear si no hay programa activo
            if (!progId || progId == 0) {
                container.innerHTML = `
                    <div style="background: #fef9c3; border: 2px dashed #ca8a04; border-radius: 12px; padding: 30px; text-align: center;">
                        <div style="font-size: 2.5rem; margin-bottom: 15px;">ðŸ—‚ï¸</div>
                        <h3 style="color: #92400e; margin-bottom: 10px;">Sin Programa Activo</h3>
                        <p style="color: #78350f; max-width: 450px; margin: 0 auto; font-size: 0.95rem;">
                            Para definir Factores, CaracterÃ­sticas y Aspectos de evaluaciÃ³n, primero debes:
                        </p>
                        <ol style="text-align: left; max-width: 350px; margin: 15px auto; color: #78350f; font-size: 0.9rem; line-height: 2;">
                            <li>Crear o seleccionar una <strong>InstituciÃ³n</strong></li>
                            <li>Crear o seleccionar un <strong>Programa AcadÃ©mico</strong></li>
                            <li>Hacer clic en <strong>"Cambiar / Cargar"</strong></li>
                        </ol>
                        <p style="color: #92400e; font-size: 0.85rem;">El modelo quedarÃ¡ vinculado exclusivamente a ese programa.</p>
                    </div>`;
                const addBtn = document.querySelector('[onclick="addFactor()"]');
                if (addBtn) { addBtn.disabled = true; addBtn.style.opacity = '0.4'; addBtn.style.cursor = 'not-allowed'; addBtn.title = 'Selecciona un programa primero'; }
                const saveBtn = document.querySelector('[onclick="syncModelWithBackend()"]');
                if (saveBtn) { saveBtn.disabled = true; saveBtn.style.opacity = '0.4'; saveBtn.style.cursor = 'not-allowed'; }
                return;
            }

            // Re-habilitar botones si hay programa activo
            const addBtn = document.querySelector('[onclick="addFactor()"]');
            if (addBtn) { addBtn.disabled = false; addBtn.style.opacity = ''; addBtn.style.cursor = ''; addBtn.title = ''; }
            const saveBtn = document.querySelector('[onclick="syncModelWithBackend()"]');
            if (saveBtn) { saveBtn.disabled = false; saveBtn.style.opacity = ''; saveBtn.style.cursor = ''; }

            const data = getDataModel();
            let html = '';

            if (data.length === 0) {
                html = '<p style="text-align: center; color: var(--text-muted); padding: 20px;">No hay factores definidos. Haz clic en "AÃ±adir Factor" para comenzar.</p>';
            } else {
                const totalFactorWeight = data.reduce((sum, f) => sum + (f.weight || 0), 0);
                if (totalFactorWeight !== 100) {
                    html += `<div style="background: #fee2e2; color: #b91c1c; padding: 10px 15px; border-radius: 8px; margin-bottom: 15px; font-size: 0.9rem;">
                                âš ï¸ <strong>Advertencia:</strong> La suma del peso de todos los factores es ${totalFactorWeight}%. Debe ser exactamente 100%.
                             </div>`;
                }
            }

            data.forEach((factor, fIndex) => {
                const totalCharWeight = factor.characteristics.reduce((sum, c) => sum + (c.weight || 0), 0);

                html += `
                    <div style="border: 1px solid var(--border-color); border-radius: 8px; margin-bottom: 15px; background: #fafafa;">
                        <div style="padding: 15px; display: flex; justify-content: space-between; align-items: center; background: #f1f5f9; border-top-left-radius: 8px; border-top-right-radius: 8px; border-bottom: 1px solid var(--border-color);">
                            <div style="font-weight: 700; color: var(--text-main); display: flex; align-items: center; gap: 15px;">
                                Factor ${factor.number}: ${factor.name}
                                <div style="font-weight: normal; font-size: 0.85rem; display: flex; align-items: center; gap: 5px;">
                                    Peso: <input type="number" min="0" max="100" style="width: 60px; padding: 3px; text-align: center; border: 1px solid var(--border-color); border-radius: 4px;" value="${factor.weight || 0}" onchange="updateFactorWeight('${factor.id}', this.value)"> %
                                </div>
                            </div>
                            <div>
                                <button class="btn-ghost" style="font-size: 0.8rem; padding: 5px 10px; color: var(--primary-color);" onclick="addCharacteristic('${factor.id}')">+ CaracterÃ­stica</button>
                                <button class="btn-ghost" style="font-size: 0.8rem; padding: 5px 10px; color: var(--primary-color);" onclick="editFactor('${factor.id}')">Editar</button>
                                <button class="btn-ghost" style="font-size: 0.8rem; padding: 5px 10px; color: #ef4444;" onclick="deleteFactor('${factor.id}')">Eliminar</button>
                            </div>
                        </div>
                        <div style="padding: 15px;">
                `;

                if (factor.characteristics.length > 0 && totalCharWeight !== 100) {
                    html += `<div style="color: #b91c1c; font-size: 0.85rem; margin-bottom: 15px;">
                                âš ï¸ La suma de las caracterÃ­sticas en este factor es ${totalCharWeight}%. Debe sumar 100%.
                             </div>`;
                }

                if (factor.characteristics.length === 0) {
                    html += '<div style="font-size: 0.85rem; color: var(--text-muted);">Sin caracterÃ­sticas asignadas.</div>';
                }

                factor.characteristics.forEach((char, cIndex) => {
                    html += `
                        <div style="margin-left: 20px; margin-bottom: 15px; border-left: 2px solid var(--border-color); padding-left: 15px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <div style="font-weight: 600; font-size: 0.95rem; color: var(--text-main); display: flex; align-items: center; gap: 15px;">
                                    Caract. ${char.number}: ${char.name}
                                    <div style="font-weight: normal; font-size: 0.8rem; display: flex; align-items: center; gap: 5px; color: var(--text-muted);">
                                        Peso: <input type="number" min="0" max="100" style="width: 50px; padding: 2px; text-align: center; border: 1px solid var(--border-color); border-radius: 4px;" value="${char.weight || 0}" onchange="updateCharWeight('${factor.id}', '${char.id}', this.value)"> %
                                    </div>
                                </div>
                                <div>
                                    <button class="btn-ghost" style="font-size: 0.75rem; padding: 4px 8px; color: var(--primary-color);" onclick="addAspect('${factor.id}', '${char.id}')">+ Aspecto</button>
                                    <button class="btn-ghost" style="font-size: 0.75rem; padding: 4px 8px; color: var(--primary-color);" onclick="editCharacteristic('${factor.id}', '${char.id}')">Editar</button>
                                    <button class="btn-ghost" style="font-size: 0.75rem; padding: 4px 8px; color: #ef4444;" onclick="deleteCharacteristic('${factor.id}', '${char.id}')">Eliminar</button>
                                </div>
                            </div>
                            <div style="margin-left: 15px;">
                    `;

                    if (char.aspects.length === 0) {
                        html += '<div style="font-size: 0.8rem; color: var(--text-muted);">Sin aspectos asignados.</div>';
                    }

                    char.aspects.forEach((asp, aIndex) => {
                        html += `
                            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: var(--text-muted); background: var(--white); padding: 8px 12px; border: 1px solid var(--border-color); border-radius: 6px; margin-bottom: 5px;">
                                <div>â€¢ Aspecto ${aIndex + 1}: ${asp.text}</div>
                                <div>
                                    <button class="btn-ghost" style="font-size: 0.75rem; padding: 2px 6px; color: var(--primary-color);" onclick="editAspect('${factor.id}', '${char.id}', '${asp.id}')">Editar</button>
                                    <button class="btn-ghost" style="font-size: 0.75rem; padding: 2px 6px; color: #ef4444;" onclick="deleteAspect('${factor.id}', '${char.id}', '${asp.id}')">X</button>
                                </div>
                            </div>
                        `;
                    });

                    html += `
                            </div>
                        </div>
                    `;
                });

                html += `
                        </div>
                    </div>
                `;
            });

            html += `
                <table class="evidence-table">
                    <thead>
                        <tr>
                            <th>Nombre del Archivo</th>
                            <th>Subido por</th>
                            <th>Fecha</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody id="evidenceList">
                        <!-- Dynamic content -->
                    </tbody>
                </table>
            `;

            container.innerHTML = html;
        }

        // Acciones ActualizaciÃ³n de Pesos
        function updateFactorWeight(factorId, weightValue) {
            const model = getDataModel();
            const factor = model.find(f => f.id === factorId);
            if (factor) {
                factor.weight = parseFloat(weightValue) || 0;
                saveDataModel(model);
                renderModelEditor();
            }
        }

        function updateCharWeight(factorId, charId, weightValue) {
            const model = getDataModel();
            const factor = model.find(f => f.id === factorId);
            if (factor) {
                const char = factor.characteristics.find(c => c.id === charId);
                if (char) {
                    char.weight = parseFloat(weightValue) || 0;
                    saveDataModel(model);
                    renderModelEditor();
                }
            }
        }

        // Acciones ActualizaciÃ³n de Pesos
        const cnaTemplate = [
            { number: "1", name: "Proyecto Educativo e Identidad Institucional", characteristics: [{ number: "1.1", name: "MisiÃ³n y visiÃ³n", aspects: [{ text: "Coherencia de la misiÃ³n" }] }] },
            { number: "2", name: "Estudiantes", characteristics: [{ number: "2.1", name: "Mecanismos de ingreso", aspects: [{ text: "Reglamento de admisiones" }] }, { number: "2.2", name: "ParticipaciÃ³n estudiantil", aspects: [{ text: "RepresentaciÃ³n en consejos" }] }] },
            { number: "3", name: "Profesores", characteristics: [{ number: "3.1", name: "SelecciÃ³n y evaluaciÃ³n", aspects: [{ text: "Estatuto docente" }] }] },
            { number: "4", name: "Egresados", characteristics: [{ number: "4.1", name: "Impacto de los egresados", aspects: [{ text: "Seguimiento a graduados" }] }] },
            { number: "5", name: "Aspectos AcadÃ©micos y Resultados", characteristics: [{ number: "5.1", name: "Plan de estudios", aspects: [{ text: "Flexibilidad curricular" }] }] },
            { number: "6", name: "Permanencia y GraduaciÃ³n", characteristics: [{ number: "6.1", name: "Estrategias de permanencia", aspects: [{ text: "TutorÃ­as y apoyos" }] }] },
            { number: "7", name: "InteracciÃ³n con el Entorno", characteristics: [{ number: "7.1", name: "ExtensiÃ³n y proyecciÃ³n social", aspects: [{ text: "Proyectos de impacto" }] }] },
            { number: "8", name: "Aportes de la InvestigaciÃ³n", characteristics: [{ number: "8.1", name: "Grupos y proyectos", aspects: [{ text: "Publicaciones" }] }] },
            { number: "9", name: "Bienestar Institucional", characteristics: [{ number: "9.1", name: "Programas de bienestar", aspects: [{ text: "Cobertura de servicios" }] }] },
            { number: "10", name: "Medios Educativos y Ambientes", characteristics: [{ number: "10.1", name: "Recursos bibliogrÃ¡ficos", aspects: [{ text: "Bases de datos" }] }, { number: "10.2", name: "Aulas y laboratorios", aspects: [{ text: "Equipamiento" }] }] },
            { number: "11", name: "OrganizaciÃ³n, AdministraciÃ³n y FinanciaciÃ³n", characteristics: [{ number: "11.1", name: "GestiÃ³n administrativa", aspects: [{ text: "Estructura organizacional" }] }] },
            { number: "12", name: "Recursos FÃ­sicos y TecnolÃ³gicos", characteristics: [{ number: "12.1", name: "Infraestructura", aspects: [{ text: "Mantenimiento" }] }] }
        ];

        // Acciones CRUD
        function addFactor() {
            let promptText = "Opciones para aÃ±adir Factor:\n\n";
            promptText += "Ingrese un nÃºmero del 1 al 12 para importar la plantilla oficial del CNA (ej. '2' para Estudiantes).\n";
            promptText += "Deje el campo en blanco y presione 'Aceptar' para crear un factor personalizado.";

            const selection = prompt(promptText);
            const model = getDataModel();

            if (selection === null) return; // CancelÃ³

            const numSel = parseInt(selection);
            if (!isNaN(numSel) && numSel >= 1 && numSel <= 12) {
                // Importar de plantilla
                const tmpl = cnaTemplate[numSel - 1];

                const newFactor = {
                    id: 'f' + generateId(),
                    number: tmpl.number,
                    name: tmpl.name,
                    weight: 0,
                    characteristics: tmpl.characteristics.map(c => ({
                        id: 'c' + generateId(),
                        number: c.number,
                        name: c.name,
                        weight: 0,
                        aspects: c.aspects.map(a => ({
                            id: 'a' + generateId(),
                            text: a.text
                        }))
                    }))
                };

                model.push(newFactor);
                saveDataModel(model);
                renderModelEditor();
            } else {
                // Factor personalizado
                const num = prompt("NÃºmero del Factor (ej. 13):");
                if (!num) return;
                const name = prompt("Nombre del Factor:");
                if (!name) return;

                model.push({ id: 'f' + generateId(), number: num, name: name, weight: 0, characteristics: [] });
                saveDataModel(model);
                renderModelEditor();
            }
        }


        function deleteFactor(factorId) {
            if (!confirm("Â¿Seguro que desea eliminar este factor y todo su contenido?")) return;
            let model = getDataModel();
            model = model.filter(f => f.id !== factorId);
            saveDataModel(model);
            renderModelEditor();
        }

        function addCharacteristic(factorId) {
            const num = prompt("NÃºmero de la caracterÃ­stica (ej. 2.1):");
            if (!num) return;
            const name = prompt("Nombre de la caracterÃ­stica:");
            if (!name) return;

            const model = getDataModel();
            const factor = model.find(f => f.id === factorId);
            if (factor) {
                factor.characteristics.push({ id: 'c' + generateId(), number: num, name: name, weight: 0, aspects: [] });
                saveDataModel(model);
                renderModelEditor();
            }
        }

        function deleteCharacteristic(factorId, charId) {
            if (!confirm("Â¿Eliminar caracterÃ­stica?")) return;
            const model = getDataModel();
            const factor = model.find(f => f.id === factorId);
            if (factor) {
                factor.characteristics = factor.characteristics.filter(c => c.id !== charId);
                saveDataModel(model);
                renderModelEditor();
            }
        }

        function addAspect(factorId, charId) {
            const text = prompt("Ingrese el texto a evaluar del aspecto:");
            if (!text) return;

            const model = getDataModel();
            const factor = model.find(f => f.id === factorId);
            if (factor) {
                const char = factor.characteristics.find(c => c.id === charId);
                if (char) {
                    char.aspects.push({ id: 'a' + generateId(), text: text });
                    saveDataModel(model);
                    renderModelEditor();
                }
            }
        }

        function deleteAspect(factorId, charId, aspectId) {
            if (!confirm("Â¿Eliminar aspecto?")) return;
            const model = getDataModel();
            const factor = model.find(f => f.id === factorId);
            if (factor) {
                const char = factor.characteristics.find(c => c.id === charId);
                if (char) {
                    char.aspects = char.aspects.filter(a => a.id !== aspectId);
                    saveDataModel(model);
                    renderModelEditor();
                }
            }
        }

        // Acciones de EdiciÃ³n
        function editFactor(factorId) {
            const model = getDataModel();
            const factor = model.find(f => f.id === factorId);
            if (factor) {
                const num = prompt("NÃºmero del Factor:", factor.number);
                if (num === null) return; // Cancelado
                const name = prompt("Nombre del Factor:", factor.name);
                if (name === null) return; // Cancelado

                factor.number = num || factor.number;
                factor.name = name || factor.name;
                saveDataModel(model);
                renderModelEditor();
            }
        }

        function editCharacteristic(factorId, charId) {
            const model = getDataModel();
            const factor = model.find(f => f.id === factorId);
            if (factor) {
                const char = factor.characteristics.find(c => c.id === charId);
                if (char) {
                    const num = prompt("NÃºmero de la caracterÃ­stica:", char.number);
                    if (num === null) return;
                    const name = prompt("Nombre de la caracterÃ­stica:", char.name);
                    if (name === null) return;

                    char.number = num || char.number;
                    char.name = name || char.name;
                    saveDataModel(model);
                    renderModelEditor();
                }
            }
        }

        function editAspect(factorId, charId, aspectId) {
            const model = getDataModel();
            const factor = model.find(f => f.id === factorId);
            if (factor) {
                const char = factor.characteristics.find(c => c.id === charId);
                if (char) {
                    const aspect = char.aspects.find(a => a.id === aspectId);
                    if (aspect) {
                        const text = prompt("Texto del aspecto:", aspect.text);
                        if (text === null) return;

                        aspect.text = text || aspect.text;
                        saveDataModel(model);
                        renderModelEditor();
                    }
                }
            }
        }

        // --- Nuevas Funciones para AcreditaciÃ³n DinÃ¡mica ---

        async function syncModelWithBackend() {
            const statusDiv = document.getElementById('syncStatus');
            statusDiv.innerHTML = '<span style="color: var(--primary-color)">â³ Sincronizando con Supabase...</span>';

            const model = getDataModel();
            try {
                const resp = await fetch(`/api/model?inst_id=${getInstId()}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(model)
                });
                const res = await resp.json();
                if (res.status === 'success') {
                    statusDiv.innerHTML = '<span style="color: #10b981;">âœ… Modelo sincronizado correctamente.</span>';
                    setTimeout(() => statusDiv.innerHTML = '', 3000);
                } else {
                    statusDiv.innerHTML = `<span style="color: #ef4444;">âŒ Error: ${res.message}</span>`;
                }
            } catch (err) {
                statusDiv.innerHTML = '<span style="color: #ef4444;">âŒ Error de conexiÃ³n con el servidor.</span>';
            }
        }

        function downloadCSVTemplate() {
            const headers = "Factor_Num;Factor_Nombre;Char_Num;Char_Nombre;Aspecto_Texto";
            const sample = "1;Proyecto Institucional;1.1;MisiÃ³n y Proyecto;La instituciÃ³n cuenta con una misiÃ³n claramente definida...\n1;Proyecto Institucional;1.2;Gobierno y GestiÃ³n;La estructura de gobierno garantiza la autonomÃ­a...";
            const blob = new Blob([`${headers}\n${sample}`], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.setAttribute("href", url);
            link.setAttribute("download", "plantilla_modelo_siac.csv");
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        function parseCSV(text) {
            const lines = text.split('\n').filter(line => line.trim() !== '');
            const factorsMap = {};
            
            // Skip header
            for (let i = 1; i < lines.length; i++) {
                const cols = lines[i].split(';');
                if (cols.length < 4) continue;
                
                const fNum = cols[0].trim();
                const fName = cols[1].trim();
                const cNum = cols[2].trim();
                const cName = cols[3].trim();
                const aText = cols[4] ? cols[4].trim() : "";

                if (!factorsMap[fNum]) {
                    factorsMap[fNum] = { id: 'f' + generateId(), number: fNum, name: fName, characteristics: {} };
                }
                
                if (!factorsMap[fNum].characteristics[cNum]) {
                    factorsMap[fNum].characteristics[cNum] = { id: 'c' + generateId(), factor_id: factorsMap[fNum].id, number: cNum, name: cName, aspects: [] };
                }
                
                if (aText) {
                    factorsMap[fNum].characteristics[cNum].aspects.push({ id: 'a' + generateId(), char_id: factorsMap[fNum].characteristics[cNum].id, text: aText });
                }
            }
            
            // Convert maps to arrays
            return Object.values(factorsMap).map(f => {
                f.characteristics = Object.values(f.characteristics);
                return f;
            });
        }

        function injectModel() {
            const fileInput = document.getElementById('modelFile');
            if (!fileInput.files[0]) {
                alert("Por favor selecciona un archivo (CSV o JSON) primero.");
                return;
            }

            const file = fileInput.files[0];
            const reader = new FileReader();
            reader.onload = function (e) {
                try {
                    let importedModel;
                    if (file.name.endsWith('.csv')) {
                        importedModel = parseCSV(e.target.result);
                    } else {
                        importedModel = JSON.parse(e.target.result);
                    }

                    if (!Array.isArray(importedModel) || importedModel.length === 0) throw new Error("Formato invÃ¡lido o archivo vacÃ­o.");

                    if (confirm(`Se han detectado ${importedModel.length} factores. Â¿Deseas reemplazar el modelo actual?`)) {
                        saveDataModel(importedModel);
                        renderModelEditor();
                        syncModelWithBackend();
                        alert("Modelo inyectado correctamente.");
                    }
                } catch (err) {
                    alert("Error al procesar el archivo: " + err.message);
                }
            };
            reader.readAsText(file);
        }

        function exportModel() {
            const data = getDataModel();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'modelo_siacredit.json';
            a.click();
            URL.revokeObjectURL(url);
        }

        // Sobrescribir saveDataModel para que sea sÃ­ncrono en local pero podamos llamar al sync manualmente
        // o llamarlo automÃ¡ticamente en cada cambio. Para evitar spam de red, usaremos el botÃ³n manual y
        // algunos automÃ¡ticos en cambios importantes.

        function assignFactors(email) {
            const factors = prompt("Ingrese los nÃºmeros de los factores asignados separados por coma (ej: 1,2,5):");
            if (factors !== null) {
                const factorsArray = factors.split(',').map(f => parseInt(f.trim())).filter(f => !isNaN(f));

                // Si es el usuario logueado, actualizar su localStorage
                if (user.email === email) {
                    user.assigned_factors = factorsArray;
                    localStorage.setItem('siac_user', JSON.stringify(user));
                }

                // Actualizar en el registro de usuarios simulado
                const regUser = JSON.parse(localStorage.getItem('siac_registered_user'));
                if (regUser && regUser.email === email) {
                    regUser.assigned_factors = factorsArray;
                    localStorage.setItem('siac_registered_user', JSON.stringify(regUser));
                }

                alert(`Factores [${factorsArray.join(', ')}] asignados a ${email}`);
                location.reload(); // Recargar para ver cambios
            }
        }

        async function init() {
            await loadDataFromAPI();
            renderModelEditor();
            loadAllInstitutions();
            loadAllPrograms();
            loadUsersFromAPI();
            renderFactorLeaders();
            updateContextBreadcrumb();
        }

        async function updateContextBreadcrumb() {
            const breadcrumb = document.getElementById('contextBreadcrumb');
            if (!breadcrumb) return;
            const progId = getProgramId();
            const instId = getInstId();
            
            if (!progId || progId == 0) {
                breadcrumb.innerHTML = `âš ï¸ <strong>Contexto:</strong> Sin programa activo &mdash; Selecciona un programa en "GestiÃ³n de Programas AcadÃ©micos" para comenzar.`;
                breadcrumb.style.background = '#fef9c3';
                breadcrumb.style.borderColor = '#ca8a04';
                breadcrumb.style.color = '#92400e';
                return;
            }

            try {
                const [instResp, progResp] = await Promise.all([
                    fetch('/api/institutions'),
                    fetch(`/api/programs?inst_id=${instId}`)
                ]);
                const institutions = await instResp.json();
                const programs = await progResp.json();

                const inst = institutions.find(i => i.id == instId);
                const prog = programs.find(p => p.id == progId);

                const instName = inst ? inst.name : `ID: ${instId}`;
                const progName = prog ? `${prog.name} (${prog.period})` : `ID: ${progId}`;

                breadcrumb.innerHTML = `ðŸ›ï¸ <strong>InstituciÃ³n:</strong> ${instName} &nbsp;â€º&nbsp; ðŸ“š <strong>Programa:</strong> ${progName}`;
                breadcrumb.style.background = '#f0f9ff';
                breadcrumb.style.borderColor = '#bae6fd';
                breadcrumb.style.color = '#0369a1';
            } catch(e) {
                breadcrumb.innerHTML = `ðŸ›ï¸ Inst. ID: ${instId} &nbsp;â€º&nbsp; ðŸ“š Prog. ID: ${progId}`;
            }
        }

        async function renderFactorLeaders() {
            const grid = document.getElementById('factorLeadersGrid');
            const area = document.getElementById('articulationArea');
            const model = getDataModel();
            
            if (!model || model.length === 0) {
                area.style.display = 'none';
                return;
            }
            
            area.style.display = 'block';
            grid.innerHTML = '<div style="grid-column: 1/-1; color: var(--text-muted);">Cargando lÃ­deres...</div>';
            
            try {
                const resp = await fetch(`/api/users?inst_id=${getInstId()}&program_id=${getProgramId()}`);
                const users = await resp.json();
                const leaders = users.filter(u => u.role === 'lider' || u.role === 'admin' || u.role === 'inst_admin');
                
                let html = '';
                model.forEach(factor => {
                    const assignedTo = factor.leader_id || '';
                    html += `
                        <div style="padding: 10px; background: white; border-radius: 6px; border: 1px solid var(--border-color);">
                            <strong>Factor ${factor.number}:</strong>
                            <div style="font-size:0.8rem; margin-bottom:5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${factor.name}">${factor.name}</div>
                            <select onchange="assignLeaderToFactor('${factor.id}', this.value)" style="width: 100%; padding: 5px; border-radius: 4px; border: 1px solid var(--border-color);">
                                <option value="">-- Sin Asignar --</option>
                                ${leaders.map(l => `<option value="${l.id}" ${assignedTo == l.id ? 'selected' : ''}>${l.name || l.email.split('@')[0]}</option>`).join('')}
                            </select>
                        </div>
                    `;
                });
                grid.innerHTML = html;
            } catch(e) {
                grid.innerHTML = '<div style="color: #ef4444;">Error cargando lÃ­deres</div>';
            }
        }

        function assignLeaderToFactor(factorId, userId) {
            const model = getDataModel();
            const factor = model.find(f => f.id === factorId);
            if (factor) {
                factor.leader_id = userId;
                saveDataModel(model);
            }
        }


        async function loadInstitution() {
            const resp = await fetch(`/api/institution?inst_id=${getInstId()}`);
            const data = await resp.json();
            if(document.getElementById('inst_name')) document.getElementById('inst_name').value = data.name || '';
            if(document.getElementById('inst_logo')) document.getElementById('inst_logo').value = data.logo_url || '';
        }

        async function saveInstitution() {
            const name = document.getElementById('inst_name').value;
            const logo = document.getElementById('inst_logo').value;

            const resp = await fetch(`/api/institution?inst_id=${getInstId()}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name, logo_url: logo })
            });

            if (resp.ok) {
                alert('InstituciÃ³n guardada correctamente.');
                loadInstitution(); // Recargar
                if (user.role === 'admin') loadAllInstitutions();
            }
        }

        async function saveProgram() {
            const name = document.getElementById('prog_name').value.trim();
            const period = document.getElementById('prog_period').value.trim();
            
            if (!name || !period) {
                alert("Debes llenar el Nombre del Programa y el Periodo."); return;
            }

            const currentProgId = getProgramId();
            
            if(!currentProgId || currentProgId == 0) {
                // Crear nuevo programa
                try {
                    const resp = await fetch(`/api/programs?inst_id=${getInstId()}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, period })
                    });
                    const result = await resp.json();
                    if (result.status === 'success') {
                        alert(`Programa '${name}' creado correctamente.`);
                        const userData = JSON.parse(localStorage.getItem('siac_user'));
                        userData.program_id = parseInt(result.data.id);
                        localStorage.setItem('siac_user', JSON.stringify(userData));
                        location.reload();
                    } else {
                        alert('Error al crear el programa.');
                    }
                } catch (err) {
                    alert("Error de conexiÃ³n.");
                }
            } else {
                // Actualizar programa existente
                try {
                    const resp = await fetch(`/api/programs/${currentProgId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: name, period: period })
                    });

                    if (resp.ok) {
                        alert('Programa guardado correctamente.');
                        loadAllPrograms();
                    } else {
                        alert('Error al guardar el programa.');
                    }
                } catch(e) {
                    alert("Error de conexiÃ³n");
                }
            }
        }

        // Cargar al inicio
        loadInstitution();

        function setTheme(themeName) {
            localStorage.setItem('siac_theme', themeName);
            document.documentElement.setAttribute('data-theme', themeName);
        }

        function resetPass(email) {
            if (confirm(`Â¿EstÃ¡ seguro de resetear la contraseÃ±a del usuario ${email}? Se enviarÃ¡ una clave temporal a su email personal.`)) {
                alert("AcciÃ³n completada. Clave reseteada.");
            }
        }

        // ========== GestiÃ³n de Usuarios DinÃ¡mica ==========

        async function loadUsersFromAPI() {
            const container = document.getElementById('usersTable');
            try {
                const resp = await fetch(`/api/users?inst_id=${getInstId()}&program_id=${getProgramId()}`);
                const users = await resp.json();
                if (!Array.isArray(users) || users.length === 0) {
                    container.innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-muted);">No hay usuarios registrados para esta instituciÃ³n.</div>';
                    return;
                }
                container.innerHTML = users.map(u => {
                    const isPending = u.name && u.name.startsWith('[PENDING]');
                    const cleanName = u.name ? u.name.replace('[PENDING] ', '').replace('[PENDING]', '') : u.email.split('@')[0];
                    const effectiveRole = isPending ? 'pending' : u.role;
                    
                    const roleBadge = effectiveRole === 'admin' || effectiveRole === 'inst_admin' ? 'role-admin' : (effectiveRole === 'pending' ? '' : 'role-leader');
                    const roleLabel = { admin: 'Super Admin', inst_admin: 'Admin Inst.', lider: 'LÃ­der', operativo: 'Operativo', pending: 'Pendiente' }[effectiveRole] || effectiveRole;
                    const isCurrentUser = u.email === user.email;
                    
                    return `<div class="user-item">
                        <div class="user-info">
                            <span class="user-name">${cleanName}</span>
                            <span class="user-role">${u.email} &middot; <em>${roleLabel}</em>${isCurrentUser ? ' â€¢ (TÃº)' : ''}</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span class="role-badge ${roleBadge}" style="${isPending ? 'background:#fef3c7; color:#d97706;' : ''}">${roleLabel.toUpperCase()}</span>
                            ${isPending && (user.role === 'admin' || user.role === 'inst_admin') ? `<button onclick="activateUser(${u.id}, '${u.email}')" class="btn-primary" style="font-size:0.7rem; padding: 4px 8px;">Activar</button>` : ''}
                            ${!isCurrentUser && !isPending ? `<button onclick="resetUserPass(${u.id}, '${u.email}')" class="btn-ghost" style="font-size:0.7rem; color:var(--primary-color);">Resetear Clave</button>` : ''}
                            ${!isCurrentUser && (user.role === 'admin' || user.role === 'inst_admin') ? `<button onclick="deleteUserFromList(${u.id}, '${u.email}')" class="btn-ghost" style="font-size:0.7rem; color:#ef4444;">Eliminar</button>` : ''}
                        </div>
                    </div>`;
                }).join('');
            } catch(e) {
                container.innerHTML = '<div style="padding:20px; color:#ef4444;">Error al cargar usuarios.</div>';
            }
        }

        function openInviteModal() {
            document.getElementById('inviteModal').style.display = 'flex';
        }

        function closeInviteModal() {
            document.getElementById('inviteModal').style.display = 'none';
        }

        async function submitInviteUser() {
            const name = document.getElementById('inv_name').value.trim();
            const email = document.getElementById('inv_email').value.trim();
            const role = document.getElementById('inv_role').value;
            const password = document.getElementById('inv_password').value.trim();
            if (!email) { alert('El correo es obligatorio.'); return; }
            try {
                const resp = await fetch(`/api/users?inst_id=${getInstId()}&program_id=${getProgramId()}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, role, password })
                });
                const result = await resp.json();
                if (result.status === 'success') {
                    alert(`âœ… Usuario creado.\n\nEmail: ${email}\nContraseÃ±a temporal: ${result.temp_password}`);
                    closeInviteModal();
                    loadUsersFromAPI();
                } else {
                    alert('Error: ' + result.message);
                }
            } catch(e) {
                alert('Error de conexiÃ³n.');
            }
        }

        async function resetUserPass(userId, email) {
            if (!confirm(`Â¿Resetear contraseÃ±a de ${email}? Se asignarÃ¡ una temporal.`)) return;
            try {
                const resp = await fetch(`/api/users/${userId}/reset-password`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                const result = await resp.json();
                if (result.status === 'success') {
                    alert(`âœ… ContraseÃ±a reseteada.\n\nNueva contraseÃ±a temporal: ${result.temp_password}\n\nCompartirla de forma segura con el usuario.`);
                } else {
                    alert('Error: ' + result.message);
                }
            } catch(e) {
                alert('Error de conexiÃ³n.');
            }
        }

        async function deleteUserFromList(userId, email) {
            if (!confirm(`Â¿Eliminar al usuario ${email}? Esta acciÃ³n no se puede deshacer.`)) return;
            try {
                await fetch(`/api/users/${userId}`, { method: 'DELETE' });
                loadUsersFromAPI();
            } catch(e) {
                alert('Error al eliminar usuario.');
            }
        }

        async function activateUser(userId, email) {
            if (!confirm(`Â¿Activar usuario ${email} como LÃ­der de Factor? (PodrÃ¡s cambiar su rol despuÃ©s si es necesario)`)) return;
            try {
                const resp = await fetch(`/api/users/${userId}/activate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ role: 'lider' })
                });
                if (resp.ok) {
                    alert('Usuario activado con Ã©xito.');
                    loadUsersFromAPI();
                } else {
                    alert('Error activando usuario.');
                }
            } catch(e) {
                alert('Error de conexiÃ³n.');
            }
        }


        async function loadAllInstitutions() {
            if (user.role === 'admin') {
                document.getElementById('instSelectorCard').style.display = 'block';
                const resp = await fetch('/api/institutions');
                const list = await resp.json();
                const select = document.getElementById('instSelect');
                select.innerHTML = '';
                list.forEach(inst => {
                    const opt = document.createElement('option');
                    opt.value = inst.id;
                    opt.textContent = `${inst.name} (${inst.description || 'Sin programa'})`;
                    if (inst.id == getInstId()) opt.selected = true;
                    select.appendChild(opt);
                });
            }
        }

        function changeCurrentInst() {
            const newId = document.getElementById('instSelect').value;
            const userData = JSON.parse(localStorage.getItem('siac_user'));
            userData.inst_id = parseInt(newId);
            localStorage.setItem('siac_user', JSON.stringify(userData));
            location.reload();
        }

        async function addNewInstitution() {
            const name = prompt("Nombre de la nueva InstituciÃ³n:");
            if (!name) return;

            try {
                const uniqueCode = 'ORG-' + Date.now().toString(36);
                const resp = await fetch('/api/institutions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: name, program: 'General', period: uniqueCode })
                });
                const result = await resp.json();
                if (result.status === 'success') {
                    alert("InstituciÃ³n creada exitosamente.");
                    loadAllInstitutions();
                }
            } catch (err) {
                alert("Error al crear instituciÃ³n");
            }
        }

        async function loadAllPrograms() {
            if (user.role === 'inst_admin' || user.role === 'admin') {
                document.getElementById('progSelectorCard').style.display = 'block';
                const resp = await fetch(`/api/programs?inst_id=${getInstId()}`);
                const list = await resp.json();
                const select = document.getElementById('progSelect');
                select.innerHTML = '<option value="0">-- Seleccione un Programa --</option>';
                list.forEach(prog => {
                    const opt = document.createElement('option');
                    opt.value = prog.id;
                    opt.textContent = `${prog.name} (${prog.period})`;
                    if (prog.id == getProgramId()) {
                        opt.selected = true;
                        // Populate fields
                        document.getElementById('prog_name').value = prog.name || '';
                        document.getElementById('prog_period').value = prog.period || '';
                    }
                    select.appendChild(opt);
                });
            }
        }

        function changeCurrentProg() {
            const newId = document.getElementById('progSelect').value;
            if (newId === "0") {
                alert("Por favor seleccione un programa vÃ¡lido.");
                return;
            }
            const userData = JSON.parse(localStorage.getItem('siac_user'));
            userData.program_id = parseInt(newId);
            localStorage.setItem('siac_user', JSON.stringify(userData));
            // TRAZABILIDAD: Recargar modelo del servidor para este programa
            loadDataFromAPI().then(() => {
                renderModelEditor();
                renderFactorLeaders();
                updateContextBreadcrumb();
            });
            location.reload();
        }

        function prepareNewProgram() {
            document.getElementById('progSelect').value = '0';
            document.getElementById('prog_name').value = '';
            document.getElementById('prog_period').value = '';
            document.getElementById('prog_name').focus();
            
            const userData = JSON.parse(localStorage.getItem('siac_user'));
            userData.program_id = 0;
            localStorage.setItem('siac_user', JSON.stringify(userData));
            alert("Rellena los campos Nombre y Periodo abajo, y presiona 'Guardar Programa' para crearlo.");
        }

        async function saveProgram() {
            const name = document.getElementById('prog_name').value.trim();
            const period = document.getElementById('prog_period').value.trim();
            
            if (!name || !period) {
                alert("Debes llenar el Nombre del Programa y el Periodo."); return;
            }

            const currentProgId = getProgramId();
            
            if(!currentProgId || currentProgId == 0) {
                // Crear nuevo programa
                try {
                    const resp = await fetch(`/api/programs?inst_id=${getInstId()}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, period })
                    });
                    const result = await resp.json();
                    if (result.status === 'success') {
                        alert(`Programa '${name}' creado correctamente.`);
                        const userData = JSON.parse(localStorage.getItem('siac_user'));
                        userData.program_id = parseInt(result.data.id);
                        localStorage.setItem('siac_user', JSON.stringify(userData));
                        location.reload();
                    } else {
                        alert('Error al crear el programa.');
                    }
                } catch (err) {
                    alert("Error de conexiÃ³n.");
                }
            } else {
                // Actualizar programa existente
                try {
                    const resp = await fetch(`/api/programs/${currentProgId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: name, period: period })
                    });

                    if (resp.ok) {
                        alert('Programa guardado correctamente.');
                        loadAllPrograms();
                    } else {
                        alert('Error al guardar el programa.');
                    }
                } catch(e) {
                    alert("Error de conexiÃ³n");
                }
            }
        }

        async function deleteProgram() {
            const progId = getProgramId();
            if (!progId || progId == 0) { alert("Selecciona un programa vÃ¡lido."); return; }
            if (!confirm(`âš ï¸ Â¿EstÃ¡s seguro de eliminar este programa acadÃ©mico? Se borrarÃ¡n sus factores, evidencias y evaluaciones correspondientes. ESTA ACCIÃ“N ES IRREVERSIBLE.`)) return;
            
            try {
                const resp = await fetch(`/api/programs/${progId}`, { method: 'DELETE' });
                if (resp.ok) {
                    alert("Programa eliminado.");
                    const userData = JSON.parse(localStorage.getItem('siac_user'));
                    userData.program_id = 0;
                    localStorage.setItem('siac_user', JSON.stringify(userData));
                    location.reload();
                } else {
                    alert("Error al eliminar.");
                }
            } catch (e) {
                alert("Error de conexiÃ³n.");
            }
        }

        async function updatePassword() {

            const old_password = document.getElementById('old_password').value;
            const new_password = document.getElementById('new_password').value;
            if (!old_password || !new_password) {
                alert("Por favor complete ambos campos.");
                return;
            }
            try {
                const response = await fetch(`/api/change-password?inst_id=${getInstId()}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        email: user.email,
                        old_password: old_password,
                        new_password: new_password
                    })
                });
                const result = await response.json();
                if (result.status === 'success') {
                    alert("ContraseÃ±a actualizada correctamente.");
                    document.getElementById('old_password').value = '';
                    document.getElementById('new_password').value = '';
                } else {
                    alert("Error: " + result.message);
                }
            } catch (err) {
                console.error(err);
                alert("Error al actualizar contraseÃ±a.");
            }
        }

        async function deleteInstitution() {
            const sel = document.getElementById('instSelect');
            const instId = sel.value;
            if (!instId || instId == '0') { alert('Selecciona una instituciÃ³n vÃ¡lida.'); return; }
            const instName = sel.options[sel.selectedIndex].text;
            if (!confirm(`âš ï¸ Â¿EstÃ¡s seguro de ELIMINAR la instituciÃ³n "${instName}"?\n\nSe borrarÃ¡n TODOS sus programas, factores, evidencias, evaluaciones y usuarios asociados.\n\nESTA ACCIÃ“N ES IRREVERSIBLE.`)) return;

            try {
                const resp = await fetch(`/api/institutions/${instId}`, { method: 'DELETE' });
                if (resp.ok) {
                    alert('âœ… InstituciÃ³n eliminada correctamente.');
                    // Reset to first institution
                    const userData = JSON.parse(localStorage.getItem('siac_user'));
                    userData.inst_id = 1;
                    userData.program_id = 0;
                    localStorage.setItem('siac_user', JSON.stringify(userData));
                    location.reload();
                } else {
                    const data = await resp.json();
                    alert('Error: ' + (data.message || 'No se pudo eliminar.'));
                }
            } catch (e) {
                alert('Error de conexiÃ³n al eliminar la instituciÃ³n.');
            }
        }

        async function suspendInstitution() {
            const sel = document.getElementById('instSelect');
            const instId = sel.value;
            if (!instId || instId == '0') { alert('Selecciona una instituciÃ³n.'); return; }
            const instName = sel.options[sel.selectedIndex].text;
            if (!confirm(`Â¿Suspender la instituciÃ³n "${instName}"? Los usuarios no podrÃ¡n acceder.`)) return;

            try {
                const resp = await fetch(`/api/institutions/${instId}/suspend`, { method: 'POST' });
                if (resp.ok) {
                    alert('InstituciÃ³n suspendida.');
                    location.reload();
                } else {
                    alert('Error al suspender.');
                }
            } catch(e) {
                alert('Error de conexiÃ³n.');
            }
        }

        init();


