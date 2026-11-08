import sys, json, copy; sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import *
# The unicorn stands on the horse's frame at s = .95: the horse's own shapes (mammals/horse.json, as they stand today)
# scaled to it, then made a unicorn -- finer (an Arabian's dry legs, a smaller muzzle, the face a little dished),
# white, its mane long and flowing to one side, a goat's beard, feathered fetlocks, cloven hooves and the spiral horn
S0 = .95
GEO = {"c", "r", "a", "b", "ra", "rb", "k", "kc", "pts", "at", "from"}
def scl(v, f):
    if isinstance(v, list): return [scl(x, f) for x in v]
    if isinstance(v, (int, float)): return v * f
    return v
horse = json.load(open(R + "mammals/horse.json"))
src = horse["sculpt"]
sh = []
for p in src["shape"]:
    q = {k: (scl(v, S0) if k in GEO else v) for k, v in p.items()}
    if q["id"].startswith("mane") and q["id"][4:].isdigit(): continue      # (the mane: written below, longer)
    if q["id"].startswith("tail"): continue                                  # (the tail: written below, long and flowing)
    sh.append(q)
by = {p["id"]: p for p in sh}
# ---- finer: the cannons and pasterns slimmer, the muzzle and jaw smaller, the face dished (a hollow below the eyes)
for pid in ("cannon", "tendon", "pastern", "hcannon", "htendon", "hpastern"):
    by[pid]["ra"] *= .88; by[pid]["rb"] *= .88
for pid in ("muzzle", "chin", "underjaw"):
    p = by[pid]
    if "r" in p: p["r"] = [x * .9 for x in p["r"]]
    else: p["ra"] *= .9; p["rb"] *= .9
for pid in ("neck", "crest", "neckBase"): by[pid]["r"] = [by[pid]["r"][0], by[pid]["r"][1] * .94, by[pid]["r"][2] * .92]
f0, f1 = by["face"]["a"], by["face"]["b"]
dish = lerp(f0, f1, .42)
sh.append({"id": "dish", "type": "ell", "bone": "head", "c": add(dish, [.777, .629, 0], .095), "r": [.07, .03, .05], "rot": [0, 0, -51], "op": "sub", "k": .03, "color": "@body"})
# ---- the mane: long locks falling to the off side from the crest, longest mid-neck; a second shorter row on the near side
rid = by["maneRidge"]["pts"]
for q in by["maneRidge"]["pts"]: q[3] = max(q[3], .045)
def ridge(t):   # along the crest's tube
    n = len(rid) - 1; i = min(int(t * n), n - 1); u = t * n - i
    return [rid[i][j] + (rid[i + 1][j] - rid[i][j]) * u for j in range(4)]
N = 10
for i in range(N):
    t = .05 + .9 * i / (N - 1); p = ridge(t)
    L = (.17 + .11 * math.sin(math.pi * min(1, t * 1.2))) * S0
    sh.append({"id": f"mane{i}", "type": "ell", "bone": "neck", "c": [p[0] - .01, p[1] - L * .45, -.075 * S0], "r": [.06 * S0, L * .55, .036],
               "rot": [16, 0, -12 + 8 * (i % 2)], "k": .022, "kc": .006, "color": "@mane", "hair": .9})
    sh.append({"id": f"maneT{i}", "type": "ell", "bone": "neck", "c": [p[0] - .05, p[1] - L * 1.0, -.1 * S0], "r": [.045 * S0, L * .42, .033],
               "rot": [24, 0, -22 + 10 * (i % 2)], "k": .022, "kc": .006, "color": "@mane", "hair": .9})
# (the buttock the horse's own, scaled: no longer enlarged and pushed back -- it overhung the hock)
cr = by["croup"]; cr["c"] = add(cr["c"], [0, -.025, 0]); cr["rot"] = [0, 0, 9]
by["belly"]["rot"] = [0, 0, -10]
e = by["ear"]; ec, er = e["c"], e["r"]
sh[sh.index(e)] = {"id": "ear", "type": "tube", "bone": e["bone"], "pts": [add(ec, [0, -.06, 0]) + [.04], add(ec, [.004, .01, .002]) + [.033], add(ec, [.012, .06, -.008]) + [.016], add(ec, [.016, .085, -.018]) + [.004]],
                   "k": .02, "kc": .006, "color": "@ear", "mirror": True}
ei = by["earIn"]; ei["r"] = [.01, ei["r"][1] * .9, .02]
fl = by["forelock"]; fl["r"] = [fl["r"][0] * 1.4, fl["r"][1] * 1.2, fl["r"][2] * 1.1]; fl["c"] = add(fl["c"], [.025, -.03, 0])
# ---- the beard: a goat's tuft under the chin
ch = by["chin"]["c"]
sh.append({"id": "beard", "type": "tube", "bone": "head", "pts": [add(ch, [-.05, -.02, 0]) + [.026], add(ch, [-.06, -.07, 0]) + [.022], add(ch, [-.075, -.115, 0]) + [.014], add(ch, [-.08, -.145, 0]) + [.006]],
           "k": .02, "kc": .006, "color": "@beard", "hair": .8})
# ---- feathered fetlocks, cloven hooves
for leg, fet, hoof, bone in (("F", "fetlock", "hoof", "legFLl"), ("H", "hfetlock", "hhoof", "legHLl")):
    c = by[fet]["c"]
    sh.append({"id": f"feather{leg}", "type": "ell", "bone": bone, "c": add(c, [-.045, -.04, 0]), "r": [.04, .065, .036], "rot": [0, 0, -30], "k": .015, "kc": .005, "color": "@feather", "hair": .8, "mirror": True})
    h = by[hoof]; a, b = h["a"], h["b"]
    sh.append({"id": f"cleft{leg}", "type": "ell", "bone": h["bone"], "c": [b[0] + h["rb"] * .9, (a[1] + b[1]) / 2 - .01, b[2]], "r": [.03, .05, .006], "op": "sub", "k": .004, "color": "@foot", "mirror": True})
# ---- the horn: a long taper from the forehead between the eyes, wound with a spiral ridge (three and a half turns)
base = [1.4155 + .03, 1.9665 - .037, 0]; ang = math.radians(46); L = .475
d = [math.cos(ang), math.sin(ang), 0]; n1 = [-math.sin(ang), math.cos(ang), 0]; n2 = [0, 0, 1]
tip = add(base, d, L); r0, r1 = .036, .005
sh.append({"id": "hornRoot", "type": "ell", "bone": "head", "c": add(base, d, -.01), "r": [.045, .022, .045], "rot": [0, 0, 52 - 90], "k": .015, "color": "@body"})
sh.append({"id": "horn", "type": "cone", "bone": "head", "a": base, "b": tip, "ra": r0, "rb": r1, "k": .006, "kc": .004, "color": "@horn", "wet": .35, "pat": "twist", "frame": {"o": base, "u": d, "r": r0}})

for i in range(5):
    t = .14 + .16 * i; c = add(base, d, L * t); rr = r0 + (r1 - r0) * t
    sh.append({"id": f"hornBand{i}", "type": "ell", "bone": "head", "c": c, "r": [.011, rr + .003, rr + .003], "rot": [0, -33.85, 40.69], "k": .004, "kc": .003, "color": "@hornRidge", "wet": .35})
# ---- the tail: a long fall of hair from the dock to below the hocks -- a fan of strands on the tail bone, each a tube
# down the bone's arc and on past its end, spreading as it falls, the outer ones shorter
TC, TR = [-2.18 * S0, 1.45 * S0], 1.2 * S0
def arcP(t):
    if t <= 1: a = -.62 * t; return [TC[0] + TR * math.cos(a), TC[1] + TR * math.sin(a)]
    e = arcP(1); return [e[0] - .3 * (t - 1) * .6, e[1] - .95 * (t - 1) * .6]
sh.append({"id": "tailRoot", "type": "cone", "bone": "tail", "a": [-.93, 1.38, 0], "b": arcP(.18) + [0], "ra": .055, "rb": .05, "k": .03, "kc": .01, "color": "@mane", "hair": .8})
STR = [(0, 1.5, .034), (.045, 1.42, .03), (-.045, 1.4, .03), (.085, 1.3, .026), (-.085, 1.28, .026), (.02, 1.46, .028), (-.02, 1.45, .028), (.11, 1.15, .022), (-.11, 1.12, .022), (0, 1.3, .03)]
for j, (zs, tend, rr) in enumerate(STR):
    back = -.025 * (j % 3)
    pts = []
    for k in range(6):
        t = .1 + (tend - .1) * k / 5; p = arcP(t); f = (t - .1) / (tend - .1)
        pts.append([p[0] + back * f + .02 * math.sin(3 * t + j), p[1], zs * f ** .7 + .012 * math.sin(4 * t + j * 1.7), rr * (1 - .7 * f ** 2)])
    sh.append({"id": f"tail{j}", "type": "tube", "bone": "tail", "pts": pts, "k": .02, "kc": .006, "color": "@mane", "hair": .9})

eyes = {k: (scl(v, S0) if k in GEO else v) for k, v in src["eyes"].items()}
eyes["lid"] = "@lid"
d = json.load(open(R + "monsters/unicorn.json"))
out = {
    "name": "unicorn",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): the horse's frame at .95 drawn by the horse's own shapes (mammals/horse.json) scaled to it and refined to an Arabian -- dry fine legs, a smaller muzzle, the face a little dished; white; the mane long and falling to the off side with a shorter row on the near side and a long forelock; a goat's beard under the chin, feathered fetlocks, cloven hooves; the spiral horn from the forehead between the eyes, half a metre long, wound with a ridge three and a half times round",
    "use": d["use"],
    "params": {"s": S0, "mane": False, "head": True},
    "colors": {"body": "#eceae2", "muzzle": "#d6cdc8", "ear": "#dcd8cc", "earIn": "#b8a8a8", "nose": "#7c7078", "lid": "#9a8e90", "leg": "#e2dfd4", "foot": "#b8b8c0",
               "tail": "#d0daee", "mane": "#d0daee", "beard": "#e2e4ec", "feather": "#f2f0ea", "back": "#ecebe4", "flank": "#e8e6de", "sock": "#eceae2", "eye": "#3a5a8e", "horn": "#e2cf8c", "hornRidge": "#b8964e"},
    "mount": d["mount"],
    "extras": [{"id": "horn", "parent": "head", "from": [round(base[0] + .0166, 4), round(base[1] + .0204, 4), 0], "to": [round(tip[0] + .0166, 4), round(tip[1] + .0204, 4), 0],
                "r1": r0, "r2": r1, "color": "#e2cf8c", "_about": "the horn's bone (and its shape where the body is drawn as parts, ?sculpt=0); the overlay draws it"}],
    "monster": True,
    "print": d["print"],
    "sculpt": {"keep": [], "shade": {"back": 1.02, "belly": "#cfcad8", "k": .16, "low": 1.0, "on": "@body"}, "mesh": {"tris": [7000, 2200]}, "shape": sh, "eyes": eyes},
}
dump("monsters/unicorn.json", out)
print(len(sh), "shapes")
