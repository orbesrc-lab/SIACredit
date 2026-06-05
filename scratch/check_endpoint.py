import os
import sys
import json

# Agregar la carpeta raíz a sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

app.config['TESTING'] = True
client = app.test_client()

print("--- Querying GET /api/surveys?inst_id=1&program_id=47&use_cloud=true ---")
resp = client.get('/api/surveys?inst_id=1&program_id=47&use_cloud=true')
print("Status Code:", resp.status_code)
print("Data:", json.loads(resp.data.decode('utf-8')))
