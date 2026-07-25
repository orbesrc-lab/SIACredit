import os

path = r"c:\SIAC\static\landing.css"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

target = """.navbar {
position: sticky; top: 0; z-index: 999;"""

replacement = """.navbar {
position: sticky; top: 0; z-index: 1050;"""

# Clean line endings
clean_content = content.replace("\r\n", "\n")
clean_target = target.replace("\r\n", "\n")
clean_replacement = replacement.replace("\r\n", "\n")

if clean_target in clean_content:
    new_content = clean_content.replace(clean_target, clean_replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("SUCCESS: landing.css navbar z-index updated successfully!")
else:
    print("ERROR: Target navbar z-index string not found!")
