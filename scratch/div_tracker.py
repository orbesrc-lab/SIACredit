import html.parser

class DivTracker(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.log = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            self.depth += 1
            attr_dict = dict(attrs)
            if 'id' in attr_dict or 'class' in attr_dict:
                self.log.append(f"<{tag} id='{attr_dict.get('id', '')}' class='{attr_dict.get('class', '')}'> -> depth {self.depth}")

    def handle_endtag(self, tag):
        if tag == 'div':
            self.log.append(f"</{tag}> -> depth {self.depth - 1}")
            self.depth -= 1

parser = DivTracker()
with open(r"c:\SIAC\templates\formacion.html", "r", encoding="utf-8") as f:
    parser.feed(f.read())

# Let's find "coursesTab" and see its depth.
for i, line in enumerate(parser.log):
    if "id='coursesTab'" in line:
        start_idx = max(0, i - 5)
        for j in range(start_idx, i + 50):
            if j < len(parser.log):
                print(parser.log[j])
        print("...")
        break

print("\n--- Looking for studentClassroom ---")
for i, line in enumerate(parser.log):
    if "id='studentClassroom'" in line:
        start_idx = max(0, i - 15)
        for j in range(start_idx, i + 15):
            if j < len(parser.log):
                print(parser.log[j])
        break

