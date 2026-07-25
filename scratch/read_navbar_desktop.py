with open(r"c:\SIAC\static\landing.css", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print("--- landing.css Lines 30 to 80 ---")
for idx in range(30, min(80, len(lines))):
    print(f"Line {idx+1}: {lines[idx].strip()}")
