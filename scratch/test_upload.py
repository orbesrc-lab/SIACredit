import requests
res = requests.post('http://127.0.0.1:5000/api/global-settings/carousel-upload', files={'image': ('test.jpg', b'dummy_content')})
print(res.status_code, res.text)
