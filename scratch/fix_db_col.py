import os

file_path = r'c:\SIAC\routes\business.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix get_matrix
content = content.replace("select('data')", "select('data_json')")
content = content.replace("res.data[0]['data']", "res.data[0]['data_json']")

# Fix save_matrix
content = content.replace("'data': data", "'data_json': data")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed routes/business.py to use data_json")
