import urllib.request

url = "https://siacmen.vercel.app/configuracion.html?t=123"
try:
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'}
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        html = response.read().decode('utf-8')
        print("Status Code:", response.getcode())
        print("Contains 'Cache-Control':", "Cache-Control" in html)
        print("Contains 'data.js?v=2.2':", "data.js?v=2.2" in html)
        
        # Search for loadAllInstitutions implementation in the HTML
        for line in html.split('\n'):
            if "loadAllInstitutions" in line:
                print("Line:", line.strip()[:100])
except Exception as e:
    print("Error:", e)
