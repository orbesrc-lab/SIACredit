import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

sb = create_client(url, key)

try:
    print("Testing insert with program_id = None (NULL)...")
    res = sb.table('statistics').insert({
        "table_id": "TEST_NULL_PROGRAM",
        "data_json": "{}",
        "inst_id": 1,
        "program_id": None
    }).execute()
    print("Insert success! Inserted ID:", res.data[0]['id'])
    
    # Delete the test row
    print("Cleaning up test row...")
    sb.table('statistics').delete().eq("id", res.data[0]['id']).execute()
    print("Cleanup success!")
except Exception as e:
    print("Insert failed:", e)
