import math, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import *

P = "mammals/elephant"
d = load(P)
# ---- the rig: an African bush elephant bull, 3.05 m at the shoulder, torso 3.3 m
d["_about"] = ("AFRICAN BUSH ELEPHANT (sculpt overlay, 2026-11-05): a 3 m bull -- highest at the withers, the back dipping "
               "into a saddle and the rump sloping off; a deep barrel on pillar legs (the fore column folds at the wrist, the hind "
               "at a low forward knee), round fore feet with pale nails, oval hind ones; a big sloping head, Africa-shaped ears "
               "laid back over the shoulders, the trunk hanging almost to the ground (its own bone: it still swings), tusks curving "
               "out and up, the tail to the hocks with a black tuft. Skin wrinkled in rings on trunk and legs.")
d["rear"] = [-0.75, 2.12, 0, 1.0, 0.78, 0.78]
d["front"] = [0.72, 2.2, 0, 0.95, 0.82, 0.8]
d["head"] = [2.0, 2.5, 0, 0.6]
d["muzzle"] = [2.35, 2.2, 0, 0.3, 0.3, 0.3]
d["eyes"] = [2.12, 2.55, 0.36, 0.035]
d["legs"] = {"front": [1.12, 2.0, 0.48, 1.45], "hind": [-1.02, 1.95, 0.43, 0.95],
             "radii": [0.3, 0.25, 0.22], "foot": [0.3, 0.12, 0.28], "kneeH": 1}
# (the tail leaves the rump going down and back and hangs to the hocks)
d["tail"] = {"c": [0.282, 2.022], "R": 2.0, "a0": 2.9, "a1": 3.4, "r1": 0.075, "r2": 0.035, "n": 4, "tuft": 0.1,
             "tuftColor": "#2a241e", "sway": 12, "speed": 0.7}
for x in d["extras"]:
    if x.get("id") == "trunk":   # (the trunk's bone: its root at the new face; it swings fore and aft as before)
        x["arc"]["c"] = [4.02, 2.1]
    if x.get("id") == "tusk":
        x["from"] = [2.36, 1.98, 0.22]; x["to"] = [3.1, 1.58, 0.34]
d["c"].update({"body": "#7d756e", "muzzle": "#7d756e", "leg": "#68615b", "tail": "#68615b", "eye": "#3a2616",
               "skin": "#7a7068", "back": "#6c635c", "dark": "#5a524c", "belly": "#857a70", "dust": "#86776a", "ear": "#6e655e", "earIn": "#8d7b76",
               "nail": "#8f887c", "tusk": "#d2c4a0", "trunk": "#6b645e", "lid": "#3e3732"})

S = Shapes()
leaf = {}   # (no pattern on the hide: the mottle read as a dot lattice; tone from shade)   # (the hide: a fine crackle network)
# ---- trunk of the body
S.ell("chest", [0.72, 2.2, 0], [0.86, 0.8, 0.74], "@skin", k=0.18, **leaf)
S.ell("belly", [-0.12, 1.92, 0], [1.05, 0.62, 0.82], "@belly", k=0.2, **leaf)
S.ell("withers", [0.72, 2.7, 0], [0.6, 0.4, 0.52], "@back", k=0.16, **leaf)
S.ell("back", [-0.2, 2.42, 0], [0.9, 0.36, 0.64], "@back", k=0.2, **leaf)
S.ell("rump", [-0.9, 2.17, 0], [0.74, 0.58, 0.7], "@skin", k=0.18, rot=[0, 0, 25], **leaf)
S.ell("scapula", [0.95, 2.3, 0.5], [0.4, 0.62, 0.26], "@skin", bone="legFLu", k=0.12, rot=[0, 0, 15], mirror=True, **leaf)
S.ell("haunch", [-1.0, 1.9, 0.42], [0.5, 0.62, 0.3], "@skin", bone="legHLu", k=0.14, rot=[0, 0, -6], mirror=True, **leaf)
S.ell("neck", [1.45, 2.5, 0], [0.42, 0.62, 0.56], "@skin", k=0.16, **leaf)
S.ell("dewlap", [1.5, 1.95, 0], [0.4, 0.3, 0.42], "@skin", k=0.14, **leaf)
# ---- fore legs: one column from the shoulder to the wrist, the foot under it
bark = {"pat": "bark"}
S.tube("arm", [[1.1, 2.0, 0.48, 0.33], [1.12, 1.6, 0.48, 0.3], [1.1, 1.3, 0.48, 0.255]], "@skin", bone="legFLu", k=0.1, mirror=True, **bark)
S.ell("elbow", [0.95, 1.33, 0.47], [0.16, 0.15, 0.17], "@skin", bone="legFLu", k=0.08, mirror=True)
S.cone("forearm", [1.1, 1.3, 0.48], [1.13, 0.6, 0.48], 0.25, 0.205, "@leg", bone="legFLu", k=0.07, mirror=True, **bark)
S.cone("wrist", [1.13, 0.62, 0.48], [1.15, 0.2, 0.48], 0.205, 0.24, "@dust", bone="legFLl", k=0.06, mirror=True, **bark)
S.ell("foot", [1.17, 0.13, 0.48], [0.29, 0.13, 0.27], "@dust", bone="footFL", k=0.05, mirror=True)
for i, a in enumerate([-48, -16, 16, 48]):
    t = math.radians(a)
    S.ell(f"nail{i}", [1.17 + 0.25 * math.cos(t), 0.06, 0.48 + 0.235 * math.sin(t)], [0.05, 0.05, 0.055], "@nail",
          bone="footFL", k=0.015, kc=0.004, rot=[0, -a, 0], mirror=True)
# ---- hind legs: the thigh in the body to a low knee, the shank to an oval foot
S.ell("knee", [-0.9, 1.08, 0.44], [0.27, 0.24, 0.25], "@skin", bone="legHLu", k=0.1, mirror=True)
S.cone("thigh", [-1.0, 1.9, 0.43], [-0.92, 1.08, 0.43], 0.36, 0.26, "@skin", bone="legHLu", k=0.12, mirror=True, **bark)
S.cone("shank", [-0.93, 1.05, 0.43], [-1.0, 0.2, 0.43], 0.245, 0.215, "@dust", bone="legHLl", k=0.07, mirror=True, **bark)
S.ell("hfoot", [-0.97, 0.12, 0.43], [0.28, 0.12, 0.23], "@dust", bone="footHL", k=0.05, mirror=True)
for i, a in enumerate([-35, 0, 35]):
    t = math.radians(a)
    S.ell(f"hnail{i}", [-0.97 + 0.255 * math.cos(t), 0.055, 0.43 + 0.205 * math.sin(t)], [0.045, 0.045, 0.05], "@nail",
          bone="footHL", k=0.015, kc=0.004, rot=[0, -a, 0], mirror=True)
# ---- the head: a big sloping skull, the trunk's broad root, cheeks, a pointed lower lip, tusk sheaths
S.ell("skull", [1.95, 2.42, 0], [0.6, 0.62, 0.5], "@skin", bone="head", k=0.16, rot=[0, 0, -12], **leaf)
S.ell("forehead", [2.22, 2.62, 0], [0.34, 0.46, 0.42], "@skin", bone="head", k=0.12, rot=[0, 0, -18], **leaf)
S.ell("temple", [1.88, 2.8, 0.3], [0.3, 0.25, 0.16], "@skin", bone="head", k=0.1, mirror=True, **leaf)
S.ell("cheek", [1.95, 2.1, 0.22], [0.36, 0.3, 0.22], "@skin", bone="head", k=0.1, mirror=True, **leaf)
S.cone("trunkRoot", [2.3, 2.45, 0], [2.43, 2.05, 0], 0.3, 0.22, "@skin", bone="head", k=0.1, **leaf)
S.ell("sheath", [2.35, 1.97, 0.21], [0.16, 0.15, 0.13], "@skin", bone="head", k=0.07, mirror=True)
S.ell("lip", [2.12, 1.83, 0], [0.24, 0.12, 0.18], "@dark", bone="head", k=0.07, rot=[0, 0, -15])
S.tube("tusk", [[2.34, 1.99, 0.21, 0.09], [2.62, 1.72, 0.28, 0.08], [2.92, 1.56, 0.33, 0.066], [3.16, 1.6, 0.33, 0.046]],
       "@tusk", bone="head", k=0.012, kc=0.004, mirror=True)
# ---- the trunk on its own bone: hanging nearly to the ground, the tip curled forward
S.tube("trunk", [[2.42, 2.12, 0, 0.21], [2.5, 1.72, 0, 0.175], [2.53, 1.28, 0, 0.135], [2.52, 0.88, 0, 0.105],
                 [2.56, 0.52, 0, 0.083], [2.7, 0.36, 0, 0.07]], "@trunk", bone="trunk", k=0.06, **bark)
S.ell("trunkTip", [2.75, 0.35, 0], [0.07, 0.06, 0.07], "@dark", bone="trunk", k=0.03, kc=0.01)
# ---- the ears: a broad upper lobe laid back over the shoulder and a pointed lower one; pinker inside
# (each a slab of an ellipsoid inside a ROLLED RIM: a tube round its outline, thicker than a grid cell, so the edge
#  meshes as a smooth curve instead of a thin aliased sawtooth; the rim runs only where the other lobe does not cover it)
def rotM(deg):
    x, y, z = [math.radians(v) for v in deg]
    a, b, c, d_, e, f = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    return [c * e, -c * f, d_, a * f + b * e * d_, a * e - b * f * d_, -b * c, b * f - a * e * d_, b * e + a * f * d_, a * c]
EARS = [([1.3, 2.35, 0.74], [0.78, 0.88], [0, 30, -4]), ([1.5, 1.6, 0.68], [0.3, 0.45], [0, 30, -26])]
RIM = 0.065
def toW(E, u, v):
    c, r, rot = E; R = rotM(rot)
    return [c[i] + R[3 * i] * u + R[3 * i + 1] * v for i in range(3)]
def inside(E, p):
    c, r, rot = E; R = rotM(rot); q = [p[i] - c[i] for i in range(3)]
    u = R[0] * q[0] + R[3] * q[1] + R[6] * q[2]; v = R[1] * q[0] + R[4] * q[1] + R[7] * q[2]
    return (u / r[0]) ** 2 + (v / r[1]) ** 2 < 0.97
for n, E in enumerate(EARS):
    c, r, rot = E; o = EARS[1 - n]
    S.ell("ear" if n == 0 else "earLobe", c, [r[0] - RIM * 0.9, r[1] - RIM * 0.9, 0.075], "@ear", bone="earL", k=0.1, kc=0.01, rot=rot, mirror=True)
    N = 40; ring = []
    for i in range(N):
        t = 2 * math.pi * i / N
        ring.append((toW(E, (r[0] - RIM) * math.cos(t), (r[1] - RIM) * math.sin(t)), inside(o, toW(E, r[0] * math.cos(t), r[1] * math.sin(t)))))
    # (the runs of the outline that are open: start the walk at a covered point so no run wraps)
    s0 = next((i for i, (_, cov) in enumerate(ring) if cov), None)
    order = ring[s0:] + ring[:s0] if s0 is not None else ring + ring[:1]
    runs, cur = [], []
    for p, cov in order:
        if cov:
            if len(cur) > 1: runs.append(cur)
            cur = []
        else: cur.append(p)
    if len(cur) > 1: runs.append(cur)
    for j, run in enumerate(runs):
        S.tube(f"earRim{n}_{j}", [[*p, RIM] for p in run[::2] + ([run[-1]] if len(run) % 2 == 0 else [])], "@ear", bone="earL", k=0.06, kc=0.01, mirror=True)
#S.ell("earRim", [1.5, 3.06, 0.64], [0.42, 0.07, 0.06], "@ear", bone="earL", k=0.04, rot=[0, 18, 8], mirror=True)
S.ell("earRoot", [1.78, 2.5, 0.48], [0.12, 0.42, 0.1], "@skin", bone="earL", k=0.08, mirror=True, **leaf)

d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; each shape rides the bone it names; `mirror` makes the right one from the left",
    "keep": ["tail\\d*", "tailTuft"],
    "mesh": {"cell": 0.055, "tris": [8500, 2700], "focus": {"head": 4, "earL": 4, "earR": 4}},
    "shape": [fix_order(p) for p in S],
    "eyes": {"at": [2.2, 2.45, 0.42], "from": [2.0, 2.45, 0], "r": 0.034, "iris": "@eye", "pupil": "round", "lid": "@lid"},
}
d["sculpt"]["shade"] = {"back": 0.85, "belly": 1.08, "low": 0.96, "on": "@skin"}
save(P, d)
print(len(S), "shapes")
