#!/usr/bin/env python3
"""tools/modern/mshot.py OUT PATH[,PATH...] [VIEWS] (2026-11-20, the modern generators' review renders; PATH under items/modern/ or items/...): each item shown in assets.html, shot from VIEWS (side,q,rear,front,top,in), one
sheet per item at OUT/<name>.png (views 2 per row, 800x600 each). One browser for all. A view `p:ex/ey/ez:tx/ty/tz`
is an eye and a target in the item's own metres -- inside a bus, a cabin, close on a detail; `open` (and `shut`) swing its
hinged doors and lids for the views after it; `steer:0.8` steers the front wheels (-1..1) for the views after it. Views are joined by commas.
Runs under the shared screenshot lock (tools/pshot.py): one browser at a time on this machine."""
import json, os, subprocess, sys
out, paths = sys.argv[1], [p if p.startswith("items/") else "items/modern/" + p for p in sys.argv[2].split(",")]
views = (sys.argv[3] if len(sys.argv) > 3 else "q,side,rear,front").split(",")
LOOK = """(() => { const B = __assets.assetBox(); const c = B.getCenter(B.min.clone()), S = B.getSize(B.min.clone());
  const L = Math.max(S.x, S.y, S.z), v = %r, eye = B.min.clone(), at = c.clone();
  if (v === 'side') eye.set(c.x, c.y + L * .12, c.z + L * 1.35);
  else if (v === 'front') eye.set(c.x + L * 1.4, c.y + L * .2, c.z + L * .05);
  else if (v === 'q') eye.set(c.x + L * .95, c.y + L * .4, c.z + L * .95);
  else if (v === 'rear') eye.set(c.x - L * .95, c.y + L * .45, c.z - L * .95);
  else if (v === 'top') eye.set(c.x + L * .01, c.y + L * 1.6, c.z);
  else if (v === 'low') eye.set(c.x + L * .7, c.y - S.y * .2, c.z + L * .9);
  else if (v.startsWith('p:')) { const [e, t] = v.slice(2).split(':').map((q) => q.split('/').map(Number)); eye.set(...e); at.set(...t); }
  else if (v === 'in') { at.set(c.x, c.y, c.z); eye.set(c.x + S.x * .02, c.y + S.y * .05, c.z + S.z * 1.5); }
  __assets.nav.lookAt(eye, at); return 1; })()"""
steps = []
for p in paths:
    n = p.rsplit("/", 1)[1]
    steps += [{"js": f"document.getElementById('spin').checked = false; __assets.show({json.dumps(p)}); 1"}, {"wait": 2500}]
    for i, v in enumerate(views):
        if v in ("open", "shut"):   # (not a view: the doors and lids swung open, or shut again -- items.js hinge)
            steps += [{"js": f"document.getElementById('openJ').checked = {'true' if v == 'open' else 'false'}; 1"}, {"wait": 1500}]; continue
        if v.startswith("steer:"):   # (not a view: the front wheels steered, -1..1, +1 full left -- items.js hinge `by`)
            steps += [{"js": f"__assets.drive('steer', {float(v[6:])}); 1"}, {"wait": 300}]; continue
        if v.startswith("open:"):   # (held part-way: open:0.4)
            steps += [{"js": f"__assets.openAt({float(v[5:])}); 1"}, {"wait": 300}]; continue
        steps += [{"js": LOOK % v}, {"wait": 900}, {"shot": f"{n}__{i}"}]
os.makedirs(out, exist_ok=True)
env = dict(os.environ, PSHOT_SIZE="800x600", PSHOT_TIMEOUT=str(120 + 25 * len(paths) * len(views)))
subprocess.run(["timeout", str(150 + 25 * len(paths) * len(views)), "python3", "/home/martin/store/apps/multiverse/tools/pshot.py", "assets.html?embed=1&a=" + paths[0], out, json.dumps(steps)], env=env)
for p in paths:
    n = p.rsplit("/", 1)[1]
    fs = [f"{out}/{n}__{i}.png" for i in range(len(views)) if os.path.exists(f"{out}/{n}__{i}.png")]
    if fs: subprocess.run(["montage", *fs, "-tile", "2x", "-geometry", "+2+2", f"{out}/{n}.png"]); [os.remove(f) for f in fs]
    print(f"{out}/{n}.png")
