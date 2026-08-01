import sys, re

# ========================================================
# FIX 1: Restore informes.html from stable commit
# ========================================================
with open(r'c:\SIAC\scratch\informes_fef38dd.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The real issue: imprimirInformeCompleto uses document.write() with a full HTML template
# that has <script> and </body></html> INSIDE a JS template literal.
# This confuses the parser. The fix is to escape those tags inside the template literal.
# Find the imprimirInformeCompleto function
fn_start = content.find('function imprimirInformeCompleto()')
fn_end = content.find('\n    function ', fn_start + 10)
if fn_end == -1:
    fn_end = content.find('\n        function ', fn_start + 10)

print(f"imprimirInformeCompleto: {fn_start} -> {fn_end}")
fn_body = content[fn_start:fn_end]
print("Function length:", len(fn_body))
print("First 200 chars:", repr(fn_body[:200]))

# Count problematic tags inside the function
print("  <script> inside fn:", fn_body.count('<script'))
print("  </script> inside fn:", fn_body.count('</script>'))
print("  </body> inside fn:", fn_body.count('</body>'))
print("  </html> inside fn:", fn_body.count('</html>'))
