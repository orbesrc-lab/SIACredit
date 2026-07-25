import sys
import os

# Aseguramos que la raíz del proyecto esté en el path para poder importar app.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app import app
    print("App importada correctamente.")
    
    with app.test_client() as client:
        # Datos de prueba simulando lo que enviaría el frontend para la Condición 1 y 2
        payload = {
            "inst_id": 1,
            "program_id": 1,
            "program_name": "Contaduría Pública",
            "inst_name": "Corporación Universitaria Centro Superior",
            "condiciones": {
                "1": {
                    "factoresRelacionados": [
                        {"numero": "1", "nombre": "Misión y Proyecto Institucional", "promedio": 4.5, "cualitativo": "Excelente"}
                    ],
                    "promedio": 4.5,
                    "justificaciones": ["El programa cuenta con un PEP actualizado a 2024."],
                    "indicadoresCubiertos": ["Denominación registrada en el SNIES"]
                },
                "2": {
                    "factoresRelacionados": [
                        {"numero": "2", "nombre": "Estudiantes y Contexto", "promedio": 3.8, "cualitativo": "Aceptable"}
                    ],
                    "promedio": 3.8,
                    "justificaciones": ["Hay estudios de impacto regional pero falta fortalecer la modalidad virtual."],
                    "indicadoresCubiertos": ["Análisis de necesidades del sector productivo"]
                }
            }
        }
        
        print("\nEnviando petición POST a /api/ai/generar_rrc ...")
        response = client.post('/api/ai/generar_rrc', json=payload)
        
        if response.status_code == 200:
            data = response.get_json()
            if data and "report" in data:
                print("\n--- REPORTE GENERADO POR LA IA ---")
                print(data["report"])
            else:
                print("\nError: Respuesta no contiene 'report'.")
                print(data)
        else:
            print(f"\nError HTTP {response.status_code}: {response.text}")
            
except Exception as e:
    print(f"Error al ejecutar la prueba: {e}")
