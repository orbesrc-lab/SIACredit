from PIL import Image

def convert_transparent():
    img_path = r"c:\SIAC\static\logo skel.webp"
    img = Image.open(img_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    # Make black pixels transparent
    for item in datas:
        r, g, b, a = item
        if r < 35 and g < 35 and b < 35:
            # Make it fully transparent
            new_data.append((r, g, b, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    
    # Automatically crop out transparent borders to maximize the logo size!
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        print(f"Image cropped to bounding box: {bbox}")

    img.save(img_path, "WEBP")
    print("Logo processed, cropped and saved as transparent webp!")

if __name__ == "__main__":
    convert_transparent()
