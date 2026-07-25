import json
import urllib.request
import os
import sys

sys.path.append('c:\\SIAC')
from utils.db import supabase

check = supabase.table('statistics').select('data_json').eq('table_id', 'GLOBAL_CONFIG').order('id', desc=True).limit(1).execute()
data = json.loads(check.data[0]['data_json'])
api_key = data.get('ai_api_key')

url = 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}
payload = {
    'model': 'gemini-flash-latest',
    'messages': [{'role': 'user', 'content': 'Hello'}]
}

try:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method='POST')
    with urllib.request.urlopen(req) as response:
        print('SUCCESS:', response.read().decode())
except Exception as e:
    print('ERROR Bearer:', e.read().decode() if hasattr(e, 'read') else str(e))

# Test with ?key= in the URL instead of Bearer
url_with_key = f'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions?key={api_key}'
headers_no_bearer = {
    'Content-Type': 'application/json'
}
try:
    req = urllib.request.Request(url_with_key, data=json.dumps(payload).encode(), headers=headers_no_bearer, method='POST')
    with urllib.request.urlopen(req) as response:
        print('SUCCESS key=:', response.read().decode())
except Exception as e:
    print('ERROR key=:', e.read().decode() if hasattr(e, 'read') else str(e))

