"""Run a page of the project in headless Chromium and take a value back from it -- what the build tools share.

    from headless import run_page
    value = run_page("textures.html", ready="window.__ready === true", result="JSON.stringify(window.__textures())",
                     flags=[...], writes={"pregen/": handler})

It serves apps/ over a local HTTP server (so the page's URLs are the dev setup's: /multiverse/...), opens the page
over the DevTools protocol, waits until `ready` is true, evaluates `result` and returns its value (a string). A
page may also WRITE files: a POST to /multiverse/<prefix><path> for a prefix in `writes` is handed to that function
with (path under the prefix, body bytes) -- nothing else is writable. Needs chromium (CHROME to override) and the
`websockets` Python module.
"""
import asyncio, functools, http.server, json, os, shutil, socket, subprocess, sys, tempfile, threading, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)                 # apps/multiverse
SERVE = os.path.dirname(PROJECT)                # served from apps/ so the page's URLs match the dev setup
SITE = "/" + os.path.basename(PROJECT) + "/"


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


async def _drive(page_url, cdp_port, ready, result, timeout, log, shot=None):
    import websockets
    tabs = None
    for _ in range(150):
        try:
            tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json/list")); break
        except Exception:
            time.sleep(.2)
    ws_url = [t for t in tabs if t["type"] == "page"][0]["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=2 ** 30) as ws:
        nid, errs = [0], []

        async def send(method, params=None):
            nid[0] += 1; me = nid[0]
            await ws.send(json.dumps({"id": me, "method": method, "params": params or {}}))
            while True:
                m = json.loads(await ws.recv())
                if m.get("method") == "Runtime.consoleAPICalled" and log:
                    args = " ".join(str(a.get("value", a.get("description", ""))) for a in m["params"]["args"])
                    print(f"  [{m['params']['type']}] {args}", flush=True)
                elif m.get("method") == "Runtime.exceptionThrown":
                    d = m["params"]["exceptionDetails"]; text = d.get("exception", {}).get("description", d.get("text"))
                    print("  [exception]", text, flush=True); errs.append((time.time(), text))
                if m.get("id") == me:
                    return m
        await send("Page.enable"); await send("Runtime.enable")
        await send("Page.navigate", {"url": page_url})
        t0 = time.time()
        while time.time() - t0 < timeout:
            r = await send("Runtime.evaluate", {"expression": ready, "returnByValue": True})
            if r.get("result", {}).get("result", {}).get("value"):
                break
            if errs and time.time() - errs[0][0] > 20:   # (an uncaught exception and still not ready: the page died loading -- not worth the whole timeout)
                sys.exit(f"{page_url} threw before it got ready: {errs[0][1]}")
            await asyncio.sleep(.5)
        else:
            sys.exit(f"{page_url} did not get ready in {timeout}s (network for three.js? console errors above?)")
        if shot:   # (the whole page as it is now: its panels and controls, not only a canvas)
            import base64
            r = await send("Page.captureScreenshot", {"format": "png"})
            open(shot, "wb").write(base64.b64decode(r["result"]["data"]))
        if result is None:
            return None
        r = await send("Runtime.evaluate", {"expression": result, "returnByValue": True, "awaitPromise": True})   # (a promise: its value)
        return r["result"]["result"].get("value", r["result"].get("exceptionDetails", {}).get("text"))


def mem_available_mb():
    """The system's free memory as the kernel counts it for a new program (MemAvailable), in MB."""
    for line in open("/proc/meminfo"):
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) // 1024
    return 0


def room(need, what, again):
    """Wait (up to half a minute: a browser just closed gives its memory back slowly) until `need` MB are free for the
    next browser -- or stop, saying what was free and what to run to carry on (`again`)."""
    for _ in range(30):
        free = mem_available_mb()
        if free >= need:
            return
        time.sleep(1)
    sys.exit(f"stopped before {what}: {free} MB free, it needs about {need} MB -- close something and run `{again}` to carry on")


def _tree_mb(root):
    """The memory a process and its children hold (proportional set size: shared pages split among them), in MB."""
    kids = {}
    for d in os.listdir("/proc"):
        if d.isdigit():
            try: kids.setdefault(int(open(f"/proc/{d}/stat").read().rsplit(")", 1)[1].split()[1]), []).append(int(d))
            except (OSError, IndexError, ValueError): pass
    total, todo = 0, [root]
    while todo:
        pid = todo.pop(); todo += kids.get(pid, [])
        try:
            for line in open(f"/proc/{pid}/smaps_rollup"):
                if line.startswith("Pss:"): total += int(line.split()[1]); break
        except OSError: pass
    return total // 1024


def run_page(page, ready, result=None, flags=(), writes=None, timeout=120, log=False, shot=None, stats=None):
    """stats: a dict given gets "peak_mb", the most the browser held at once (sampled each second)."""
    port, cdp = free_port(), free_port()
    writes = writes or {}

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass

        def end_headers(self):
            self.send_header("cache-control", "no-store")
            super().end_headers()

        def do_POST(self):
            path = self.path.split("?")[0]
            for prefix, fn in writes.items():
                if path.startswith(SITE + prefix):
                    body = self.rfile.read(int(self.headers.get("content-length", 0)))
                    fn(path[len(SITE + prefix):], body)
                    self.send_response(200); self.end_headers(); return
            self.send_error(403, "not writable")

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Handler, directory=SERVE))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    prof = tempfile.mkdtemp(prefix="bannerfield-headless-")
    chrome = subprocess.Popen([os.environ.get("CHROME", "chromium-browser"), "--headless=new", f"--remote-debugging-port={cdp}",
                               f"--user-data-dir={prof}", *flags, "--no-first-run", "--no-default-browser-check", "about:blank"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    stop = threading.Event()
    if stats is not None:
        stats["peak_mb"] = 0
        def sample():
            while not stop.wait(1):
                stats["peak_mb"] = max(stats["peak_mb"], _tree_mb(chrome.pid))
        threading.Thread(target=sample, daemon=True).start()
    try:
        return asyncio.run(_drive(f"http://127.0.0.1:{port}{SITE}{page}", cdp, ready, result, timeout, log, shot))
    finally:
        stop.set(); chrome.terminate(); httpd.shutdown()
        time.sleep(.3); shutil.rmtree(prof, ignore_errors=True)   # (chrome may still be closing its profile)
