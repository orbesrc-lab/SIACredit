with open(r"c:\SIAC\templates\configuracion.html", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "loadAllInstitutions" in line or "loadAllPrograms" in line:
        clean_line = "".join([c if ord(c) < 128 else "?" for c in line])
        print(f"Line {i+1}: {clean_line.strip()}")
