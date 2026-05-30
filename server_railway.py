import http.server
import urllib.request
import urllib.parse
import json
import os

PORT = int(os.environ.get('PORT', 8080))
API_KEY = 'Bi0yZ1iLm5pleggEpjdIVOfsgmyozIomwihPf0gAl7oppNl7ZWIK'
SARAMIN_BASE = 'https://oapi.saramin.co.kr/job-search'

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # 메인 HTML 페이지
        if parsed.path == '/' or parsed.path == '/index.html':
            try:
                with open('index.html', 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_cors()
                self.end_headers()
                self.wfile.write(data)
            except:
                self.send_response(404)
                self.end_headers()
            return

        # 사람인 API 프록시
        if parsed.path == '/job-search':
            try:
                params = urllib.parse.parse_qs(parsed.query)
                qs = parsed.query
                url = f'{SARAMIN_BASE}?{qs}'
                req = urllib.request.Request(url, headers={
                    'Accept': 'application/json',
                    'User-Agent': 'Mozilla/5.0'
                })
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_cors()
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                err = json.dumps({'error': str(e)}).encode()
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_cors()
                self.end_headers()
                self.wfile.write(err)
            return

        self.send_response(404)
        self.end_headers()

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'서버 시작: 포트 {PORT}')
    server.serve_forever()
