import json
import os

msg_dir = r"C:\Users\John Orbes\.gemini\antigravity-ide\brain\fab1ba3d-6578-4a7d-85da-af946c12ec3a\.system_generated\messages"
for f_name in ["43746336-f34a-4167-920d-360dbfa1be8f.json", "70a769c4-9c02-4078-9df4-a087774f7a47.json"]:
    path = os.path.join(msg_dir, f_name)
    if os.path.exists(path):
        print(f"--- CONTENT OF {f_name} ---")
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Pretty print the json data
            print(json.dumps(data, indent=2, ensure_ascii=False))
        print("="*60)
