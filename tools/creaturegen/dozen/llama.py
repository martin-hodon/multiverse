# THE LLAMA (2026-11-09): the camel at .68 (1.15 m at the shoulder), its hump and the hump's fall gone, the back lying
# level; the neck re-set long and nearly upright -- the camel's five neck lobes laid along a line from the shoulder to a
# head carried 1.8 m up, the head's shapes and the rig's neck/head/muzzle/eyes/ears moved with it -- upright banana ears,
# a short woolly coat (hair over the body's shapes, the belly and legs barer), a short tail carried up; white as the
# base, coats brown, black, pied (pinto patches gated on `pied`), fawn. A mount. Written whole by this script.
import sys, os, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import *

f = 0.68
d = load("mammals/camel"); scale_def(d, f)
d["name"] = "llama"; d["graze"] = 0.9; d["rest"] = 0.8
d["mount"] = {"h": 1.9, "speed": 1.4}
d["params"] = {"pied": False, "plain": True}
d["_about"] = ("THE LLAMA (2026-11-09, tools/creaturegen/dozen/llama.py): the camel at .68, no hump, the neck long and upright with the "
               "head carried 1.8 m up, banana ears, a woolly coat, a short tail; white base, coats brown, black, pied (pinto on `pied`), fawn. Written whole by its script.")

# ---- no hump: the back lies level from the withers to the rump
drop(d, "hump", "humpFall")
d["extras"] = [e for e in d["extras"] if e["id"] != "hump"]
add(d, {"id": "back", "type": "ell", "c": [-0.05, 1.03, 0], "r": [0.36, 0.09, 0.17], "k": 0.1, "color": "@body", "pat": "agouti"}, after="barrel")
over(d, "rump", c=[-0.38, 1.0, 0], rot=[0, 0, -10])
over(d, "dock", c=[-0.6, 1.03, 0])

# ---- the neck: from the shoulder (0.42, 1.0) to the head at (0.62, 1.72), nearly upright
A, B = [0.42, 1.0], [0.60, 1.68]
ang = math.degrees(math.atan2(B[1] - A[1], B[0] - A[0]))
for i, (t, r) in enumerate([(0.08, [0.17, 0.15, 0.13]), (0.28, [0.16, 0.125, 0.11]), (0.48, [0.16, 0.11, 0.1]), (0.68, [0.15, 0.1, 0.09]), (0.88, [0.14, 0.095, 0.085])]):
    over(d, f"neck{i}", c=[round(A[0] + (B[0] - A[0]) * t, 4), round(A[1] + (B[1] - A[1]) * t, 4), 0.0], r=r, rot=[0, 0, round(ang, 2)])
over(d, "neckBase", c=[0.4, 1.0, 0], r=[0.18, 0.2, 0.15], rot=[0, 0, -10])
# the head: the camel's (cranium at .68 of (1.563, 2.369)) carried to (0.66, 1.76), level
old = shape(d, "cranium")["c"]; new = [0.66, 1.76, 0.0]
dx, dy = new[0] - old[0], new[1] - old[1]
for i in ("cranium", "brow", "face", "jaw", "lipU", "lipL", "nostril", "ear"): move(d, i, dx, dy, 0)
e = d["sculpt"]["eyes"]; e["at"] = [round(e["at"][0] + dx, 4), round(e["at"][1] + dy, 4), e["at"][2]]; e["from"] = [round(e["from"][0] + dx, 4), round(e["from"][1] + dy, 4), 0]
# the rig follows: neck pill, head, muzzle, eyes, ears, the neck2 extra
d["neck"] = [0.44, 1.02, 0, 0.6, 1.66, 0, 0.11, 0.09]
d["head"] = [round(d["head"][0] * 0 + new[0], 3), round(new[1], 3), 0, round(d["head"][3], 3)]
for k in ("muzzle", "eyes", "ears"):
    v = d[k]; d[k] = [round(v[0] + dx, 4), round(v[1] + dy, 4), v[2], round(v[3] + dx, 4), round(v[4] + dy, 4), v[5]] + [round(x, 4) for x in v[6:]] if k != "eyes" else [round(v[0] + dx, 4), round(v[1] + dy, 4), v[2], v[3]]
for ex in d["extras"]:
    if ex["id"] == "neck2": ex["from"] = [0.5, 1.3, 0]; ex["to"] = [0.6, 1.62, 0]; ex["r1"] = 0.1; ex["r2"] = 0.085
# ---- the ears: upright bananas as a leaf blade turned 45 degrees so they read from the side and the front alike
ear = shape(d, "ear")
bl = fin_blade([0.636, 1.815, 0.052], [0.7, 0.0, 0.7], [-0.12, 0.95, 0.22], L=0.16, W=0.06, tipness=0.65)
ear.update(bl); ear["thick"] = 0.007; ear["cup"] = 0.4; ear["inner"] = "@earIn"; ear["innerRim"] = 0.004
ear["face"] = [0.6, 0.3, 0.5]; ear["fair"] = {"r": 0.012, "sink": 3}
d["ears"] = [0.636, 1.815, 0.052, 0.62, 1.96, 0.085, 0.028, 0.01]
# ---- the wool: hair over the body and neck, the lobes a little lumpy
WOOL = ("chest", "barrel", "back", "belly", "rump", "haunch", "neckBase", "neck0", "neck1", "neck2", "neck3", "neck4", "thigh", "arm", "scapula", "dock")
for i in WOOL:
    s = shape(d, i); s["hair"] = 0.7; s["pat"] = [{"when": "pied", "v": "pinto"}, {"when": "plain", "v": "agouti"}]
for i in ("barrel", "chest", "rump", "neck1", "neck2", "neck3"): shape(d, i)["lumps"] = {"amp": 0.012, "size": 0.06}
drop(d, "keel", "pad")   # (no chest pad: a camel's callus)
# a deeper, woollier trunk; the camel's hanging lower lip drawn in
grow(d, "barrel", 1.0, 1.28, 1.12); grow(d, "chest", 1.0, 1.18, 1.05); move(d, "belly", 0, -0.04); grow(d, "belly", 1.0, 1.3, 1.1)
grow(d, "rump", 1.0, 1.15, 1.05); grow(d, "haunch", 1.0, 1.1, 1.0)
# deeper still, the legs a touch stouter: a llama's legs are about half its height, not a camel's stilts
grow(d, "barrel", 1.0, 1.1, 1.0); move(d, "barrel", 0, -0.02); move(d, "belly", 0, -0.03)
d["legs"]["radii"] = [round(r * 1.18, 4) for r in d["legs"]["radii"]]
over(d, "lipL", r=[0.045, 0.025, 0.03]); move(d, "lipL", -0.01, 0.02)
for i in ("cranium", "brow", "face", "jaw", "lipU", "lipL", "forearm", "gaskin", "ham", "cannon", "hcannon"): shape(d, i)["pat"] = [{"when": "pied", "v": "pinto"}, {"when": "plain", "v": "agouti"}]
# ---- the tail: short, carried up
drop(d, "tailStem", "tailTuft")
over(d, "tailDock", a=[-0.62, 1.03, 0], b=[-0.68, 1.06, 0], ra=0.035, rb=0.028)
add(d, {"id": "tailBrush", "type": "ell", "bone": "tail", "c": [-0.7, 1.07, 0], "r": [0.045, 0.075, 0.04], "rot": [0, 0, 55], "k": 0.025, "color": "@tuft", "hair": 0.9})
d["tail"] = {"c": [-0.62, 0.98], "R": 0.12, "a0": 0.9, "a1": 1.7, "r1": 0.03, "r2": 0.02, "n": 3, "tuft": 0.0, "sway": 12, "speed": 0.7}
# ---- colours
recolor(d, body="#e9e3d8", muzzle="#cfc6b8", ear="#ddd5c8", leg="#e2dbd0", foot="#6a5a48", tail="#e9e3d8", eye="#2a1a10", pad="#a0907c", nose="#3a3028", nail="#4a3e30", tuft="#e2dbd0", earIn="#d8c0b4")
d["coats"] = [
  {"name": "white"}, {"name": "white"},
  {"name": "brown", "body": "#7a5636", "muzzle": "#8a6a4c", "ear": "#6e4c30", "leg": "#6e4c30", "tail": "#7a5636", "tuft": "#6e4c30", "pad": "#5a4030", "foot": "#4a3626", "earIn": "#b89080"},
  {"name": "black", "body": "#2c2826", "muzzle": "#3a3634", "ear": "#262220", "leg": "#262220", "tail": "#2c2826", "tuft": "#262220", "pad": "#2a2624", "foot": "#1e1a18", "earIn": "#5a4e4a"},
  {"name": "pied", "params": {"pied": True, "plain": False}},
  {"name": "fawn", "body": "#c8a67c", "muzzle": "#b89468", "ear": "#b89468", "leg": "#bc9c72", "tail": "#c8a67c", "tuft": "#b08a5e", "pad": "#8a6e50", "foot": "#6a5440", "earIn": "#d8b8a4"},
]
save("mammals/llama", d)
index_add("creatures/mammals/llama", "Mammals")
if "--shot" in sys.argv: render("creatures/mammals/llama", "llama")
