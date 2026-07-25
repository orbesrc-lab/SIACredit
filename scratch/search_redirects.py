import os
import re

patterns = {
    "eval": r"\beval\b",
    "base64/atob/btoa": r"\b(atob|btoa)\b",
    "String.fromCharCode": r"String\.fromCharCode",
    "unescape": r"\bunescape\b",
    "location.replace/href": r"location\.(replace|href)\s*=",
    "iframe": r"<iframe",
    "suspicious script": r"<script[^>]*src=\"http[s]?://(?!(cdn\.jsdelivr\.net|fonts\.googleapis\.com|wa\.me|www\.gstatic\.com|code\.jquery\.com|cdn\.socket\.io|unpkg\.com|cdnjs\.cloudflare\.com)).*\""
}

workspace = r"c:\SIAC"

for root, dirs, files in os.walk(workspace):
    # Skip git and cache dirs
    if ".git" in root or "__pycache__" in root or ".gemini" in root or "scratch" in root:
        continue
    for file in files:
        if file.endswith((".html", ".js", ".py", ".css")):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                for name, pattern in patterns.items():
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    if matches:
                        for m in matches[:5]: # Print first 5 matches
                            start = max(0, m.start() - 40)
                            end = min(len(content), m.end() + 40)
                            snippet = content[start:end].replace("\n", " ")
                            print(f"[SUSPICIOUS] {file} - Pattern '{name}': ... {snippet.strip()} ...")
            except Exception as e:
                pass
