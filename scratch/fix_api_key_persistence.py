import os

file_path = r'c:\SIAC\routes\ai.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix save_ai_config to never wipe existing ai_api_key if incoming is empty or masked
old_save_block = """        if 'ai_api_key' in data:
            current_data['ai_api_key'] = data.get('ai_api_key')"""

new_save_block = """        if 'ai_api_key' in data:
            new_key = data.get('ai_api_key', '').strip()
            if new_key and '••••' not in new_key:
                current_data['ai_api_key'] = new_key
            elif new_key == '' and 'clear_key' in data and data['clear_key']:
                current_data.pop('ai_api_key', None)"""

content = content.replace(old_save_block, new_save_block)

# Also check other key saving blocks in routes/ai.py
old_save_block_2 = """        elif 'ai_api_key' in data and data['ai_api_key'].strip():
            current_data['ai_api_key'] = data['ai_api_key'].strip()"""

new_save_block_2 = """        elif 'ai_api_key' in data:
            new_key = data['ai_api_key'].strip()
            if new_key and '••••' not in new_key:
                current_data['ai_api_key'] = new_key"""

content = content.replace(old_save_block_2, new_save_block_2)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("routes/ai.py updated so API key is NEVER wiped out by empty/masked saves!")
