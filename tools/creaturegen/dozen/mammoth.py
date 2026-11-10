# THE WOOLLY MAMMOTH (2026-11-09): the elephant at .95, then a mammoth's build -- a high domed head, a steep shoulder
# hump sloping down the back to lower hindquarters, small ears, long tusks curving out, down, forward and back up in a
# spiral, a thick shaggy coat (coarse hair on every body shape, a skirt of lumpy locks hanging under the belly and off
# the flanks and chest, chaps on the upper legs), a short tail with a brush. Dark reddish brown, cream tusks. A mount.
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import *

S = 0.95
d = load("mammals/elephant")
scale_def(d, S)
# (what scale_rig leaves: the tail's path and the raw ear parts)
d["tail"]["path"] = [[x * S, y * S] for x, y in d["tail"]["path"]]
for e in d["extras"]:
    if "raw" in e and "size" in e["raw"]:
        z = e["raw"]["size"]
        for k in ("a", "b", "c"): z[k] = [v * S for v in z[k]]
        z["r"] *= S
d["name"] = "mammoth"
d["mount"] = {"h": 3.4, "speed": 1.2}
d["fur"] = True

# ---- the build: the head and everything on it raised, a dome on the skull, the hump over the shoulders, the back sloping
UP = 0.15
for i in ids(d): 
    s = shape(d, i)
    if s.get("bone") in ("head", "trunk", "earL"): move(d, i, dy=UP)
d["head"][1] += UP; d["muzzle"][1] += UP; d["eyes"][1] += UP
d["sculpt"]["eyes"]["at"][1] += UP; d["sculpt"]["eyes"]["from"][1] += UP
for e in d["extras"]:
    if "arc" in e: e["arc"]["c"][1] += UP
    if e.get("id") == "tusk": e["from"][1] += UP; e["to"][1] += UP
add(d, {"id": "dome", "type": "ell", "bone": "head", "c": [1.9 * S, 3.0 * S + UP, 0], "r": [0.42 * S, 0.4 * S, 0.44 * S], "k": 0.14, "color": "@skin"}, after="forehead")
over(d, "forehead", c=[2.2 * S, 2.78 * S + UP, 0], r=[0.34 * S, 0.5 * S, 0.42 * S])
over(d, "temple", c=[1.86 * S, 2.95 * S + UP, 0.3 * S])
# the hump: the withers raised and a second mass over them; the back sloping down to the rump, the rump lower and smaller
over(d, "withers", c=[0.72 * S, 2.95 * S, 0], r=[0.62 * S, 0.5 * S, 0.54 * S])
add(d, {"id": "hump", "type": "ell", "c": [0.78 * S, 3.14 * S, 0], "r": [0.52 * S, 0.36 * S, 0.44 * S], "rot": [0, 0, -10], "k": 0.18, "color": "@back"}, after="withers")
# (the nape: one mass from the dome down into the hump, so the two do not stand as separate bumps with a dip between)
add(d, {"id": "nape", "type": "ell", "c": [1.3 * S, 2.95 * S, 0], "r": [0.5 * S, 0.42 * S, 0.46 * S], "rot": [0, 0, 20], "k": 0.22, "color": "@back"}, after="hump")
over(d, "back", c=[-0.25 * S, 2.5 * S, 0], r=[0.95 * S, 0.34 * S, 0.62 * S], rot=[0, 0, -11])
over(d, "rump", c=[-0.95 * S, 2.05 * S, 0], r=[0.68 * S, 0.5 * S, 0.64 * S], rot=[0, 0, 30])
over(d, "haunch", c=[-1.0 * S, 1.82 * S, 0.42 * S])
over(d, "neck", c=[1.42 * S, 2.6 * S, 0], r=[0.44 * S, 0.66 * S, 0.56 * S])
d["rear"][1] -= 0.08; d["rear"][4] *= 0.92
# ---- small ears: the fin scaled .45 about the middle of its root; the rig's ear triangles the same about their root
ear = shape(d, "ear")
rm = [(ear["root"][0][i] + ear["root"][1][i]) / 2 for i in range(3)]
sh = lambda p: [rm[i] + (p[i] - rm[i]) * 0.45 for i in range(3)] + list(p[3:])
ear["root"] = [sh(p) for p in ear["root"]]; ear["edge"] = [sh(p) for p in ear["edge"]]
ear["thick"] *= 0.6; ear["innerRim"] *= 0.5; ear["fair"]["r"] *= 0.6
for e in d["extras"]:
    if "raw" in e and e["raw"]["id"].startswith("ear"):
        z = e["raw"]["size"]; a = z["a"]
        for k in ("b", "c"): z[k] = [a[i] + (z[k][i] - a[i]) * 0.45 for i in range(3)]
        z["r"] *= 0.6
# ---- the tusks: 3 m, out of the sheath, down and out, forward, then curving back up and in (the spiral), cream
sx, sy, sz = 2.34 * S, 1.99 * S + UP, 0.21 * S
over(d, "tusk", pts=[[sx - 0.1, sy + 0.05, sz - 0.02, 0.125], [sx, sy, sz, 0.12], [sx + 0.42, sy - 0.42, sz + 0.17, 0.108], [sx + 0.92, sy - 0.74, sz + 0.3, 0.092],
                     [sx + 1.48, sy - 0.8, sz + 0.34, 0.075], [sx + 1.98, sy - 0.55, sz + 0.26, 0.056], [sx + 2.3, sy - 0.1, sz + 0.1, 0.036], [sx + 2.4, sy + 0.3, sz - 0.04, 0.012], [sx + 2.38, sy + 0.45, sz - 0.1, 0.0]],
     fair=0.09, tipAt=0.75, tip="#efe8d2", aspect=0.95)
for e in d["extras"]:
    if e.get("id") == "tusk": e["to"] = [sx + 2.38, sy + 0.45, sz - 0.1]; e["r1"] = 0.1
over(d, "sheath", r=[0.2 * S, 0.19 * S, 0.17 * S])
# ---- the coat: coarse hair on the body, head and upper legs; the skirt of locks under belly, flanks and chest
for i in ("chest", "belly", "withers", "hump", "back", "rump", "scapula", "haunch", "neck", "dewlap", "skull", "forehead", "dome", "temple", "cheek", "arm", "thigh", "elbow", "knee", "tailDock", "trunkRoot"):
    over(d, i, pat="coarse", hair=0.12)
over(d, "forearm", hair=0.08, pat="coarse"); over(d, "shank", hair=0.08, pat="coarse")
skirt = [(1.15, 1.55, 0.0, 0.42, 0.34, 0.66), (0.55, 1.3, 0.0, 0.5, 0.3, 0.84), (-0.1, 1.22, 0.0, 0.55, 0.3, 0.86), (-0.7, 1.3, 0.0, 0.5, 0.3, 0.78), (-1.2, 1.5, 0.0, 0.36, 0.3, 0.58)]
for j, (x, y, z, rx, ry, rz) in enumerate(skirt):
    add(d, {"id": f"skirt{j}", "type": "ell", "c": [x * S, y * S, z], "r": [rx * S, ry * S, rz * S], "k": 0.16, "color": "@belly", "pat": "coarse", "hair": 0.14}, after="belly")
# (flank locks were tried as ells standing off the sides: they read as plates from behind -- the skirt and the hair texture carry the coat)
add(d, {"id": "humpLock", "type": "ell", "c": [0.9 * S, 3.3 * S, 0], "r": [0.3 * S, 0.14 * S, 0.3 * S], "k": 0.1, "color": "@back", "pat": "coarse", "hair": 0.14}, after="hump")
add(d, {"id": "chinLock", "type": "ell", "bone": "head", "c": [1.75 * S, 1.75 * S + UP, 0], "r": [0.3 * S, 0.22 * S, 0.3 * S], "k": 0.1, "color": "@skin", "pat": "coarse", "hair": 0.14}, after="dewlap")
# ---- a short tail: the tail bone's shapes compressed toward the dock, the brush kept
T0 = 2.47 * S
for i in ids(d, r"^tail"):
    s = shape(d, i)
    if s.get("bone") == "tail" and "pts" in s: s["pts"] = [[p[0], T0 + (p[1] - T0) * 0.68, p[2], p[3]] for p in s["pts"]]
d["tail"]["path"] = [[x, T0 + (y - T0) * 0.68] for x, y in d["tail"]["path"]]
d["sculpt"]["mesh"]["focus"] = {"head": 4, "tail": 6}
recolor(d, body="#4a2e1c", skin="#4a2e1c", muzzle="#4a2e1c", back="#3b2415", belly="#5a3a24", leg="#3a2416", dust="#33200f", trunk="#4a2e1c", dark="#2a1a10",
        ear="#4a2e1c", earIn="#6a4a38", tail="#3a2416", tuft="#24160c", tusk="#e6dcc4", nail="#8a8070", lid="#2e1e14")
d["_about"] = ("THE WOOLLY MAMMOTH (2026-11-09, tools/creaturegen/dozen/mammoth.py): the elephant at .95, then a mammoth's build -- the head "
               "raised and domed, a steep shoulder hump sloping down the back to a lower rump, small ears (the fin at .45), tusks 3 m long curving out, "
               "down, forward and back up, a thick shaggy coat (coarse hair everywhere, a skirt of locks under the belly and off the flanks and chest), a short "
               "tail with a brush; dark reddish brown, cream tusks. Written whole by its script; nothing patches it after.")
save("mammals/mammoth", d)
index_add("creatures/mammals/mammoth", "Mammals")
if "--shot" in sys.argv: render("creatures/mammals/mammoth", "mammoth", views=tuple(sys.argv[sys.argv.index("--shot") + 1].split(",")) if len(sys.argv) > sys.argv.index("--shot") + 1 else ("side", "front", "q", "rear", "head"))
