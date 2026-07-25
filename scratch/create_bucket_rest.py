import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("No credentials")
    exit(1)

endpoint = f"{url}/storage/v1/bucket"
headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}
data = {
    "id": "lms_files",
    "name": "lms_files",
    "public": True
}

try:
    response = requests.post(endpoint, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
