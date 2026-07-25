import codecs
import re

app_path = r"c:\SIAC\app.py"
with codecs.open(app_path, 'r', 'utf-8') as f:
    app_content = f.read()

proxy_code = """
import urllib.request
import urllib.parse
import urllib.error
import json

@app.route('/api/library/search', methods=['GET'])
def library_search():
    try:
        q = request.args.get('q', '')
        if not q:
            return jsonify({'results': []})
        
        # Prepare the OpenAlex API URL
        url = f"https://api.openalex.org/works?search={urllib.parse.quote(q)}&filter=is_oa:true&per-page=20"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'SIACredit/1.0 (mailto:orbesrc@gmail.com)'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return jsonify(data)
    except Exception as e:
        print(f"Error fetching OpenAlex: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/library/saved', methods=['GET', 'POST'])
"""

app_content = app_content.replace("@app.route('/api/library/saved', methods=['GET', 'POST'])", proxy_code)

with codecs.open(app_path, 'w', 'utf-8') as f:
    f.write(app_content)

# Now modify formacion.html
html_path = r"c:\SIAC\templates\formacion.html"
with codecs.open(html_path, 'r', 'utf-8') as f:
    html_content = f.read()

html_content = html_content.replace(
    "const url = `https://api.openalex.org/works?search=${encodeURIComponent(query)}&filter=is_oa:true&per-page=20`;",
    "const url = `/api/library/search?q=${encodeURIComponent(query)}`;"
)

pattern_js_error = r'(const data = await response\.json\(\);)'
replacement_js_error = r'\1\n                if (data.error) throw new Error(data.error);'
html_content = re.sub(pattern_js_error, replacement_js_error, html_content)

with codecs.open(html_path, 'w', 'utf-8') as f:
    f.write(html_content)

print("Backend proxy injected!")
