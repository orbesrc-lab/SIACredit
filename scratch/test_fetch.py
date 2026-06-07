import requests
resp = requests.get('https://siacmen.vercel.app/api/courses/c_943c97c20?inst_id=1&program_id=47')
print("Status:", resp.status_code)
print("JSON:", resp.text)
