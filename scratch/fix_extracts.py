import re

with open('templates/evidencias.html', 'r', encoding='utf-8') as f:
    text = f.read()

# We want to find `.push({\n    ... \n});` inside the extractFactor... functions
# A robust regex would be to find: `.push({` and then find the closing `}` before `);`
# But it's easier to just match the `\n                }` that closes the object literal.
# For example:
#                 profesores.push({
#                     periodo: inputs[0].value,
#                     ...
#                     exp: inputs[5].value
#                 });

def inject_adjunto(match):
    prefix = match.group(1)
    # the last property line, e.g. "exp: inputs[5].value"
    last_prop = match.group(2)
    # The suffix, e.g. "\n                });"
    suffix = match.group(3)
    
    # Check if adjunto is already there
    if 'adjunto:' in prefix or 'adjunto:' in last_prop:
        return match.group(0)
    
    # Inject it
    return prefix + last_prop + ",\n                    adjunto: tr.dataset.adjunto || ''" + suffix

# Regex to match the push object
# \s*push\(\{\s*(.*?)\s+([\w\s]+:\s*[^,]+?)(\s*\}\);)
# Group 1: Everything before the last property
# Group 2: The last property
# Group 3: The closing braces
# Since there are varying spaces, let's use a simpler approach:
# Replace `([^\s,])(\s*\}\);)` with `\1,\n                    adjunto: tr.dataset.adjunto || ''\2`
# But we ONLY want to do this inside the extractFactor functions!

extract_func_bodies = re.findall(r'function extractFactor.*?\{.*?(?=\n\s*function|\n\s*\</script)', text, re.DOTALL)
for body in extract_func_bodies:
    new_body = re.sub(r'([^\s,])(\s*\}\);)', r"\1,\n                    adjunto: tr.dataset.adjunto || ''\2", body)
    text = text.replace(body, new_body)

with open('templates/evidencias.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Injected adjunto into all push objects.")
