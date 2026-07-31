import sys, json
sys.path.append('c:\\SIAC')
from utils.db import supabase

# Get images
res_img = supabase.storage.from_('evidencias').list('carousel')
imgs = [supabase.storage.from_('evidencias').get_public_url(f"carousel/{x['name']}") for x in res_img if x['name'] != '.emptyFolderPlaceholder']
imgs = imgs[:3] # take first 3

# Get latest config
res = supabase.table('statistics').select('id, data_json').eq('table_id', 'GLOBAL_CONFIG').order('id', desc=True).limit(1).execute()
if res.data:
    row_id = res.data[0]['id']
    data = json.loads(res.data[0]['data_json'])
    data['carousel_images'] = imgs
    # Update DB
    supabase.table('statistics').update({"data_json": json.dumps(data)}).eq('id', row_id).execute()
    print("Injected images successfully!")
else:
    print("No global config found.")
