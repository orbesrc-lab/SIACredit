import urllib.request, urllib.error, json

req = urllib.request.Request(
    'https://siacmcn.vercel.app/api/informe_dinamico?inst_id=1&program_id=47',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
)

try:
    resp = urllib.request.urlopen(req)
    print('Status:', resp.getcode())
    print('Body:', resp.read().decode()[:500])
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code)
    print('Error Body:', e.read().decode()[:1000])
except Exception as e:
    print('Other error:', e)
