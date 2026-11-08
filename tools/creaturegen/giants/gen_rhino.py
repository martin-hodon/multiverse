import math, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import *

P = "mammals/rhinoceros"
d = load(P)
d["_about"] = ("WHITE RHINOCEROS (sculpt overlay, 2026-11-05): a grazer 1.8 m at the shoulder, 3.9 m head and body -- a "
               "nuchal hump before the withers, a deep barrel on short thick legs (fore folding at the wrist, hind at the hock), "
               "three-toed feet; the long head held low to a broad square lip, a long front horn curving back and a short rear "
               "one, tubular ears high on the skull; skin folds behind the shoulder, before the thigh and round the neck.")
d["rear"] = [-0.8, 1.2, 0, 0.9, 0.62, 0.6]
d["front"] = [0.5, 1.28, 0, 0.85, 0.6, 0.6]
d["neck"] = [1.05, 1.4, 0, 1.5, 1.2, 0, 0.42, 0.34]
d["head"] = [1.65, 1.1, 0, 0.32]
d["muzzle"] = [1.8, 1.0, 0, 2.25, 0.7, 0, 0.2, 0.16]
d["ears"] = [1.55, 1.38, 0.14, 1.52, 1.58, 0.2, 0.07, 0.03]
d["eyes"] = [1.88, 1.05, 0.2, 0.022]
HB = -0.08
d["legs"] = {"front": [0.8, 1.05, 0.38, 0.6], "hind": [-0.95 + HB, 1.12, 0.36, 0.68], "radii": [0.2, 0.16, 0.14],
             "foot": [0.16, 0.07, 0.15]}
d["tail"] = {"c": [-1.87, 1.45], "R": 0.35, "a0": 0, "a1": -1.0, "r1": 0.05, "r2": 0.03, "n": 3, "tuft": 0.05,
             "tuftColor": "#3a3530", "sway": 20, "speed": 1.2}
d.pop("pat", None); d.pop("patOn", None)
d["c"].update({"body": "#7c776f", "skin": "#7c776f", "back": "#726c64", "belly": "#867c70", "dust": "#857a6c", "fold": "#67625b", "leg": "#6c665d",
               "foot": "#6c6358", "horn": "#6a6258", "hornTip": "#564e44", "lip": "#6f6a63", "nail": "#857e72",
               "ear": "#77726a", "earIn": "#9a8a80", "lid": "#5a554e", "tuft": "#3a3530"})

S = Shapes()
bark = {"pat": "bark"}
mot = {}
S.ell("barrel", [-0.2, 1.12, 0], [1.25, 0.6, 0.64], "@skin", k=0.16, **mot)
S.ell("saddle", [-0.15, 1.5, 0], [0.75, 0.2, 0.42], "@back", k=0.14, **mot)
S.ell("withers", [0.55, 1.45, 0], [0.45, 0.28, 0.42], "@back", k=0.12, **mot)
S.ell("hump", [0.98, 1.68, 0], [0.36, 0.28, 0.33], "@back", k=0.14, **mot)
S.ell("rump", [-0.95, 1.3, 0], [0.52, 0.48, 0.57], "@back", k=0.14, rot=[0, 0, 12], **mot)
S.ell("belly", [-0.15, 0.68, 0], [0.9, 0.32, 0.58], "@belly", k=0.16, **mot)
S.ell("chest", [0.78, 1.0, 0], [0.4, 0.42, 0.46], "@skin", k=0.12)
S.ell("neck", [1.22, 1.32, 0], [0.38, 0.38, 0.38], "@skin", k=0.12, rot=[0, 0, -25])
S.ell("neckFold", [1.2, 1.3, 0], [0.04, 0.4, 0.4], "@fold", k=0.03, kc=0.015, rot=[0, 0, -10])
S.ell("neckFold2", [1.34, 1.24, 0], [0.035, 0.34, 0.35], "@fold", k=0.03, kc=0.015, rot=[0, 0, -15])
S.ell("shoulderFold", [0.3, 1.1, 0], [0.07, 0.6, 0.68], "@fold", k=0.06, kc=0.04, rot=[0, 0, 8])
S.ell("flankFold", [-0.62, 1.02, 0], [0.07, 0.56, 0.67], "@fold", k=0.06, kc=0.04, rot=[0, 0, -18])
S.ell("scapula", [0.7, 1.2, 0.36], [0.3, 0.42, 0.2], "@skin", bone="legFLu", k=0.1, rot=[0, 0, 15], mirror=True)
# ---- legs
S.cone("arm", [0.8, 1.0, 0.38], [0.8, 0.45, 0.38], 0.23, 0.15, "@leg", bone="legFLu", k=0.08, mirror=True, **bark)
S.ell("elbowFold", [0.72, 0.72, 0.38], [0.18, 0.06, 0.2], "@fold", bone="legFLu", k=0.03, kc=0.015, rot=[0, 0, 20], mirror=True)
S.cone("fore", [0.8, 0.46, 0.38], [0.82, 0.12, 0.38], 0.145, 0.13, "@dust", bone="legFLl", k=0.05, mirror=True, **bark)
S.ell("foot", [0.84, 0.07, 0.38], [0.16, 0.07, 0.15], "@foot", bone="footFL", k=0.04, mirror=True)
S.ell("thigh", [-0.93, 1.0, 0.36], [0.36, 0.46, 0.25], "@skin", bone="legHLu", k=0.1, rot=[0, 0, -10], mirror=True)
S.cone("gaskin", [-0.9, 0.75, 0.36], [-1.0, 0.44, 0.36], 0.19, 0.13, "@leg", bone="legHLu", k=0.06, mirror=True, **bark)
S.cone("cannon", [-1.0, 0.45, 0.36], [-0.95, 0.12, 0.36], 0.13, 0.125, "@dust", bone="legHLl", k=0.04, mirror=True, **bark)
S.ell("hfoot", [-0.92, 0.07, 0.36], [0.16, 0.07, 0.145], "@foot", bone="footHL", k=0.04, mirror=True)
for i, a in enumerate([-40, 0, 40]):
    t = math.radians(a)
    S.ell(f"nail{i}", [0.84 + 0.15 * math.cos(t), 0.045, 0.38 + 0.14 * math.sin(t)], [0.045, 0.04, 0.045], "@nail",
          bone="footFL", k=0.01, kc=0.004, mirror=True)
    S.ell(f"hnail{i}", [-0.92 + 0.15 * math.cos(t), 0.045, 0.36 + 0.135 * math.sin(t)], [0.045, 0.04, 0.045], "@nail",
          bone="footHL", k=0.01, kc=0.004, mirror=True)
# ---- the head, long and low, the square lip of a grazer
S.ell("skull", [1.7, 1.17, 0], [0.33, 0.22, 0.24], "@skin", bone="head", k=0.09, rot=[0, 0, -30])
S.cone("face", [1.78, 1.08, 0], [2.2, 0.76, 0], 0.21, 0.165, "@skin", bone="head", k=0.08)
S.ell("lip", [2.24, 0.67, 0], [0.09, 0.12, 0.24], "@lip", bone="head", k=0.07)
S.ell("jaw", [1.92, 0.82, 0], [0.32, 0.14, 0.19], "@skin", bone="head", k=0.07, rot=[0, 0, -32])
S.ell("cheek", [1.66, 0.98, 0.15], [0.2, 0.16, 0.1], "@skin", bone="head", k=0.07, mirror=True)
S.ell("brow", [1.86, 1.1, 0.15], [0.07, 0.04, 0.05], "@skin", bone="head", k=0.03, mirror=True)
def horn(id, pts, flat=0.72):
    for j, (a, b) in enumerate(zip(pts, pts[1:])):
        m = [(a[q] + b[q]) / 2 for q in range(2)]; L = math.hypot(b[0] - a[0], b[1] - a[1])
        ang = math.degrees(math.atan2(-(b[0] - a[0]), b[1] - a[1]))
        r = (a[2] + b[2]) / 2
        S.ell(f"{id}{j}", [m[0], m[1], 0], [r * flat, L * 0.62 + r * 0.3, r], "@horn" if j < len(pts) - 2 else "@hornTip",
              bone="head", k=0.035, kc=0.008, rot=[0, 0, ang])
S.tube("horn", [[2.1, 0.86, 0, 0.13], [2.17, 1.1, 0, 0.1], [2.19, 1.29, 0, 0.07], [2.15, 1.42, 0, 0.045], [2.07, 1.5, 0, 0.022]], "@horn", bone="head", k=0.035, kc=0.008)
S.cone("hornTip", [2.13, 1.45, 0], [2.07, 1.5, 0], 0.036, 0.022, "@hornTip", bone="head", k=0.01, kc=0.008)
S.tube("horn2", [[1.91, 1.04, 0, 0.1], [1.94, 1.22, 0, 0.068], [1.93, 1.34, 0, 0.03]], "@horn", bone="head", k=0.035, kc=0.008)
S.cone("ear", [1.55, 1.42, 0.15], [1.6, 1.64, 0.24], 0.06, 0.07, "@ear", bone="earL", k=0.03, kc=0.01, mirror=True)
S.ell("earTip", [1.61, 1.66, 0.245], [0.07, 0.035, 0.065], "@ear", bone="earL", k=0.03, kc=0.01, rot=[-20, 0, 15], mirror=True)
S.ell("earIn", [1.645, 1.6, 0.23], [0.02, 0.08, 0.045], "@earIn", bone="earL", k=0.01, kc=0.004, rot=[-20, 0, 15], mirror=True)

for p in S:   # (the hind legs set further back under the rump: no overhanging buttock)
    if p.get("bone", "") in ("legHLu", "legHLl", "footHL"):
        for key in ("c", "a", "b"):
            if key in p: p[key][0] += HB
        for q in p.get("pts", []): q[0] += HB
floorR(S, ("horn",), 0.021)
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; each shape rides the bone it names; `mirror` makes the right one from the left",
    "keep": ["tail\\d*", "tailTuft"],
    "mesh": {"cell": 0.034, "tris": [7500, 2400]},
    "shape": [fix_order(p) for p in S],
    "eyes": {"at": [1.9, 1.04, 0.19], "from": [1.75, 1.04, 0], "r": 0.022, "iris": "#2a2018", "pupil": "round", "lid": "@lid"},
}
d["sculpt"]["shade"] = {"back": 0.84, "belly": 1.1, "low": 0.96, "on": "@skin"}
save(P, d)
print(len(S), "shapes")
