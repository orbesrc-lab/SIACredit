import re

with open('templates/formacion.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the first 768px media query with 950px
content = content.replace('@media (max-width: 768px) {', '@media (max-width: 950px) {')
content = content.replace('.user-grid, .grid-catalog {', '.user-grid {')
content = content.replace('grid-template-columns: 1fr !important;\n            }\n            .content-area', 'grid-template-columns: 1fr !important;\n            }\n            .grid-catalog {\n                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)) !important;\n                gap: 15px !important;\n            }\n            .content-area')

# Find the end of the first 950px media query and append the topic-content-body fixes
content = content.replace('.form-grid {\n                grid-template-columns: 1fr !important;\n            }', '.form-grid {\n                grid-template-columns: 1fr !important;\n            }\n            .topic-content-body {\n                font-size: 0.9rem !important;\n                word-wrap: break-word !important;\n                overflow-wrap: break-word !important;\n                line-height: 1.4 !important;\n                padding: 0 5px;\n            }')

# Replace the second media query for the videos
content = content.replace('max-width: calc(100vw - 60px) !important;', 'max-width: calc(100vw - 40px) !important;\n                height: auto !important;\n                aspect-ratio: 16 / 9;')

# Replace the portrait one
content = content.replace('@media (max-width: 768px) and (orientation: portrait) {', '@media (max-width: 950px) and (orientation: portrait) {')

with open('templates/formacion.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated formacion.html CSS')
