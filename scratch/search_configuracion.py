with open(r"c:\SIAC\templates\configuracion.html", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "style.display" in line or "card" in line.lower() or "role" in line:
        clean_line = "".join([c if ord(c) < 128 else "?" for c in line])
        if "style" in clean_line or "display" in clean_line:
            print(f"Line {i+1}: {clean_line.strip()}")
