#!/usr/bin/env python3
"""cshot.py PATH NAME OUTDIR VIEWS [--dress JSON] [--extra JSON]: screenshots of one asset in assets.html, headless on the
real GPU (the flags that work on this PC: see build/headless.py), ONE BROWSER AT A TIME (flock on a lock file: another
run waits). Views: side (eye on +x: the figure faces +z in the viewer), front, q (front three-quarter), rear (rear
three-quarter, low), rearlow, head (the head close up, from the front-side), top. Writes OUTDIR/NAME_VIEW.png and prints
the asset's box and any console errors."""
import asyncio, base64, fcntl, http.server, json, os, shutil, socket, subprocess, sys, tempfile, threading, time, urllib.request
import websockets
PROJECT = "/home/martin/store/apps/multiverse"; SERVE = os.path.dirname(PROJECT); SITE = "/multiverse/"
LOCK = "/tmp/claude-1000/cshot.lock"
FLAGS = ["--headless=new", "--no-sandbox", "--ignore-gpu-blocklist", "--enable-features=Vulkan", "--use-angle=vulkan", "--enable-unsafe-webgpu",
         "--window-size=1100,900", "--hide-scrollbars"]
def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p
LOOK = """(() => { const B = __assets.assetBox(); const c = B.getCenter(B.min.clone()), S = B.getSize(B.min.clone());
  const L = Math.max(S.x, S.y, S.z), v = %r, eye = B.min.clone(), at = c.clone();
  if (v === 'side') eye.set(c.x + L * 1.7, c.y + L * .25, c.z);
  else if (v === 'front') eye.set(c.x, c.y + L * .3, c.z + L * 1.7);
  else if (v === 'q') eye.set(c.x + L * 1.2, c.y + L * .45, c.z + L * 1.2);
  else if (v === 'rear') eye.set(c.x - L * 1.2, c.y + L * .55, c.z - L * 1.2);
  else if (v === 'rearlow') eye.set(c.x - L * 1.0, c.y - L * .05, c.z - L * 1.4);
  else if (v === 'top') eye.set(c.x + L * .01, c.y + L * 2.0, c.z);
  else if (v === 'head') { at.set(c.x, B.max.y - S.y * .14, B.max.z - S.z * .16); eye.set(at.x + S.z * .55, at.y + S.y * .12, at.z + S.z * .45); }
  else if (v === 'headside') { at.set(c.x, B.max.y - S.y * .14, B.max.z - S.z * .16); eye.set(at.x + S.z * .7, at.y + S.y * .05, at.z); }
  else if (v === 'feet') { at.set(c.x, B.min.y + S.y * .12, c.z); eye.set(c.x + L * .9, B.min.y + S.y * .2, c.z + L * .6); }
  __assets.nav.lookAt(eye, at); return [B.min.toArray(), B.max.toArray()].map((a) => a.map((x) => +x.toFixed(2))); })()"""
async def drive(url, cdp, steps, timeout=400):
    tabs = None
    for _ in range(150):
        try: tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{cdp}/json/list")); break
        except Exception: time.sleep(.2)
    ws_url = [t for t in tabs if t["type"] == "page"][0]["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=2 ** 30) as ws:
        nid = [0]; reqs = {}
        async def send(method, params=None):
            nid[0] += 1; me = nid[0]
            await ws.send(json.dumps({"id": me, "method": method, "params": params or {}}))
            while True:
                m = json.loads(await ws.recv())
                if m.get("method") == "Runtime.consoleAPICalled":
                    args = " ".join(str(a.get("value", a.get("description", ""))) for a in m["params"]["args"])
                    if m["params"]["type"] in ("warning", "error"): print(f"  [{m['params']['type']}] {args[:400]}", flush=True)
                elif m.get("method") == "Network.loadingFailed":
                    print(f"  [net] {m['params'].get('errorText')} {m['params'].get('type')} {reqs.get(m['params']['requestId'], '?')}", flush=True)
                elif m.get("method") == "Network.requestWillBeSent":
                    reqs[m["params"]["requestId"]] = m["params"]["request"]["url"]
                elif m.get("method") == "Runtime.exceptionThrown":
                    d = m["params"]["exceptionDetails"]; print("  [exception]", str(d.get("exception", {}).get("description", d.get("text")))[:500], flush=True)
                if m.get("id") == me: return m
        await send("Page.enable"); await send("Runtime.enable"); await send("Network.enable")
        await send("Emulation.setDeviceMetricsOverride", {"width": 1100, "height": 900, "deviceScaleFactor": 1, "mobile": False})
        await send("Page.navigate", {"url": url})
        async def until(expr, tmo):
            t0 = time.time()
            while time.time() - t0 < tmo:
                r = await send("Runtime.evaluate", {"expression": expr, "returnByValue": True})
                if r.get("result", {}).get("result", {}).get("value"): return True
                await asyncio.sleep(.5)
            print("  timed out waiting for", expr[:80]); return False
        if not await until("!!window.__assets", timeout): return False
        # (the panels hidden: the view takes the whole window, so the figure is as large as the shot)
        await send("Runtime.evaluate", {"expression": "document.head.insertAdjacentHTML('beforeend', '<style>#list,#edit{display:none!important}#mid{width:100vw!important;max-width:none!important;flex:1 1 100%!important}body{grid-template-columns:1fr!important}</style>'); dispatchEvent(new Event('resize')); 1"})
        for st in steps:
            if st.get("until") and not await until(st["until"], st.get("timeout", 300)): print("  the asset never got ready: no shots"); return False
            if st.get("js"):
                r = await send("Runtime.evaluate", {"expression": st["js"], "returnByValue": True, "awaitPromise": True})
                v = r["result"]["result"].get("value", r["result"].get("exceptionDetails"))
                if v is not None and v != 1: print("  js ->", str(v)[:3000], flush=True)
            if st.get("wait"): await asyncio.sleep(st["wait"] / 1000)
            if st.get("shot"):
                r = await send("Page.captureScreenshot", {"format": "png"})
                open(st["shot"], "wb").write(base64.b64decode(r["result"]["data"])); print("  shot", st["shot"], flush=True)
def main():
    path, name, out, views = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(",")
    dress = json.loads(sys.argv[sys.argv.index("--dress") + 1]) if "--dress" in sys.argv else None
    extra = json.loads(sys.argv[sys.argv.index("--extra") + 1]) if "--extra" in sys.argv else []
    ready = "__assets.bodies.ready() && performance.now() > 4000"
    steps = [{"until": ready, "timeout": 300, "wait": 1500}]
    if dress: steps += [{"js": f"__assets.pickDress({json.dumps(dress)}); 1", "wait": 1500}, {"until": ready, "timeout": 300, "wait": 1500}]
    for v in views: steps.append({"js": LOOK % v, "wait": 700, "shot": os.path.join(out, f"{name}_{v}.png")})
    steps += extra
    port, cdp = free_port(), free_port()
    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
        def end_headers(self): self.send_header("cache-control", "no-store"); super().end_headers()
    class Srv(http.server.ThreadingHTTPServer):
        request_queue_size = 512   # (the catalogue is 1300 files fetched at once: at the default backlog of 5 connections were refused -- "Failed to fetch" -- on a busy machine)
    srv = Srv(("127.0.0.1", port), lambda *a, **k: H(*a, directory=SERVE, **k))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    import signal
    def bail(*_): raise SystemExit("wall clock exceeded -- the browser is killed, the lock freed")
    signal.signal(signal.SIGALRM, bail); signal.signal(signal.SIGTERM, bail)   # (killed from outside too: the browser goes with us, not on as an orphan)
    lock = open(LOCK, "w"); fcntl.flock(lock, fcntl.LOCK_EX)
    signal.alarm(int(os.environ.get("CSHOT_TIMEOUT", "900")))   # (a wedged browser never holds the lock for good: every run ends within this)
    prof = tempfile.mkdtemp(prefix="cshot_")
    chrome = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    url = f"http://127.0.0.1:{port}{SITE}assets.html?a={path}&bodycache=0"
    # (two tries: under memory pressure the page's fetches fail or the browser dies before the asset is ready)
    for attempt in range(2):
        proc = subprocess.Popen([chrome, *FLAGS, f"--remote-debugging-port={cdp}", f"--user-data-dir={prof}", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        ok = False
        try: ok = asyncio.run(drive(url, cdp, steps)) is not False
        except Exception as e: print("  the browser went away:", type(e).__name__, str(e)[:200])
        finally:
            proc.terminate()
            try: proc.wait(10)
            except Exception: proc.kill()
            try: os.killpg(proc.pid, signal.SIGKILL)   # (its whole process group: the GPU and renderer processes too)
            except Exception: pass
            shutil.rmtree(prof, ignore_errors=True)
        if ok: break
        print("  trying once more"); time.sleep(5); prof = tempfile.mkdtemp(prefix="cshot_")
    fcntl.flock(lock, fcntl.LOCK_UN)
if __name__ == "__main__": main()
