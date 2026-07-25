import os
import sys
import json

# Agregar la carpeta raíz a sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import supabase
import survey_storage

print("--- Testing Supabase Survey Storage with Composite Keys (Safe Mode) ---")

# Usar inst_id y program_id válidos de la base de datos (1/47 para UNICUCES y 2/48 para UTAP)
inst_1 = 1
prog_1 = 47

inst_2 = 2
prog_2 = 48

test_survey_1 = {
    "id": "survey_comp_test_1",
    "title": "Encuesta Temporal Prueba 1",
    "description": "Prueba de llaves compuestas inst 1 prog 47",
    "target": "estudiantes",
    "status": "activo",
    "questions": []
}

test_survey_2 = {
    "id": "survey_comp_test_2",
    "title": "Encuesta Temporal Prueba 2",
    "description": "Prueba de llaves compuestas inst 2 prog 48",
    "target": "estudiantes",
    "status": "activo",
    "questions": []
}

original_surveys_1 = []
original_surveys_2 = []

try:
    # 1. Obtener y respaldar datos existentes en Supabase
    print("Backing up existing surveys from Supabase...")
    
    # Programa 1
    res_surv1 = supabase.table('statistics').select("data_json").eq("table_id", f"SURVEY_DEFINITIONS_{inst_1}_{prog_1}").execute()
    if not res_surv1.data:
        res_surv1 = supabase.table('statistics').select("data_json").eq("table_id", "SURVEY_DEFINITIONS").eq("inst_id", inst_1).eq("program_id", prog_1).execute()
    if res_surv1.data:
        original_surveys_1 = json.loads(res_surv1.data[0]['data_json'])
        print(f"Backed up {len(original_surveys_1)} surveys for inst {inst_1} prog {prog_1}")
    else:
        print(f"No existing surveys found for inst {inst_1} prog {prog_1}")

    # Programa 2
    res_surv2 = supabase.table('statistics').select("data_json").eq("table_id", f"SURVEY_DEFINITIONS_{inst_2}_{prog_2}").execute()
    if not res_surv2.data:
        res_surv2 = supabase.table('statistics').select("data_json").eq("table_id", "SURVEY_DEFINITIONS").eq("inst_id", inst_2).eq("program_id", prog_2).execute()
    if res_surv2.data:
        original_surveys_2 = json.loads(res_surv2.data[0]['data_json'])
        print(f"Backed up {len(original_surveys_2)} surveys for inst {inst_2} prog {prog_2}")
    else:
        print(f"No existing surveys found for inst {inst_2} prog {prog_2}")

    # 2. Guardar encuestas temporales localmente incluyendo el respaldo
    print("Saving test surveys locally...")
    surveys_to_save_1 = [s for s in original_surveys_1 if s.get('id') != "survey_comp_test_1"] + [test_survey_1]
    survey_storage.save_local_surveys(inst_1, prog_1, surveys_to_save_1)
    
    surveys_to_save_2 = [s for s in original_surveys_2 if s.get('id') != "survey_comp_test_2"] + [test_survey_2]
    survey_storage.save_local_surveys(inst_2, prog_2, surveys_to_save_2)
    
    # 3. Sincronizar Programa 1 a Supabase
    print("Syncing surveys for program 1...")
    survey_storage.sync_surveys_only(inst_1, prog_1, supabase)
    print("Successfully synced program 1!")
    
    # 4. Sincronizar Programa 2 a Supabase
    # Esto probará si ocurre o no la colisión de clave única "statistics_table_id_key"
    print("Syncing surveys for program 2...")
    survey_storage.sync_surveys_only(inst_2, prog_2, supabase)
    print("Successfully synced program 2! (No unique constraint error!)")
    
    # 5. Verificar registros en Supabase usando la clave compuesta nueva
    print("Verifying composite keys in Supabase...")
    res_db1 = supabase.table('statistics').select("*").eq("table_id", f"SURVEY_DEFINITIONS_{inst_1}_{prog_1}").execute()
    assert len(res_db1.data) == 1, "Registro de base de datos para programa 1 no encontrado"
    
    res_db2 = supabase.table('statistics').select("*").eq("table_id", f"SURVEY_DEFINITIONS_{inst_2}_{prog_2}").execute()
    assert len(res_db2.data) == 1, "Registro de base de datos para programa 2 no encontrado"
    print("Composite keys verified successfully in Supabase.")
    
    # 6. Verificar búsqueda global con .like()
    print("Testing global query fallback using .like()...")
    res_like = supabase.table('statistics').select("data_json, inst_id, program_id").like("table_id", "SURVEY_DEFINITIONS%").execute()
    
    found_1 = False
    found_2 = False
    for row in res_like.data:
        survs = json.loads(row['data_json'])
        for s in survs:
            if s.get('id') == "survey_comp_test_1":
                found_1 = True
            if s.get('id') == "survey_comp_test_2":
                found_2 = True
                
    assert found_1, "Survey 1 no fue encontrada con la consulta global .like()"
    assert found_2, "Survey 2 no fue encontrada con la consulta global .like()"
    print("Global query verified successfully.")

finally:
    # 7. Restaurar los datos originales de vuelta a Supabase y localmente para dejar el entorno intacto
    print("\nCleaning up and restoring original data...")
    try:
        # Programa 1
        survey_storage.save_local_surveys(inst_1, prog_1, original_surveys_1)
        survey_storage.sync_surveys_only(inst_1, prog_1, supabase)
        # Si no había nada original, remover la clave compuesta creada
        if not original_surveys_1:
            supabase.table('statistics').delete().eq("table_id", f"SURVEY_DEFINITIONS_{inst_1}_{prog_1}").execute()
        
        # Programa 2
        survey_storage.save_local_surveys(inst_2, prog_2, original_surveys_2)
        survey_storage.sync_surveys_only(inst_2, prog_2, supabase)
        if not original_surveys_2:
            supabase.table('statistics').delete().eq("table_id", f"SURVEY_DEFINITIONS_{inst_2}_{prog_2}").execute()
            
        print("Restore completed successfully!")
    except Exception as cleanup_err:
        print(f"Error during cleanup restore: {cleanup_err}")

print("\n--- ALL TESTS PASSED SUCCESSFULLY! ---")
