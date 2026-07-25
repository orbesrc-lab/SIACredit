
        document.addEventListener("DOMContentLoaded", () => {
            const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
            document.getElementById('userInfo').textContent = user.email || 'Usuario';
            if(user.role === 'admin') {
                const crmLink = document.getElementById('menuCrm');
                if(crmLink) crmLink.style.display = 'block';
            }
            
            // Iniciar carga
            loadPlanningData();
        });

        // Toggle acordeones
        function toggleBody(btn) {
            const container = btn.closest('.node-content');
            if(!container) return;
            const body = container.querySelector('.node-body');
            const icon = btn.querySelector('.toggle-icon');
            if(!body) return;
            
            if(body.style.display === 'block') {
                body.style.display = 'none';
                if(icon) icon.className = 'fas fa-chevron-down toggle-icon';
            } else {
                body.style.display = 'block';
                if(icon) icon.className = 'fas fa-chevron-up toggle-icon';
            }
        }

        function getWeightBadge(items, max = 100) {
            if(!items) return '';
            const total = items.reduce((sum, item) => sum + parseFloat(item.weight_percentage || 0), 0);
            const isError = total !== max;
            return `<span class="badge badge-weight ${isError ? 'error' : ''}" title="Suma de pesos de los hijos">
                <i class="${isError ? 'fas fa-exclamation-circle' : 'fas fa-check-circle'}"></i> 
                Pesos Hijos: ${total}%
            </span>`;
        }

        let ganttChart = null;

        function openGantt() {
            const activities = [];
            // Recorrer todo el árbol para extraer actividades
            planningData.forEach(axis => {
                (axis.strategies || []).forEach(st => {
                    (st.general_objectives || []).forEach(go => {
                        (go.specific_objectives || []).forEach(so => {
                            (so.activities || []).forEach(act => {
                                // Default dates if none
                                let start = act.start_date ? act.start_date.substring(0, 10) : new Date().toISOString().substring(0, 10);
                                let end = act.end_date ? act.end_date.substring(0, 10) : new Date(Date.now() + 86400000).toISOString().substring(0, 10);
                                
                                // Frappe Gantt requires specific format
                                activities.push({
                                    id: 'act_' + act.id,
                                    name: act.description,
                                    start: start,
                                    end: end,
                                    progress: act.status === 'Completada' ? 100 : (act.status === 'En Proceso' ? 50 : 0),
                                    custom_class: act.status === 'Completada' ? 'gantt-green' : 'gantt-blue'
                                });
                            });
                        });
                    });
                });
            });

            if(activities.length === 0) {
                alert('No hay actividades para mostrar en el cronograma.');
                return;
            }

            document.getElementById('ganttModal').style.display = 'flex';
            
            // Clear previous
            document.getElementById('gantt').innerHTML = '';
            
            ganttChart = new Gantt("#gantt", activities, {
                on_date_change: async function(task, start, end) {
                    const dbId = task.id.replace('act_', '');
                    const s = start.toISOString().substring(0,10);
                    const e = end.toISOString().substring(0,10);
                    
                    try {
                        await fetch('/api/planning/node/edit', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                type: 'activity',
                                id: parseInt(dbId),
                                start_date: s,
                                end_date: e
                            })
                        });
                        // Recargar datos en background
                        loadPlanningData();
                    } catch(err) {
                        console.error('Error updating gantt date', err);
                    }
                },
                language: 'es'
            });
            ganttChart.change_view_mode('Week');
        }

        async function loadPlanningData() {
            try {
                const res = await fetch(`/api/planning/tree?inst_id=${getInstId()}`);
                const data = await res.json();
                if(data.status === 'success') {
                    renderTree(data.tree);
                } else {
                    document.getElementById('planningTree').innerHTML = `<p style="color:red">Error: ${data.message}</p>`;
                }
            } catch(e) {
                document.getElementById('planningTree').innerHTML = `<p style="color:red">Error de red: ${e}</p>`;
            }
        }

        function renderTree(tree) {
            const container = document.getElementById('planningTree');
            if(!tree || tree.length === 0) {
                container.innerHTML = `<div style="text-align: center; padding: 40px; color: #64748b;">
                    <i class="fas fa-seedling fa-3x" style="color: #cbd5e1; margin-bottom:15px;"></i>
                    <p>No hay Ejes Estratégicos. Por favor ve al módulo DOFA y guarda la matriz para generar las estrategias base.</p>
                </div>`;
                return;
            }

            let html = '';
            tree.forEach(axis => {
                html += `
                <div class="node-wrapper lvl-axis">
                    
                    <div class="node-content">
                        <div class="node-header" onclick="toggleBody(this)">
                            <div>
                                <span style="color:#64748b; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; display:block; margin-bottom:4px;">Eje Estratégico</span>
                                ${axis.name}
                            </div>
                            <i class="fas fa-chevron-down toggle-icon" style="color:#94a3b8;"></i>
                        </div>
                        
                          <div class="node-body" style="display:block;">
                              <div style="display:flex; gap:10px; margin-bottom:15px; flex-wrap:wrap;">
                                  <button class="btn-toolbar" onclick="editNode('axis', ${axis.id}, {'name': \`${axis.name.replace(/`/g, '')}\`, 'description': \`${(axis.description||'').replace(/`/g, '')}\`}, event)"><i class="fas fa-pencil-alt"></i> Editar Eje</button>
                                  <button class="btn-toolbar delete" onclick="deleteNode('axis', ${axis.id}, event)"><i class="fas fa-trash"></i> Eliminar Eje</button>
                                  <button class="btn-toolbar" onclick="addNode('strategy', ${axis.id})"><i class="fas fa-plus"></i> Añadir Estrategia</button>
                              </div>

                            <p style="font-size:0.9rem; color:#64748b; margin-top:0; margin-bottom:20px;">${axis.description || 'Sin descripción'}</p>
                            ${renderStrategies(axis.strategies, axis.id)}
                        </div>
                    </div>
                </div>`;
            });
            container.innerHTML = html;
        }

        function renderStrategies(strats, axisId) {
            let html = '<div class="children-list">';
            if(strats && strats.length > 0) {
                strats.forEach(st => {
                    const wBadge = getWeightBadge(st.general_objectives, 100);
                    html += `
                    <div class="node-wrapper lvl-strat">
                        
                        <div class="node-content">
                            <div class="node-header" onclick="toggleBody(this)">
                                <div style="flex-grow:1; padding-right:15px;">
                                    <span class="badge" style="background:#e0f2fe; color:#0284c7; margin-bottom:5px;">${st.quadrant || 'MANUAL'}</span>
                                    <div style="font-weight:600; line-height:1.4;">${st.description}</div>
                                </div>
                                <div style="display:flex; align-items:center; gap:10px; flex-shrink:0;">
                                    <span class="badge badge-weight">Peso: ${st.weight_percentage}%</span>
                                    ${wBadge}
                                    
                                    <i class="fas fa-chevron-down toggle-icon" style="color:#cbd5e1; margin-left:10px;"></i>
                                </div>
                            </div>
                            
                            <div class="node-body">
                                <div style="display:flex; gap:10px; margin-bottom:15px; flex-wrap:wrap;">
                                    <button class="btn-toolbar" onclick="editNode('strategy', ${st.id}, {'description': \`${st.description.replace(/`/g, '')}\`, 'weight_percentage': ${st.weight_percentage||0}}, event)"><i class="fas fa-pencil-alt"></i> Editar Estrategia</button>
                                    <button class="btn-toolbar delete" onclick="deleteNode('strategy', ${st.id}, event)"><i class="fas fa-trash"></i> Eliminar Estrategia</button>
                                    <button class="btn-toolbar" onclick="addNode('gen_obj', ${st.id})"><i class="fas fa-plus"></i> Añadir Obj. General</button>
                                </div>
                                ${renderGenObjs(st.general_objectives, st.id)}
                            </div>
                        </div>
                    </div>`;
                });
            } else {
                html += `<p style="font-size:0.85rem; color:#94a3b8; ">No hay estrategias definidas.</p>`;
            }
            html += `
                <div style=" margin-top:10px;">
                    <button class="btn-add" onclick="addNode('strategy', ${axisId})"><i class="fas fa-plus"></i> Añadir Estrategia</button>
                </div>
            </div>`;
            return html;
        }

        function renderGenObjs(gens, stratId) {
            let html = '<div class="children-list">';
            if(gens && gens.length > 0) {
                gens.forEach(g => {
                    const wBadge = getWeightBadge(g.specific_objectives, 100);
                    // Validar cantidad (2 a 4)
                    let countErr = (g.specific_objectives && (g.specific_objectives.length < 2 || g.specific_objectives.length > 4));
                    let countWarning = countErr ? `<span class="badge badge-weight error" style="margin-left:5px;"><i class="fas fa-exclamation-triangle"></i> Requisito: 2 a 4 Obj. Específicos</span>` : '';
                    
                    html += `
                    <div class="node-wrapper lvl-gen">
                        
                        <div class="node-content">
                            <div class="node-header" onclick="toggleBody(this)">
                                <div style="flex-grow:1; padding-right:15px;">
                                    <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; display:block; margin-bottom:4px;">Objetivo General</span>
                                    <div style="font-weight:600; line-height:1.4;">${g.description}</div>
                                </div>
                                <div style="display:flex; align-items:center; gap:10px; flex-shrink:0;">
                                    ${wBadge}
                                    
                                    <i class="fas fa-chevron-down toggle-icon" style="color:#cbd5e1; margin-left:10px;"></i>
                                </div>
                            </div>
                            
                            <div class="node-body">
                                <div style="display:flex; gap:10px; margin-bottom:15px; flex-wrap:wrap;">
                                    <button class="btn-toolbar" onclick="editNode('gen_obj', ${g.id}, {'description': \`${g.description.replace(/`/g, '')}\`}, event)"><i class="fas fa-pencil-alt"></i> Editar Objetivo</button>
                                    <button class="btn-toolbar delete" onclick="deleteNode('gen_obj', ${g.id}, event)"><i class="fas fa-trash"></i> Eliminar Objetivo</button>
                                    <button class="btn-toolbar" onclick="addNode('spec_obj', ${g.id})"><i class="fas fa-plus"></i> Añadir Obj. Específico</button>
                                </div>
                                ${countWarning ? `<div style="margin-bottom:15px;">${countWarning}</div>` : ''}
                                ${renderSpecObjs(g.specific_objectives, g.id)}
                            </div>
                        </div>
                    </div>`;
                });
            } else {
                html += `<p style="font-size:0.85rem; color:#94a3b8; ">Sin objetivos generales.</p>`;
            }
            html += `
                <div style=" margin-top:10px; display:flex; gap:10px;">
                    <button class="btn-add" onclick="addNode('gen_obj', ${stratId})"><i class="fas fa-plus"></i> Obj. General Manual</button>
                    <button class="btn-add btn-ai" onclick="suggestGenObjAI(${stratId})"><i class="fas fa-robot"></i> Sugerir IA</button>
                </div>
            </div>`;
            return html;
        }

        function renderSpecObjs(specs, genId) {
            let html = '<div class="children-list">';
            if(specs && specs.length > 0) {
                specs.forEach(s => {
                    // Validar cantidad (2 a 5)
                    let acts = s.activities || [];
                    let countErr = (acts.length < 2 || acts.length > 5);
                    let countWarning = countErr ? `<span class="badge badge-weight error" style="margin-left:5px;"><i class="fas fa-exclamation-triangle"></i> Requisito: 2 a 5 Actividades</span>` : '';

                    html += `
                    <div class="node-wrapper lvl-spec">
                        
                        <div class="node-content">
                            <div class="node-header" onclick="toggleBody(this)">
                                <div style="flex-grow:1; padding-right:15px;">
                                    <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; display:block; margin-bottom:4px;">Objetivo Específico</span>
                                    <div style="font-weight:600; line-height:1.4;">${s.description}</div>
                                </div>
                                <div style="display:flex; align-items:center; gap:10px; flex-shrink:0;">
                                    <span class="badge badge-weight">Peso: ${s.weight_percentage}%</span>
                                    
                                    <i class="fas fa-chevron-down toggle-icon" style="color:#cbd5e1; margin-left:10px;"></i>
                                </div>
                            </div>
                            <div class="node-body">
                                <div style="background:#f8fafc; padding:10px 15px; border-radius:6px; margin-bottom:15px; font-size:0.85rem; color:#475569;">
                                    <i class="fas fa-chart-line" style="margin-right:5px; color:#f59e0b;"></i> <strong>Indicador:</strong> ${s.indicator_type || 'N/A'} - ${s.indicator_description || ''}
                                </div>
                                ${countWarning ? `<div style="margin-bottom:15px;">${countWarning}</div>` : ''}
                                ${renderActivities(s.activities, s.id)}
                            </div>
                        </div>
                    </div>`;
                });
            } else {
                html += `<p style="font-size:0.85rem; color:#94a3b8; ">Sin objetivos específicos.</p>`;
            }
            html += `
                <div style=" margin-top:10px; display:flex; gap:10px;">
                    <button class="btn-add" onclick="addNode('spec_obj', ${genId})"><i class="fas fa-plus"></i> Obj. Específico Manual</button>
                    <button class="btn-add btn-ai" onclick="suggestSpecObjAI(${genId})"><i class="fas fa-robot"></i> Sugerir IA</button>
                </div>
            </div>`;
            return html;
        }

        function renderActivities(acts, specId) {
            let html = '<div class="children-list">';
            if(acts && acts.length > 0) {
                acts.forEach(a => {
                    let badgeClass = 'badge-pending';
                    if(a.status === 'En Progreso') badgeClass = 'badge-progress';
                    if(a.status === 'Completado') badgeClass = 'badge-done';
                    
                    html += `
                    <div class="node-wrapper lvl-act">
                        
                        <div class="node-content">
                            <div class="node-header" style="cursor:default;">
                                <div style="flex-grow:1;">
                                    <div style="font-weight:600; line-height:1.4; color:#334155;">${a.description}</div>
                                    <div class="activity-meta" style="margin-top:10px;">
                                        <span title="Responsable"><i class="fas fa-user"></i> ${a.responsible || 'Sin responsable'}</span>
                                        <span title="Fechas"><i class="far fa-calendar"></i> ${a.start_date || 'N/A'} a ${a.end_date || 'N/A'}</span>
                                        <span title="Presupuesto Financiero (Incluye carga prestacional)"><i class="fas fa-money-bill-wave"></i> $${(a.financial_budget || 0).toLocaleString('es-CO')}</span>
                                    </div>
                                </div>
                                <div style="flex-shrink:0; margin-left:15px;">
                                    
                                      <span class="badge ${badgeClass}">${a.status || 'Pendiente'}</span>
                                  </div>
                                  <div style="margin-top:10px; display:flex; gap:10px; flex-wrap:wrap;">
                                      <button class="btn-toolbar" onclick="editNode('activity', ${a.id}, {'description': \`${a.description.replace(/`/g, '')}\`, 'start_date': \`${(a.start_date||'').substring(0,10)}\`, 'end_date': \`${(a.end_date||'').substring(0,10)}\`, 'financial_budget': ${a.financial_budget||0}, 'responsible': \`${(a.responsible||'').replace(/`/g, '')}\`}, event)"><i class="fas fa-pencil-alt"></i> Editar Actividad</button>
                                      <button class="btn-toolbar delete" onclick="deleteNode('activity', ${a.id}, event)"><i class="fas fa-trash"></i> Eliminar</button>
                                  </div>

                            </div>
                        </div>
                    </div>`;
                });
            } else {
                html += `<p style="font-size:0.85rem; color:#94a3b8; ">Sin actividades.</p>`;
            }
            html += `
                <div style=" margin-top:10px; display:flex; gap:10px;">
                    <button class="btn-add" onclick="addNode('activity', ${specId})"><i class="fas fa-plus"></i> Actividad Manual</button>
                    <button class="btn-add btn-ai" onclick="suggestActivitiesAI(${specId})"><i class="fas fa-robot"></i> Sugerir IA</button>
                </div>
            </div>`;
            return html;
        }

        let currentNodeType = '';
        let currentParentId = 0;

        
        function editNode(type, id, data, event) {
            if(event) event.stopPropagation();
            document.getElementById('nodeForm').reset();
            document.getElementById('nodeType').value = type;
            document.getElementById('parentId').value = '';
            document.getElementById('nodeId').value = id;
            document.getElementById('modalTitle').textContent = 'Editar Elemento';
            
            const body = document.getElementById('modalBody');
            if(type === 'axis') {
                body.innerHTML = `
                    <div class="form-group"><label>Nombre del Eje</label><input type="text" id="f_name" value="${data.name || ''}"></div>
                    <div class="form-group"><label>Descripción</label><textarea id="f_desc" rows="3">${data.description || ''}</textarea></div>
                `;
            } else if(type === 'strategy') {
                body.innerHTML = `
                    <div class="form-group"><label>Descripción</label><textarea id="f_desc" rows="3">${data.description || ''}</textarea></div>
                    <div class="form-group"><label>Peso (%)</label><input type="number" id="f_weight" value="${data.weight_percentage || 0}" min="0" max="100"></div>
                `;
            } else if(type === 'gen_obj') {
                body.innerHTML = `
                    <div class="form-group"><label>Descripción</label><textarea id="f_desc" rows="3">${data.description || ''}</textarea></div>
                `;
            } else if(type === 'spec_obj') {
                body.innerHTML = `
                    <div class="form-group"><label>Descripción</label><textarea id="f_desc" rows="3">${data.description || ''}</textarea></div>
                    <div class="form-group"><label>Peso (%)</label><input type="number" id="f_weight" value="${data.weight_percentage || 0}" min="0" max="100"></div>
                    <div class="form-group"><label>Tipo de Indicador</label><input type="text" id="f_ind_type" value="${data.indicator_type || ''}"></div>
                    <div class="form-group"><label>Descripción del Indicador</label><input type="text" id="f_ind_desc" value="${data.indicator_description || ''}"></div>
                `;
            } else if(type === 'activity') {
                body.innerHTML = `
                    <div class="form-group"><label>Descripción</label><textarea id="f_desc" rows="3">${data.description || ''}</textarea></div>
                    <div style="display:flex; gap:10px;">
                        <div class="form-group" style="flex:1;"><label>Fecha Inicio</label><input type="date" id="f_start" value="${data.start_date || ''}"></div>
                        <div class="form-group" style="flex:1;"><label>Fecha Fin</label><input type="date" id="f_end" value="${data.end_date || ''}"></div>
                    </div>
                    <div class="form-group"><label>Presupuesto Financiero ($)</label><input type="number" id="f_budget" value="${data.financial_budget || 0}"></div>
                    <div class="form-group"><label>Responsable</label><input type="text" id="f_resp" value="${data.responsible || ''}"></div>
                `;
            }
            document.getElementById('nodeModal').style.display = 'flex';
        }

        function addNode(type, parentId) {
            currentNodeType = type;
            currentParentId = parentId;
            const modal = document.getElementById('nodeModal');
            const title = document.getElementById('modalTitle');
            const body = document.getElementById('modalBody');
            
            if(type === 'strategy') {
                title.textContent = 'Nueva Estrategia';
                body.innerHTML = `
                    <div class="form-group"><label>Descripción</label><textarea id="f_desc" rows="3"></textarea></div>
                    <div class="form-group"><label>Peso (%)</label><input type="number" id="f_weight" value="0" min="0" max="100"></div>
                `;
            } else if(type === 'gen_obj') {
                title.textContent = 'Nuevo Objetivo General';
                body.innerHTML = `
                    <div class="form-group"><label>Descripción</label><textarea id="f_desc" rows="3"></textarea></div>
                    <div class="form-group"><label>Alineación (PDI)</label><input type="text" id="f_align" placeholder="Opcional"></div>
                `;
            } else if(type === 'spec_obj') {
                title.textContent = 'Nuevo Objetivo Específico';
                body.innerHTML = `
                    <div class="form-group"><label>Descripción</label><textarea id="f_desc" rows="3"></textarea></div>
                    <div class="form-group"><label>Peso (%)</label><input type="number" id="f_weight" value="0" min="0" max="100"></div>
                    <div class="form-group"><label>Tipo de Indicador</label><input type="text" id="f_ind_type" placeholder="Ej: Porcentaje, Número..."></div>
                    <div class="form-group"><label>Descripción del Indicador</label><input type="text" id="f_ind_desc"></div>
                `;
            } else if(type === 'activity') {
                title.textContent = 'Nueva Actividad';
                body.innerHTML = `
                    <div class="form-group"><label>Descripción</label><textarea id="f_desc" rows="3"></textarea></div>
                    <div style="display:flex; gap:10px;">
                        <div class="form-group" style="flex:1;"><label>Fecha Inicio</label><input type="date" id="f_start"></div>
                        <div class="form-group" style="flex:1;"><label>Fecha Fin</label><input type="date" id="f_end"></div>
                    </div>
                    <div class="form-group"><label>Meta Numérica / Entregable</label><input type="text" id="f_goal"></div>
                    <div class="form-group"><label>Responsable</label><input type="text" id="f_resp"></div>
                    <div class="form-group"><label>Presupuesto (Valor Hora Base)</label><input type="number" id="f_budget" placeholder="Si aplica (el sistema calculará +1.54)"></div>
                `;
            }

            modal.style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('nodeModal').style.display = 'none';
        }

        async function saveNode() {
            const btn = document.getElementById('btnSaveNode');
            btn.textContent = 'Guardando...';
            btn.disabled = true;

            const payload = {
                inst_id: getInstId(),
                type: currentNodeType,
                parent_id: currentParentId,
                description: document.getElementById('f_desc') ? document.getElementById('f_desc').value : ''
            };

            
            if(currentNodeType === 'axis') {
                payload.name = document.getElementById('f_name').value || '';
            } else if(currentNodeType === 'strategy') {
                payload.weight_percentage = document.getElementById('f_weight').value || 0;
                payload.quadrant = 'MANUAL';
            } else if(currentNodeType === 'gen_obj') {
                payload.alignment_pdi = document.getElementById('f_align').value || '';
            } else if(currentNodeType === 'spec_obj') {
                payload.weight_percentage = document.getElementById('f_weight').value || 0;
                payload.indicator_type = document.getElementById('f_ind_type').value || '';
                payload.indicator_description = document.getElementById('f_ind_desc').value || '';
            } else if(currentNodeType === 'activity') {
                payload.start_date = document.getElementById('f_start').value || null;
                payload.end_date = document.getElementById('f_end').value || null;
                payload.goal = document.getElementById('f_goal').value || '';
                payload.responsible = document.getElementById('f_resp').value || '';
                let budget = parseFloat(document.getElementById('f_budget').value || 0);
                payload.financial_budget = budget * 1.54; // Carga prestacional
            }

            try {
                
            if (nodeId) payload.id = nodeId;
            
            const res = await fetch('/api/planning/node', {
                    method: nodeId ? 'PUT' : 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if(data.status === 'success') {
                    closeModal();
                    loadPlanningData();
                } else {
                    alert('Error: ' + data.message);
                }
            } catch(e) {
                alert('Error de conexión');
            }
            
            btn.textContent = 'Guardar';
            btn.disabled = false;
        }

        async function deleteNode(type, id, event) {
            if(event) event.stopPropagation(); // Evitar que se abra el acordeón
            if(!confirm('¿Estás seguro de que deseas eliminar este elemento? Todos los elementos hijos también se eliminarán de forma irreversible.')) return;

            try {
                
            if (nodeId) payload.id = nodeId;
            
            const res = await fetch('/api/planning/node', {
                    method: 'DELETE',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ type: type, id: id })
                });
                const data = await res.json();
                if(data.status === 'success') {
                    loadPlanningData();
                } else {
                    alert('Error al eliminar: ' + data.message);
                }
            } catch(e) {
                alert('Error de conexión al intentar eliminar');
            }
        }

        async function suggestGenObjAI(strategyId) {
            try {
                // Pre-open the modal so the user sees it loading
                addNode('gen_obj', strategyId);
                const descField = document.getElementById('f_desc');
                descField.value = 'Generando sugerencia con Inteligencia Artificial...';
                descField.disabled = true;
                
                const res = await fetch('/api/planning/suggest', {
                    method: nodeId ? 'PUT' : 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ type: 'gen_obj', target_id: strategyId, inst_id: getInstId() })
                });
                const data = await res.json();
                
                descField.disabled = false;
                if(data.status === 'success') {
                    descField.value = data.suggestion;
                } else {
                    descField.value = 'Error al sugerir: ' + data.message;
                }
            } catch(e) {
                document.getElementById('f_desc').disabled = false;
                document.getElementById('f_desc').value = 'Error de red al conectar con IA.';
            }
        }

        async function suggestActivitiesAI(specId) {
            try {
                // We pre-open the modal but wait... suggestActivitiesAI might suggest multiple activities!
                // For now, let's suggest ONE activity to fit in the modal, or a block of text
                addNode('activity', specId);
                const descField = document.getElementById('f_desc');
                descField.value = 'Generando actividad con Inteligencia Artificial...';
                descField.disabled = true;

                const res = await fetch('/api/planning/suggest', {
                    method: nodeId ? 'PUT' : 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ type: 'activity', target_id: specId, inst_id: getInstId() })
                });
                const data = await res.json();
                
                descField.disabled = false;
                if(data.status === 'success') {
                    descField.value = data.suggestion;
                    // Optional: parse if AI returns dates, but text is fine for description
                } else {
                    descField.value = 'Error al sugerir: ' + data.message;
                }
            } catch(e) {
                document.getElementById('f_desc').disabled = false;
                document.getElementById('f_desc').value = 'Error de red al conectar con IA.';
            }
        }

        async function suggestSpecObjAI(genId) {
            try {
                addNode('spec_obj', genId);
                const descField = document.getElementById('f_desc');
                descField.value = 'Generando sugerencia con Inteligencia Artificial...';
                descField.disabled = true;
                
                const res = await fetch('/api/planning/suggest', {
                    method: nodeId ? 'PUT' : 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ type: 'spec_obj', target_id: genId, inst_id: getInstId() })
                });
                const data = await res.json();
                
                descField.disabled = false;
                if(data.status === 'success') {
                    descField.value = data.suggestion;
                } else {
                    descField.value = 'Error al sugerir: ' + data.message;
                }
            } catch(e) {
                document.getElementById('f_desc').disabled = false;
                document.getElementById('f_desc').value = 'Error de red al conectar con IA.';
            }
        }
    