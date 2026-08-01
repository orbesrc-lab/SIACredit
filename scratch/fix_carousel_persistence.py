import os
import sys
sys.path.append(r'c:\SIAC')

from utils.db import supabase
import json

# 1. Update routes/ai.py to preserve carousel_images unless explicitly cleared
file_ai = r'c:\SIAC\routes\ai.py'
with open(file_ai, 'r', encoding='utf-8') as f:
    content_ai = f.read()

old_carousel_save = "if 'carousel_images' in data: current_data['carousel_images'] = data.get('carousel_images')"
new_carousel_save = """if 'carousel_images' in data:
            c_imgs = data.get('carousel_images')
            if c_imgs and len(c_imgs) > 0:
                current_data['carousel_images'] = c_imgs
            elif data.get('clear_carousel'):
                current_data['carousel_images'] = []"""

if old_carousel_save in content_ai:
    content_ai = content_ai.replace(old_carousel_save, new_carousel_save)
    with open(file_ai, 'w', encoding='utf-8') as f:
        f.write(content_ai)
    print("routes/ai.py updated so carousel_images is NEVER accidentally wiped!")

# 2. Ensure GLOBAL_CONFIG in Supabase DB has valid carousel_images
res = supabase.table('statistics').select('id, data_json').eq('table_id', 'GLOBAL_CONFIG').order('id', desc=True).limit(1).execute()
if res.data:
    row = res.data[0]
    data = json.loads(row['data_json'])
    
    # Check if carousel_images exists and has images
    if 'carousel_images' not in data or not data['carousel_images']:
        data['carousel_images'] = [
            "/static/uploads/carousel_1.jpg",
            "/static/uploads/carousel_2.jpg",
            "/static/uploads/carousel_3.jpg"
        ]
        data['carousel_speed'] = 3
        data['carousel_size'] = 'medium'
        
        supabase.table('statistics').update({"data_json": json.dumps(data)}).eq("id", row['id']).execute()
        print(f"Updated GLOBAL_CONFIG row {row['id']} with default carousel_images!")
    else:
        print("GLOBAL_CONFIG already has carousel_images:", data['carousel_images'])
