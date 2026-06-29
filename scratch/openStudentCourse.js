async function openStudentCourse(courseId) {
            try {
                const resp = await fetch(`/api/courses/${courseId}?inst_id=${getInstId()}&program_id=${getProgramId()}`);
                const course = await resp.json();
                
                // Cargar entregas de este estudiante para este curso
                let studentSubmissions = [];
                try {
                    const subResp = await fetch(`/api/submissions?course_id=${courseId}&student_email=${user.email}&inst_id=${getInstId()}&program_id=${getProgramId()}`);
                    studentSubmissions = await subResp.json();
                } catch (e) {
                    console.error("Error al cargar entregas:", e);
                }
                
                document.getElementById('studentCourseTitle').textContent = `Aula Virtual: ${course.title}`;
                document.getElementById('studentCourseDesc').textContent = course.description || '';
                document.getElementById('studentCourseDuration').textContent = `⏱️ Duración: ${course.duration || 10} horas`;
                document.getElementById('studentCourseLevel').textContent = `📊 Nivel: ${course.level || 'Principiante'}`;
                document.getElementById('studentCourseCertifier').textContent = `🎓 Certifica: ${course.certifier || 'SKEL'}`;
                
                // Mostrar perfil del profesor asignado
                const teacherProfileDiv = document.getElementById('studentCourseTeacherProfile');
                if (course.teacher_id) {
                    try {
                        const tResp = await fetch(`/api/teachers?inst_id=${getInstId()}`);
                        const teachers = await tResp.json();
                        const teacher = teachers.find(t => t.id === course.teacher_id);
                        if (teacher) {
                            document.getElementById('studentCourseTeacherAvatar').src = teacher.avatar || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100';
                            document.getElementById('studentCourseTeacherName').textContent = `Profesor: ${teacher.name}`;
                            document.getElementById('studentCourseTeacherEmail').textContent = teacher.email;
                            teacherProfileDiv.style.display = 'flex';
                        } else { teacherProfileDiv.style.display = 'none'; }
                    } catch(e) { teacherProfileDiv.style.display = 'none'; }
                } else { teacherProfileDiv.style.display = 'none'; }
                
                loadStudentGamification(courseId);

                const outcomesUl = document.getElementById('studentOutcomesList');
                outcomesUl.innerHTML = Object.values(course.outcomes || {}).map(o => `<li>${escapeHtml(o)}</li>`).join('') || '<li>Sin resultados registrados.</li>';
                
                const competenciesUl = document.getElementById('studentCompetenciesList');
                competenciesUl.innerHTML = Object.values(course.competencies || {}).map(c => `<li>${escapeHtml(c)}</li>`).join('') || '<li>Sin competencias registradas.</li>';
                
                // Clases Sincrónicas (Videoconferencia)
                const meetingsDiv = document.getElementById('studentMeetingsList');
                const meetings = Object.values(course.meetings || {});
                if (meetings.length === 0) {
                    meetingsDiv.innerHTML = '<div style="font-size:0.8rem; color:var(--text-muted); padding:10px; text-align:center;">No hay videoconferencias programadas.</div>';
                } else {
                    meetingsDiv.innerHTML = meetings.map(m => `
                        <div style="background:white; border:1px solid #bbf7d0; border-radius:8px; padding:10px; margin-bottom:8px; font-size:0.8rem;">
                            <strong>${escapeHtml(m.title)}</strong><br>
                            📅 ${m.date} - 🕒 ${m.time}<br>
                            <a href="${m.url}" target="_blank" class="btn-primary" style="display:block; text-align:center; padding:6px; margin-top:8px; font-size:0.75rem; text-decoration:none; background: linear-gradient(135deg, #10b981, #059669); border:none; color:white; border-radius:6px; font-weight:600;">Ingresar a Clase 🚀</a>
                        </div>
                    `).join('');
                }
                
                // Temario y Repositorio por Unidad
                const unitsContainer = document.getElementById('studentUnitsContainer');
                unitsContainer.innerHTML = '';
                const units = Object.values(course.units || {});
                
                if (units.length === 0) {
                    unitsContainer.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:30px; border:1px dashed var(--border-color); border-radius:8px;">Este curso aún no tiene lecciones creadas.</div>';
                } else {
                    let previousUnitCompleted = true; // La unidad 1 siempre inicia desbloqueada

                    units.forEach((unit, uIdx) => {
                        const box = document.createElement('div');
                        box.className = 'unit-box';
                        box.style = 'margin-bottom: 20px; transition: all 0.3s ease;';
                        
                        // Si la unidad anterior no fue completada, bloqueamos esta unidad
                        if (!previousUnitCompleted) {
                            box.style.opacity = '0.6';
                            box.innerHTML = `
                                <div class="unit-header" style="background: #e2e8f0; color: #64748b; border-color: #cbd5e1; display:flex; justify-content:space-between; align-items:center;">
                                    <span>🔒 Unidad ${uIdx + 1}: ${escapeHtml(unit.name)}</span>
                                    <span style="font-size:0.75rem; background:white; padding:2px 8px; border-radius:12px;">Bloqueada</span>
                                </div>
                                <div style="padding:30px; background: #f8fafc; text-align: center; color: var(--text-muted); border: 1px solid #e2e8f0; border-top: none; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;">
                                    <div style="font-size: 2rem; margin-bottom: 10px;">🔒</div>
                                    <h4 style="margin: 0 0 10px 0; color: #64748b;">Contenido Bloqueado</h4>
                                    <p style="font-size: 0.85rem; margin: 0; max-width: 400px; margin-left: auto; margin-right: auto;">Para acceder a esta unidad, primero debes completar y enviar todas las actividades de la unidad anterior.</p>
                                </div>
                            `;
                            unitsContainer.appendChild(box);
                            
                            // Como esta unidad está bloqueada, lógicamente no está completada
                            // por lo que las siguientes también se bloquearán.
                            previousUnitCompleted = false;
                            return; // No renderizamos el contenido
                        }

                        // Temas con acordeón interactivo para ver el contenido HTML redactado por el profesor
                        let topicsHtml = '';
                        const tArr = Object.values(unit.topics || {});
                        if (tArr.length === 0) {
                            topicsHtml = '<div style="color:var(--text-muted); font-size:0.8rem; padding:5px;">Sin temas asignados.</div>';
                        } else {
                            topicsHtml = '<div style="display:flex; flex-direction:column; gap:8px; margin-top:5px;">';
                            tArr.forEach((rawT, tIdx) => {
                                const t = typeof rawT === 'string' ? { id: 't_' + tIdx, title: rawT, content: "" } : rawT;
                                const hasContent = t.content && t.content.trim() !== "";
                                
                                topicsHtml += `
                                    <div style="border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; background: rgba(99,102,241,0.02);">
                                        <div onclick="toggleTopicAccordion('${unit.id}_${t.id}')" style="padding: 12px 18px; font-weight: 600; font-size: 0.88rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: rgba(99,102,241,0.04); color: var(--text-main); transition: background 0.2s;">
                                            <span>📖 ${escapeHtml(t.title)}</span>
                                            <span style="font-size:0.75rem; color:var(--primary-color); font-weight:700;">
                                                ${hasContent ? 'Leer Lección 👁️' : 'Sin Contenido'}
                                            </span>
                                        </div>
                                        <div id="acc_${unit.id}_${t.id}" style="display: none; padding: 20px; background: var(--card-bg); border-top: 1px solid var(--border-color); font-size: 0.92rem; line-height: 1.7; color: var(--text-main); text-align: left; overflow-x: auto;">
                                            ${hasContent ? t.content : '<span style="color:var(--text-muted); font-style:italic;">Esta lección no contiene texto ni recursos embebidos todavía.</span>'}
                                        </div>
                                    </div>
                                `;
                            });
                            topicsHtml += '</div>';
                        }
                        
                        // Repositorio: Recursos para afianzar
                        let resHtml = '';
                        const rArr = Object.values(unit.resources || {});
                        if (rArr.length > 0) {
                            resHtml = '<strong style="display:block; font-size:0.85rem; color:var(--primary-color); margin-top:16px; margin-bottom: 6px;">📁 Recursos de Estudio (Repositorio):</strong>';
                            rArr.forEach(r => {
                                const typeIcon = r.type === 'document' ? '📄 PDF' : (r.type === 'video' ? '🎥 Video' : (r.type === 'infographic' ? '📊 Infografía' : '🔗 Web'));
                                resHtml += `
                                    <div class="resource-card" style="margin-top:5px;">
                                        <span><strong>${typeIcon}:</strong> ${escapeHtml(r.name)}</span>
                                        <a href="${r.url}" target="_blank" style="color:var(--primary-color); font-weight:700; text-decoration:none;">Abrir Recurso</a>
                                    </div>`;
                            });
                        }
                        
                        // Actividades
                        let actHtml = '';
                        const aArr = Object.values(unit.activities || {});
                        if (aArr.length > 0) {
                            actHtml = '<strong style="display:block; font-size:0.85rem; color:var(--primary-color); margin-top:16px; margin-bottom: 6px;">📝 Actividades y Entregas:</strong>';
                            aArr.forEach(act => {
                                // Buscar entrega existente para esta actividad
                                const sub = studentSubmissions.find(s => s.activity_id === act.id);
                                let statusHtml = '';
                                let buttonText = 'Entregar Trabajo';
                                let feedbackHtml = '';
                                
                                if (sub) {
                                    if (sub.status === 'graded') {
                                        statusHtml = ` <span class="status aprobado" style="font-size:0.7rem; padding: 2px 8px; border-radius: 12px; margin-left:8px; background: #e6f4ea; color: #137333; font-weight: 700;">Calificado: ${parseFloat(sub.grade).toFixed(1)}</span>`;
                                        buttonText = 'Volver a Entregar';
                                        feedbackHtml = `
                                            <div style="background: rgba(16,185,129,0.04); border-left: 4px solid #10b981; border-radius: 6px; padding: 10px; margin-top: 8px; font-size: 0.8rem; text-align: left;">
                                                <strong style="color:#10b981;">Nota:</strong> ${parseFloat(sub.grade).toFixed(1)} / 5.0<br>
                                                <strong>Retroalimentación:</strong> ${escapeHtml(sub.feedback || 'Sin comentarios.')}
                                            </div>
                                        `;
                                    } else {
                                        statusHtml = ` <span class="status revision" style="font-size:0.7rem; padding: 2px 8px; border-radius: 12px; margin-left:8px; background: #fef7e0; color: #b06000; font-weight: 700;">Entregado (Pendiente)</span>`;
                                        buttonText = 'Actualizar Entrega';
                                        feedbackHtml = `
                                            <div style="background: rgba(245,158,11,0.04); border-left: 4px solid #f59e0b; border-radius: 6px; padding: 10px; margin-top: 8px; font-size: 0.8rem; text-align: left; color: var(--text-muted);">
                                                <strong>Tu entrega actual:</strong> <span style="font-style:italic;">${escapeHtml(sub.content)}</span>
                                            </div>
                                        `;
                                    }
                                }

                                actHtml += `
                                    <div class="activity-item" style="margin-top:8px; display:flex; flex-direction:column; align-items:stretch; gap:6px;">
                                        <div style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                                            <div>
                                                <strong>${escapeHtml(act.title)}</strong>${statusHtml}<br>
                                                <span style="font-size:0.75rem; color:var(--text-muted);">${escapeHtml(act.description)}</span><br>
                                                <span style="font-size:0.72rem; font-weight:700; color:var(--accent-color); display:block; margin-top:4px;">Fecha límite: ${act.due_date || 'Sin límite'}</span>
                                            </div>
                                            <button class="btn-primary" style="padding:8px 16px; font-size:0.8rem; background: var(--success-gradient); border:none; color:white; font-weight:600; border-radius:10px;" onclick="submitActivityDelivery('${courseId}', '${unit.id}', '${act.id}', '${escapeHtml(act.title).replace(/'/g, "\\'")}')">${buttonText}</button>
                                        </div>
                                        ${feedbackHtml}
                                    </div>`;
                            });
                        }
                        
                        // Evaluaciones
                        let evalHtml = '';
                        if (unit.evaluations && unit.evaluations.length > 0) {
                            evalHtml = '<strong style="display:block; font-size:0.85rem; color:var(--primary-color); margin-top:16px; margin-bottom: 6px;">🏆 Evaluaciones (Escala CNA):</strong>';
                            unit.evaluations.forEach(ev => {
                                evalHtml += `
                                    <div class="evaluation-item" style="margin-top:5px;">
                                        <div>
                                            <strong>${escapeHtml(ev.title)}</strong><br>
                                            <span style="font-size:0.72rem; color:var(--text-muted);">Calificación CNA (Aprobación: ${ev.min_grade})</span>
                                        </div>
                                        <button class="btn-primary" style="padding:8px 16px; font-size:0.8rem; background: var(--primary-gradient); border:none; color:white; border-radius:10px;" onclick="presentQuiz('${escapeHtml(ev.title).replace(/'/g, "\\'")}', ${ev.min_grade || 3.0}, ${ev.max_grade || 5.0})">Presentar Examen</button>
                                    </div>`;
                            });
                        }
                        
                        box.innerHTML = `
                            <div class="unit-header">
                                Unidad ${uIdx + 1}: ${escapeHtml(unit.name)}
                            </div>
                            <div style="padding:20px; background: var(--card-bg);">
                                <div style="font-size:0.88rem; line-height:1.5; color:var(--text-muted);">
                                    <strong>Lecciones del Tema:</strong><br>
                                    ${topicsHtml}
                                </div>
                                ${resHtml}
                                ${actHtml}
                                ${evalHtml}
                            </div>
                        `;
                        unitsContainer.appendChild(box);
                        
                        // Lógica para determinar si esta unidad habilita la siguiente
                        let currentUnitCompleted = true;
                        if (unit.activities && unit.activities.length > 0) {
                            // Todas las actividades deben tener al menos una entrega
                            const submittedCount = unit.activities.filter(act => 
                                studentSubmissions.some(s => s.activity_id === act.id)
                            ).length;
                            
                            if (submittedCount < unit.activities.length) {
                                currentUnitCompleted = false;
                            }
                        }
                        
                        // Actualizar el flag para la siguiente iteración
                        previousUnitCompleted = currentUnitCompleted;
                    });
                }
                
                document.getElementById('studentCourseViewer').style.display = 'block';
                document.getElementById('studentCourseViewer').scrollIntoView({ behavior: 'smooth' });
            } catch(e) { alert("Error al ingresar al curso."); }
        }

        