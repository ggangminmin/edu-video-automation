#!/usr/bin/env python3
"""마루시공 11~20강 POC 서버 (포트 8162) — 마키 카타나 serve.py 복사 + /_open 허용 폴더에 완주_삼례와길수 추가

python3 -m http.server 는 HTTP Range 요청을 지원하지 않아서(항상 200 전체 응답)
크롬이 webm을 '탐색 불가'로 판단 → 영상 컷 구간 seek이 먹지 않거나 불안정해진다.
이 서버는 206 Partial Content를 지원해 컷별 구간 재생이 정상 동작한다.

  cd nanami && nohup python3 serve.py > /tmp/nanami_poc.log 2>&1 &
  → http://localhost:8097/poc.html
"""
import os
import re
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8162
# /_open 이 열어도 되는 서버 루트 밖 폴더 (캐논 원본이 사는 곳)
EXTRA_ROOTS = [os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_작업"))]


class RangeHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"   # keep-alive — 연속 seek 요청이 빨라짐


    # ── /_open?p=<루트 기준 상대경로> → Finder 에서 그 파일을 선택해 연다 ──
    #    브라우저는 http 페이지에서 file:// 링크를 막기 때문에(크롬 정책)
    #    로컬 서버가 대신 `open -R` 을 호출한다. 서버 루트 밖 경로는 거부.
    def do_GET(self):
        if self.path.split("?")[0] == "/_open":
            return self._open_in_finder()
        return super().do_GET()

    def _open_in_finder(self):
        import json
        import subprocess
        from urllib.parse import urlparse, parse_qs, unquote

        rel = unquote(parse_qs(urlparse(self.path).query).get("p", [""])[0]).lstrip("/")
        root = os.path.abspath(os.getcwd())
        target = os.path.abspath(os.path.join(root, rel))
        inside = any(target == r or target.startswith(r + os.sep) for r in [root] + EXTRA_ROOTS)

        if not rel or not inside or not os.path.exists(target):
            code, payload = 404, {"ok": False, "error": "not found or outside root", "path": rel}
        else:
            subprocess.Popen(["open", "-R", target])
            code, payload = 200, {"ok": True, "path": rel}

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_head(self):
        rng = self.headers.get("Range")
        if not rng:
            return super().send_head()

        path = self.translate_path(self.path)
        if os.path.isdir(path) or not os.path.exists(path):
            return super().send_head()

        m = re.match(r"bytes=(\d*)-(\d*)$", rng.strip())
        if not m:
            return super().send_head()

        size = os.path.getsize(path)
        first, last = m.group(1), m.group(2)
        if first == "":                       # bytes=-N (마지막 N바이트)
            length = min(int(last or 0), size)
            start, end = size - length, size - 1
        else:
            start = int(first)
            end = min(int(last), size - 1) if last else size - 1
        if start >= size or start > end:
            self.send_response(416)
            self.send_header("Content-Range", "bytes */%d" % size)
            self.end_headers()
            return None

        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        self._range = (start, end)
        return f

    def copyfile(self, source, outputfile):
        rng = getattr(self, "_range", None)
        if not rng:
            return super().copyfile(source, outputfile)
        start, end = rng
        self._range = None
        remaining = end - start + 1
        while remaining > 0:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)

    def end_headers(self):
        if self.command == "GET" and "Accept-Ranges" not in self._headers_buffer_str():
            self.send_header("Accept-Ranges", "bytes")
        # html/json 은 절대 캐시하지 않음 (컷 데이터 갱신이 새로고침에 바로 반영되게)
        if self.path.split("?")[0].endswith((".html", ".json")) and "Cache-Control" not in self._headers_buffer_str():
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def _headers_buffer_str(self):
        return b"".join(getattr(self, "_headers_buffer", [])).decode("latin-1", "replace")

    def log_message(self, fmt, *args):
        pass  # 조용히


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = partial(RangeHandler, directory=os.getcwd())
    print("공모전 리스트 POC → http://localhost:%d/  (root=%s, Range·/_open 지원)" % (PORT, os.getcwd()))
    ThreadingHTTPServer(("", PORT), handler).serve_forever()
