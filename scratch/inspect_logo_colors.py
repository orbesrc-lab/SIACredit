from PIL import Image
from collections import Counter

def inspect():
    img_path = r"c:\SIAC\static\logo skel.webp"
    img = Image.open(img_path)
    img_rgba = img.convert("RGBA")
    pixels = list(img_rgba.getdata())
    
    # Filter for pixels that are NOT fully transparent (alpha > 0)
    visible_pixels = [p for p in pixels if p[3] > 0]
    
    counter = Counter(visible_pixels)
    print("\nTop 50 most common VISIBLE colors (alpha > 0):")
    for color, count in counter.most_common(50):
        print(f"Color: {color}, Count: {count}")

if __name__ == "__main__":
    inspect()
