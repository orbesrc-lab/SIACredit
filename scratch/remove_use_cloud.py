"""
Remove all use_cloud logic from app.py since formacion_storage now handles it internally.
"""
with open('c:/SIAC/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Replace:  use_cloud = formacion_storage.IS_VERCEL or ...
# With nothing (remove the line)
content = re.sub(
    r"    use_cloud = formacion_storage\.IS_VERCEL or request\.args\.get\('use_cloud', 'false'\)\.lower\(\) == 'true'\r?\n",
    "",
    content
)

# Replace blocks like:
#     if use_cloud:
#         try:
#             formacion_storage.pull_from_supabase(inst_id, program_id, supabase)
#         except Exception as e:
#             print(f"Error pulling: {e}")
content = re.sub(
    r"    if use_cloud:\r?\n        try:\r?\n            formacion_storage\.pull_from_supabase\(inst_id, program_id(?:, supabase)?\)\r?\n        except Exception as e:\r?\n            print\(f\"Error pulling: \{e\}\"\)\r?\n",
    "",
    content
)

# Replace:
#     if use_cloud:
#         try:
#             formacion_storage.sync_courses_only(...)
#         except Exception as e:
#             print(f"Error syncing: {e}")
content = re.sub(
    r"            if use_cloud:\r?\n                try:\r?\n                    formacion_storage\.sync_courses_only\(inst_id, program_id(?:, supabase)?\)\r?\n                except Exception as e:\r?\n                    print\(f\"Error syncing: \{e\}\"\)\r?\n",
    "",
    content
)

with open('c:/SIAC/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
remaining = [i+1 for i, l in enumerate(content.splitlines()) if 'use_cloud = formacion_storage' in l]
print(f"Remaining use_cloud = formacion_storage lines: {remaining}")

# Also check if there are still use_cloud references
other_use_cloud = [i+1 for i, l in enumerate(content.splitlines()) if 'use_cloud' in l and 'formacion_storage' not in l]
print(f"Other use_cloud references: {other_use_cloud}")
