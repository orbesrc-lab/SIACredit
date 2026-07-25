import os

path = r"c:\SIAC\static\landing.css"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Normalize line endings
content_norm = content.replace("\r\n", "\n")

idx = content_norm.find(".navbar {")
if idx != -1:
    # Find the next z-index: 999;
    idx_z = content_norm.find("z-index: 999;", idx)
    if idx_z != -1 and idx_z < idx + 100: # ensure it's within the navbar block
        new_content = content_norm[:idx_z] + "z-index: 1050;" + content_norm[idx_z + len("z-index: 999;"):]
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("SUCCESS: navbar z-index updated fuzzily!")
    else:
        print("ERROR: z-index not found near navbar class!")
else:
    print("ERROR: navbar class not found!")
