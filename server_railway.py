import http.server
import urllib.request
import urllib.parse
import json
import os

PORT = int(os.environ.get('PORT', 8080))
SARAMIN_BASE = 'https://oapi.saramin.co.kr/job-search'

# 현재 파일 위치 기준으로 index.html 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
            html_path = os.path.join(BASE_DIR, 'index.html')
            print(f"HTML 경로: {html_path}, 존재: {os.path.exists(html_path)}")
            try:
                with open(html_path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_cors()
                self.end_headers()
                self.wfile.write(data)
                print(f"HTML 전송 완료: {len(data)} bytes")
            except Exception as e:
                print(f"HTML 오류: {e}")
                # 파일 목록 출력
                print(f"현재 폴더 파일: {os.listdir(BASE_DIR)}")
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error: {e}\nFiles: {os.listdir(BASE_DIR)}".encode())
            return

        # 사람인 API 프록시
        if parsed.path == '/job-search':
            try:
                qs = parsed.query
                url = f'{SARAMIN_BASE}?{qs}'
                print(f"API 호출: {url[:80]}")
                req = urllib.request.Request(url, headers={
                    'Accept': 'application/json',
                    'User-Agent': 'Mozilla/5.0',
                    'Referer': 'http://50plus.or.kr',
                    'Origin': 'http://50plus.or.kr',
                })
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()
                print(f"API 응답: {len(data)} bytes")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_cors()
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                print(f"API 오류: {e}")
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
    print(f"서버 시작: 포트 {PORT}")
    print(f"작업 폴더: {BASE_DIR}")
    print(f"파일 목록: {os.listdir(BASE_DIR)}")
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    server.serve_forever()
