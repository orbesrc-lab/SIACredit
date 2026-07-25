import re

with open('c:/SIAC/routes/ai.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace exact matches of "INST_AI_CONFIG" with f"INST_AI_CONFIG_{inst_id}" in specific query lines
content = content.replace('eq("table_id", "INST_AI_CONFIG")', 'eq("table_id", f"INST_AI_CONFIG_{inst_id}")')
content = content.replace('table_id": "INST_AI_CONFIG"', 'table_id": f"INST_AI_CONFIG_{inst_id}"')

# For the status_all query, we need to fetch using `.like`
old_status_query = '''configs = supabase.table('statistics').select("inst_id, data_json").eq("table_id", "INST_AI_CONFIG").execute()'''
new_status_query = '''configs = supabase.table('statistics').select("inst_id, data_json").like("table_id", "INST_AI_CONFIG_%").execute()'''
content = content.replace(old_status_query, new_status_query)

with open('c:/SIAC/routes/ai.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced successfully.")
