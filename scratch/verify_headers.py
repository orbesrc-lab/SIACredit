import urllib.request

try:
    resp = urllib.request.urlopen("http://127.0.0.1:5000/")
    print("Status:", resp.status)
    print("\nHeaders:")
    for k, v in resp.headers.items():
        print(f"  {k}: {v}")
except Exception as e:
    print("Error querying local server:", e)
