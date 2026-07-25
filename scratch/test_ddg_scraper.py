import urllib.request, urllib.parse, re, json
def search_ddg_pdf(query):
    # Ensure filetype:pdf is in query
    if 'filetype:pdf' not in query:
        query = 'filetype:pdf ' + query
    
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
            # Find all result snippets
            # DDG HTML results are inside <a class="result__url" href="...">
            results = []
            
            # Find blocks of results
            blocks = html.split('class="result ')
            for block in blocks[1:]:
                # Extract title
                title_match = re.search(r'<h2 class="result__title">.*?<a[^>]*>(.*?)</a>', block, re.IGNORECASE | re.DOTALL)
                title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else 'Documento PDF'
                
                # Extract URL
                url_match = re.search(r'<a class="result__url" href="([^"]+)"', block)
                if url_match:
                    pdf_url = url_match.group(1)
                    if pdf_url.startswith('//'):
                        pdf_url = 'https:' + pdf_url
                        
                    # Extract snippet
                    snippet_match = re.search(r'<a class="result__snippet[^>]*>(.*?)</a>', block, re.IGNORECASE | re.DOTALL)
                    snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip() if snippet_match else ''
                    
                    results.append({
                        'title': title,
                        'publication_year': 'S.F.',
                        'authorships': [{'author': {'display_name': 'Web Resource'}}],
                        'primary_location': {'source': {'display_name': snippet[:50] + '...' if snippet else 'Búsqueda Web'}},
                        'doi': '',
                        'open_access': {'oa_url': pdf_url},
                        'type': 'pdf'
                    })
            return results
    except Exception as e:
        print(f"Error scraping DDG: {e}")
        return []

print(json.dumps(search_ddg_pdf("filetype:pdf Calidad Educacion Colombia")))
