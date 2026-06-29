import bs4

def analyze():
    with open(r"c:\SIAC\templates\formacion.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = bs4.BeautifulSoup(html, "html5lib")
    
    viewer = soup.find(id="globalLibraryContainer")
    if not viewer:
        print("globalLibraryContainer NOT FOUND!")
        return
        
    print("Ancestors of globalLibraryContainer:")
    parent = viewer.parent
    while parent and parent.name != "body":
        if parent.name == "div":
            id_val = parent.get("id", "")
            class_val = parent.get("class", [])
            print(f"-> div id='{id_val}' class='{class_val}'")
        else:
            print(f"-> {parent.name}")
        parent = parent.parent

if __name__ == "__main__":
    analyze()
