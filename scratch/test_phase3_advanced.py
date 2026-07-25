import requests
import json

BASE_URL = "http://127.0.0.1:5000"
program_id = 47

print("--- DIAGNOSTICO AVANZADO PLANES DE MEJORA FASE 3 ---")

# Obtener una característica válida
try:
    res_model = requests.get(f"{BASE_URL}/api/model?inst_id=1&program_id={program_id}")
    model = res_model.json()
    char_id = model[0]['characteristics'][0]['id']
    print(f"Usando char_id: '{char_id}'")
except Exception as e:
    print(f"Error fetching model: {e}")
    exit(1)

# A. PRUEBA INDICADOR DE TIPO DOCUMENTO
print("\n--- A. PRUEBA DE INDICADOR TIPO DOCUMENTO ---")
doc_payload = {
    "char_id": char_id,
    "accion": "Acción con soporte documental",
    "responsable": "doc_test@correo.com",
    "fecha_limite": "2026-12-31",
    "indicador_tipo": "documento",
    "avance": 0,
    "estado": "Pendiente"
}
res_doc = requests.post(f"{BASE_URL}/api/planes_mejora?inst_id=1&program_id={program_id}", json=doc_payload)
print(f"Crear Plan Documento Status: {res_doc.status_code}")
doc_plan_id = res_doc.json()["data"][0]["id"]
print(f"ID Plan Documento: {doc_plan_id}")

# Verificar avance inicial (debe ser 0)
res_get = requests.get(f"{BASE_URL}/api/planes_mejora?inst_id=1&program_id={program_id}&char_id={char_id}")
planes = res_get.json()
plan = next(p for p in planes if p["id"] == doc_plan_id)
print(f"Avance inicial (sin doc): {plan['avance']}%, Estado: {plan['estado']}")

# Simular que se sube un documento (actualizando indicador_documento_url)
update_payload = {
    "indicador_documento_url": "https://supabase.co/storage/v1/object/public/evidencias/planes_soporte/test.pdf"
}
res_put = requests.put(f"{BASE_URL}/api/planes_mejora/{doc_plan_id}?inst_id=1&program_id={program_id}", json=update_payload)
print(f"Actualizar Soporte Status: {res_put.status_code}")

# Verificar avance final (debe ser 100% y Completado)
res_get = requests.get(f"{BASE_URL}/api/planes_mejora?inst_id=1&program_id={program_id}&char_id={char_id}")
planes = res_get.json()
plan = next(p for p in planes if p["id"] == doc_plan_id)
print(f"Avance final (con doc): {plan['avance']}%, Estado: {plan['estado']}")


# B. PRUEBA INDICADOR DE TIPO OPINIÓN (VINCULADO A ENCUESTA)
print("\n--- B. PRUEBA DE INDICADOR TIPO OPINIÓN ---")
# 1. Obtener encuestas del programa
res_surveys = requests.get(f"{BASE_URL}/api/surveys?inst_id=1&program_id={program_id}")
surveys = res_surveys.json()
if not surveys:
    print("No hay encuestas disponibles en el programa. Creando una encuesta de prueba...")
    # Crear encuesta de prueba
    survey_payload = [{
        "id": "survey_test_p3",
        "title": "Encuesta de Satisfacción Docente",
        "target": "docentes",
        "status": "activo",
        "questions": [
            {"id": "q1", "type": "rating", "text": "¿Cómo califica los medios educativos?"}
        ]
    }]
    requests.post(f"{BASE_URL}/api/surveys?inst_id=1&program_id={program_id}", json=survey_payload)
    survey_id = "survey_test_p3"
    question_id = "q1"
else:
    # Usar la primera encuesta y pregunta
    survey_id = surveys[0]["id"]
    if not surveys[0].get("questions"):
        surveys[0]["questions"] = [{"id": "q_default", "type": "rating", "text": "Pregunta de opinión"}]
        requests.post(f"{BASE_URL}/api/surveys?inst_id=1&program_id={program_id}", json=surveys)
    question_id = surveys[0]["questions"][0]["id"]

print(f"Vinculando a encuesta '{survey_id}', pregunta '{question_id}'")

# 2. Crear plan de tipo opinión
opinion_payload = {
    "char_id": char_id,
    "accion": "Acción vinculada a opiniones",
    "responsable": "opinion_test@correo.com",
    "fecha_limite": "2026-12-31",
    "indicador_tipo": "opinion",
    "indicador_survey_id": survey_id,
    "indicador_question_id": question_id,
    "avance": 0,
    "estado": "Pendiente"
}

res_opinion = requests.post(f"{BASE_URL}/api/planes_mejora?inst_id=1&program_id={program_id}", json=opinion_payload)
print(f"Crear Plan Opinión Status: {res_opinion.status_code}")
opinion_plan_id = res_opinion.json()["data"][0]["id"]
print(f"ID Plan Opinión: {opinion_plan_id}")

# 3. Registrar respuestas en la encuesta vinculada con use_cloud=true
requests.post(f"{BASE_URL}/api/surveys/{survey_id}/respond?use_cloud=true", json={question_id: 4.0})
requests.post(f"{BASE_URL}/api/surveys/{survey_id}/respond?use_cloud=true", json={question_id: 5.0})
print("Registradas respuestas: 4.0 y 5.0 en la encuesta (con use_cloud=true)")

# 4. Consultar y verificar el avance dinámico (debe ser (4.5 / 5.0) * 100 = 90%)
res_get = requests.get(f"{BASE_URL}/api/planes_mejora?inst_id=1&program_id={program_id}&char_id={char_id}")
planes = res_get.json()
plan = next(p for p in planes if p["id"] == opinion_plan_id)
print(f"Avance calculado dinámicamente de opinión: {plan['avance']}% (Esperado: 90%), Estado: {plan['estado']}")


# C. LIMPIEZA
print("\n--- C. LIMPIEZA DE REGISTROS DE PRUEBA ---")
requests.delete(f"{BASE_URL}/api/planes_mejora/{doc_plan_id}?inst_id=1&program_id={program_id}")
requests.delete(f"{BASE_URL}/api/planes_mejora/{opinion_plan_id}?inst_id=1&program_id={program_id}")
print("Registros de prueba eliminados correctamente.")

print("\n--- PRUEBAS COMPLETADAS CON EXITO ---")
