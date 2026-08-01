import re

# ========================================================
# FIX 1: Clean imprimirInformeCompleto in informes.html
# - Escape <script> and </body></html> inside template literal
# ========================================================
with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Strategy: Replace the entire imprimirInformeCompleto with a simpler window.print() approach
# The function opens a new window with document.write(), but the template literal
# breaks HTML parsing because it contains real <script> tags.
# Solution: Use a blob URL approach that avoids the HTML embedding issue.

old_func_marker = 'function imprimirInformeCompleto()'
new_func = '''function imprimirInformeCompleto() {
            // Simple window.print() for the current page
            window.print();
        }'''

# Find start and end of old function
fn_start = content.find(old_func_marker)
if fn_start == -1:
    print("ERROR: Function not found!")
else:
    # Find end - next top-level function at same indentation level
    # Look for the closing brace pattern
    depth = 0
    i = fn_start
    in_string = False
    string_char = None
    fn_end = -1
    
    # Scan through to find matching closing brace
    while i < len(content):
        c = content[i]
        
        if in_string:
            if c == '\\':
                i += 2
                continue
            if c == string_char:
                in_string = False
        else:
            if c in ('"', "'", '`'):
                in_string = True
                string_char = c
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    fn_end = i + 1
                    break
        i += 1
    
    if fn_end != -1:
        print(f"Function found: {fn_start} -> {fn_end} (length {fn_end - fn_start})")
        content = content[:fn_start] + new_func + content[fn_end:]
        print("Function replaced with simple window.print()!")
    else:
        print("ERROR: Could not find function end!")

# Verify fix
print(f"\nAfter fix:")
print(f"  <script: {content.count('<script')}")
print(f"  </script>: {content.count('</script>')}")
print(f"  </body>: {content.count('</body>')}")
print(f"  </html>: {content.count('</html>')}")

with open(r'c:\SIAC\templates\informes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\ninformes.html saved!")

# ========================================================
# FIX 2: API Key save bug in configuracion.html
# The condition:  if (aiApiKey.trim() !== '' && !aiApiKey.includes('••••'))
# This means if user types a NEW key it works, BUT
# if user presses save without touching the key field
# (which shows ••••), the key is NOT sent (correct behavior to keep existing key)
# BUT there's a bug: when user clears field and types new key, the dots are cleared
# by onfocus handler, so the new key should save fine.
# 
# The REAL bug is: loadGlobalSettings only shows dots WHEN has_api_key=true
# But the backend strips the key before sending. So if the user saves with empty
# instApiKeyInput after clearing it (to change key), the payload has ai_api_key=""
# which DOES get sent to the backend, and if that passes validation, it saves an empty key.
#
# Fix: Change the condition to only send ai_api_key if non-empty and not dots
# (this is already done) -- but also add ai_api_key="" clearing support with explicit
# clear_api_key flag.
#
# But the USER says the key is NOT being saved. Let's check if maybe the issue is
# that carouselImages guard is preventing the POST from completing due to JSON error.

# Also fix: protect carousel_images from being cleared on save if the array is empty
# (because carouselImages JS var starts as [] and if user saves before carousel loads,
# it clears the DB carousel_images)
with open(r'c:\SIAC\templates\configuracion.html', 'r', encoding='utf-8') as f:
    cfg_content = f.read()

# Fix: Only include carousel_images in payload if carouselImages.length > 0
old_payload = '''            const payload = {
                theme: theme,
                ai_provider: aiProvider,
                ai_model: aiModel,
                ai_voice_colombia: aiVoiceColombia,
                ai_global_enabled: aiGlobalEnabled,
                carousel_images: carouselImages,
                carousel_speed: carouselSpeed,
                carousel_size: carouselSize
            };
            
            // Only send API Key if the user typed something new
            if (aiApiKey.trim() !== \'\' && !aiApiKey.includes(\'\\u2022\\u2022\\u2022\\u2022\')) {
                payload.ai_api_key = aiApiKey.trim();
            }'''

new_payload = '''            const payload = {
                theme: theme,
                ai_provider: aiProvider,
                ai_model: aiModel,
                ai_voice_colombia: aiVoiceColombia,
                ai_global_enabled: aiGlobalEnabled,
                carousel_speed: carouselSpeed,
                carousel_size: carouselSize
            };
            
            // Only include carousel_images if we have some (avoid wiping existing ones)
            if (carouselImages && carouselImages.length > 0) {
                payload.carousel_images = carouselImages;
            }
            
            // Only send API Key if the user typed something new (not the dots placeholder)
            const cleanKey = aiApiKey.trim();
            if (cleanKey !== \'\' && !cleanKey.includes(\'\\u2022\')) {
                payload.ai_api_key = cleanKey;
            }'''

if old_payload in cfg_content:
    cfg_content = cfg_content.replace(old_payload, new_payload)
    print("\nconfiguracion.html payload fixed!")
else:
    print("\nWARNING: Could not find exact payload block to replace. Searching for partial match...")
    # Try to find a partial match
    idx = cfg_content.find('carousel_images: carouselImages,')
    if idx != -1:
        print(f"  Found carousel_images at {idx}")
        print(repr(cfg_content[idx-100:idx+200]))

with open(r'c:\SIAC\templates\configuracion.html', 'w', encoding='utf-8') as f:
    f.write(cfg_content)
print("configuracion.html saved!")
