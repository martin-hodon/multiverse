#!/usr/bin/env python3
"""The project's own server, for working on it: static files, plus PUT to save an asset.

    python3 tools/serve.py [port]        # then open http://127.0.0.1:8080/assets.html

A plain static server is enough to RUN the game; this one is what the asset viewer (assets.html) saves
through. A PUT to a path under assets/ writes that file -- nothing else is writable, and nothing outside the
project can be reached.
"""
import http.server, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_PUT(self):
        path = self.path.split("?")[0].lstrip("/")
        full = os.path.normpath(os.path.join(ROOT, path))
        if not full.startswith(os.path.join(ROOT, "assets") + os.sep) or not full.endswith(".json"):
            self.send_error(403, "only assets/**.json may be written")
            return
        body = self.rfile.read(int(self.headers.get("content-length", 0)))
        try:
            text = json.dumps(json.loads(body.decode("utf-8")), indent=2) + "\n"   # (also checks it is JSON)
        except Exception as e:
            self.send_error(400, f"not JSON: {e}")
            return
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)
        self.send_response(200)
        self.send_header("content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"saved\n")

    def end_headers(self):
        self.send_header("cache-control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"serving {ROOT} on http://127.0.0.1:{PORT}  (assets.html is the asset viewer)")
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
