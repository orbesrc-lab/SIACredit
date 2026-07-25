import re
import subprocess

def test_js():
    with open('c:\\SIAC\\templates\\backup.html', 'r', encoding='utf-8') as f:
        html = f.read()
    scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
    for i, script in enumerate(scripts):
        with open(f'c:\\SIAC\\scratch\\test_{i}.js', 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"Testing script {i}...")
        try:
            subprocess.run(['node', '-c', f'c:\\SIAC\\scratch\\test_{i}.js'], check=True)
            print("OK")
        except Exception as e:
            print("Error:", e)
            
if __name__ == '__main__':
    test_js()
