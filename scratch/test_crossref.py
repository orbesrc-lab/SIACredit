import urllib.request, json
url = "https://api.crossref.org/works?query=calidad&select=title,author,URL,published-print,DOI,type,link&rows=5"
req = urllib.request.Request(url, headers={'User-Agent': 'SIACredit/1.0 (mailto:orbesrc@gmail.com)'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf-8'))
    for item in data['message']['items']:
        print(item.get('title', [''])[0])
        links = item.get('link', [])
        pdf_url = ""
        for link in links:
            if link.get('content-type') == 'application/pdf':
                pdf_url = link.get('URL')
                break
        print(f"PDF: {pdf_url}")
