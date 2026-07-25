import json

with open('c:/SIAC/scratch/tables.json', 'r', encoding='utf-16') as f:
    data = json.load(f)

with open('c:/SIAC/scratch/table_headers.txt', 'w', encoding='utf-8') as out:
    for t in data:
        if t["data"]:
            out.write(f"Table {t['index']}: {t['data'][0]}\n")
