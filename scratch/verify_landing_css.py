with open(r"c:\SIAC\static\landing.css", "r", encoding="utf-8") as f:
    content = f.read()

if "-webkit-backdrop-filter: blur(20px)" in content:
    print("SUCCESS: Found newly added responsive mobile styles!")
else:
    print("WARNING: Could not find responsive styles inside landing.css!")
