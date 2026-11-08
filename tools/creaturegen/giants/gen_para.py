import math, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import *

P = "dinosaurs/parasaurolophus"
d = load(P)
d["_about"] = ("PARASAUROLOPHUS WALKERI (sculpt overlay, 2026-11-05, after Hartman's skeletal): 8.5 m, the hips 2.2 m up -- "
               "a hadrosaur walking on all fours or on its hind legs, the back level and high over the hips (tall neural "
               "spines), a deep, flattened tail held out level; a curved neck; a long downturned duck-billed face and the "
               "metre-long tubular crest sweeping back from the snout over the neck; slender hoofed forelimbs, the hind legs "
               "digitigrade on three hoofed toes. Countershaded olive, pale below, the crest rust.")
d["rear"] = [-1.0, 2.4, 0, 1.2, 0.6, 0.7]
d["front"] = [0.5, 1.95, 0, 1.0, 0.6, 0.68]
d["neck"] = [1.2, 2.1, 0, 2.2, 3.2, 0, 0.4, 0.3]
d["head"] = [2.45, 3.3, 0, 0.28]
d["eyes"] = [2.62, 3.38, 0.17, 0.04]
d["legs"] = {"front": [0.85, 1.15, 0.45, 0.53], "hind": [-1.3, 2.2, 0.46, 1.05], "radii": [0.22, 0.17, 0.14],
             "foot": [0.26, 0.09, 0.24], "kneeH": 1, "kneeF": -1}
TAIL = {"c": [-1.8, -17.4], "R": 20, "a0": 1.5708, "a1": 1.7773}
d["tail"] = {**TAIL, "r1": 0.5, "r2": 0.06, "n": 6, "sway": 8, "speed": 0.35}
d["extras"] = [x for x in d["extras"] if x.get("id") not in ("bill", "jaw", "crest")]
d.pop("pat", None); d.pop("patOn", None)
d["c"].update({"back": "#55573c", "body": "#6c6e4e", "belly": "#bdb38e", "leg": "#5c5e43", "foot": "#3e3e30",
               "hoof": "#2e2c24", "head": "#71714f", "bill": "#4a4032", "crest": "#a9613a", "crestTop": "#7e4428",
               "eye": "#2a2014", "lid": "#3a4030", "mouth": "#3a2e26"})
sc = {"pat": "scales", "frame": {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.5}}
S = Shapes()
def ty(x):
    c, R = TAIL["c"], TAIL["R"]; return c[1] + math.sqrt(R * R - (x - c[0]) ** 2)
# ---- the body: level, high over the hips
S.ell("torso", [-0.3, 2.22, 0], [1.4, 0.6, 0.58], "@body", k=0.16, rot=[0, 0, -9], **sc)
S.ell("hips", [-1.05, 2.55, 0], [0.8, 0.45, 0.48], "@back", k=0.16, kc=0.12, **sc)
S.ell("chest", [0.6, 1.78, 0], [0.7, 0.58, 0.5], "@body", k=0.14, **sc)
S.ell("spine", [-0.5, 2.74, 0], [1.4, 0.22, 0.28], "@back", k=0.14, kc=0.12, rot=[0, 0, -10], **sc)
S.ell("sacral", [-1.0, 2.95, 0], [0.95, 0.2, 0.13], "@back", k=0.14, kc=0.1, **sc)
S.ell("belly", [-0.1, 1.7, 0], [1.1, 0.28, 0.46], "@belly", k=0.12, kc=0.1, rot=[0, 0, -9], **sc)
# ---- the tail: deep, flattened side to side, held out level
txs = [-1.6, -2.6, -3.6, -4.7, -5.9]; trs = [0.48, 0.36, 0.25, 0.14, 0.05]
S.tube("tail", [[x, ty(x), 0, r] for x, r in zip(txs, trs)], "@body", bone="tail", k=0.12, **sc)
S.ell("tailDeep", [-2.5, ty(-2.5) - 0.02, 0], [1.3, 0.55, 0.26], "@body", bone="tail", k=0.14, **sc)
S.tube("tailTop", [[x, ty(x) + r * 0.6, 0, r * 0.45] for x, r in zip(txs[:4], trs[:4])], "@back", bone="tail", k=0.12, kc=0.1, **sc)
S.tube("tailBelly", [[x, ty(x) - r * 0.6, 0, r * 0.5] for x, r in zip(txs[:4], trs[:4])], "@belly", bone="tail", k=0.12, kc=0.1, **sc)
# ---- the neck: curving up to the head
S.tube("neck", [[0.95, 2.05, 0, 0.46], [1.45, 2.36, 0, 0.34], [1.85, 2.84, 0, 0.28], [2.12, 3.2, 0, 0.25], [2.38, 3.28, 0, 0.24]], "@body", bone="neck", k=0.14, **sc)
S.tube("throat", [[1.0, 1.86, 0, 0.32], [1.5, 2.16, 0, 0.23], [1.95, 2.7, 0, 0.17], [2.2, 3.05, 0, 0.15]], "@belly", bone="neck", k=0.12, kc=0.1, **sc)
# ---- the head: the long downturned face, the duck-bill, the crest from the snout back over the neck
S.ell("skull", [2.5, 3.02, 0], [0.3, 0.2, 0.18], "@head", bone="head", k=0.08, **sc)
S.ell("face", [2.85, 2.9, 0], [0.34, 0.13, 0.15], "@head", bone="head", k=0.08, rot=[0, 0, -18], **sc)
S.ell("bill", [3.12, 2.77, 0], [0.1, 0.065, 0.15], "@bill", bone="head", k=0.04, kc=0.02)
S.ell("jaw", [2.78, 2.79, 0], [0.3, 0.09, 0.14], "@belly", bone="head", k=0.06, kc=0.03, rot=[0, 0, -12], **sc)
S.ell("cheek", [2.56, 2.92, 0.13], [0.14, 0.1, 0.07], "@head", bone="head", k=0.05, mirror=True, **sc)
S.ell("nostril", [3.08, 2.84, 0.09], [0.05, 0.02, 0.025], "@bill", bone="head", k=0.008, mirror=True)
S.tube("crest", [[2.82, 2.98, 0, 0.09], [2.5, 3.2, 0, 0.1], [2.1, 3.36, 0, 0.09], [1.75, 3.43, 0, 0.075], [1.55, 3.42, 0, 0.06]],
       "@crest", bone="head", k=0.05, kc=0.02, **sc)
S.tube("crestTop", [[2.45, 3.27, 0, 0.05], [2.05, 3.42, 0, 0.05], [1.65, 3.47, 0, 0.035]], "@crestTop", bone="head", k=0.03, kc=0.02)
# ---- forelimbs: slender, the hands hoof-like
S.ell("scapula", [0.75, 1.58, 0.4], [0.24, 0.42, 0.15], "@body", bone="legFLu", k=0.1, rot=[0, 0, 30], mirror=True, **sc)
S.cone("humerus", [0.85, 1.38, 0.45], [0.74, 0.76, 0.47], 0.14, 0.08, "@leg", bone="legFLu", k=0.07, mirror=True, **sc)
S.cone("forearm", [0.74, 0.76, 0.47], [0.88, 0.12, 0.46], 0.07, 0.055, "@leg", bone="legFLl", k=0.04, mirror=True, **sc)
S.ell("hand", [0.92, 0.06, 0.46], [0.08, 0.06, 0.07], "@hoof", bone="footFL", k=0.03, mirror=True)
# ---- hind legs: a heavy thigh, the ankle high, three hoofed toes
x, z = -1.3, 0.46
S.ell("thigh", [x + 0.05, 1.72, z - 0.03], [0.46, 0.62, 0.27], "@body", bone="legHLu", k=0.22, rot=[0, 0, 10], mirror=True, **sc)
S.ell("knee", [x + 0.05, 1.18, z], [0.18, 0.16, 0.17], "@leg", bone="legHLu", k=0.07, mirror=True, **sc)
S.cone("shin", [x, 1.15, z], [x - 0.08, 0.5, z], 0.17, 0.1, "@leg", bone="legHLl", k=0.06, mirror=True, **sc)
S.ell("calf", [x - 0.1, 0.92, z], [0.14, 0.24, 0.13], "@leg", bone="legHLl", k=0.06, mirror=True, **sc)
S.cone("metatarsus", [x - 0.08, 0.5, z], [x + 0.14, 0.13, z], 0.1, 0.085, "@leg", bone="legHLl", k=0.05, mirror=True, **sc)
for j, (ang, ln) in enumerate([(0, 0.36), (24, 0.28), (-24, 0.28)]):
    a = math.radians(ang); ux, uz = math.cos(a), math.sin(a)
    b = [x + 0.15, 0.1, z]
    p = lambda t, y, r: [b[0] + ux * t, y, b[2] + uz * t, r]
    S.tube(f"toe{j}", [p(0, 0.1, 0.08), p(ln, 0.05, 0.05)], "@foot", bone="footHL", k=0.04, mirror=True)
    e = p(ln, 0.05, 0)
    S.ell(f"hoof{j}", [e[0] + ux * 0.04, 0.04, e[2] + uz * 0.04], [0.07, 0.04, 0.06], "@hoof", bone="footHL", k=0.01, mirror=True)
FF = 1.15 / 1.38
for p in S:   # (the forelimb shorter: about half the hind leg)
    if p.get("bone") in ("legFLu", "legFLl") and not p["id"].startswith("scapula"):
        for key in ("c", "a", "b"):
            if key in p: p[key][1] *= FF
        if isinstance(p.get("r"), list): p["r"][1] *= FF
for p in S:   # (the head carried higher on the S of the neck)
    if p.get("bone") == "head":
        for key in ("c", "a", "b"):
            if key in p: p[key][1] += 0.3
        for q in p.get("pts", []): q[1] += 0.3
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; each shape rides the bone it names; `mirror` makes the right one from the left",
    "keep": [],
    "mesh": {"cell": 0.055, "tris": [9000, 2800]},
    "shape": [fix_order(p) for p in S],
    "eyes": {"at": [2.62, 3.38, 0.16], "from": [2.5, 3.34, 0], "r": 0.04, "iris": "@eye", "pupil": "round", "lid": "@lid"},
}
d["sculpt"]["shade"] = {"back": 0.8, "belly": 1.12, "low": 0.96, "on": "@body"}
save(P, d)
print(len(S), "shapes")
