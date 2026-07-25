import sys

with open('c:/SIAC/templates/configuracion.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 2540 (0-indexed: 2539) is the mangled one-liner
# Replace the bad block (lines 2540 to where loadPartners starts)
bad_start = 2539  # 0-indexed (line 2540)

# Find where "async function loadPartners" is after bad_start
load_partners_line = None
for i in range(bad_start, min(bad_start + 5, len(lines))):
    if 'async function loadPartners' in lines[i]:
        load_partners_line = i
        break

print(f"bad_start: {bad_start}, load_partners_line: {load_partners_line}")

if load_partners_line is None:
    print("Could not find loadPartners, searching further...")
    for i in range(bad_start, bad_start + 10):
        if i < len(lines):
            print(f"  {i}: {repr(lines[i][:80])}")
