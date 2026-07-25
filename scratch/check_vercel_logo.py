import urllib.request

url = "https://siacmen.vercel.app/static/logo_skel.png"
print("Fetching:", url)
try:
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        print("Status Code:", response.getcode())
        print("Headers:")
        for k, v in response.getheaders():
            print(f"  {k}: {v}")
        content = response.read()
        print("Received content length:", len(content))
except Exception as e:
    print("Error:", e)
