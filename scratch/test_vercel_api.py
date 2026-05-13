import urllib.request, urllib.error
try:
    resp = urllib.request.urlopen('https://siacmcn.vercel.app/api/informe_dinamico?inst_id=1&program_id=47')
    print('Status:', resp.getcode())
    print('Body:', resp.read().decode()[:500])
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code)
    print('Error Body:', e.read().decode()[:1000])
except Exception as e:
    print('Other error:', e)
