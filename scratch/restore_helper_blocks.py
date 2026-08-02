import subprocess

# 1. Fetch exact blocks from d0aaeb0
d0_full = subprocess.check_output(['git', 'show', 'd0aaeb0:templates/informes.html'], encoding='utf-8', errors='ignore')
d0_lines = d0_full.split('\n')

# Block 1: lines 1656 to 1986
block1 = '\n'.join(d0_lines[1655:1986])

# Block 2: lines 2119 to 2688
rrc_start = -1
for i, l in enumerate(d0_lines):
    if 'const RRC_CONDICIONES =' in l:
        rrc_start = i
        break

rrc_end = -1
for i in range(rrc_start, len(d0_lines)):
    if 'function updateContextBreadcrumb' in d0_lines[i] or 'function toggleSidebarGroup' in d0_lines[i]:
        rrc_end = i
        break
if rrc_end == -1:
    rrc_end = 2688

block2 = '\n'.join(d0_lines[rrc_start:rrc_end])

print(f"Block 1 size: {len(block1)} chars")
print(f"Block 2 size: {len(block2)} chars")

# Read current file
with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    curr = f.read()

# Insert Block 1 right after <script> tag opening (around line 771)
script_idx = curr.find('<script>', 42000) # main script tag
if script_idx == -1:
    print("ERROR: main script tag not found")
else:
    # Insert right after <script>
    insert_pos = curr.find('\n', script_idx) + 1
    curr_updated = curr[:insert_pos] + "\n        // ===== CHART & FACTOR HELPERS =====\n" + block1 + "\n\n" + curr[insert_pos:]
    
    # Insert Block 2 right before closing </script> tag of main block
    close_script_idx = curr_updated.find('</script>', insert_pos + len(block1) + 1000)
    if close_script_idx != -1:
        curr_updated = curr_updated[:close_script_idx] + "\n        // ===== REGISTRO CALIFICADO (RRC) HELPERS =====\n" + block2 + "\n\n" + curr_updated[close_script_idx:]
        print("Both blocks inserted successfully!")
        
        with open(r'c:\SIAC\templates\informes.html', 'w', encoding='utf-8') as f:
            f.write(curr_updated)
        print("informes.html updated!")
    else:
        print("ERROR: closing script tag not found")
