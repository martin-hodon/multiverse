import sys, json; sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import *
# The manticore: a lion's body -- the lion's own rig and shapes (mammals/lion.json, as they stand today) scaled from its
# .95 to the manticore's .9 -- in cinnabar red, its mane in the lion's fleece; a dragon's bat wings at the withers, folded along the flank at rest;
# and in place of the lion's tail a SCORPION's: a path of tubes from the croup arching up and forward over the
# hindquarters, drawn as seven glossy knobbed segments to a bulbous vesicle and the aculeus curving forward and down
K = .9 / .95
GEO = {"c", "r", "a", "b", "ra", "rb", "k", "kc", "pts", "at", "from"}
def scl(v, f):
    if isinstance(v, list): return [scl(x, f) for x in v]
    if isinstance(v, (int, float)): return v * f
    return v
lion = json.load(open(R + "mammals/lion.json"))
src = lion["sculpt"]
sh = [{k: (scl(v, K) if k in GEO else v) for k, v in p.items()} for p in src["shape"]]
# (the mane matte and soft: no hair sheen, no fleece lumps on its prims -- those read as glossy crumpled foil)
for p in sh:
    if p.get("id", "").startswith("mane"):
        for k_ in ("hair", "fleece", "sheen", "wet"): p.pop(k_, None)
by = {p["id"]: p for p in sh}
def mv(pid, dx=0, dy=0, keys=("c", "a", "b")):
    p = by[pid]
    for k in keys:
        if k in p: p[k] = [p[k][0] + dx, p[k][1] + dy, p[k][2]]
# (the face: the muzzle drawn forward a lion's length, the whisker pads and the chin with it, the nose down onto its tip)
mv("muzzle", .05); by["muzzle"]["r"] = [by["muzzle"]["r"][0] * 1.3, by["muzzle"]["r"][1], by["muzzle"]["r"][2]]
mv("pad", .065, -.008); by["pad"]["r"] = [x * 1.12 for x in by["pad"]["r"]]
mv("chin", .05, -.005); mv("lip", .06, -.006)
by["bridge"]["b"] = [by["bridge"]["b"][0] + .065, by["bridge"]["b"][1] - .012, 0]
mv("nose", .068, -.03)
# (the ears up out of the mane, larger)
for pid in ("ear", "earIn", "earBack"):
    mv(pid, -.005, .055); by[pid]["r"] = [x * 1.25 for x in by[pid]["r"]]
# (the legs a lion's: forearms and paws a fifth heavier)
f = by["forearm"]; f["ra"] *= 1.2; f["rb"] *= 1.2
by["paw"]["r"] = [.085, .05, .078]; by["hpaw"]["r"] = [.08, .048, .072]
for pid, bone in (("paw", "footFL"), ("hpaw", "footHL")):
    p = by[pid]; p["color"] = "@leg"; c, r = p["c"], p["r"]
    for j, dz in enumerate((-.66, -.22, .22, .66)):   # four toes across the paw's front, each a dark pad under it
        tc = [c[0] + r[0] * (.62 - .12 * abs(dz)), c[1] - r[1] * .15, c[2] + dz * r[2] * .8]
        sh.append({"id": f"{pid}Toe{j}", "type": "ell", "bone": bone, "c": tc, "r": [.026, .03, .02], "k": .012, "color": "@leg", "mirror": True})
        sh.append({"id": f"{pid}Pad{j}", "type": "ell", "bone": bone, "c": [tc[0] + .012, tc[1] - .022, tc[2]], "r": [.023, .013, .017], "k": .004, "kc": .003, "color": "@toePad", "mirror": True})
for pid in ("arm", "pastern"):
    p = by.get(pid)
    if p and "pts" in p: p["pts"] = [q[:3] + [q[3] * 1.15] for q in p["pts"]]
    elif p and "ra" in p: p["ra"] *= 1.15; p["rb"] *= 1.15
rig = {k: scl(lion[k], K) for k in ("rear", "front", "neck", "head", "muzzle", "nose", "ears", "eyes")}
legs = {k: scl(v, K) for k, v in lion["legs"].items()}
# ---- the scorpion's tail: the rig's path (mammals.js pathChain: a quadratic B-spline through the sides' middles, one
# tube per corner), and the same curve here to lay the segments along it
P = [[-.8, .95], [-1.05, 1.1], [-1.1, 1.42], [-.95, 1.66], [-.68, 1.7], [-.52, 1.55]]
mid = lambda a, b: [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
tubes = []
for i, C in enumerate(P[1:-1]):
    A = mid(P[i], C) if i else P[0]; B = P[-1] if i == len(P) - 3 else mid(C, P[i + 2]); tubes.append((A, C, B))
def bez(t, A, C, B):
    u = 1 - t; return [u * u * A[j] + 2 * u * t * C[j] + t * t * B[j] for j in range(2)]
samples = []   # (point, tangent, bone)
for i, (A, C, B) in enumerate(tubes):
    for j in range(40):
        t = j / 40; p = bez(t, A, C, B); q = bez(t + .001, A, C, B)
        samples.append((p, [q[0] - p[0], q[1] - p[1]], "tail" if i == 0 else f"tail{i}"))
samples.append((P[-1], [P[-1][0] - P[-2][0], P[-1][1] - P[-2][1]], f"tail{len(tubes) - 1}"))
acc = [0.0]
for a, b in zip(samples, samples[1:]): acc.append(acc[-1] + math.dist(a[0], b[0]))
Ltot = acc[-1]
def at(s):   # point, tangent angle, bone at arc length s
    for i in range(len(acc) - 1):
        if acc[i + 1] >= s: break
    p, t, b = samples[i]; return p, math.degrees(math.atan2(t[1], t[0])), b
R1, R2 = .072, .05
NS = 7
for i in range(NS):
    s0, s1 = Ltot * (.03 + .97 * i / NS), Ltot * (.03 + .97 * (i + 1) / NS)
    sm = (s0 + s1) / 2; p, ang, b = at(sm); r = R1 + (R2 - R1) * sm / Ltot; half = (s1 - s0) / 2
    col = "@tailRoot" if i == 0 else ("@sting" if i % 2 else "@sting2")
    sh.append({"id": f"meta{i}", "type": "ell", "bone": b, "c": [p[0], p[1], 0], "r": [half * 1.1, r, r * .92], "rot": [0, 0, ang], "k": .007, "kc": .005, "color": col,
               **({"hair": 1} if i == 0 else {"wet": .3})})
    # (a knob each side at the segment's far end, and the keel along its top: a scorpion's segments are ridged)
    pe, ange, be = at(s1 - half * .3)
    sh.append({"id": f"knob{i}", "type": "sphere", "bone": be, "c": [pe[0], pe[1], r * .62], "r": r * .42, "k": .01, "kc": .004, "color": col, "mirror": True, **({} if i == 0 else {"wet": .3})})
# (the core the segments are strung on: one tube per bone along its own curve, narrower -- the joints' waists)
for i, (A, C, B) in enumerate(tubes):
    pts = []
    for j in range(5):
        p = bez(j / 4, A, C, B); s_ = acc[min(len(acc) - 1, i * 40 + j * 10)]
        pts.append([p[0], p[1], 0, (R1 + (R2 - R1) * s_ / Ltot) * .6])
    sh.append({"id": f"core{i}", "type": "tube", "bone": "tail" if i == 0 else f"tail{i}", "pts": pts, "k": .01, "kc": .005, "color": "@body" if i == 0 else "@sting", **({"hair": 1} if i == 0 else {"wet": .3})})
# the telson: the bulbous vesicle at the tip, the aculeus curving forward and down from it
pT, angT, bT = at(Ltot); d = [math.cos(math.radians(angT)), math.sin(math.radians(angT))]; n = [d[1], -d[0]]   # (n: below the curve -- its inside)
vc = [pT[0] + d[0] * .08, pT[1] + d[1] * .08]
sh.append({"id": "vesicle", "type": "ell", "bone": bT, "c": vc + [0], "r": [.14, .098, .09], "rot": [0, 0, angT], "k": .02, "kc": .006, "color": "@sting2", "wet": .4})
ac = [[vc[0] + d[0] * .11, vc[1] + d[1] * .08, 0, .04], [vc[0] + d[0] * .18 + n[0] * .03, vc[1] + d[1] * .15 + n[1] * .03, 0, .025],
      [vc[0] + d[0] * .22 + n[0] * .1, vc[1] + d[1] * .19 + n[1] * .1, 0, .013], [vc[0] + d[0] * .2 + n[0] * .17, vc[1] + d[1] * .17 + n[1] * .17, 0, .005]]
sh.append({"id": "aculeus", "type": "tube", "bone": bT, "pts": ac, "k": .01, "kc": .004, "color": "@stingTip", "wet": .5})

eyes = {k: (scl(v, K) if k in GEO else v) for k, v in src["eyes"].items()}
# (countershaded: bodymesh.js shade -- the back darker, the belly and inner legs paler, the legs back to the coat below)
coat = dict(src["coat"]); coat.update({"tip": "#7a2c1c", "base": "#2e100a", "darkTip": "#1a0806"})
m = json.load(open(R + "monsters/manticore.json"))
import subprocess
WK, WAT = .8, [.38, 1.0, .17]
W = json.loads(subprocess.check_output(["node", __file__.rsplit("/", 1)[0] + "/dwing.mjs", json.dumps({"k": WK, "bone": "#5a2618", "mem": "#3a1812", "speed": .35, "deg": 3, "rest": {"hand": -213, "tilt": 20, "close": .15, "pleat": .4, "fpleat": .2}}), json.dumps(WAT)]))
extras = []
for S_, sg in (("L", 1), ("R", -1)):
    for i, p in enumerate(W[S_]["parts"]):
        extras.append({"raw": p, "at": [WAT[0], WAT[1], sg * WAT[2]]} if i == 0 else {"raw": p})
g = W["L"]["geo"]; k = g["k"]
def T_(pid, pts, col, bone, kk):
    sh.append({"id": pid, "type": "tube", "bone": bone, "pts": pts, "k": kk, "color": col, "mirror": True})
T_("humerus", [g["S0"] + [.085 * k], lerp(g["S0"], g["Elb"], .5) + [.06 * k], g["Elb"] + [.042 * k]], "@wbone", "wArmL", .03)
T_("forearmW", [g["Elb"] + [.042 * k], lerp(g["Elb"], g["W"], .5) + [.03 * k], g["W"] + [.036 * k]], "@wbone", "wArmL", .02)
sh.append({"id": "wrist", "type": "sphere", "bone": "wArmL", "c": g["W"], "r": .045 * k, "k": .015, "color": "@wbone", "mirror": True})
sh.append({"id": "thumb", "type": "cone", "bone": "wHandL", "a": g["W"], "b": g["thumb"], "ra": .02 * k, "rb": .004 * k, "k": 0, "color": "@stingTip", "mirror": True})
for i, f in enumerate(g["fingers"]):
    # (one cone from inside the wrist to the tip -- the knuckle lies within 1 cm of its axis: one mesh, rooted in the
    #  wrist; two chained cones were two detail meshes, the outer one counted as floating, and a thin tube's lathe splits)
    sh.append({"id": f"finger{i}", "type": "cone", "bone": f["bone"] + "L", "a": g["W"], "b": f["tip"], "ra": .021 * k, "rb": .007 * k, "k": 0, "color": "@wbone", "mirror": True})
sh.append({"id": "wingMound", "type": "ell", "c": [g["S0"][0] - .04, g["S0"][1] - .08, g["S0"][2] * .6], "r": [.2, .1, .11], "rot": [-20, 0, 0], "k": .07, "color": "@body", "mirror": True})
def membranes():
    """the wedges of skin, authored from the rig's own (each on its bone: they open aloft), and over each FOLDED bundle a
    smooth cover -- one plate, its outline the bundle's hull, a lighter middle and a darker rim -- on a bone that does
    not open (the arm for the arm's skin, the leading finger for the hand's), so that aloft it lies inside the spread
    membrane's own plane (the arm's skin between the leading edge and the root; the first gap, behind the first finger)
    (SUPERSEDED 2026-11-08: plates on different bones posed apart and their shared edges opened into slivers aloft.
    var/isl/mantwing.py now makes each wing ONE membrane with shared vertices from these plates' outline, and drops
    the plates, the covers, the hand cover (var/isl/mantcov.py) and the plates' bones)"""
    import numpy as np
    tris = json.loads(subprocess.check_output(["node", __file__.rsplit("/", 1)[0] + "/mwing.mjs", "manticore", "wMem\\S*"], cwd="/home/martin/store/apps/multiverse"))
    res = [{"id": q["bone"] + "M", "type": "tri", "bone": q["bone"], "a": q["a"], "b": q["b"], "c": q["c"], "r": q["r"], "color": "@mem"} for q in tris]
    for S_, sg in (("L", 1), ("R", -1)):
        for grp, bone in (("wMemA", f"wArm{S_}"), ("wMemB", f"wFinger0{S_}")):
            P = np.array([v for q in tris if q["bone"].startswith(grp) and q["bone"].endswith(S_) for v in (q["a"], q["b"], q["c"])])
            C = P.mean(0); U, Sv, Vt = np.linalg.svd(P - C); e1, e2, n = Vt[0], Vt[1], Vt[2]
            if n[2] * sg < 0: n = -n
            if np.cross(e1, e2) @ n < 0: e2 = -e2
            uv = (P - C) @ np.stack([e1, e2]).T; dev = ((P - C) @ n).max()
            pts = sorted(set(map(tuple, np.round(uv, 5))))
            def half(seq):
                h = []
                for p in seq:
                    while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0: h.pop()
                    h.append(p)
                return h
            hull = half(pts)[:-1] + half(pts[::-1])[:-1]
            # (the hull's corners rounded: each point pulled a third of the way to its neighbours' middle, twice)
            H = np.array(hull)
            for _ in range(2):
                H = H * .67 + (np.roll(H, 1, 0) + np.roll(H, -1, 0)) * .165
            m0 = H.mean(0); dH = H - m0; H = H + dH / np.linalg.norm(dH, axis=1)[:, None] * .06   # (a little over the bundle's edge: seen aslant, no wedge peeps past it)
            m2 = H.mean(0); lift = lambda q2: (C + e1 * q2[0] + e2 * q2[1] + n * (dev + .006)).tolist()
            out_ = [lift(q2) for q2 in H]; inn = [lift(m2 + (q2 - m2) * .72) for q2 in H]; cen = lift(m2)
            th = tris[0]["r"]
            for i in range(len(H)):
                j = (i + 1) % len(H); tag = f"{grp}Cov{S_}{i}"
                res += [{"id": tag + "c", "type": "tri", "bone": bone, "a": cen, "b": inn[i], "c": inn[j], "r": th, "color": "@memIn"},
                        {"id": tag + "e", "type": "tri", "bone": bone, "a": inn[i], "b": out_[i], "c": out_[j], "r": th, "color": "@mem"},
                        {"id": tag + "f", "type": "tri", "bone": bone, "a": inn[i], "b": out_[j], "c": inn[j], "r": th, "color": "@mem"}]
    return res
out = {
    "name": "manticore",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a lion's body -- the lion's own rig and shapes (mammals/lion.json) scaled from its .95 to .9 -- in cinnabar red, the mane in the lion's fleece, darker; a dragon's bat wings at the withers (dragons.js dragonBatWing, as rig parts: four finger bones drawn by the body, the membranes kept), folded along the flank at rest and spread aloft by flyRot; and for a tail a scorpion's, on a path of tubes from the croup arching up and forward over the hindquarters (clear of a rider), drawn as seven glossy knobbed segments, the bulbous vesicle and the aculeus curving forward and down",
    "use": m["use"],
    "params": {"s": .9, "tuft": 0, "tailSway": 10},
    **rig,
    "legs": legs,
    "tail": {"path": P, "r1": R1, "r2": R2, "tuft": 0, "sway": 10, "speed": .5},
    "colors": {"body": "#8e3b28", "head": "#a04a30", "muzzle": "#c27a52", "ear": "#5a2418", "leg": "#7e3424", "eye": "#d9a520", "nose": "#3a1a14", "tuft": "#3a2a20",
               "tail": "#8e3b28", "white": "#d29a78", "cream": "#b8684a", "pale": "#a85a3c", "black": "#1a0c08", "bridge": "#963f2a",
               "maneF": "#5e2418", "maneM": "#562016", "tear": "#3e160e", "mane": "#4a1c12", "maneD": "#34120c", "sting": "#3c1812", "wbone": "#5a2618", "mem": "#30130c", "memIn": "#52241a", "back": "#6a2618", "tailRoot": "#5e2216", "toePad": "#22100a", "sting2": "#4a1e16", "stingTip": "#140806"},
    "mount": m["mount"],
    "extras": extras,
    "flight": {"beat": 7, "handK": .6},
    "monster": True,
    "print": m["print"],
    "sculpt": {"keep": ["wMem\\S*"], "shade": {"back": .72, "belly": 1.3, "k": .2, "low": 1.0, "on": "@body"}, "mesh": {"tris": [6000, 2000]}, "shape": sh, "eyes": eyes, "coat": coat},
}
dump("monsters/manticore.json", out)          # (pass 1: the membranes kept, to read where the overlay puts them)
mem = membranes()
out["sculpt"]["keep"] = []; out["sculpt"]["shape"] = sh + mem
out["_about"] = out["_about"].replace("the membranes kept), folded along the flank at rest", "the membranes authored: each wedge of skin a plate on its own bone, darker at its edge), folded up and back over the rump at rest")
dump("monsters/manticore.json", out)
print(len(sh), "shapes, tail length", round(Ltot, 3))
