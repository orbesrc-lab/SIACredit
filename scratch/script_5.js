
    let currentWizStep = 1;
    let aiDraftCourse = null;
    let createdAiCourseId = null;

    function openAICourseWizard() {
        document.getElementById('aiWizardModal').style.display = 'flex';
        currentWizStep = 1;
        updateWizUI();
        document.getElementById('aiProgressState').style.display = 'block';
        document.getElementById('aiCompleteState').style.display = 'none';
        document.getElementById('aiProgressBar').style.width = '0%';
        document.getElementById('aiProgressLog').innerHTML = '';
        
        // Reset form
        document.getElementById('aiCourseName').value = '';
        document.getElementById('aiCourseDesc').value = '';
        document.getElementById('aiGeneralComp').value = '';
        document.getElementById('aiSpecificCompsList').innerHTML = `
            <div style="display:flex; gap:10px;">
                <input type="text" class="ai-specific-comp-input" style="flex:1; padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1;" placeholder="Ej: Diseñar embudos de conversión efectivos.">
                <button class="btn-ghost" onclick="this.parentElement.remove()" style="color: #ef4444; border: 1px solid #fca5a5; padding: 0 12px; border-radius: 8px;"><i class="fas fa-trash"></i></button>
            </div>
        `;
    }

    function closeAICourseWizard(refresh = false) {
        document.getElementById('aiWizardModal').style.display = 'none';
    }

    function updateWizUI() {
        for(let i=1; i<=4; i++){
            document.getElementById(`wizardContent${i}`).style.display = (i === currentWizStep) ? 'block' : 'none';
            const stepDiv = document.getElementById(`wizStep${i}`);
            const circle = stepDiv.querySelector('.wizard-step-circle');
            if(i < currentWizStep) {
                circle.style.background = '#10b981';
                circle.innerHTML = '<i class="fas fa-check"></i>';
            } else if (i === currentWizStep) {
                circle.style.background = '#3b82f6';
                circle.innerHTML = i;
            } else {
                circle.style.background = '#334155';
                circle.innerHTML = i;
            }
        }
        
        document.getElementById('wizBtnPrev').style.display = (currentWizStep > 1 && currentWizStep < 4) ? 'block' : 'none';
        document.getElementById('wizBtnNext').style.display = (currentWizStep < 3) ? 'block' : 'none';
        document.getElementById('wizBtnGenerate').style.display = (currentWizStep === 3) ? 'block' : 'none';
        
        if(currentWizStep === 4) {
            document.getElementById('wizardFooter').style.display = 'none';
        } else {
            document.getElementById('wizardFooter').style.display = 'flex';
        }
    }

    function wizNextStep() {
        if(currentWizStep === 1) {
            if(!document.getElementById('aiCourseName').value || !document.getElementById('aiCourseDesc').value) {
                alert("Por favor completa los campos obligatorios."); return;
            }
        }
        if(currentWizStep === 2) {
            if(!document.getElementById('aiGeneralComp').value) {
                alert("Por favor ingresa la competencia general."); return;
            }
        }
        if(currentWizStep < 3) {
            currentWizStep++;
            updateWizUI();
        }
    }

    function wizPrevStep() {
        if(currentWizStep > 1) {
            currentWizStep--;
            updateWizUI();
        }
    }

    function toggleAiUnitsView() {
        const val = document.querySelector('input[name="aiUnitsDecision"]:checked').value;
        document.getElementById('aiUnitsAutoView').style.display = val === 'auto' ? 'block' : 'none';
        document.getElementById('aiUnitsManualView').style.display = val === 'manual' ? 'block' : 'none';
    }

    function addAiSpecificComp() {
        const div = document.createElement('div');
        div.style = "display:flex; gap:10px;";
        div.innerHTML = `
            <input type="text" class="ai-specific-comp-input" style="flex:1; padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1;" placeholder="Siguiente competencia...">
            <button class="btn-ghost" onclick="this.parentElement.remove()" style="color: #ef4444; border: 1px solid #fca5a5; padding: 0 12px; border-radius: 8px;"><i class="fas fa-trash"></i></button>
        `;
        document.getElementById('aiSpecificCompsList').appendChild(div);
    }

    function addAiManualUnit() {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="padding: 8px 0;"><input type="text" class="ai-unit-name" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;" placeholder="Ej: Siguiente Unidad"></td>
            <td style="padding: 8px 5px;"><input type="number" class="ai-unit-hours" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;" placeholder="10"></td>
            <td style="padding: 8px 0; text-align:center;"><button class="btn-ghost" onclick="this.parentElement.parentElement.remove()" style="color:#ef4444;"><i class="fas fa-times"></i></button></td>
        `;
        document.getElementById('aiManualUnitsTable').appendChild(tr);
    }
    
    function logAiProgress(msg) {
        const logContainer = document.getElementById('aiProgressLog');
        const div = document.createElement('div');
        div.style.marginBottom = '5px';
        div.innerHTML = `<span style="color:#8b5cf6;">[${new Date().toLocaleTimeString()}]</span> ${msg}`;
        logContainer.appendChild(div);
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    async function startAiGeneration() {
        currentWizStep = 4;
        updateWizUI();
        
        const courseData = {
            name: document.getElementById('aiCourseName').value,
            description: document.getElementById('aiCourseDesc').value,
            duration: document.getElementById('aiCourseHours').value + " horas",
            level: document.getElementById('aiCourseLevel').value,
            modality: document.getElementById('aiCourseModality').value,
            type: document.getElementById('aiCourseType').value,
            general_competence: document.getElementById('aiGeneralComp').value,
            specific_competencies: Array.from(document.querySelectorAll('.ai-specific-comp-input')).map(i => i.value).filter(v => v)
        };
        
        const isAutoUnits = document.querySelector('input[name="aiUnitsDecision"]:checked').value === 'auto';
        let units = [];
        
        try {
            document.getElementById('aiProgressBar').style.width = '10%';
            logAiProgress("Iniciando creación de borrador...");
            
            // Si es auto, llamar a la IA para estructura
            if(isAutoUnits) {
                logAiProgress("🤖 Solicitando a la IA la estructura de unidades...");
                document.getElementById('aiProgressSubtitle').innerText = "Generando estructura temática...";
                
                const structResp = await fetch('/api/ai/course/structure', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(courseData)
                });
                const structRes = await structResp.json();
                if(structRes.status === 'error') throw new Error(structRes.message);
                
                units = structRes.data.units;
                logAiProgress(`✔ Estructura recibida: ${units.length} unidades generadas.`);
            } else {
                const names = document.querySelectorAll('.ai-unit-name');
                const hours = document.querySelectorAll('.ai-unit-hours');
                for(let i=0; i<names.length; i++){
                    if(names[i].value) {
                        units.push({
                            name: names[i].value,
                            hours: hours[i].value || 10
                        });
                    }
                }
                logAiProgress(`✔ Estructura manual cargada: ${units.length} unidades.`);
            }
            
            document.getElementById('aiProgressBar').style.width = '25%';
            
            // Loop a través de las unidades para generar su contenido
            for(let i=0; i<units.length; i++) {
                const u = units[i];
                const pctBase = 25 + ((i / units.length) * 65);
                document.getElementById('aiProgressBar').style.width = pctBase + '%';
                
                document.getElementById('aiProgressSubtitle').innerText = `Generando Contenidos: ${u.name}`;
                logAiProgress(`🤖 Generando contenido académico para: ${u.name}...`);
                
                // Contenido
                const contResp = await fetch('/api/ai/course/unit_content', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ course_name: courseData.name, unit_info: u })
                });
                const contRes = await contResp.json();
                u.description = contRes.data.html_content;
                logAiProgress(`✔ Contenido académico generado.`);
                
                // Actividades
                document.getElementById('aiProgressBar').style.width = (pctBase + 5) + '%';
                logAiProgress(`🤖 Diseñando actividades para: ${u.name}...`);
                const actResp = await fetch('/api/ai/course/unit_activities', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ course_name: courseData.name, unit_info: u })
                });
                const actRes = await actResp.json();
                u.activities = actRes.data.activities || [];
                
                // Evaluaciones
                document.getElementById('aiProgressBar').style.width = (pctBase + 10) + '%';
                logAiProgress(`🤖 Diseñando evaluaciones para: ${u.name}...`);
                const evalResp = await fetch('/api/ai/course/unit_evaluations', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ course_name: courseData.name, unit_info: u })
                });
                const evalRes = await evalResp.json();
                u.evaluations = evalRes.data.evaluations || [];
                
                // Recursos
                logAiProgress(`🤖 Buscando recursos recomendados para: ${u.name}...`);
                const recResp = await fetch('/api/ai/course/unit_resources', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ course_name: courseData.name, unit_info: u })
                });
                const recRes = await recResp.json();
                u.resources = recRes.data.resources || [];
                
                // Format topics and IDs
                u.id = 'u_' + Math.random().toString(36).substr(2, 9);
                if(u.activities) u.activities.forEach(a => a.id = 'act_' + Math.random().toString(36).substr(2, 9));
                if(u.evaluations) u.evaluations.forEach(e => e.id = 'eval_' + Math.random().toString(36).substr(2, 9));
                
                logAiProgress(`✔ Unidad ${i+1} completada.`);
            }
            
            document.getElementById('aiProgressBar').style.width = '95%';
            document.getElementById('aiProgressSubtitle').innerText = "Guardando curso en repositorio...";
            logAiProgress("Guardando datos en la base de datos...");
            
            // Guardar en la base de datos local
            const finalCourse = {
                title: courseData.name,
                description: courseData.description,
                duration: courseData.duration,
                category: courseData.type,
                level: courseData.level,
                competencies: [courseData.general_competence, ...courseData.specific_competencies],
                outcomes: [],
                meetings: [],
                units: units,
                teacher_name: "Generado por IA"
            };
            
            const saveResp = await fetch(`/api/courses?inst_id=${getInstId()}&program_id=0`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(finalCourse)
            });
            const saveRes = await saveResp.json();
            
            document.getElementById('aiProgressBar').style.width = '100%';
            logAiProgress("✨ ¡Proceso Finalizado!");
            
            setTimeout(() => {
                document.getElementById('aiProgressState').style.display = 'none';
                document.getElementById('aiCompleteState').style.display = 'block';
                createdAiCourseId = saveRes.data.id;
            }, 1000);
            
        } catch (error) {
            console.error(error);
            logAiProgress(`❌ ERROR: ${error.message}`);
            document.getElementById('aiProgressSubtitle').innerText = "Ocurrió un error en la generación.";
            document.getElementById('aiProgressBar').style.background = '#ef4444';
        }
    async function improveWithAi(action) {
        const editorBox = document.getElementById('richTextEditorBox');
        let content = editorBox.innerHTML;
        
        // If there's a selection, we could theoretically just improve the selection, 
        // but for simplicity let's improve the whole content
        const sel = window.getSelection();
        const selectedText = sel.toString();
        let targetContent = selectedText && selectedText.length > 10 ? selectedText : content;
        let isSelection = selectedText && selectedText.length > 10;
        
        if(!targetContent || targetContent.trim() === '') {
            alert("No hay contenido para mejorar.");
            return;
        }
        
        // Show loading state
        const originalBg = editorBox.style.background;
        editorBox.style.background = '#f1f5f9';
        editorBox.style.opacity = '0.7';
        
        try {
            const resp = await fetch('/api/ai/course/improve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: action, content: targetContent })
            });
            const res = await resp.json();
            
            if(res.status === 'error') {
                alert("Error de IA: " + res.message);
            } else {
                if(isSelection) {
                    // Replace only selection
                    document.execCommand('insertHTML', false, res.data);
                } else {
                    editorBox.innerHTML = res.data;
                }
            }
        } catch (e) {
            console.error(e);
            alert("Error al comunicarse con la IA.");
        } finally {
            editorBox.style.background = originalBg;
            editorBox.style.opacity = '1';
        }
    }
    