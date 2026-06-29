import html.parser

class DivTracker(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            self.depth += 1

    def handle_endtag(self, tag):
        if tag == 'div':
            self.depth -= 1
            if self.depth < 0:
                print(f"Warning: Depth dropped to {self.depth} at line {self.getpos()[0]}")

parser = DivTracker()
with open(r"c:\SIAC\templates\formacion.html", "r", encoding="utf-8") as f:
    parser.feed(f.read())
