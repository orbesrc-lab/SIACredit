with open(r"c:\SIAC\static\landing.css", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print("--- landing.css Lines 390 to 450 ---")
for idx in range(390, min(450, len(lines))):
    print(f"Line {idx+1}: {lines[idx].strip()}")
