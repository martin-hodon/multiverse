import math, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import *

P = "dinosaurs/tyrannosaur"
d = load(P)
d["_about"] = ("TYRANNOSAURUS REX (sculpt overlay, 2026-11-05, after Hartman's skeletals of Sue and Stan): 12.2 m nose to "
               "tail, the hips 3.15 m up -- a horizontal backbone balanced over the hips, a deep chest and gastral belly with the "
               "pubic boot under it, a long tail held level and deep at its root (the caudofemoralis), a short thick S-neck; "
               "a 1.45 m skull deep and broad behind, narrowing to the snout, brow bosses over forward-set eyes, lipped jaws; "
               "tiny two-fingered arms; massive thighs, slim shanks, a long metatarsus to three forward toes (the ankle off "
               "the ground). Countershaded: dark olive back, tan flanks, cream belly, scaled all over.")
d["rear"] = [-0.2, 3.3, 0, 1.5, 0.75, 0.62]
d["front"] = [1.4, 3.1, 0, 1.2, 0.8, 0.6]
d["neck"] = [2.3, 3.5, 0, 3.4, 4.05, 0, 0.6, 0.5]
d["head"] = [3.85, 4.25, 0, 0.5]
d["eyes"] = [4.08, 4.45, 0.33, 0.06]
L = d["legs"]
L["hind"] = [-0.1, 3.15, 0.66, 1.25]
L["bend"] = [1, 1.06]
d["tail"] = {"c": [-0.9, -36.65], "R": 40, "a0": 1.5708, "a1": 1.7258, "r1": 0.6, "r2": 0.05, "n": 7, "sway": 7, "speed": 0.3}
for x in d["extras"]:
    if x.get("id") == "arm": x["from"] = [2.1, 2.72, 0.5]; x["to"] = [2.3, 2.4, 0.55]
    if x.get("id") == "fore": x["from"] = [2.3, 2.4, 0.55]; x["to"] = [2.55, 2.36, 0.52]
    if x.get("id") == "snout": x["from"] = [3.95, 4.3, 0]; x["to"] = [5.0, 4.15, 0]
    if x.get("id") == "jaw": x["ell"] = [4.35, 3.85, 0, 0.75, 0.18, 0.3]
d["c"].update({"back": "#4b4630", "body": "#635b3d", "flank": "#6f6644", "belly": "#b9a77f", "head": "#524a31",
               "lip": "#6a6044", "leg": "#5a5338", "foot": "#3b3524", "claw": "#2a251c", "nostril": "#2a2418",
               "eye": "#d9a520", "lid": "#3a3424", "mouth": "#3a2a22", "brow": "#4a4430"})
sc = {"pat": "scales", "frame": {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.55}}
S = Shapes()
# ---- the trunk, level: hips, a deep ribcage, the gastral belly and the pubic boot; countershaded
S.ell("hips", [-0.1, 3.38, 0], [0.95, 0.46, 0.55], "@back", k=0.18, **sc)
S.ell("torso", [0.9, 3.08, 0], [1.5, 0.66, 0.62], "@body", k=0.2, **sc)
S.ell("ribs", [1.45, 2.95, 0], [0.95, 0.76, 0.58], "@body", k=0.18, **sc)
S.ell("spine", [0.8, 3.5, 0], [1.6, 0.26, 0.36], "@back", k=0.18, kc=0.12, **sc)
S.ell("belly", [1.05, 2.5, 0], [1.15, 0.32, 0.46], "@belly", k=0.16, kc=0.12, **sc)
S.ell("boot", [0.25, 2.3, 0], [0.36, 0.14, 0.2], "@belly", k=0.14, **sc)
S.ell("chest", [2.05, 2.95, 0], [0.5, 0.58, 0.48], "@body", k=0.16, **sc)
S.ell("breast", [2.1, 2.62, 0], [0.42, 0.3, 0.38], "@belly", k=0.12, kc=0.1, **sc)
# ---- the tail on its own bone: level, deep at the root, whip-thin at the end; its underside pale
S.tube("tail", [[-0.6, 3.32, 0, 0.6], [-1.6, 3.3, 0, 0.47], [-2.8, 3.14, 0, 0.34], [-4.0, 2.95, 0, 0.23],
                [-5.2, 2.86, 0, 0.13], [-6.4, 2.9, 0, 0.08], [-7.05, 2.95, 0, 0.045]], "@body", bone="tail", k=0.12, **sc)
S.ell("tailRoot", [-1.25, 3.2, 0], [0.95, 0.6, 0.44], "@body", bone="tail", k=0.16, **sc)
S.tube("tailRidge", [[-0.4, 3.6, 0, 0.3], [-2.0, 3.48, 0, 0.22], [-3.8, 3.12, 0, 0.14], [-5.6, 2.98, 0, 0.07]], "@back",
       bone="tail", k=0.14, kc=0.12, **sc)
S.tube("tailBelly", [[-0.7, 2.95, 0, 0.42], [-2.2, 3.0, 0, 0.27], [-3.8, 2.8, 0, 0.16], [-5.2, 2.76, 0, 0.08]], "@belly",
       bone="tail", k=0.14, kc=0.12, **sc)
# ---- the neck: short, thick, rising in an S to the head
S.tube("neck", [[2.05, 3.3, 0, 0.6], [2.7, 3.6, 0, 0.55], [3.25, 3.95, 0, 0.5], [3.65, 4.1, 0, 0.45]], "@body", bone="neck", k=0.16, **sc)
S.tube("nape", [[2.0, 3.6, 0, 0.34], [2.8, 3.9, 0, 0.3], [3.5, 4.3, 0, 0.26]], "@back", bone="neck", k=0.14, kc=0.12, **sc)
S.ell("throat", [2.95, 3.35, 0], [0.5, 0.28, 0.36], "@flank", bone="neck", k=0.14, kc=0.1, **sc)
# ---- the head: deep and broad behind, the snout narrower; lips over the teeth
S.box("cranium", [3.98, 4.28, 0], [0.36, 0.3, 0.4], "@head", bone="head", k=0.12, round=0.14, **sc)
S.box("snout", [4.6, 4.22, 0], [0.52, 0.2, 0.22], "@head", bone="head", k=0.14, round=0.1, rot=[0, 0, -9], **sc)
S.ell("roof", [4.35, 4.46, 0], [0.8, 0.12, 0.24], "@brow", bone="head", k=0.12, rot=[0, 0, -12], **sc)
S.ell("muzzle", [5.0, 4.1, 0], [0.14, 0.16, 0.19], "@head", bone="head", k=0.08, **sc)
S.ell("upperLip", [4.5, 3.98, 0], [0.62, 0.1, 0.25], "@lip", bone="head", k=0.07, kc=0.04, **sc)
S.box("jawBack", [3.95, 3.82, 0], [0.34, 0.2, 0.42], "@head", bone="head", k=0.12, round=0.12, **sc)
S.box("jaw", [4.55, 3.82, 0], [0.5, 0.11, 0.22], "@head", bone="head", k=0.12, round=0.08, rot=[0, 0, 4], **sc)
S.ell("mouth", [4.55, 3.92, 0], [0.62, 0.04, 0.42], "@mouth", bone="head", k=0.02, op="sub")
S.ell("boss", [4.02, 4.6, 0.3], [0.15, 0.08, 0.1], "@brow", bone="head", k=0.06, mirror=True)
S.ell("lacrimal", [4.28, 4.55, 0.22], [0.12, 0.07, 0.08], "@brow", bone="head", k=0.05, mirror=True)
S.ell("jugal", [4.0, 4.02, 0.4], [0.16, 0.09, 0.08], "@brow", bone="head", k=0.06, mirror=True)
S.ell("nostril", [5.05, 4.22, 0.12], [0.06, 0.04, 0.04], "@nostril", bone="head", k=0.01, kc=0.003, mirror=True)
# ---- the arms: tiny, two fingers
S.cone("arm", [2.1, 2.72, 0.5], [2.3, 2.4, 0.55], 0.11, 0.08, "@body", bone="armL", k=0.06, mirror=True, **sc)
S.cone("fore", [2.3, 2.4, 0.55], [2.53, 2.36, 0.52], 0.075, 0.055, "@body", bone="foreL", k=0.04, mirror=True, **sc)
for j, dz in enumerate([0.045, -0.045]):
    S.cone(f"finger{j}", [2.52, 2.36, 0.52 + dz], [2.68, 2.27, 0.52 + dz * 1.5], 0.05, 0.03, "@body", bone="foreL", k=0.015, mirror=True)
    S.cone(f"fclaw{j}", [2.67, 2.275, 0.52 + dz * 1.5], [2.75, 2.19, 0.52 + dz * 1.6], 0.03, 0.01, "@claw", bone="foreL", k=0.004, mirror=True)
# ---- the legs: a massive thigh, a slim shank, the ankle off the ground, a long metatarsus, three toes flat on it
x, z = -0.1, 0.66
S.ell("thigh", [x + 0.1, 2.42, z - 0.04], [0.66, 1.1, 0.44], "@body", bone="legHLu", k=0.25, rot=[0, 0, 12], mirror=True, **sc)
S.ell("knee", [x + 0.1, 1.92, z], [0.28, 0.24, 0.25], "@leg", bone="legHLu", k=0.1, mirror=True, **sc)
S.cone("shin", [x, 1.9, z], [x - 0.08, 0.72, z], 0.3, 0.2, "@leg", bone="legHLl", k=0.08, mirror=True, **sc)
S.ell("calf", [x - 0.12, 1.45, z], [0.27, 0.45, 0.23], "@leg", bone="legHLl", k=0.08, mirror=True, **sc)
S.sph("ankle", [x - 0.08, 0.68, z], 0.19, "@leg", bone="legHLl", k=0.06, mirror=True, **sc)
S.cone("metatarsus", [x - 0.08, 0.68, z], [x + 0.17, 0.17, z], 0.17, 0.13, "@leg", bone="legHLl", k=0.06, mirror=True, **sc)
for j, (ang, ln) in enumerate([(0, 0.82), (26, 0.62), (-26, 0.62)]):
    a = math.radians(ang); ux, uz = math.cos(a), math.sin(a)
    b = [x + 0.18, 0.12, z]
    p = lambda t, y, r: [b[0] + ux * t, y, b[2] + uz * t, r]
    S.tube(f"toe{j}", [p(0, 0.12, 0.11), p(ln * 0.45, 0.085, 0.085), p(ln, 0.06, 0.055)], "@foot", bone="footHL", k=0.05, mirror=True)
    e = p(ln, 0.06, 0)
    S.cone(f"claw{j}", e[:3], [e[0] + ux * 0.15, 0.025, e[2] + uz * 0.15], 0.045, 0.01, "@claw", bone="footHL", k=0.01, mirror=True)

d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; each shape rides the bone it names; `mirror` makes the right one from the left",
    "keep": [],
    "mesh": {"cell": 0.055, "tris": [9500, 3000]},
    "shape": [fix_order(p) for p in S],
    "eyes": {"at": [4.14, 4.45, 0.36], "from": [3.95, 4.42, 0], "r": 0.055, "iris": "@eye", "pupil": "round", "lid": "@lid"},
}
d["sculpt"]["shade"] = {"back": 0.78, "belly": 1.12, "low": 0.96, "on": "@body"}
save(P, d)
print(len(S), "shapes")
