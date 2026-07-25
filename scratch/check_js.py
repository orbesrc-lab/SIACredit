import re
import sys
import os
import subprocess

with open(r"c:\SIAC\templates\formacion.html", "r", encoding="utf-8") as f:
    content = f.read()

scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
if scripts:
    with open(r"c:\SIAC\scratch\formacion_script.js", "w", encoding="utf-8") as f:
        f.write(scripts[0])
    
    print("Script extracted. Attempting to check syntax using node...")
    try:
        result = subprocess.run(["node", "-c", r"c:\SIAC\scratch\formacion_script.js"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Syntax OK!")
        else:
            print("Syntax Error:")
            print(result.stderr)
    except Exception as e:
        print("Node not found or error:", e)
else:
    print("No script found.")
