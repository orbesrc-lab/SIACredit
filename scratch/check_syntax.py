import re

with open('scratch/script_0.js', 'r', encoding='utf-8') as f:
    text = f.read()

def strip_comments_strings(text):
    # Remove single line comments
    text = re.sub(r'//.*', '', text)
    # Remove multiline comments
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    # We must be careful removing strings to not unbalance anything.
    # Actually, if we just count backticks, single quotes, double quotes
    print(f"Backticks count: {text.count('`')}")
    print(f"Single quotes count: {text.count(chr(39))}")
    print(f"Double quotes count: {text.count(chr(34))}")
    
    # Remove strings
    text = re.sub(r"`.*?`", '``', text, flags=re.DOTALL)
    text = re.sub(r"'.*?'", "''", text, flags=re.DOTALL)
    text = re.sub(r'".*?"', '""', text, flags=re.DOTALL)
    return text

cleaned = strip_comments_strings(text)
print(f"{{ count: {cleaned.count('{')}, }} count: {cleaned.count('}')}")
print(f"( count: {cleaned.count('(')}, ) count: {cleaned.count(')')}")
print(f"[ count: {cleaned.count('[')}, ] count: {cleaned.count(']')}")

# Let's find lines with unclosed parentheses if they are on same line
lines = text.split('\n')
for i, line in enumerate(lines):
    if line.count('(') != line.count(')'):
        pass # this might be noisy

