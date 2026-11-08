# drive.py OUTDIR PAGE STEPS.js  -- one headless session of assets.html: STEPS.js is the body of an async function run in
# the page with helpers (wait, shot(name, clip?), pick(p), settle()); shots go through Page.captureScreenshot
import asyncio, base64, functools, http.server, json, os, shutil, subprocess, sys, tempfile, threading, time, urllib.request
sys.path.insert(0, "/home/martin/store/apps/multiverse/build")
import headless
out, page, steps = sys.argv[1], sys.argv[2], open(sys.argv[3]).read()
W, H = (int(x) for x in (sys.argv[4] if len(sys.argv) > 4 else "1600x1000").split("x"))
os.makedirs(out, exist_ok=True)
HELP = r"""
window.__shots = []; window.__log = [];
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const frames = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
const A = () => window.__assets;
const skinned = () => { let sm = null; A().scene.traverse((o) => { if (o.isSkinnedMesh && o.visible && (!sm || o.geometry.attributes.position.count > sm.geometry.attributes.position.count)) sm = o; }); return sm; };
async function settle(min = 2500, max = 40000, old = null) {   // until the sculpted surface is there (a new one, if `old`) and its box holds still
  const TH = await import('three'); const t0 = Date.now(); let last = -1, same = 0; await wait(min);
  while (old && Date.now() - t0 < max && (!skinned() || skinned().geometry === old)) await wait(300);
  while (Date.now() - t0 < max) { let sm = null; A().scene.traverse((o) => { if (o.isSkinnedMesh && o.visible && (o.geometry?.attributes?.position?.count || 0) > 500) sm = o; });
    const z = sm ? new TH.Box3().setFromObject(sm).getSize(new TH.Vector3()).length() : 0;
    if (sm && Math.abs(z - last) < 1e-3 * z) { if (++same >= 2) break; } else same = 0; last = z; await wait(700); }
  await frames(); }
async function view(kind, d0) {   // b: the page's own framing (three-quarter); h: the head, from the front quarter; side
  const TH = await import('three');
  if (kind === 'b') { A().frame(); await wait(400); await frames(); return; }
  // (as r3.py: the skinned mesh's box is its rest frame -- x nose to tail -- and the figure stands turned, rest x along world z)
  const sm = skinned(), bb = new TH.Box3().setFromObject(sm), xl = bb.max.x - bb.min.x, yl = bb.max.y - bb.min.y;
  if (kind === 'bf') { const d = Math.max(xl, yl) * 1.5, C = new TH.Vector3(0, (bb.min.y + bb.max.y) / 2, (bb.min.x + bb.max.x) / 2); A().nav.lookAt(new TH.Vector3(C.x + .3 * d, C.y + .3 * d, C.z + d), C); await wait(400); await frames(); return; }
  if (kind === 'sidefix') { const C = new TH.Vector3(0, .75, 0); A().nav.lookAt(new TH.Vector3(C.x + d0, C.y + .1 * d0, C.z), C); await wait(400); await frames(); return; }
  if (kind === 'side') { const d = Math.max(xl, yl) * 1.3, C = new TH.Vector3(0, (bb.min.y + bb.max.y) / 2, (bb.min.x + bb.max.x) / 2); A().nav.lookAt(new TH.Vector3(C.x + d, C.y + .05 * d, C.z), C); await wait(400); await frames(); return; }
  const P = sm.geometry.attributes.position, v = new TH.Vector3(); let n = 0, sy = 0, sx = 0, y0 = 1e9, y1 = -1e9;
  for (let i = 0; i < P.count; i++) { v.fromBufferAttribute(P, i).applyMatrix4(sm.matrixWorld); if (v.x > bb.max.x - .22 * xl && v.y > bb.min.y + .5 * yl) { n++; sy += v.y; sx += v.x; y0 = Math.min(y0, v.y); y1 = Math.max(y1, v.y); } }
  const C = new TH.Vector3(0, sy / n, sx / n), d = Math.max(.22 * xl, y1 - y0) * 2.2 * (d0 ?? 1);
  if (kind === 'hs') A().nav.lookAt(new TH.Vector3(C.x + d * 1.05, C.y + .08 * d, C.z), C); else
  if (kind === 'hf') A().nav.lookAt(new TH.Vector3(C.x + d * .3, C.y + .35 * d, C.z + d * .9), C); else
  A().nav.lookAt(new TH.Vector3(C.x + d * .75, C.y + .2 * d, C.z + d * .55), C);
  await wait(400); await frames(); }
const shot = async (name, clip) => { await frames(); window.__shots.push([name, clip ?? null]); while (window.__shots.length) await wait(100); };
const rect = (id) => { const r = document.getElementById(id).getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height, scale: 1 }; };
"""
async def drive(url, cdp):
    import websockets
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
                if m.get("method") == "Runtime.exceptionThrown":
                    d = m["params"]["exceptionDetails"]; print("  [exception]", d.get("exception", {}).get("description", d.get("text")), flush=True)
                elif m.get("method") == "Runtime.consoleAPICalled" and m["params"]["type"] in ("error", "warning", "log"):
                    print(f"  [{m['params']['type']}]", " ".join(str(a.get("value", a.get("description", ""))) for a in m["params"]["args"])[:300], flush=True)
                if m.get("id") == me: return m
        await send("Page.enable"); await send("Runtime.enable")
        await send("Emulation.setDeviceMetricsOverride", {"width": W, "height": H, "deviceScaleFactor": 1, "mobile": False})
        await send("Page.navigate", {"url": url})
        t0 = time.time()
        while time.time() - t0 < 180:
            r = await send("Runtime.evaluate", {"expression": "!!window.__ready", "returnByValue": True})
            if r.get("result", {}).get("result", {}).get("value"): break
            await asyncio.sleep(.5)
        else: sys.exit("no __ready")
        await send("Runtime.evaluate", {"expression": HELP + "\nwindow.__done = false; (async () => { try {\n" + steps + "\n} catch (e) { window.__log.push('ERR ' + e.stack); } window.__done = true; })();"})
        k = 0
        while time.time() - t0 < 900:
            r = await send("Runtime.evaluate", {"expression": "JSON.stringify([window.__done, window.__shots[0] ?? null, window.__log.splice(0)])", "returnByValue": True})
            done, sh, logs = json.loads(r["result"]["result"]["value"])
            for l in logs: print("  log:", l, flush=True)
            if sh:
                p = {"format": "png"}
                if sh[1]: p["clip"] = sh[1]
                img = await send("Page.captureScreenshot", p)
                fn = os.path.join(out, sh[0] + ".png"); open(fn, "wb").write(base64.b64decode(img["result"]["data"])); print("shot", fn, flush=True)
                await send("Runtime.evaluate", {"expression": "window.__shots.shift()"})
                continue
            if done: break
            await asyncio.sleep(.3)
port, cdp = headless.free_port(), headless.free_port()
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def end_headers(self): self.send_header("cache-control", "no-store"); super().end_headers()
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Handler, directory=headless.SERVE))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
prof = tempfile.mkdtemp(prefix="bannerfield-headless-")
chrome = subprocess.Popen([os.environ.get("CHROME", "chromium-browser"), "--headless=new", f"--remote-debugging-port={cdp}", f"--user-data-dir={prof}",
                           "--enable-unsafe-webgpu", "--enable-features=Vulkan", "--use-angle=vulkan", f"--window-size={W},{H}", "--no-first-run", "--no-default-browser-check", "about:blank"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try: asyncio.run(drive(f"http://127.0.0.1:{port}{headless.SITE}{page}", cdp))
finally:
    chrome.terminate(); httpd.shutdown(); time.sleep(.5); shutil.rmtree(prof, ignore_errors=True)
