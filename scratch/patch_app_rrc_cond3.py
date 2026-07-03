import re

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the justification_str in ai_generar_rrc
old_just = 'justification_str = f"\\nEvidencia de Justificaci\u00f3n/Estudio de Oferta adjunta: {justification_url}. EXIGENCIA: Analizar obligatoriamente el contexto territorial en la Condici\u00f3n 2 bas\u00e1ndose en este estudio."'
new_just = 'justification_str = f"\\nEvidencia documental adjunta (Soporte global): {justification_url}. EXIGENCIA: Analizar y referenciar expl\u00edcitamente esta evidencia donde aplique."'
content = content.replace(old_just, new_just)

with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied to app.py")
