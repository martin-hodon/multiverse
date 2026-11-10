# THE EURASIAN OTTER (2026-11-09, dozen/otter.py): the least weasel's rig and sculpt at 3.2 (64 cm nose to rump), the
# trunk thickened, a thick tapering tail of 40 cm on a longer tail arc, a broad flat head with a wide muzzle, long
# whiskers and small ears, short legs on broad webbed feet; dark brown above, cream throat and belly (the weasel's own
# two-tone coat), a black nose. No bounding (the weasel's hop and sentinel pose dropped; a small flex of the back).
import sys, os, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import *

S = 3.2
d = load("mammals/weasel")
scale_def(d, S)
d["name"] = "otter"; d["shy"] = 6; d["graze"] = 0.2; d["headTurn"] = 20
d.pop("hop", None); d.pop("upright", None); d["flex"] = 8
# the trunk: fatter, rounder
for i in ("rump", "loin", "waist", "chest"): grow(d, i, 1.0, 1.42, 1.5)
for k in ("rear", "front"): d[k][4] *= 1.42; d[k][5] *= 1.5
for i in ("arm", "forearm", "thigh", "shank"): grow(d, i, 1.35)
d["legs"]["radii"] = [v * 1.3 for v in d["legs"]["radii"]]
over(d, "neck", pts=[[p[0], p[1], p[2], p[3] * 1.25] for p in shape(d, "neck")["pts"]])
d["neck"][6] *= 1.25; d["neck"][7] *= 1.25
# the head: broad and flat, the muzzle wide
grow(d, "cranium", 1.12, 0.92, 1.4); grow(d, "cheek", 1.3, 1.1, 1.3); move(d, "cheek", 0, 0, 0.004)
m = shape(d, "muzzle"); over(d, "muzzle", ra=m["ra"] * 1.5, rb=m["rb"] * 1.8, b=[m["b"][0] - 0.02, m["b"][1], 0])
move(d, "nose", -0.02, 0, 0); move(d, "whiskers", -0.015, 0, 0.004); d["nose"][0] -= 0.02; d["muzzle"][3] -= 0.02
grow(d, "jaw", 1.2, 1.2, 1.5); grow(d, "nose", 1.4, 1.3, 1.5)
d["head"][3] *= 1.15; d["muzzle"][6] *= 1.4; d["muzzle"][7] *= 1.6; d["nose"][3] *= 1.4
w = shape(d, "whiskers"); w["len"] = [v * 1.5 for v in w["len"]]; w["rows"] = 4; w["per"] = 4; w["r"] *= 1.3
# the ears small (the weasel's scaled are already small: a little smaller), set a touch lower and further back
grow(d, "ear", 0.85)
# the feet: broad, flat, webbed
grow(d, "paw", 1.35, 0.9, 1.8); grow(d, "foot", 1.3, 0.9, 1.8)
d["legs"]["foot"][0] *= 1.3; d["legs"]["foot"][2] *= 1.7
# THE TAIL: an arc of five links 41 cm long, back and a little down; the one tube along it, thick at the root
a0, span, Rr = 1.3954, 0.55, 0.75
start = [-0.33, 0.15]
c = [start[0] - Rr * math.cos(a0), start[1] - Rr * math.sin(a0)]
d["tail"] = {"c": c, "R": Rr, "a0": a0, "a1": a0 + span, "r1": 0.045, "r2": 0.012, "n": 5, "sway": 12, "speed": 0.5}
pts = []
for i in range(9):
    t = i / 8; a = a0 + span * t
    r = 0.048 * (1 - t) ** 0.9 + 0.011 * t
    pts.append([round(c[0] + Rr * math.cos(a) + (0.02 if i == 0 else 0), 4), round(c[1] + Rr * math.sin(a), 4), 0, round(r, 4)])
over(d, "tail", pts=pts, k=0.02, kc=0.01)
# the coat: the weasel's shader pattern is metric for the weasel's size -- gone; the cream underside painted instead
for sh in shapes(d): sh.pop("pat", None)
d.pop("pat", None); d.pop("patOn", None)
add(d, {"id": "bellyP", "type": "ell", "op": "paint", "c": [-0.06, 0.082, 0], "r": [0.36, 0.045, 0.062], "kc": 0.01, "color": "@belly"})
add(d, {"id": "throatP", "type": "ell", "op": "paint", "bone": "neck", "c": [0.2, 0.118, 0], "r": [0.1, 0.035, 0.05], "kc": 0.008, "color": "@belly"})
add(d, {"id": "chinP", "type": "ell", "op": "paint", "bone": "head", "c": [0.295, 0.128, 0], "r": [0.055, 0.02, 0.034], "kc": 0.006, "color": "@belly"})
recolor(d, body="#4a3626", muzzle="#4a3626", ear="#3e2c1e", leg="#3f2d20", tail="#3f2d20", belly="#d9ccb4", paw="#3a2a1e", nose="#141010", whisker="#e8e0d4", whiskerW="#e8e0d4")
d["sculpt"]["mesh"]["tris"] = [8000, 2600]
d["_about"] = "THE EURASIAN OTTER (2026-11-09, tools/creaturegen/dozen/otter.py): the least weasel's rig and sculpt at 3.2 -- 64 cm nose to rump, a 41 cm thick tapering tail on an arc of five links, the trunk thickened, a broad flat head with a wide muzzle and long pale whiskers, small ears, broad webbed feet; dark brown above and cream below (the weasel's two-tone coat), black nose; no bounding. Written whole by its script."
save("mammals/otter", d)
index_add("creatures/mammals/otter", "Mammals")
if "--shot" in sys.argv: render("creatures/mammals/otter", "otter", views=("side", "q", "rear", "head"))
