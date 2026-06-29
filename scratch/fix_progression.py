import re

with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_logic = """let currentUnitCompleted = true;
                        if (unit.activities && unit.activities.length > 0) {
                            // Todas las actividades deben tener al menos una entrega
                            const submittedCount = unit.activities.filter(act => 
                                studentSubmissions.some(s => s.activity_id === act.id)
                            ).length;
                            
                            if (submittedCount < unit.activities.length) {
                                currentUnitCompleted = false;
                            }
                        }"""

new_logic = """let currentUnitCompleted = true;
                        if (unit.activities && unit.activities.length > 0) {
                            // Todas las actividades deben tener al menos una entrega
                            const submittedCount = unit.activities.filter(act => 
                                studentSubmissions.some(s => s.activity_id === act.id)
                            ).length;
                            
                            if (submittedCount < unit.activities.length) {
                                currentUnitCompleted = false;
                            }
                        }
                        
                        // Lógica de evaluaciones: también deben haber sido enviadas
                        if (unit.evaluations && unit.evaluations.length > 0) {
                            const submittedEvalsCount = unit.evaluations.filter(ev => 
                                studentSubmissions.some(s => s.activity_id === ev.id)
                            ).length;
                            
                            if (submittedEvalsCount < unit.evaluations.length) {
                                currentUnitCompleted = false;
                            }
                        }"""

html = html.replace(old_logic, new_logic)

with open('c:\\SIAC\\templates\\formacion.html', 'w', encoding='utf-8') as f:
    f.write(html)
