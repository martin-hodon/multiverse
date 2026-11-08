#!/usr/bin/env python3
# mane.py IN.json OUT.json MODE : a horse-frame creature's mane in LOCKS (2026-11-07), replacing the slab of flat
# ellipsoids (mane\d+, maneT\d+) and the one-blob forelock. MODE horse | unicorn | zebra.
#  horse / unicorn: a crest of tapering locks rooted along the top of the neck (in the crest's under-layer, maneRidge,
#   kept), lifting a little over the crest and falling down the off (right, -z) side -- two layers, the outer longer, so
#   it has depth, every lock its own length so the lower edge is separated and ragged, the tips leaning back and a
#   little out; a few short locks flopped over to the near side; a short forelock of locks from the poll down the
#   forehead (a unicorn's longer, parted round the horn, and its near-side row longer).
#  zebra: the short upright brush -- rows of stiff tufts standing on the crest, striped as the neck's bands run up
#   into them (each bristle black or white by the band at its root), the top one smooth rounded line.
# Each lock is a tube thin enough for the grid to leave it to be drawn exactly (bodyspec.js details: r under .8 of the
# cell, over .15), rooted inside the crest so it is never loose, on the neck's bone (the head's, the forelock) so it
# rides every pose of the neck -- the nod, the walk, the flight. The mesh cell is pinned to what it was, so the body
# is drawn as before and the locks stay details.
import json, math, random, subprocess, sys, os, re, tempfile
src, out, mode = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(src))
sh = d["sculpt"]["shape"]
OLD = re.compile(r"^(mane\d+P?|maneT\d+|forelock|lk[A-Z]\w*|fl\d+\w*|brush\w*)$")
ids = {q.get("id"): q for q in sh}
s = {"horse": 1.0, "unicorn": .95, "zebra": .85}[mode]
CELL = {"horse": .026, "unicorn": .0253, "zebra": .0309}[mode] if not d["sculpt"].get("mesh", {}).get("cell") else d["sculpt"]["mesh"]["cell"]
RMAX, RMIN = .78 * CELL, .17 * CELL
d["sculpt"].setdefault("mesh", {})["cell"] = CELL
old_fore = ids.get("forelock") or {   # (run again on its own output: where the placeholder forelock stood)
    "horse": {"c": [1.5201, 2.097, 0], "r": [.1088, .0453, .0484], "rot": [0, 0, -71.04]},
    "unicorn": {"c": [1.4691, 1.9621, 0], "r": [.1447, .0516, .0506], "rot": [0, 0, -71.04]},
    "zebra": {"c": [1.2664, 1.8178, 0], "r": [.0735, .0283, .0339], "rot": [0, 0, -71.41]},
    "pegasus": {"c": [1.536, 2.07, 0], "r": [.078, .042, .046], "rot": [0, 0, -71.04]}}["pegasus" if d.get("name") == "pegasus" else mode]
SQ = {}
R5 = lambda v: round(v, 4)
if mode == "zebra":
    # (the zebra keeps its banded plates -- the neck's stripes running up into its mane -- but low, a base the brush
    # stands in; the slab's smooth top edge is gone under the bristles)
    OLD = re.compile(r"^(forelock|lk[A-Z]\w*|fl\d+\w*|brush\w*)$")
    done = any(q.get("id", "").startswith("brush") for q in sh)    # (already squashed: run again on its own output)
    for q in sh:
        if not done and re.match(r"^mane\d+P?$", q.get("id", "")):
            h0 = q["r"][1]; h1 = round(h0 * .72, 4); a = math.radians(q["rot"][2]); up = (-math.sin(a), math.cos(a))
            q["c"] = [round(q["c"][0] - up[0] * (h0 - h1) * .8, 4), round(q["c"][1] - up[1] * (h0 - h1) * .8, 4), q["c"][2]]
            q["r"] = [q["r"][0], h1, q["r"][2]]; SQ[q["id"]] = q
sh[:] = [q for q in sh if not OLD.match(q.get("id", ""))]
# THE POLL (2026-11-08): the crest's ellipsoid ends ~10 cm short of the back of the skull, and the neck's top fell into a
# notch there (10-12 cm deep: 2.07 m at x 1.16 down to 1.98 at 1.30, then the cranium at 2.10 -- the horse's, the
# pegasus's, the unicorn's and the zebra's alike, scaled): "a gap on top of the neck between head and neck". A tube on
# the neck's bone, from the crest's end up into the back of the cranium, fills it -- the top rising smoothly to the
# poll (probe.mjs: 2.08 .. 2.14) -- painted as the crest is. Added once, before the neck's top is probed for the locks
NEW = []
if not any(q.get("id") == "poll" for q in sh):
    cr = ids["crest"]
    poll = {"id": "poll", "type": "tube", "bone": "neck",
            "pts": [[R5(x * s), R5(y * s), 0, R5(r * s)] for x, y, r in ((1.10, 1.99, .075), (1.22, 2.01, .074), (1.31, 2.03, .07))],
            "k": R5(.05 * s), "color": cr["color"], **{k: cr[k] for k in ("pat", "frame") if k in cr}}
    sh.insert(sh.index(cr) + 1, poll); NEW.append(poll)
tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); json.dump(d, tmp); tmp.close()
def retmp():
    with open(tmp.name, "w") as f: json.dump(d, f)

def probe(Q):
    qf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); json.dump(Q, qf); qf.close()
    r = subprocess.run(["node", HERE + "/probe.mjs", tmp.name, qf.name], capture_output=True, text=True, check=True)
    os.unlink(qf.name)
    return json.loads(r.stdout)

# ---- the neck's top along the crest (with the crest's under-layer), and its sides: a table on x and height
X0, X1 = .40 * s, 1.30 * s    # (the last few cm behind the poll bare: the bridle path. 2026-11-08: 1.24 -> 1.30, the mane
                              #  running on over the filled poll to the forelock -- a hand of bare neck read as a gap)
xs = [X0 - .06 * s + i * .015 * s for i in range(int((X1 - X0 + .12 * s) / (.015 * s)) + 1)]
tops = probe([{"o": [x, (1.62 + .49 * (x / s - .44) / .88) * s - .12 * s, 0], "d": [0, 1, 0]} for x in xs])
T = {x: (1.62 + .49 * (x / s - .44) / .88) * s - .12 * s + t for x, t in zip(xs, tops) if t is not None}
def lerp1(tab, x):
    ks = sorted(tab); x = min(max(x, ks[0]), ks[-1])
    for a, b in zip(ks, ks[1:]):
        if a <= x <= b: return tab[a] + (tab[b] - tab[a]) * (x - a) / (b - a)
    return tab[ks[-1]]
top = lambda x: lerp1(T, x)
ridge = next((q for q in sh if q.get("id") == "maneRidge"), None)
if ridge is not None:
    # the crest's under-layer was laid straight from withers to poll and stood clear of the neck behind the poll, where
    # the neck's top dips (a block the slab hid): now laid along the neck's own top (found with it out), just under it,
    # thinning to the poll -- so the locks rooted in it sit on the neck everywhere
    sh.remove(ridge); retmp()
    tops = probe([{"o": [x, (1.62 + .49 * (x / s - .44) / .88) * s - .12 * s, 0], "d": [0, 1, 0]} for x in xs])
    T0 = {x: (1.62 + .49 * (x / s - .44) / .88) * s - .12 * s + t for x, t in zip(xs, tops) if t is not None}
    zr = ridge["pts"][0][2]
    rx = [.44, .62, .80, .95, 1.08, 1.18, 1.29]; rr_ = [.032, .04, .04, .038, .034, .03, .022]    # (ending at the poll)
    ridge["pts"] = [[R5(x * s), R5(lerp1(T0, x * s) - (r * .55) * s), zr, R5(r * s)] for x, r in zip(rx, rr_)]
    sh.insert(next(i for i, q in enumerate(sh) if q.get("id") == "crest") + 1, ridge); SQ["maneRidge"] = ridge; retmp()
    tops = probe([{"o": [x, (1.62 + .49 * (x / s - .44) / .88) * s - .12 * s, 0], "d": [0, 1, 0]} for x in xs])
    T = {x: (1.62 + .49 * (x / s - .44) / .88) * s - .12 * s + t for x, t in zip(xs, tops) if t is not None}
DROPS = [i * .015 * s for i in range(28)]
side = {}
for sg in (-1, 1):
    Q = [{"o": [x, top(x) - dr, 0], "d": [0, 0, sg]} for x in xs for dr in DROPS]
    R = probe(Q); i = 0
    for x in xs:
        for dr in DROPS:
            side[(sg, x, dr)] = R[i]; i += 1
def zside(sg, x, dr):   # the side's z (signed) at x, dr below the top there; None below the neck
    ks = xs; x = min(max(x, ks[0]), ks[-1])
    j = max(0, min(len(ks) - 2, int((x - ks[0]) / (ks[1] - ks[0])))); fx = (x - ks[j]) / (ks[1] - ks[0])
    k = max(0, min(len(DROPS) - 2, int(dr / DROPS[1]))); fd = min(1, max(0, (dr - DROPS[k]) / DROPS[1]))
    v = [side[(sg, ks[j + a], DROPS[k + b])] for a in (0, 1) for b in (0, 1)]
    if any(q is None for q in v): return None
    return sg * ((v[0] * (1 - fd) + v[1] * fd) * (1 - fx) + (v[2] * (1 - fd) + v[3] * fd) * fx)

rnd = random.Random({"horse": 7, "unicorn": 11, "zebra": 5}[mode])
R5 = lambda v: round(v, 4)
locks = []
def lock(lid, x, L, r0, g, sg=-1, lift=.028, back=.16, flare=.10, bone="neck", rtip=None, extra=None):
    """a lock rooted on the crest at x, over to side sg and falling L below the top"""
    t = top(x); rt = max(RMIN, rtip or r0 * .28)
    P = [[x + .012 * s, t - .03 * s, -sg * .012 * s, r0 * .85],
         [x + .006 * s, t + lift * .7 * s, sg * .004 * s, r0],
         [x, t + lift * .55 * s, sg * .035 * s, r0 * .97]]
    n = 5
    zlast = None
    for j in range(1, n + 1):
        f = j / n; dr = .025 * s + (L - .025 * s) * f ** 1.1
        xd = x - back * dr - .004 * s * j
        rd = r0 * (1 - f ** 1.3) + rt * f ** 1.3
        zs = zside(sg, xd, dr)
        if zs is None: zs = (zlast if zlast is not None else sg * .06 * s) + sg * .01 * s
        if zlast is not None and sg * zs < sg * zlast: zs = zlast      # (no kinks back in, where the neck narrows at the throat)
        zlast = zs
        P.append([xd, t - dr, zs + sg * (rd + g + flare * dr * f), rd])
    q = {"id": lid, "type": "tube", "bone": bone, "pts": [[R5(v) for v in p] for p in P], "k": 0, "color": "@mane"}
    if extra: q.update(extra)
    locks.append(q)

if mode in ("horse", "unicorn"):
    U = mode == "unicorn"
    r0 = min(RMAX, .0145 * s)
    nA = 34
    poll = lambda u: max(.6, min(1, (1 - u) / .16))    # (shorter to the poll, as a mane is behind the ears)
    for i in range(nA):   # the outer layer: long, each its own length, the tips apart
        u = (i + .5) / nA; x = X0 + (X1 - X0) * u + rnd.uniform(-.006, .006) * s
        base = (.13 + .11 * math.sin(math.pi * min(1, u * 1.08)) ** .8) * s * (1.35 if U else 1)
        L = base * rnd.uniform(.72, 1.22) * (.8 if i % 4 == 3 else 1) * poll(u)
        lock(f"lkA{i}", x, L, r0, g=.012 * s, lift=rnd.uniform(-.004, .008), flare=rnd.uniform(.05, .15))
    nB = 28
    for i in range(nB):   # under it, shorter and closer to the neck: the mane's depth
        u = (i + 1) / (nB + 1); x = X0 + (X1 - X0) * u + rnd.uniform(-.008, .008) * s
        base = (.10 + .08 * math.sin(math.pi * u) ** .8) * s * (1.3 if U else 1)
        lock(f"lkB{i}", x, base * rnd.uniform(.75, 1.15) * poll(u), r0 * .9, g=.002 * s, lift=-.006, flare=.04)
    nC = 9 if U else 6
    for i in range(nC):   # a few flopped over to the near side
        u = .08 + .84 * (i + rnd.uniform(.2, .8)) / nC; x = X0 + (X1 - X0) * u
        L = (rnd.uniform(.08, .13) if not U else rnd.uniform(.13, .2)) * s
        lock(f"lkC{i}", x, L, r0 * .85, g=.002 * s, sg=1, lift=-.004, flare=.03)
    # ---- the forelock: from the poll between the ears forward and down the forehead, short (a unicorn's longer, parted
    # round its horn); the forehead found by rays up from inside the head, the locks laid along it, a radius off it
    fx0 = old_fore["c"][0]
    def surf(Q):   # [(x, z)] -> the head's top y there (None off it)
        r = probe([{"o": [x, 1.86 * s, z], "d": [0, 1, 0]} for x, z in Q])
        return [None if v is None else 1.86 * s + v for v in r]
    cand = [fx0 - .16 * s + .005 * s * i for i in range(33)]
    prof = surf([(x, 0) for x in cand])
    xp = max((y, x) for x, y in zip(cand, prof) if y is not None and y < 2.4 * s)[1] - .012 * s    # the poll
    # (a unicorn's: between its ears, then parting to either side of the horn, clear of it)
    zs = [(-.036, -.066), (-.024, -.044), (-.012, -.02), (0, .002), (.012, .024), (.024, .046), (.034, .062)] if not U else \
         [(-.022, -.088), (-.013, -.072), (-.005, -.056), (.005, .056), (.013, .072), (.022, .088)]
    FL = (.24 if not U else .26) * s
    plan = []
    for j, z0 in enumerate(zs):
        L = FL * rnd.uniform(.62, 1.05)
        xs_ = [xp - .008 * s + .008 * s * k for k in range(int((L * .75 + .008 * s) / (.008 * s)) + 2)]
        za, zb = z0; sm = lambda f: f * f * (3 - 2 * f)
        zz = [za + (zb - za) * (min(1, max(0, x - xp) / (L * .75)) if not U else sm(min(1, max(0, (x - xp - .045 * s) / (.075 * s))))) for x in xs_]
        plan.append((L, xs_, zz))
    flat = [(x, z) for L, xs_, zz in plan for x, z in zip(xs_, zz)]
    Y = surf(flat); i = 0
    for j, (L, xs_, zz) in enumerate(plan):
        ys = Y[i:i + len(xs_)]; i += len(xs_)
        pts_ = []
        for x, y, z in zip(xs_, ys, zz):    # (not over an ear: a step up off the line of the forehead)
            if y is None or (len(pts_) > 1 and y > pts_[-1][1] + .012 * s): continue
            pts_.append((x, y, z))
        r1 = min(RMAX, .0135 * s); rt = max(RMIN, r1 * .3)
        P = [[pts_[0][0], pts_[0][1] - .03 * s, pts_[0][2], r1 * .8]]       # the root, in the poll
        arc = 0; prev = None; m = len(pts_)
        for k in range(1, m, 1 if m < 9 else 2):
            x, y, z = pts_[k]; xa, ya, _ = pts_[k - 1]
            if prev: arc += math.hypot(x - prev[0], y - prev[1])
            prev = (x, y)
            tx, ty = x - xa, y - ya; n_ = math.hypot(tx, ty); nx, ny = -ty / n_, tx / n_
            if ny < 0: nx, ny = -nx, -ny
            f = min(1, arc / L); rr = r1 * (1 - f ** 1.4) + rt * f ** 1.4
            off = rr + .003 * s + .024 * s * f * f     # (the tips a little off the face)
            P.append([x + nx * off, y + ny * off, z, rr])
            if arc >= L: break
        locks.append({"id": f"fl{j}", "type": "tube", "bone": "head", "pts": [[R5(v) for v in p] for p in P], "k": 0, "color": "@mane"})
elif mode == "zebra":
    # the brush (2026-11-07, second pass): a zebra's mane stands up stiff and DENSE -- three staggered rows of thin
    # bristles, each standing along the crest's own normal (a touch back), as tall as the next but for a few per cent,
    # so the top is one smooth rounded line: highest mid-neck, low at the withers and at the poll; the outer rows a
    # little shorter, so it is rounded across too. STRIPED: each bristle black or white as the neck's bands are at its
    # root -- read off the render itself (var/zeb/bands.json: samp.js + parse.py; stripe.mjs, a CPU copy of coatpat.js
    # stripesOf, the fallback), so the bands
    # run on up through the brush; and the Grevy's coat (patScale .6) its own narrower bands: four colour keys, the
    # plains band and the Grevy's band at the root (zbWW .. zbDD), which the coats fill. No forelock (a zebra's is
    # barely there).
    r0 = .0085; rt = max(RMIN, .006)
    n = 66; rows = ((0.0, -.0085), (1 / 3, .0), (2 / 3, .0085))
    # (the plates seated low: a striped base under the brush, never standing through it -- each one's top at most
    #  1.2 cm over the neck's top there)
    for q in sh:
        if re.match(r"^mane\d+P?$", q.get("id", "")):
            a = math.radians(q["rot"][2]); ty = q["c"][1] + math.hypot(q["r"][0] * math.sin(a), q["r"][1] * math.cos(a))
            ex = ty - (top(q["c"][0]) + .012)
            if ex > 1e-4: q["c"] = [q["c"][0], round(q["c"][1] - ex, 4), q["c"][2]]; SQ[q["id"]] = q
    # (the tips on the neck's top SMOOTHED -- a running mean over 12 cm -- so a bump of the crest under the brush does
    #  not step its edge)
    ts = lambda x: sum(top(x + k * .01) for k in range(-6, 7)) / 13
    sl = lambda x: (ts(x + .01 * s) - ts(x - .01 * s)) / (.02 * s)
    B = []
    for i in range(n):
        for k, (off, dz) in enumerate(rows):
            u = (i + off + .2) / n
            x = X0 - .03 * s + (X1 - X0 + .03 * s) * u
            t = top(x); t1 = ts(x); m_ = sl(x); nl = math.hypot(m_, 1); nx, ny = -m_ / nl, 1 / nl
            a = math.radians(12); nx, ny = nx * math.cos(a) - ny * math.sin(a), nx * math.sin(a) + ny * math.cos(a)   # (a touch back)
            h = (.03 + .085 * math.sin(math.pi * min(1, max(0, u))) ** .75) * s * (.9 if dz else 1) * rnd.uniform(.97, 1.03)
            z0 = dz * s; tx, ty_ = x + nx * h, t1 + ny * h
            P = [[x - nx * .022 * s, t - ny * .022 * s, z0 * .6, r0 * .9], [x, t, z0, r0],
                 [(x + tx) / 2, (t + ty_) / 2, z0 * 1.12, r0 * .85], [tx, ty_, z0 * 1.2, rt]]
            B.append((f"brush{i}{'abc'[k]}", P, [x, t, 0]))
    BT = os.path.join(HERE, "..", "zeb", "bands.json")
    if os.path.exists(BT):   # (the bands as the render draws them, read off it: var/zeb/samp.js + parse.py)
        tab = {float(k): v for k, v in json.load(open(BT))["x"].items()}
        M = [[tab[min(tab, key=lambda q: abs(q - b[2][0]))][0], tab[min(tab, key=lambda q: abs(q - b[2][0]))][1]] for b in B]
    else:    # (or as the shader's own function computes them on the CPU -- close, not exact: its hashes are sin-based)
      qf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); json.dump({"pts": [b[2] for b in B], "S": [1, .6]}, qf); qf.close()
      M = json.loads(subprocess.run(["node", HERE + "/../zeb/stripe.mjs", HERE + "/../zeb/dump.json", qf.name], capture_output=True, text=True, check=True).stdout)
      os.unlink(qf.name)
    for (bid, P, _), (m1, m2) in zip(B, M):
        key = "zb" + ("D" if m1 > .5 else "W") + ("D" if m2 > .5 else "W")
        locks.append({"id": bid, "type": "tube", "bone": "neck", "pts": [[R5(v) for v in p] for p in P], "k": 0, "color": "@" + key})
os.unlink(tmp.name)
# (written into the file's own text: the old mane's lines out, the locks' lines in after the crest's under-layer, the
# mesh line pinned -- every other line as it was, so the file keeps its own layout)
lines = open(src).read().split("\n")
def sid(l):
    m = re.match(r'\s*\{"id": "([^"]+)"', l); return m and m.group(1)
ind = next(l[:len(l) - len(l.lstrip())] for l in lines if sid(l) == "crest")
keep = [l for l in lines if not (sid(l) and OLD.match(sid(l)))]
keep = [(l[:len(l) - len(l.lstrip())] + json.dumps(SQ[sid(l)], ensure_ascii=False) + ("," if l.rstrip().endswith(",") else "")) if sid(l) in SQ else l for l in keep]
for q in NEW:   # (the poll's line, after the crest's)
    ci = next(i for i, l in enumerate(keep) if sid(l) == "crest")
    keep.insert(ci + 1, ind + json.dumps(q, ensure_ascii=False) + ",")
at = next((i for i, l in enumerate(keep) if sid(l) == "maneRidge"), None)
if at is None: at = next(i for i, l in enumerate(keep) if sid(l) == "crest")
keep[at + 1:at + 1] = [ind + json.dumps(q, ensure_ascii=False) + "," for q in locks]
txt = "\n".join(keep)
txt = re.sub(r'"mesh": \{[^}]*\}', '"mesh": ' + json.dumps(d["sculpt"]["mesh"]), txt, count=1)
if mode == "zebra":
    DK = "#3a3939"
    txt = re.sub(r'\n\s*"zb[WD][WD]": "#[0-9a-f]+",?', "", txt)
    txt = re.sub(r', "zb[WD][WD]": "#[0-9a-f]+"', "", txt)
    m0 = re.search(r'\n(\s*)"mane": "#[0-9a-f]+",', txt)
    body = re.search(r'"colors": \{[^}]*"body": "(#[0-9a-f]+)"', txt).group(1)
    txt = txt[:m0.end()] + "".join(f'\n{m0.group(1)}"zb{a}{b}": "{DK if a == "D" else body}",' for a in "WD" for b in "WD") + txt[m0.end():]
    def grevy(mm):
        l = mm.group(0); gb = re.search(r'"body": "(#[0-9a-f]+)"', l).group(1)
        return l[:-1] + "".join(f', "zb{a}{b}": "{DK if b == "D" else gb}"' for a in "WD" for b in "WD") + "}"
    txt = re.sub(r'\{"name": "Grevy\'s"[^\n]*?\}(?=,?\n)', grevy, txt, count=1)
json.loads(txt)
open(out, "w").write(txt)
print(mode, "locks", len(locks), "cell", CELL, "rmax", round(RMAX, 4), "max r", max(p[3] for q in locks for p in q["pts"]), "min r", min(p[3] for q in locks for p in q["pts"]))
