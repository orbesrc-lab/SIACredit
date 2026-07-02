import urllib.request, urllib.parse, re
query = "filetype:pdf Calidad de Educacion en Colombia"
url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        # Extract titles and URLs
        results = re.findall(r'<a class="result__snippet[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
        for r in results:
            print(f"URL: {r[0]}")
except Exception as e:
    print(f"Error: {e}")
