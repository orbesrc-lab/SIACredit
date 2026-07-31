import os
from config.db import supabase

try:
    res = supabase.table('business_matrices').select('*').limit(1).execute()
    print("Table exists, data:", res.data)
except Exception as e:
    print("Error:", e)
