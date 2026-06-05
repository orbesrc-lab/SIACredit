import subprocess

res = subprocess.run(['git', 'show', 'b7082b002d2766c92e0e8682bad51ff6d23a8a98'], capture_output=True, text=True, encoding='utf-8', errors='ignore')
lines = res.stdout.split('\n')

for i, line in enumerate(lines):
    if 'uploadGridEvidence' in line:
        safe_line = line.encode('ascii', 'ignore').decode('ascii')
        print(f"Commit line {i+1}: {safe_line}")
