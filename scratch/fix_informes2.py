import re

with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all injected scripts first
content = re.sub(r'<script>\s*function toggleSidebarGroup\(element\) \{.*?\<\/script>\s*', '', content, flags=re.DOTALL)

injected_script = '''<script>
function toggleSidebarGroup(element) {
const group = element.parentElement;
const allGroups = document.querySelectorAll('.sidebar-group');
allGroups.forEach(g => {
if(g !== group) g.classList.remove('active');
});
group.classList.toggle('active');
}
</script>
'''

# We want to inject it ONLY right before the FINAL </body> tag.
# We can do an rsplit to replace only the last occurrence.
parts = content.rsplit('</body>', 1)
if len(parts) == 2:
    content = parts[0] + injected_script + '</body>' + parts[1]
else:
    print('Error: could not find final </body> tag')

with open(r'c:\SIAC\templates\informes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('informes.html cleaned up for real!')
