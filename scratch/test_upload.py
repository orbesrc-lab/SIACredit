import requests

url = "https://siacmen.vercel.app/api/upload"
files = {'file': ('test.pdf', b'%PDF-1.4 test', 'application/pdf')}
data = {
    'inst_id': '1',
    'program_id': '1',
    'aspect_id': 'BIBLIOTECA_INST',
    'period': 'Biblioteca',
    'email': 'orbesrc@gmail.com'
}

try:
    r = requests.post(url, files=files, data=data)
    print("Status:", r.status_code)
    print("Response:", r.text[:500])
except Exception as e:
    print("Exception:", e)
