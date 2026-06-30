import os
from PIL import Image
import glob

static_dir = r"c:\SIAC\static"
png_files = glob.glob(os.path.join(static_dir, "*.png"))

for file_path in png_files:
    file_size = os.path.getsize(file_path)
    if file_size > 500 * 1024: # > 500KB
        webp_path = file_path.replace(".png", ".webp")
        print(f"Compressing {os.path.basename(file_path)} ({file_size/1024/1024:.2f} MB)...")
        try:
            with Image.open(file_path) as img:
                # Convert RGBA to RGB if saving as webp and you want smaller size,
                # but webp supports alpha. Let's keep alpha just in case.
                img.save(webp_path, "webp", quality=80, method=6)
            new_size = os.path.getsize(webp_path)
            print(f" -> Saved {os.path.basename(webp_path)} ({new_size/1024/1024:.2f} MB)")
        except Exception as e:
            print(f"Error compressing {file_path}: {e}")
