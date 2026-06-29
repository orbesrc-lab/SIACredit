import os

file_path = r"c:\SIAC\templates\formacion.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace padding-bottom hack with aspect-ratio in inline styles
content = content.replace(
    'padding-bottom:56.25%; height:0;',
    'aspect-ratio:16/9; width:100%; height:auto;'
)

# Replace padding-bottom hack in JS template literals
content = content.replace(
    'padding-bottom: 56.25%; height: 0;',
    'aspect-ratio: 16/9; width: 100%; height: auto;'
)

# Also ensure max-width is constrained on mobile via CSS
css_addition = """
        @media (max-width: 768px) {
            .topic-content-body iframe,
            .topic-content-body video,
            div[id^="acc_"] iframe,
            div[id^="acc_"] video {
                max-width: calc(100vw - 60px) !important;
            }
        }
"""

if 'max-width: calc(100vw - 60px) !important;' not in content:
    content = content.replace('</style>', css_addition + '</style>')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Inline responsive media styles fixed.")
