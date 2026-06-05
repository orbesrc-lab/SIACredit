import requests

url = "https://siacmen.vercel.app/api/institutions"
r = requests.get(url)
print("Status Code:", r.status_code)
try:
    print("JSON Response:", r.json())
except Exception as e:
    print("Could not parse JSON:", e)
    print("Response text:", r.text[:500])
