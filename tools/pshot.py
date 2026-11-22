#!/usr/bin/env python3
"""pshot.py PAGE OUTDIR STEPS_JSON: screenshots of any page of the project (grove.html?forest=1000, ...) headless on the
real GPU, ONE BROWSER AT A TIME (the same lock as creaturegen/dozen/cshot.py). STEPS is a JSON list of
{until: js-expr, timeout: s} / {js: expr} / {wait: ms} / {shot: name} (written to OUTDIR/name.png) / {profile: ms, top: n}
(the JS's self time by function, sampled); the page is first
waited for until `window.__ready` (or the env PSHOT_READY's expression: a page that sets none). Prints console warnings, errors and exceptions as they come."""
import asyncio, base64, fcntl, json, os, shutil, signal, subprocess, sys, tempfile, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "creaturegen", "dozen"))
import cshot   # (its server, flags, lock and CDP plumbing)
import websockets, urllib.request, http.server

async def drive(url, cdp, steps, out, size):
    tabs = None
    for _ in range(150):
        try: tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{cdp}/json/list")); break
        except Exception: time.sleep(.2)
    ws_url = [t for t in tabs if t["type"] == "page"][0]["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=2 ** 30) as ws:
        nid = [0]
        async def send(method, params=None):
            nid[0] += 1; me = nid[0]
            await ws.send(json.dumps({"id": me, "method": method, "params": params or {}}))
            while True:
                m = json.loads(await ws.recv())
                if m.get("method") == "Runtime.consoleAPICalled" and m["params"]["type"] in ("warning", "error", "log"):
                    args = " ".join(str(a.get("value", a.get("description", ""))) for a in m["params"]["args"])
                    print(f"  [{m['params']['type']}] {args[:600]}", flush=True)
                elif m.get("method") == "Runtime.exceptionThrown":
                    d = m["params"]["exceptionDetails"]; print("  [exception]", str(d.get("exception", {}).get("description", d.get("text")))[:900], flush=True)
                if m.get("id") == me: return m
        await send("Page.enable"); await send("Runtime.enable")
        await send("Emulation.setDeviceMetricsOverride", {"width": size[0], "height": size[1], "deviceScaleFactor": 1, "mobile": False})
        await send("Page.navigate", {"url": url})
        async def until(expr, tmo):
            t0 = time.time()
            while time.time() - t0 < tmo:
                r = await send("Runtime.evaluate", {"expression": expr, "returnByValue": True})
                if r.get("result", {}).get("result", {}).get("value"): return True
                await asyncio.sleep(.5)
            print("  timed out waiting for", expr[:80]); return False
        if not await until(os.environ.get("PSHOT_READY", "!!window.__ready"), 240): return False
        for st in steps:
            if st.get("until") and not await until(st["until"], st.get("timeout", 120)): return False
            if st.get("dark") is not None:   # the page as in a dark (or light) system theme
                await send("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-color-scheme", "value": "dark" if st["dark"] else "light"}]})
            if st.get("js"):
                r = await send("Runtime.evaluate", {"expression": st["js"], "returnByValue": True, "awaitPromise": True})
                v = r["result"]["result"].get("value", r["result"].get("exceptionDetails"))
                if v is not None and v != 1: print("  js ->", str(v)[:3000], flush=True)
            if st.get("wait"): await asyncio.sleep(st["wait"] / 1000)
            if st.get("profile"):   # sample the page's JS for that many ms: the functions with the most self time
                await send("Profiler.enable"); await send("Profiler.setSamplingInterval", {"interval": 200}); await send("Profiler.start")
                await asyncio.sleep(st["profile"] / 1000)
                prof = (await send("Profiler.stop"))["result"]["profile"]
                count, total = {}, 0
                byId = {n["id"]: n for n in prof["nodes"]}
                for sid in prof["samples"]:
                    cf = byId[sid]["callFrame"]; key = f'{cf["functionName"] or "(anon)"} {cf["url"].rsplit("/", 1)[-1]}:{cf["lineNumber"] + 1}'
                    count[key] = count.get(key, 0) + 1; total += 1
                print(f"  profile ({total} samples):", flush=True)
                for k, n in sorted(count.items(), key=lambda kv: -kv[1])[:st.get("top", 25)]: print(f"    {n * 100 / total:5.1f}%  {k}", flush=True)
            if st.get("shot"):
                r = await send("Page.captureScreenshot", {"format": "png"})
                p = os.path.join(out, st["shot"] + ".png"); open(p, "wb").write(base64.b64decode(r["result"]["data"])); print("  shot", p, flush=True)

def main():
    page, out, steps = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
    size = [int(v) for v in os.environ.get("PSHOT_SIZE", "1280x800").split("x")]
    os.makedirs(out, exist_ok=True)
    port, cdp = cshot.free_port(), cshot.free_port()
    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
        def end_headers(self): self.send_header("cache-control", "no-store"); super().end_headers()
    class Srv(http.server.ThreadingHTTPServer): request_queue_size = 512
    srv = Srv(("127.0.0.1", port), lambda *a, **k: H(*a, directory=cshot.SERVE, **k))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    def bail(*_): raise SystemExit("wall clock exceeded")
    signal.signal(signal.SIGALRM, bail); signal.signal(signal.SIGTERM, bail)
    lock = open(cshot.LOCK, "w"); fcntl.flock(lock, fcntl.LOCK_EX)
    signal.alarm(int(os.environ.get("PSHOT_TIMEOUT", "600")))
    prof = tempfile.mkdtemp(prefix="pshot_")
    chrome = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    url = f"http://127.0.0.1:{port}{cshot.SITE}{page}"
    flags = [f for f in cshot.FLAGS if not f.startswith("--window-size")] + [f"--window-size={size[0]},{size[1]}"]
    proc = subprocess.Popen([chrome, *flags, f"--remote-debugging-port={cdp}", f"--user-data-dir={prof}", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try: asyncio.run(drive(url, cdp, steps, out, size))
    finally:
        proc.terminate()
        try: proc.wait(10)
        except Exception: proc.kill()
        try: os.killpg(proc.pid, signal.SIGKILL)
        except Exception: pass
        shutil.rmtree(prof, ignore_errors=True)
        fcntl.flock(lock, fcntl.LOCK_UN)
if __name__ == "__main__": main()
