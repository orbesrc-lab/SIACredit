import urllib.request
import json

url = "https://siacmen.vercel.app/api/institutions"
try:
    with urllib.request.urlopen(url, timeout=10) as response:
        html = response.read().decode('utf-8')
        print("Status Code:", response.getcode())
        print("Response:", html)
except Exception as e:
    print("Error querying API:", e)
