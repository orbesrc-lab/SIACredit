import os
import sys
import json

# Add root folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import survey_storage

print("Testing survey_storage helper...")
try:
    survey_storage.ensure_files_exist()
    print("Files ensured.")
    
    # Save a mock survey
    survey = {
        "id": "test_surv_123",
        "title": "Encuesta de Prueba",
        "description": "Esta es una encuesta de prueba local",
        "target": "estudiantes",
        "status": "activo",
        "questions": [
            {"id": "q1", "type": "rating", "text": "Pregunta de calificación"},
            {"id": "q2", "type": "select", "text": "Pregunta de selección", "options": ["Op1", "Op2"]},
            {"id": "q3", "type": "text", "text": "Pregunta de texto"}
        ]
    }
    
    success = survey_storage.save_local_surveys(1, 1, [survey])
    print("Save local surveys success:", success)
    
    surveys = survey_storage.load_local_surveys(1, 1)
    print("Loaded surveys count:", len(surveys))
    assert len(surveys) == 1
    assert surveys[0]['id'] == "test_surv_123"
    print("Local survey data verified.")
    
    # Add a mock response
    response = {
        "survey_id": "test_surv_123",
        "submitted_at": "2026-05-31T00:00:00",
        "answers": {
            "q1": "5",
            "q2": "Op1",
            "q3": "Test comment"
        }
    }
    success_resp = survey_storage.save_local_response(1, 1, response)
    print("Save local response success:", success_resp)
    
    responses = survey_storage.load_local_responses_for_survey("test_surv_123")
    print("Loaded responses count:", len(responses))
    assert len(responses) == 1
    assert responses[0]['answers']['q1'] == "5"
    print("Local response data verified.")
    
    # Cleanup test data
    surveys = [s for s in survey_storage.load_local_surveys(1, 1) if s.get('id') != "test_surv_123"]
    survey_storage.save_local_surveys(1, 1, surveys)
    
    # Cleanup responses as well
    with open(survey_storage.RESPONSES_FILE, 'r', encoding='utf-8') as f:
        all_resps = json.load(f)
    all_resps = [r for r in all_resps if r.get('survey_id') != "test_surv_123"]
    with open(survey_storage.RESPONSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_resps, f, indent=2, ensure_ascii=False)
    
    print("Cleanup verified.")
    print("All local tests passed successfully!")
    
except Exception as e:
    print("Test failed with error:", e)
    sys.exit(1)
