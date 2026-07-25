from rembg import remove
from PIL import Image

input_path = "c:\\SIAC\\logo1 skel.jpeg"
output_path = "c:\\SIAC\\static\\logo_skel_transparent.png"

# Use rembg to remove background
with open(input_path, 'rb') as i:
    with open(output_path, 'wb') as o:
        input_data = i.read()
        output_data = remove(input_data)
        o.write(output_data)

# Open the new transparent image and crop the bounding box
img = Image.open(output_path)
bbox = img.getbbox()
if bbox:
    img = img.crop(bbox)
    img.save(output_path)
print("Background removed and cropped successfully.")
