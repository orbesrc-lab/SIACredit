from config import supabase; res = supabase.table('statistics').select('data_json').eq('table_id', 'GLOBAL_CONFIG').order('id', desc=True).limit(1).execute(); print(res.data)
