import urllib.request, json
url = 'https://skel360.online/api/courses?inst_id=1&program_id=0'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as r:
        courses = json.loads(r.read())
        print(f"Total returned: {len(courses)}")
        if courses:
            print("Type of first item:", type(courses[0]))
            print("First item:", repr(courses[0]))
except Exception as e:
    print('Error:', e)
