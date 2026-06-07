"""
The bracket checker is getting confused by regex patterns inside JS.
Regex like /width=\"[^\"]*\"/ contain [ and ] that confuse the checker.
Let me recheck ignoring content inside regex literals.
"""
import re

with open('c:/SIAC/templates/formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
all_js = '\n'.join(scripts)

# Remove regex literals first (they confuse bracket counting)
# Regex: /pattern/flags - simplified removal
def strip_regex_literals(text):
    # Replace content of regex literals with placeholder
    result = []
    i = 0
    while i < len(text):
        # Look for potential regex: preceded by = ( , ; [ & | ! ?
        if text[i] == '/' and i > 0 and text[i-1] in '=(,;[&|!?:':
            j = i + 1
            while j < len(text) and text[j] != '/' and text[j] != '\n':
                if text[j] == '\\':
                    j += 2  # skip escaped char
                else:
                    j += 1
            if j < len(text) and text[j] == '/':
                result.append('/REGEX/')
                i = j + 1
                # Skip flags
                while i < len(text) and text[i] in 'gimsuy':
                    i += 1
                continue
        result.append(text[i])
        i += 1
    return ''.join(result)

clean_js = strip_regex_literals(all_js)

# Now count brackets
opens = {'(': 0, '{': 0, '[': 0}
closes = {')': '(', '}': '{', ']': '['}
in_string = False
string_char = ''
escape = False

for ch in clean_js:
    if escape:
        escape = False
        continue
    if ch == '\\':
        escape = True
        continue
    if not in_string:
        if ch in ('"', "'", '`'):
            in_string = True
            string_char = ch
        elif ch in opens:
            opens[ch] += 1
        elif ch in closes:
            expected = closes[ch]
            if opens[expected] > 0:
                opens[expected] -= 1
    else:
        if ch == string_char and string_char != '`':
            in_string = False
        elif ch == '`' and string_char == '`':
            in_string = False

print(f"After removing regex literals:")
print(f"Unclosed ( = {opens['(']}")
print(f"Unclosed {{ = {opens['{']}")
print(f"Unclosed [ = {opens['[']}")
if opens['('] == 0 and opens['{'] == 0 and opens['['] == 0:
    print("\n✅ JS brackets are BALANCED - the file is OK!")
else:
    print("\n❌ Brackets still unbalanced")
