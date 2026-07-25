import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    url = "https://phet.colorado.edu/services/metadata/1.2/simulations?format=json&type=html&locale=es"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode('utf-8'))
        print(f"Projects found: {len(data.get('projects', []))}")
        if data.get('projects'):
            first_proj = data['projects'][0]
            print(f"First project subjects: {[s.get('name') for s in first_proj.get('subjects', [])]}")
            for sim in first_proj.get('simulations', [])[:2]:
                print(f"Sim name: {sim.get('name')}")
                title = sim.get('localizedTitles', {}).get('es') or sim.get('localizedTitles', {}).get('en')
                print(f"Title: {title}")
                desc = sim.get('description', {}).get('es') or sim.get('description', {}).get('en')
                print(f"Desc: {str(desc)[:50]}...")
except Exception as e:
    print(f"Error: {e}")
