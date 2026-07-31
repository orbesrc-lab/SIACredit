import re

with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The injected script looks like this:
injected_script = '''
<script>
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

# We also need to consider whitespace variations.
# Let's use a regex to find all <script> tags containing toggleSidebarGroup and remove them.
content = re.sub(r'<script>\s*function toggleSidebarGroup\(element\) \{.*?\<\/script>\s*', '', content, flags=re.DOTALL)

# But we still need ONE valid copy at the very end of the file.
content = content.replace('</body>\n</html>', injected_script + '\n</body>\n</html>')

with open(r'c:\SIAC\templates\informes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('informes.html cleaned up!')
