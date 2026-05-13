import urllib.request
import json

url = "http://127.0.0.1:5000/api/model?inst_id=1&program_id=1"
try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        for f in data:
            print(f"Factor ID: {f.get('id')}, Number: {repr(f.get('number'))}, Name: {f.get('name')}")
except Exception as e:
    print("Error:", e)
