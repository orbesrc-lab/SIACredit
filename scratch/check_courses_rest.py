import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

endpoint = f"{url}/rest/v1/lms_courses"
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(endpoint, headers=headers)
    print(f"Status Code: {response.status_code}")
    courses = response.json()
    print("Courses in DB:", len(courses))
    if len(courses) > 0:
        for c in courses:
            data = c.get('data', {})
            print(f"- {data.get('title') or data.get('name')} (ID: {c.get('id')}, Inst: {c.get('inst_id')})")
except Exception as e:
    print(f"Error: {e}")
