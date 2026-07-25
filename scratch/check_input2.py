with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the submission modal textarea to see its class
idx = html.find('id="subContent"')
if idx >= 0:
    print("subContent context:")
    print(html[max(0,idx-100):idx+200].encode('ascii','ignore').decode('ascii'))
else:
    print("subContent not found")

# Find all inline styled inputs near existing modals
idx2 = html.find('id="gradeFeedback"')
if idx2 >= 0:
    print("\ngradeFeedback context:")
    print(html[max(0,idx2-100):idx2+200].encode('ascii','ignore').decode('ascii'))

# Check CSS for existing input styles
import re
style_blocks = re.findall(r'<style>(.*?)</style>', html, re.DOTALL)
for sb in style_blocks:
    if 'input' in sb.lower() or 'textarea' in sb.lower():
        # find relevant lines
        for line in sb.split('\n'):
            if 'input' in line.lower() or 'textarea' in line.lower() or 'form-' in line:
                print(line.encode('ascii','ignore').decode('ascii'))
