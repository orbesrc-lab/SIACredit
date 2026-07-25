import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("--- DIAGNOSTICO DE ENDPOINTS FASE 3 ---")

program_id = 47

# Obtener una caracteristica valida
print("Buscando una caracteristica valida...")
try:
    res_model = requests.get(f"{BASE_URL}/api/model?inst_id=1&program_id={program_id}")
    model = res_model.json()
    char_id = model[0]['characteristics'][0]['id']
    print(f"Usando char_id: '{char_id}' (Caracteristica {model[0]['characteristics'][0]['number']})")
except Exception as e:
    print(f"Error fetching model: {e}")
    exit(1)

# 1. Crear un plan de mejora de prueba
payload = {
    "char_id": char_id,
    "accion": "Accion de prueba automatizada",
    "responsable": "test_responsable@correo.com",
    "fecha_limite": "2026-12-31",
    "avance": 0,
    "estado": "Pendiente"
}

print("\n1. Creando plan de prueba...")
res = requests.post(f"{BASE_URL}/api/planes_mejora?inst_id=1&program_id={program_id}", json=payload)
print(f"Status: {res.status_code}")
try:
    plan_data = res.json()
    print(f"Response: {json.dumps(plan_data, indent=2)}")
    plan_id = plan_data["data"][0]["id"]
    print(f"Plan ID Creado: {plan_id}")
except Exception as e:
    print(f"Error parsing response: {e}")
    exit(1)

# 2. Consultar el plan creado
print("\n2. Consultando planes de mejora...")
res = requests.get(f"{BASE_URL}/api/planes_mejora?inst_id=1&program_id={program_id}&char_id={char_id}")
print(f"Status: {res.status_code}")
planes = res.json()
print(f"Planes encontrados: {len(planes)}")

# 3. Verificar notificacion creada
print("\n3. Consultando notificaciones para el responsable...")
res = requests.get(f"{BASE_URL}/api/notificaciones?inst_id=1&program_id={program_id}&email=test_responsable@correo.com")
notifs = res.json()
print(f"Notificaciones encontradas: {len(notifs)}")
notif_id = None
if notifs:
    print(f"Ultima Notif: '{notifs[0]['titulo']}' - Mensaje: '{notifs[0]['mensaje']}' - Leido: {notifs[0]['leido']}")
    notif_id = notifs[0]['id']

# 4. Actualizar avance al 50%
print("\n4. Actualizando avance al 50%...")
res = requests.put(f"{BASE_URL}/api/planes_mejora/{plan_id}?inst_id=1&program_id={program_id}", json={
    "avance": 50,
    "estado": "Pendiente",
    "accion": "Accion de prueba automatizada",
    "responsable": "test_responsable@correo.com",
    "fecha_limite": "2026-12-31"
})
print(f"Status: {res.status_code}")
updated_plan = res.json()["data"][0]
print(f"Avance: {updated_plan['avance']}%, Estado: {updated_plan['estado']}")

# 5. Actualizar avance al 100% (debe cambiar a Completado)
print("\n5. Actualizando avance al 100%...")
res = requests.put(f"{BASE_URL}/api/planes_mejora/{plan_id}?inst_id=1&program_id={program_id}", json={
    "avance": 100,
    "estado": "En proceso",
    "accion": "Accion de prueba automatizada",
    "responsable": "test_responsable@correo.com",
    "fecha_limite": "2026-12-31"
})
print(f"Status: {res.status_code}")
completed_plan = res.json()["data"][0]
print(f"Avance: {completed_plan['avance']}%, Estado: {completed_plan['estado']}")

# 6. Marcar notificacion como leida
if notif_id:
    print(f"\n6. Marcando notificacion {notif_id} como leida...")
    res = requests.post(f"{BASE_URL}/api/notificaciones/{notif_id}/read")
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")

# 7. Eliminar plan de prueba
print("\n7. Eliminando plan de prueba...")
res = requests.delete(f"{BASE_URL}/api/planes_mejora/{plan_id}?inst_id=1&program_id={program_id}")
print(f"Status: {res.status_code}")
print(f"Response: {res.json()}")

print("\n--- PRUEBAS COMPLETADAS ---")
