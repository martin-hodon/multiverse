# ears.py (2026-11-08): the zebra's, giraffe's and kangaroo's EAR sheets (sharp.js `fin`) dressed and reshaped -- their
# knobs (a field ball at the root) gone, each root FAIRED into the head (`fair`); colour by the fin's own bands (`rim`,
# `rimAt`, `tip`, `inner`, `innerRim`) and a pattern on the back only (`patFace`). Run from tools/creaturegen/sharp:
# python3 ears.py (it works from the backup of the ears as named.py left them: ears_orig.json beside it, made once)
import json, math, os
from shp import load, save, sub, add, mul, dot, crs, nrm, ln
HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
BK = HERE + "ears_orig.json"
SP = {"mammals/zebra": ["ear", "earBase"], "mammals/giraffe": ["ear", "earBase"], "mammals/kangaroo": ["ear", "earB"]}
if not os.path.exists(BK):
    json.dump({sp: [p for p in load(sp)[1]["sculpt"]["shape"] if p.get("id") in ids] for sp, ids in SP.items()}, open(BK, "w"))
ORIG = json.load(open(BK))

def rot(v, a, th):   # v about the unit axis a by th (Rodrigues)
    c, s = math.cos(th), math.sin(th)
    return add(add(mul(v, c), crs(a, v), s), a, dot(a, v) * (1 - c))

def about(p, o, a, th): return add(o, rot(sub(p, o), a, th))

def r4(v): return [round(x, 4) for x in v]

def ear_of(sp): return json.loads(json.dumps([p for p in ORIG[sp] if p["id"] == "ear"][0]))

def put(sp, ear):
    txt, d = load(sp); sh = d["sculpt"]["shape"]
    drop = set(SP[sp]) - {"ear"}
    out = []
    for p in sh:
        if p.get("id") in drop: continue
        out.append(ear if p.get("id") == "ear" else p)
    save(sp, out, txt)

# ZEBRA: the shape kept (named.py's); the BACK striped (the coat's bands in a frame up the ear: stripes across it), a
# dark band round the edge and the tip dark, the hollow white and hairy (`inner`, plain), the root faired
e = ear_of("mammals/zebra")
R0 = [(a + b) / 2 for a, b in zip(e["root"][0], e["root"][1])]; TIP = e["edge"][e["corners"][0]][:3]
e.update({"pat": "bands", "patFace": "back", "frame": {"o": r4(R0), "u": r4(nrm(sub(TIP, R0))), "v": r4([-x for x in e["face"]]), "r": 0.03},
          "rim": 0.005, "rimColor": "@mane", "tip": "@mane", "tipAt": 0.72, "inner": "@earIn", "innerRim": 0.004, "fair": 0.012, "cup": 0.6})
put("mammals/zebra", e)

# GIRAFFE: a fuller cupped LEAF -- turned about its length so the hollow faces forward and out (it faced the ground),
# widened, drooping a little, thicker at the root; pale inside, the far rim dark
e = ear_of("mammals/giraffe")
R0 = [(a + b) / 2 for a, b in zip(e["root"][0], e["root"][1])]; ti = e["corners"][0]; TIP = e["edge"][ti][:3]
ax = nrm(sub(TIP, R0))
def width(p, f):   # (its offset from the ear's axis line, times f)
    q = sub(p[:3], R0); along = mul(ax, dot(q, ax)); return add(add(R0, along), sub(q, along), f)
want = nrm([0.55, -0.25, 0.8])
best = max((dot(rot(e["face"], ax, math.radians(t)), want), t) for t in range(-180, 180, 2))[1]
th = math.radians(best)
droop_ax = nrm(crs(ax, [0, 1, 0]))   # (horizontal, square to the ear: turning about it tips the ear down)
dr = math.radians(18)
if dot(rot(ax, droop_ax, dr), [0, 1, 0]) > dot(ax, [0, 1, 0]): dr = -dr
def move(p, f=1.25):
    q = width(p, f); q = about(q, R0, ax, th); q = about(q, R0, droop_ax, dr); return r4(q) + list(p[3:])
e["edge"] = [move(p) for p in e["edge"]]
e["root"] = [move(p, 1.0) for p in e["root"]]
e["face"] = r4(rot(rot(e["face"], ax, th), droop_ax, dr))
e.update({"cup": 0.75, "thick": 0.017, "slope": 0.4, "inner": "@body", "innerRim": 0.006, "rim": 0.006, "rimColor": "@maneTip", "rimAt": 0.55,
          "tip": "@mane", "tipAt": 0.8, "fair": 0.015})
put("mammals/giraffe", e)

# KANGAROO: a tall rounded-tipped cone of skin (the corner at the tip dropped and the outline there rounded), cupped
# deep toward the front, its far edge dark; no ball at the root, the root faired
e = ear_of("mammals/kangaroo")
ti = e["corners"][0]; E = e["edge"]
c = [(a + b) / 2 for a, b in zip(E[ti - 2][:3], E[ti + 2][:3])]
for k in (-1, 0, 1):   # (the three points round the tip pulled in toward the chord below them: a round end)
    p = E[ti + k]; f = 0.45 if k == 0 else 0.25
    E[ti + k] = r4(add(p[:3], sub(c, p[:3]), f)) + list(p[3:])
e.pop("corners", None)
# (its root sunk into the head: it stood on the ball before, 1.5-3 cm clear of the skin -- the root line moved down the
#  ear's axis, the rim's first and last points carried down halfway with it)
R0 = [(a + b) / 2 for a, b in zip(e["root"][0], e["root"][1])]; down = nrm(sub(R0, E[ti][:3]))
e["root"] = [r4(add(p, down, 0.045)) for p in e["root"]]
E[0] = r4(add(E[0][:3], down, 0.022)) + list(E[0][3:]); E[-1] = r4(add(E[-1][:3], down, 0.022)) + list(E[-1][3:])
e.update({"cup": 0.9, "rim": 0.004, "rimColor": "@tip", "rimAt": 0.5, "tip": "@tip", "tipAt": 0.78, "inner": "@earIn", "innerRim": 0.004, "fair": 0.01})
put("mammals/kangaroo", e)
print("ears: zebra, giraffe (turned %d deg, droop %d), kangaroo" % (best, round(math.degrees(dr))))
from shp import note
note("mammals/zebra", "(2026-11-08, ears.py)", "The ears: the back striped (the coat's bands in a frame up the ear, `patFace` back), a dark edge band (`rim`) and dark tip, the hollow plain white; no ball at the root, FAIRED into the head (`fair`).")
note("mammals/giraffe", "(2026-11-08, ears.py)", "The ears: fuller cupped leaves, the hollow turned forward and out, drooping a little, thicker at the root; pale inside, the far edge dark (`rim`, `rimAt`); FAIRED into the head.")
note("mammals/kangaroo", "(2026-11-08, ears.py)", "The ears: tall cones of skin with ROUNDED tips, cupped deep toward the front, the far edge dark (`rim`, `rimAt`); the ball at the root gone, the root FAIRED into the head.")
