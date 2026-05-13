import urllib.request

def test_download():
    url = "https://www.google.com"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'SIACredit/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            print("Success, length:", len(data))
    except Exception as e:
        print("Error:", e)

test_download()
