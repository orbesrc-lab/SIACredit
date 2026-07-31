import sys, json
sys.path.append('c:\\SIAC')
from utils.db import supabase

res = supabase.table('statistics').select('id, data_json').eq('table_id', 'GLOBAL_CONFIG').order('id', desc=True).limit(5).execute()
print(f"Total config rows found: {len(res.data)}")
for row in res.data:
    try:
        data = json.loads(row["data_json"])
        images = data.get("carousel_images", [])
        print(f"ID: {row['id']} | Has carousel_images: {'carousel_images' in data} | Images count: {len(images)}")
        if images:
            for img in images:
                print(f"  - {img}")
    except Exception as e:
        print(f"Error reading row {row['id']}: {e}")
