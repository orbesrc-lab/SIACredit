with open(r"c:\SIAC\static\landing.css", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print("--- Searching mobile styles in landing.css ---")
in_media = False
braces = 0
for i, line in enumerate(lines):
    if "@media" in line or "mobile-menu" in line or "nav-links" in line or "hamburger" in line:
        print(f"Line {i+1}: {line.strip()}")
