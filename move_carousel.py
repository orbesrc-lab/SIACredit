import sys

with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if '{% if config and config.carousel_images %}' in line:
        start_idx = i
    if '        {% endif %}' in line and start_idx != -1 and i > start_idx:
        end_idx = i
        break

if start_idx == -1 or end_idx == -1:
    print("Could not find carousel block")
    sys.exit(1)

carousel_block = lines[start_idx:end_idx+1]
del lines[start_idx:end_idx+1]

insert_idx = -1
for i, line in enumerate(lines):
    if '<div class="smart-features-grid">' in line:
        insert_idx = i
        break

if insert_idx == -1:
    print("Could not find insert point")
    sys.exit(1)

lines.insert(insert_idx, '\n')
for line in reversed(carousel_block):
    lines.insert(insert_idx, line)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Carousel moved successfully.")
