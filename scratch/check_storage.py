import sys
sys.path.append('c:\\SIAC')
from utils.db import supabase

res = supabase.storage.from_('evidencias').list('carousel')
print(f"Files found in carousel/: {len(res) if res else 0}")
for f in (res or []):
    print(f['name'])
