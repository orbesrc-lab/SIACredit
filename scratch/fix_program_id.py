import os

file_path = r'c:\SIAC\routes\business.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace 'program_id': 0 with 'program_id': None in save_matrix
content = content.replace("'program_id': 0,", "'program_id': None,")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed program_id constraint issue in routes/business.py")
