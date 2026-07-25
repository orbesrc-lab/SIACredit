import codecs
import re

app_path = r"c:\SIAC\app.py"
with codecs.open(app_path, 'r', 'utf-8') as f:
    app_content = f.read()

ovas_code = """
@app.route('/api/library/ovas', methods=['GET'])
def get_ovas():
    try:
        url = "https://phet.colorado.edu/services/metadata/1.2/simulations?format=json&type=html&locale=es"
        req = urllib.request.Request(url, headers={'User-Agent': 'SIACredit/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            sims = []
            for proj in data.get('projects', []):
                for sim in proj.get('simulations', []):
                    title = sim.get('title', 'Sin título')
                    if 'es' in sim.get('localizedTitles', {}):
                        title = sim['localizedTitles']['es']
                    elif 'en' in sim.get('localizedTitles', {}):
                        title = sim['localizedTitles']['en']
                        
                    sims.append({
                        'id': sim.get('name', ''),
                        'title': title,
                        'description': sim.get('description', {}).get('es', sim.get('description', {}).get('en', 'Simulador interactivo PhET')),
                        'runUrl': f"https://phet.colorado.edu/sims/html/{sim.get('name')}/latest/{sim.get('name')}_es.html",
                        'thumbUrl': f"https://phet.colorado.edu/sims/html/{sim.get('name')}/latest/{sim.get('name')}-600.png"
                    })
            
            # Sort by title
            sims.sort(key=lambda x: x['title'])
            return jsonify({'status': 'success', 'ovas': sims})
    except Exception as e:
        print(f"Error fetching OVAs: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/library/saved', methods=['GET', 'POST'])
"""

app_content = app_content.replace("@app.route('/api/library/saved', methods=['GET', 'POST'])", ovas_code)

with codecs.open(app_path, 'w', 'utf-8') as f:
    f.write(app_content)

print("Backend OVA endpoint injected!")
