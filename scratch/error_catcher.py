import http.server
import socketserver
import urllib.parse
import sys

class LoggerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/log'):
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            print(f"JS ERROR: {query.get('msg', [''])[0]} at line {query.get('line', [''])[0]}")
            sys.exit(0)
        return super().do_GET()

with socketserver.TCPServer(("", 8080), LoggerHandler) as httpd:
    print("Serving at port 8080")
    httpd.serve_forever()
