with open(r"c:\SIAC\templates\index.html", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

import re
scripts = re.findall(r"<script.*?>.*?</script>", content, re.DOTALL | re.IGNORECASE)
print(f"Found {len(scripts)} script tags in index.html:")
for i, s in enumerate(scripts):
    print(f"\n--- Script {i+1} ---")
    print(s[:300] + "..." if len(s) > 300 else s)
