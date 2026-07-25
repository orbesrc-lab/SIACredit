with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Search in style blocks only
import re
style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
if style_match:
    css = style_match.group(1)
    print("=== CSS LENGTH:", len(css))
    # Find anything with 'modal'
    for i, line in enumerate(css.split('\n')):
        if 'modal' in line.lower() or 'overlay' in line.lower():
            print(f"Line {i}: {line.encode('ascii','ignore').decode('ascii')}")
else:
    print("No style block found")
    
# Also check if there's a linked CSS file
links = re.findall(r'<link[^>]+href="([^"]*\.css[^"]*)"', html)
print("\nLinked CSS files:", links)
