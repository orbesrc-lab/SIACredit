import os

file_path = r'c:\SIAC\routes\business.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        if res.data:
            return jsonify({'data': res.data[0]['data_json']})'''

replacement = '''        if res.data:
            import json
            data_val = res.data[0]['data_json']
            if isinstance(data_val, str):
                try:
                    data_val = json.loads(data_val)
                except:
                    pass
            return jsonify({'data': data_val})'''

content = content.replace(target, replacement)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed get_matrix string parsing in business.py")
