import math, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import *

P = "mammals/hippo"
d = load(P)
d["_about"] = ("HIPPOPOTAMUS (sculpt overlay, 2026-11-05): a 1.5 m bull, 3.7 m head and body -- a broad barrel slung low "
               "between very short pillar legs, the belly a hand off the knees; a huge boxy head, the face pinched behind a "
               "muzzle WIDER than the brow with swollen lip pads, the eyes, ears and nostrils raised on top in a line; folds "
               "round the thick neck; four-toed feet; a short flat tail. Grey-brown above, pink below and round eyes, ears and lips.")
d["rear"] = [-0.75, 1.0, 0, 0.75, 0.5, 0.7]
d["front"] = [0.45, 1.02, 0, 0.75, 0.5, 0.7]
d["neck"] = [0.95, 1.0, 0, 1.2, 1.02, 0, 0.42, 0.36]
d["head"] = [1.3, 1.05, 0, 0.36]
d["muzzle"] = [1.5, 0.95, 0, 1.95, 0.9, 0, 0.26, 0.26]
d["ears"] = [1.22, 1.32, 0.17, 1.2, 1.42, 0.2, 0.05, 0.035]
d["eyes"] = [1.47, 1.3, 0.2, 0.03]
HB = -0.1
d["legs"] = {"front": [0.72, 0.75, 0.42, 0.38], "hind": [-0.88 + HB, 0.78, 0.38, 0.38], "radii": [0.2, 0.16, 0.14],
             "foot": [0.15, 0.06, 0.15]}
d["tail"] = {"c": [-1.68, 1.05], "R": 0.35, "a0": 0, "a1": -1.1, "r1": 0.055, "r2": 0.03, "n": 3, "tuft": 0.04,
             "tuftColor": "#3e3430", "sway": 24, "speed": 1.6}
d["c"].update({"body": "#6b605b", "muzzle": "#6b605b", "leg": "#625853", "tail": "#625853", "ear": "#5e5450",
               "skin": "#6e5f58", "back": "#625550", "flank": "#7c675e", "pink": "#a07468", "belly": "#a47c70", "lip": "#8e7268", "front": "#8a6a64",
               "dark": "#544a46", "nail": "#8a7c70", "nostril": "#2a2220", "eye": "#3a251a", "lid": "#8c6458"})

S = Shapes()
mot = {}   # (no mottle: it read as polka dots; the shade carries the tone)
S.ell("barrel", [-0.15, 0.95, 0], [1.15, 0.5, 0.72], "@skin", k=0.16, **mot)
S.ell("shoulder", [0.58, 1.02, 0], [0.5, 0.5, 0.66], "@back", k=0.14, **mot)
S.ell("rump", [-0.8, 1.06, 0], [0.52, 0.52, 0.64], "@back", k=0.16, **mot)
S.ell("flank", [-0.1, 0.78, 0.3], [0.9, 0.3, 0.42], "@flank", k=0.14, mirror=True, **mot)
S.ell("belly", [-0.1, 0.54, 0], [0.85, 0.24, 0.6], "@belly", k=0.16)
S.ell("neck", [1.0, 1.0, 0], [0.32, 0.42, 0.5], "@skin", k=0.12)
S.ell("fold1", [0.98, 1.0, 0], [0.045, 0.43, 0.52], "@dark", k=0.06, kc=0.04)
S.ell("fold2", [1.1, 0.98, 0], [0.04, 0.39, 0.48], "@dark", k=0.06, kc=0.04)
S.ell("throat", [1.05, 0.78, 0], [0.32, 0.22, 0.36], "@pink", k=0.1)
# ---- legs: short pillars, four toes
S.ell("elbow", [0.66, 0.66, 0.42], [0.22, 0.24, 0.19], "@skin", bone="legFLu", k=0.08, mirror=True)
S.cone("arm", [0.72, 0.78, 0.42], [0.73, 0.36, 0.42], 0.22, 0.17, "@leg", bone="legFLu", k=0.07, mirror=True)
S.cone("fore", [0.73, 0.37, 0.42], [0.75, 0.1, 0.42], 0.165, 0.15, "@leg", bone="legFLl", k=0.05, mirror=True)
S.ell("foot", [0.77, 0.065, 0.42], [0.17, 0.065, 0.16], "@dark", bone="footFL", k=0.04, mirror=True)
S.ell("thigh", [-0.86, 0.78, 0.38], [0.32, 0.34, 0.24], "@skin", bone="legHLu", k=0.1, mirror=True)
S.cone("shank", [-0.86, 0.42, 0.38], [-0.84, 0.1, 0.38], 0.18, 0.15, "@leg", bone="legHLl", k=0.05, mirror=True)
S.ell("hfoot", [-0.82, 0.065, 0.38], [0.17, 0.065, 0.16], "@dark", bone="footHL", k=0.04, mirror=True)
for i, a in enumerate([-50, -17, 17, 50]):
    t = math.radians(a)
    S.ell(f"nail{i}", [0.77 + 0.16 * math.cos(t), 0.045, 0.42 + 0.15 * math.sin(t)], [0.04, 0.035, 0.035], "@nail",
          bone="footFL", k=0.01, kc=0.004, mirror=True)
    S.ell(f"hnail{i}", [-0.82 + 0.16 * math.cos(t), 0.045, 0.38 + 0.15 * math.sin(t)], [0.04, 0.035, 0.035], "@nail",
          bone="footHL", k=0.01, kc=0.004, mirror=True)
# ---- the head: a flat brow, raised eyes, the face pinched before a broad muzzle with lip pads, a deep lower jaw
S.ell("cranium", [1.28, 1.1, 0], [0.32, 0.27, 0.3], "@skin", bone="head", k=0.1, **mot)
S.ell("orbit", [1.43, 1.28, 0.19], [0.1, 0.08, 0.09], "@skin", bone="head", k=0.06, mirror=True)
S.ell("orbitPink", [1.47, 1.26, 0.22], [0.06, 0.05, 0.06], "@pink", bone="head", k=0.03, kc=0.02, mirror=True)
S.ell("face", [1.62, 1.07, 0], [0.3, 0.19, 0.22], "@skin", bone="head", k=0.1)
S.box("muzzle", [1.86, 0.96, 0], [0.3, 0.22, 0.36], "@skin", bone="head", k=0.1, round=0.1)
S.ell("snoutFront", [2.0, 0.92, 0], [0.16, 0.2, 0.3], "@front", bone="head", k=0.08)
S.ell("pad", [1.93, 0.86, 0.22], [0.2, 0.2, 0.16], "@front", bone="head", k=0.07, kc=0.03, mirror=True)
S.ell("nares", [1.98, 1.2, 0.09], [0.085, 0.07, 0.075], "@skin", bone="head", k=0.03, mirror=True)   # (audit 2026-11-07: raised -- they were smoothed into the box)
S.ell("nostril", [2.02, 1.262, 0.088], [0.022, 0.014, 0.036], "@nostril", bone="head", k=0.008, kc=0.002, rot=[0, 30, 0], mirror=True)
S.ell("jaw", [1.62, 0.72, 0], [0.44, 0.24, 0.31], "@pink", bone="head", k=0.08)
S.ell("jowl", [1.24, 0.88, 0.24], [0.26, 0.22, 0.15], "@skin", bone="head", k=0.08, mirror=True)
S.ell("ear", [1.2, 1.4, 0.17], [0.035, 0.065, 0.05], "@skin", bone="earL", k=0.025, kc=0.008, rot=[-15, 0, -10], mirror=True)
S.ell("earIn", [1.225, 1.4, 0.17], [0.012, 0.045, 0.034], "@pink", bone="earL", k=0.01, kc=0.004, rot=[-15, 0, -10], mirror=True)

for p in S:   # (the hind legs set further back under the rump: no overhanging buttock)
    if p.get("bone", "") in ("legHLu", "legHLl", "footHL"):
        for key in ("c", "a", "b"):
            if key in p: p[key][0] += HB
        for q in p.get("pts", []): q[0] += HB
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; each shape rides the bone it names; `mirror` makes the right one from the left",
    "keep": ["tail\\d*", "tailTuft"],
    "mesh": {"cell": 0.03, "tris": [7000, 2200]},
    "shape": [fix_order(p) for p in S],
    "eyes": {"at": [1.47, 1.3, 0.2], "from": [1.36, 1.22, 0], "r": 0.028, "iris": "@eye", "pupil": "round", "lid": "@lid"},
}
d["sculpt"]["shade"] = {"back": 0.84, "belly": 1.1, "low": 0.96, "on": "@skin"}
# (audit 2026-11-07) the CALF variant (index.html kin("hippo","calf")) -- load() reads orig/, so it is set here
d["variants"] = {"calf": {"scale": 0.32, "colors": {"flank": "#8c6e64", "pink": "#b48274", "belly": "#b4887a", "front": "#9a7468"}}}
save(P, d)
print(len(S), "shapes")
