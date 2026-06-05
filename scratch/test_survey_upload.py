import requests
import io

url = "http://127.0.0.1:5000/api/surveys/upload"

# Create a dummy file in memory
file_data = b"This is a test survey attachment file content."
file_name = "test_survey_doc.txt"

files = {
    'file': (file_name, io.BytesIO(file_data), 'text/plain')
}
data = {
    'survey_id': 'test_survey_123',
    'inst_id': '1',
    'program_id': '47'
}

print("Enviando petición POST a /api/surveys/upload...")
try:
    resp = requests.post(url, files=files, data=data)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"Error connecting: {e}")
