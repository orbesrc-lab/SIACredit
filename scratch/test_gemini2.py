import urllib.request
import json
url = 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer AIzaSyCUzl0g6_n35SGaBoMH8cf7mvSP8TkszUg'
}
data = {
    'model': 'gemini-2.5-flash',
    'messages': [{'role': 'user', 'content': 'Actúa como par académico del CNA. Analiza los siguientes datos estadísticos del cuadro table_docentes e identifica tendencias, fortalezas o aspectos críticos. Responde directamente con el análisis en formato Markdown. Datos: [{"Periodo": "2023-2", "doctorado": "3", "maestria": "36", "especializacion": "4", "pregrado": "2", "totalDocentes": "45"}]'}],
}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode())
        print('FINISH REASON:', res['choices'][0]['finish_reason'])
        print('TEXT LENGTH:', len(res['choices'][0]['message']['content']))
        print('TEXT:', res['choices'][0]['message']['content'])
except Exception as e:
    print('ERROR:', e)
