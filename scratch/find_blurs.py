with open(r"c:\SIAC\static\landing.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("--- Occurrences of 'blur' in landing.css ---")
for idx, line in enumerate(lines):
    if "blur" in line:
        print(f"Line {idx+1}: {line.strip()}")
