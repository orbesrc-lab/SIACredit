import html.parser

class DivTracker(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            self.depth += 1
            print(f"L{self.getpos()[0]}: <div ...> depth {self.depth}")

    def handle_endtag(self, tag):
        if tag == 'div':
            print(f"L{self.getpos()[0]}: </div> depth {self.depth - 1}")
            self.depth -= 1

parser = DivTracker()
with open(r"c:\SIAC\templates\formacion.html", "r", encoding="utf-8") as f:
    parser.feed(f.read())
