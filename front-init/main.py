import mimetypes
import urllib.parse
import logging
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
HTTP_PORT = 3000
HTTP_HOST = 'localhost'

env = Environment(loader=FileSystemLoader(str(BASE_DIR / 'templates')))

class HomeFramework(BaseHTTPRequestHandler):

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case '/':
                self.send_html('index.html')
            case '/message':
                self.send_html('message.html')
            case _:
                static_path = None
                # Serve CSS
                if route.path.startswith('/css/'):
                    static_path = BASE_DIR / route.path[1:]
                # Serve images
                elif route.path.startswith('/img/'):
                    static_path = BASE_DIR / route.path[1:]
                else:
                    self.send_html('error.html', 404)
                    return

                if static_path and static_path.exists():
                    self.send_static(static_path)
                else:
                    self.send_html('error.html', 404)

    def send_html(self, template_name, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        template = env.get_template(template_name)
        html = template.render()
        self.wfile.write(html.encode('utf-8'))

    def send_static(self, filepath, status_code=200):
        self.send_response(status_code)
        mime_type, *_ = mimetypes.guess_type(str(filepath))
        self.send_header('Content-Type', mime_type or 'application/octet-stream')
        self.end_headers()
        with open(filepath, 'rb') as file:
            self.wfile.write(file.read())

def run_http_server(host, port):
    address = (host, port)
    http_server = HTTPServer(address, HomeFramework)
    logging.info("Starting http server")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        http_server.server_close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    server = Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT))
    server.start()
