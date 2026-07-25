import bs4

def analyze():
    with open(r"c:\SIAC\templates\formacion.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = bs4.BeautifulSoup(html, "html5lib")
    
    viewer = soup.find(id="studentCourseViewer")
    print(f"studentCourseViewer is in DOM: {viewer is not None}")
    
    # print direct children of studentCourseViewer
    for child in viewer.find_all(recursive=False):
        print(f"Child: {child.name} id={child.get('id')} class={child.get('class')}")
        
    print("---")
    
    # print direct children of settings-card
    settings_card = soup.find(class_="settings-card")
    print(f"settings-card is in DOM: {settings_card is not None}")
    for child in settings_card.find_all(recursive=False):
        print(f"Settings Card Child: {child.name} id={child.get('id')} class={child.get('class')}")
        
if __name__ == "__main__":
    analyze()
