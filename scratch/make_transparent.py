import sys
from PIL import Image

def make_transparent(input_path, output_path, tolerance=30):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    newData = []
    # Assumes white background. Top-left pixel is a good sample for background if it's a logo on white.
    # We'll just look for pixels close to white (255, 255, 255)
    for item in datas:
        # Check if pixel is close to white
        if item[0] >= 255 - tolerance and item[1] >= 255 - tolerance and item[2] >= 255 - tolerance:
            newData.append((255, 255, 255, 0)) # transparent
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(output_path, "PNG")

if __name__ == "__main__":
    make_transparent("C:\\SIAC\\logo1 skel.jpeg", "C:\\SIAC\\static\\logo_skel_transparent.png")
    print("Done")
